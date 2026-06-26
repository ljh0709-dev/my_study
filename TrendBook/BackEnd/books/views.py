import hashlib
import json

from django.conf import settings
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .list_utils import BOOK_LIST_PAGE_SIZE, apply_book_list_filters

from ai.models import AISummary
from ai.serializers import AISummarySerializer
from trends.ai_client import AIServiceClient, AIServiceError

from .models import AladinCategory, Book, BookBookmark, BookRanking, MallType
from .serializers import (
    AladinCategorySerializer,
    BookDetailSerializer,
    BookListSerializer,
    BookRankingSerializer,
    BookBookmarkSerializer,
)


CATEGORY_RECOMMENDATION_LIMIT = 5


def get_preferred_book(isbn):
    return Book.objects.filter(isbn=isbn).annotate(
        mall_priority=Case(
            When(mall_type=MallType.BOOK, then=Value(0)),
            When(mall_type=MallType.FOREIGN, then=Value(1)),
            default=Value(2), output_field=IntegerField(),
        )
    ).order_by('mall_priority').first()


def category_descendant_filter(category):
    filters = {'mall_type': category.mall_type}
    for field in ('depth1', 'depth2', 'depth3', 'depth4', 'depth5'):
        value = getattr(category, field)
        if not value:
            break
        filters[field] = value
    return filters


def parse_preferred_depths(value):
    tokens = []
    for raw in (value or '').replace('|', ',').split(','):
        raw = raw.strip()
        if raw and raw not in tokens:
            tokens.append(raw)
    if not tokens:
        return []

    depths = []
    cid_tokens = [int(token) for token in tokens if token.isdigit()]
    cid_depths = {
        str(row['cid']): row['depth1']
        for row in AladinCategory.objects.filter(
            cid__in=cid_tokens,
            mall_type=MallType.BOOK,
            is_active=True,
        ).values('cid', 'depth1')
    }
    valid_depths = set(AladinCategory.objects.filter(
        mall_type=MallType.BOOK,
        is_active=True,
    ).values_list('depth1', flat=True).distinct())
    for token in tokens:
        depth = cid_depths.get(token) if token.isdigit() else token
        if depth in valid_depths and depth not in depths:
            depths.append(depth)
    return depths


def books_for_depth1(depth1):
    return Book.objects.filter(
        adult=False,
        mall_type=MallType.BOOK,
        category_links__category__mall_type=MallType.BOOK,
        category_links__category__depth1=depth1,
    )


def latest_ranked_books_for_depth1(depth1, list_type, limit=20):
    queryset = BookRanking.objects.filter(
        list_type=list_type,
        book__adult=False,
        book__mall_type=MallType.BOOK,
    )
    queryset = queryset.filter(
        Q(category__mall_type=MallType.BOOK, category__depth1=depth1)
        | Q(category__isnull=True, book__category_links__category__mall_type=MallType.BOOK, book__category_links__category__depth1=depth1)
    )
    latest_period = queryset.order_by('-period_start').values_list('period_start', flat=True).first()
    if latest_period is None:
        return []
    return [
        ranking.book
        for ranking in queryset.filter(period_start=latest_period)
        .select_related('book')
        .order_by('rank', '-book__sales_point')[:limit]
    ]


def mixed_ranked_books_for_depth1(depth1):
    bestsellers = latest_ranked_books_for_depth1(depth1, BookRanking.ListType.BESTSELLER)
    editors = latest_ranked_books_for_depth1(depth1, BookRanking.ListType.EDITOR_CHOICE)
    mixed = []
    seen_isbns = set()
    max_length = max(len(bestsellers), len(editors))
    for index in range(max_length):
        for rows in (bestsellers, editors):
            if index >= len(rows):
                continue
            book = rows[index]
            if book.isbn in seen_isbns:
                continue
            seen_isbns.add(book.isbn)
            mixed.append(book)
            if len(mixed) >= CATEGORY_RECOMMENDATION_LIMIT:
                return mixed
    if len(mixed) < CATEGORY_RECOMMENDATION_LIMIT:
        for book in books_for_depth1(depth1).order_by('-sales_point', '-customer_review_rank', 'id'):
            if book.isbn in seen_isbns:
                continue
            seen_isbns.add(book.isbn)
            mixed.append(book)
            if len(mixed) >= CATEGORY_RECOMMENDATION_LIMIT:
                break
    return mixed


def recommendation_category_for_book(book, depth1_values):
    book_depths = set(
        book.category_links.filter(
            category__mall_type=MallType.BOOK,
        ).values_list('category__depth1', flat=True)
    )
    for depth1 in depth1_values:
        if depth1 in book_depths:
            return depth1
    return depth1_values[0] if depth1_values else ''


def serialize_category_recommendations(books, depth1_values):
    rows = BookListSerializer(books, many=True).data
    single_category = len(depth1_values) == 1
    for row, book in zip(rows, books):
        category = recommendation_category_for_book(book, depth1_values)
        row['recommendation_category'] = category
        row['recommendation_reason'] = (
            f'{category} 카테고리의 베스트셀러와 추천 도서를 함께 반영했습니다.'
            if single_category
            else f'{category} 카테고리에서 판매지수와 평점이 높은 도서입니다.'
        )
    return rows


class BookListPagination(PageNumberPagination):
    page_size = BOOK_LIST_PAGE_SIZE
    page_query_param = 'page'


class BookListView(generics.ListAPIView):
    serializer_class = BookListSerializer
    pagination_class = BookListPagination

    def get_queryset(self):
        queryset = Book.objects.all()
        mall_type = self.request.query_params.get('mall_type')
        category_id = self.request.query_params.get('category_id')
        search = (
            self.request.query_params.get('q')
            or self.request.query_params.get('search')
            or ''
        ).strip()

        if mall_type in MallType.values:
            queryset = queryset.filter(mall_type=mall_type)
        if category_id:
            try:
                category = AladinCategory.objects.get(cid=int(category_id))
            except ValueError:
                return queryset.none()
            except AladinCategory.DoesNotExist:
                return queryset.none()
            descendant_categories = AladinCategory.objects.filter(
                **category_descendant_filter(category),
            )
            queryset = queryset.filter(
                Q(category_links__category=category)
                | Q(category_links__category__in=descendant_categories)
            )
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(author__icontains=search)
                | Q(publisher__icontains=search)
            )
        queryset = apply_book_list_filters(queryset, self.request.query_params)
        return queryset


class BookDetailView(generics.RetrieveAPIView):
    serializer_class = BookDetailSerializer

    def get_object(self):
        queryset = Book.objects.prefetch_related('category_links__category')
        mall_type = self.request.query_params.get('mall_type')
        if mall_type in MallType.values:
            queryset = queryset.filter(mall_type=mall_type)
        else:
            queryset = queryset.annotate(
                mall_priority=Case(
                    When(mall_type=MallType.BOOK, then=Value(0)),
                    When(mall_type=MallType.FOREIGN, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('mall_priority')

        book = queryset.filter(isbn=self.kwargs['isbn']).first()
        if book is None:
            raise Http404
        self.check_object_permissions(self.request, book)
        return book


class CategoryListView(generics.ListAPIView):
    serializer_class = AladinCategorySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = AladinCategory.objects.filter(is_active=True).order_by(
            'mall_type', 'depth1', 'depth2', 'depth3', 'depth4', 'depth5',
        )
        mall_type = self.request.query_params.get('mall_type')
        depth1 = self.request.query_params.get('depth1')
        if mall_type in MallType.values:
            queryset = queryset.filter(mall_type=mall_type)
        if depth1:
            queryset = queryset.filter(depth1=depth1)
        return queryset


class BestsellerListView(generics.ListAPIView):
    serializer_class = BookRankingSerializer

    def get_queryset(self):
        queryset = BookRanking.objects.filter(
            list_type=BookRanking.ListType.BESTSELLER,
        ).select_related('book', 'category')
        mall_type = self.request.query_params.get('mall_type')
        category_id = self.request.query_params.get('category_id')

        if mall_type in MallType.values:
            queryset = queryset.filter(book__mall_type=mall_type)
        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return queryset.none()
            queryset = queryset.filter(
                Q(category_id=category_id)
                | Q(category__isnull=True, book__category_links__category_id=category_id)
            )

        latest_period = queryset.order_by('-period_start').values_list(
            'period_start', flat=True,
        ).first()
        if latest_period is None:
            return queryset.none()
        return queryset.filter(period_start=latest_period).order_by('rank').distinct()


class BookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, isbn):
        book = get_preferred_book(isbn)
        if not book:
            return Response({'detail': '도서를 찾을 수 없습니다.'}, status=404)
        bookmark, created = BookBookmark.objects.get_or_create(user=request.user, book=book)
        return Response(
            BookBookmarkSerializer(bookmark).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, isbn):
        book = get_preferred_book(isbn)
        if not book:
            return Response(status=status.HTTP_204_NO_CONTENT)
        BookBookmark.objects.filter(user=request.user, book=book).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyBookmarkListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookBookmarkSerializer

    def get_queryset(self):
        return BookBookmark.objects.filter(user=self.request.user).select_related('book').order_by('-created_at')


class MyCategoryRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        depth1_values = parse_preferred_depths(request.user.preferred_genres)
        if not depth1_values:
            return Response([])

        if len(depth1_values) == 1:
            books = mixed_ranked_books_for_depth1(depth1_values[0])
        else:
            queryset = Book.objects.none()
            for depth1 in depth1_values:
                queryset = queryset | books_for_depth1(depth1)
            books = list(
                queryset.distinct().order_by(
                    '-sales_point',
                    '-customer_review_rank',
                    'id',
                )[:CATEGORY_RECOMMENDATION_LIMIT]
            )
        return Response(serialize_category_recommendations(books, depth1_values))


def _book_analysis_payload(book, review_excerpts):
    return {
        'isbn': book.isbn,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'categories': [link.category.path for link in book.category_links.all()],
        'sales_point': book.sales_point,
        'customer_review_rank': float(book.customer_review_rank) if book.customer_review_rank is not None else None,
        'review_excerpts': review_excerpts,
    }


class BookAIAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, isbn):
        book = get_preferred_book(isbn)
        if not book:
            return Response({'detail': '도서를 찾을 수 없습니다.'}, status=404)
        summary = AISummary.objects.filter(book=book).first()
        if not summary:
            return Response({'book_isbn': book.isbn, 'status': 'not_started'})
        return Response(AISummarySerializer(summary).data)


class BookAIAnalysisGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, isbn):
        book = get_preferred_book(isbn)
        if not book:
            return Response({'detail': '도서를 찾을 수 없습니다.'}, status=404)
        review_excerpts = request.data.get('review_excerpts', [])
        if (
            not isinstance(review_excerpts, list)
            or len(review_excerpts) > 30
            or any(not isinstance(value, str) or not value.strip() or len(value) > 2000 for value in review_excerpts)
        ):
            return Response(
                {'detail': 'review_excerpts는 2,000자 이하 문자열 최대 30개여야 합니다.'}, status=400,
            )
        review_excerpts = [value.strip() for value in review_excerpts]
        payload = _book_analysis_payload(
            Book.objects.prefetch_related('category_links__category').get(pk=book.pk),
            review_excerpts,
        )
        digest = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode('utf-8'),
        ).hexdigest()
        summary, _ = AISummary.objects.get_or_create(book=book)
        force = request.data.get('force') in {True, 'true', 'True', '1', 1}
        if not force and summary.status == AISummary.Status.COMPLETED and summary.source_hash == digest:
            return Response(AISummarySerializer(summary).data)
        summary.status = AISummary.Status.PENDING
        summary.review_source_count = len(review_excerpts)
        summary.save(update_fields=['status', 'review_source_count', 'updated_at'])
        try:
            result = AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS).analyze_book(payload)
        except AIServiceError as exc:
            summary.status = AISummary.Status.FAILED
            summary.save(update_fields=['status', 'updated_at'])
            return Response({'code': 'AI_ANALYSIS_UNAVAILABLE', 'detail': str(exc)}, status=503)
        summary.sales_reason = result['sales_reason']
        summary.review_summary = result['review_summary']
        summary.model = result['model']
        summary.source_hash = digest
        summary.review_source_count = len(review_excerpts)
        summary.status = AISummary.Status.COMPLETED
        summary.save()
        return Response(AISummarySerializer(summary).data)
