import tempfile
from datetime import date
from io import StringIO
from pathlib import Path
from threading import Lock
from unittest.mock import patch

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from .aladin_catalog import (
    build_list_type_catalog,
    build_recent_books_catalog,
    load_book_category_ids,
    merge_fixture_files,
    normalized_to_fixture_row,
    raw_items_to_fixture_rows,
    sort_by_recent_publication,
    write_fixture_file,
)
from .embeddings import cosine_similarity, sync_book_embeddings
from .list_utils import get_recent_cutoff
from .models import AladinCategory, Book, BookCategory, BookEmbedding, BookRanking, MallType
from .services import normalize_aladin_item, upsert_aladin_items


class CategoryModelTests(TestCase):
    def test_supports_three_target_malls_and_builds_path(self):
        self.assertEqual(
            {choice for choice, _ in MallType.choices},
            {'BOOK', 'FOREIGN', 'EBOOK'},
        )
        category = AladinCategory.objects.create(
            cid=53513,
            name='가정의례',
            mall_type=MallType.BOOK,
            depth1='가정/요리/뷰티',
            depth2='결혼/가족',
            depth3='가정의례',
        )
        self.assertEqual(category.path, '가정/요리/뷰티 > 결혼/가족 > 가정의례')


class BookCategoryModelTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(isbn='9780000000001', title='테스트 도서')
        self.categories = [
            AladinCategory.objects.create(
                cid=cid,
                name=name,
                mall_type=MallType.BOOK,
                depth1='국내도서 테스트',
                depth2=name,
            )
            for cid, name in ((1, '분류 A'), (2, '분류 B'))
        ]

    def test_only_one_primary_category_is_allowed_per_book(self):
        BookCategory.objects.create(
            book=self.book,
            category=self.categories[0],
            is_primary=True,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookCategory.objects.create(
                book=self.book,
                category=self.categories[1],
                is_primary=True,
            )


class BookRankingModelTests(TestCase):
    def test_same_book_list_and_period_cannot_be_duplicated(self):
        book = Book.objects.create(isbn='9780000000002', title='랭킹 테스트 도서')
        values = {
            'book': book,
            'list_type': BookRanking.ListType.BESTSELLER,
            'rank': 1,
            'period_start': date(2026, 6, 22),
        }
        BookRanking.objects.create(**values)
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookRanking.objects.create(**values)


class BookAPITests(APITestCase):
    def setUp(self):
        self.category = AladinCategory.objects.create(
            cid=100,
            name='소설',
            mall_type=MallType.BOOK,
            depth1='소설/시/희곡',
            depth2='소설',
        )
        self.child_category = AladinCategory.objects.create(
            cid=101,
            name='한국소설',
            mall_type=MallType.BOOK,
            depth1='소설/시/희곡',
            depth2='소설',
            depth3='한국소설',
        )
        self.book = Book.objects.create(
            isbn='9780000000100',
            mall_type=MallType.BOOK,
            title='검색 가능한 국내도서',
            author='테스트 저자',
            publisher='테스트 출판사',
            sales_point=100,
        )
        BookCategory.objects.create(
            book=self.book,
            category=self.category,
            is_primary=True,
        )
        self.foreign_book = Book.objects.create(
            isbn='9780000000200',
            mall_type=MallType.FOREIGN,
            title='Foreign Book',
            sales_point=50,
        )
        self.child_category_book = Book.objects.create(
            isbn='9780000000500',
            mall_type=MallType.BOOK,
            title='하위 카테고리 도서',
            sales_point=20,
        )
        BookCategory.objects.create(
            book=self.child_category_book,
            category=self.child_category,
            is_primary=True,
        )
        BookRanking.objects.create(
            book=self.book,
            list_type=BookRanking.ListType.BESTSELLER,
            rank=1,
            period_start=date(2026, 6, 22),
        )

    def test_book_list_supports_search_mall_and_category_filters(self):
        response = self.client.get('/api/v1/books', {'q': '국내도서'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['isbn'], self.book.isbn)

        response = self.client.get('/api/v1/books', {'mall_type': MallType.FOREIGN})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['isbn'], self.foreign_book.isbn)

        response = self.client.get('/api/v1/books', {'category_id': self.category.cid})
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            {item['isbn'] for item in response.data['results']},
            {self.book.isbn, self.child_category_book.isbn},
        )

    def test_book_detail_returns_category_relationship(self):
        response = self.client.get(f'/api/v1/books/{self.book.isbn}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['isbn'], self.book.isbn)
        self.assertEqual(response.data['categories'][0]['category']['cid'], self.category.cid)

    def test_category_list_supports_mall_and_depth_filter(self):
        response = self.client.get(
            '/api/v1/categories',
            {'mall_type': MallType.BOOK, 'depth1': '소설/시/희곡'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual({item['cid'] for item in response.data}, {self.category.cid, self.child_category.cid})

    def test_bestseller_list_returns_latest_rankings(self):
        response = self.client.get('/api/v1/bestsellers', {'mall_type': MallType.BOOK})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['rank'], 1)
        self.assertEqual(response.data['results'][0]['book']['isbn'], self.book.isbn)

    def test_book_list_supports_section_ordering_and_page_size(self):
        cutoff = get_recent_cutoff()
        recent_book = Book.objects.create(
            isbn='9780000000300',
            mall_type=MallType.BOOK,
            title='최근 신간',
            pub_date=cutoff,
            sales_point=10,
        )
        old_book = Book.objects.create(
            isbn='9780000000400',
            mall_type=MallType.BOOK,
            title='오래된 도서',
            pub_date=cutoff.replace(year=cutoff.year - 1),
            sales_point=9999,
        )
        BookRanking.objects.create(
            book=old_book,
            list_type=BookRanking.ListType.BESTSELLER,
            rank=2,
            period_start=cutoff,
        )

        response = self.client.get('/api/v1/books', {'section': 'new', 'ordering': 'newest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['isbn'], recent_book.isbn)

        response = self.client.get('/api/v1/books', {'section': 'bestseller', 'ordering': 'popular'})
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['isbn'], old_book.isbn)

        recommended_book = Book.objects.create(
            isbn='9780000000600',
            mall_type=MallType.BOOK,
            title='편집자 추천 도서',
            sales_point=500,
        )
        BookRanking.objects.create(
            book=recommended_book,
            list_type=BookRanking.ListType.EDITOR_CHOICE,
            rank=1,
            period_start=cutoff,
        )
        BookRanking.objects.create(
            book=old_book,
            list_type=BookRanking.ListType.EDITOR_CHOICE,
            rank=3,
            period_start=cutoff,
        )
        response = self.client.get('/api/v1/books', {'section': 'recommended', 'ordering': 'popular'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            {item['isbn'] for item in response.data['results']},
            {recommended_book.isbn, old_book.isbn},
        )

        response = self.client.get('/api/v1/books', {'section': 'all', 'ordering': 'oldest', 'q': '오래된'})
        self.assertEqual(response.data['results'][0]['isbn'], old_book.isbn)

        for index in range(21):
            Book.objects.create(
                isbn=f'9780000001{index:03d}',
                mall_type=MallType.BOOK,
                title=f'페이지 도서 {index}',
                sales_point=index,
            )
        response = self.client.get('/api/v1/books', {'section': 'all', 'page': 1})
        self.assertEqual(len(response.data['results']), 12)
        response = self.client.get('/api/v1/books', {'section': 'all', 'page': 2})
        self.assertEqual(len(response.data['results']), 12)

    def test_category_recommendations_use_rankings_for_single_category(self):
        from django.contrib.auth import get_user_model

        cutoff = get_recent_cutoff()
        editor_book = Book.objects.create(
            isbn='9780000000700',
            mall_type=MallType.BOOK,
            title='편집자 추천 도서',
            sales_point=1,
        )
        BookCategory.objects.create(book=editor_book, category=self.category, is_primary=True)
        BookRanking.objects.create(
            book=editor_book,
            list_type=BookRanking.ListType.EDITOR_CHOICE,
            rank=1,
            period_start=cutoff,
        )
        user = get_user_model().objects.create_user(
            username='category-user',
            email='category@example.com',
            nickname='카테고리 사용자',
            password='pw',
            preferred_genres=str(self.category.cid),
        )
        self.client.force_authenticate(user)
        response = self.client.get('/api/v1/users/me/category-recommendations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(editor_book.isbn, [item['isbn'] for item in response.data])
        item = next(item for item in response.data if item['isbn'] == editor_book.isbn)
        self.assertEqual(item['recommendation_category'], self.category.depth1)
        self.assertIn('베스트셀러', item['recommendation_reason'])

    def test_category_recommendations_accept_depth1_preferences(self):
        from django.contrib.auth import get_user_model

        depth_book = Book.objects.create(
            isbn='9780000000704',
            mall_type=MallType.BOOK,
            title='Depth1 추천 도서',
            sales_point=7777,
            customer_review_rank=9.0,
        )
        BookCategory.objects.create(book=depth_book, category=self.category)
        user = get_user_model().objects.create_user(
            username='depth-category-user',
            email='depth-category@example.com',
            nickname='Depth 사용자',
            password='pw',
            preferred_genres=self.category.depth1,
        )
        self.client.force_authenticate(user)
        response = self.client.get('/api/v1/users/me/category-recommendations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(depth_book.isbn, [item['isbn'] for item in response.data])

    def test_category_recommendations_sort_multiple_categories_by_sales_and_review(self):
        from django.contrib.auth import get_user_model

        second_category = AladinCategory.objects.create(
            cid=200,
            name='경제',
            mall_type=MallType.BOOK,
            depth1='경제경영',
            depth2='경제',
        )
        high_sales = Book.objects.create(
            isbn='9780000000701',
            mall_type=MallType.BOOK,
            title='판매 높은 도서',
            sales_point=9000,
            customer_review_rank=8.0,
        )
        high_review = Book.objects.create(
            isbn='9780000000702',
            mall_type=MallType.BOOK,
            title='평점 높은 도서',
            sales_point=9000,
            customer_review_rank=9.5,
        )
        low_sales = Book.objects.create(
            isbn='9780000000703',
            mall_type=MallType.BOOK,
            title='판매 낮은 도서',
            sales_point=100,
            customer_review_rank=10.0,
        )
        BookCategory.objects.create(book=high_sales, category=self.category)
        BookCategory.objects.create(book=high_review, category=second_category)
        BookCategory.objects.create(book=low_sales, category=second_category)
        user = get_user_model().objects.create_user(
            username='multi-category-user',
            email='multi-category@example.com',
            nickname='복수 카테고리 사용자',
            password='pw',
            preferred_genres=f'not-a-cid,{self.category.cid},{second_category.cid}',
        )
        self.client.force_authenticate(user)
        response = self.client.get('/api/v1/users/me/category-recommendations')
        self.assertEqual(response.status_code, 200)
        isbns = [item['isbn'] for item in response.data]
        self.assertLess(isbns.index(high_review.isbn), isbns.index(high_sales.isbn))
        self.assertLess(isbns.index(high_sales.isbn), isbns.index(low_sales.isbn))
        item = next(item for item in response.data if item['isbn'] == high_review.isbn)
        self.assertEqual(item['recommendation_category'], second_category.depth1)
        self.assertIn('판매지수', item['recommendation_reason'])

    def test_category_recommendations_require_auth_and_ignore_invalid_cids(self):
        self.assertEqual(self.client.get('/api/v1/users/me/category-recommendations').status_code, 401)
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(
            username='invalid-category-user',
            email='invalid-category@example.com',
            nickname='무효 카테고리 사용자',
            password='pw',
            preferred_genres='abc,999999',
        )
        self.client.force_authenticate(user)
        response = self.client.get('/api/v1/users/me/category-recommendations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class AladinSyncServiceTests(TestCase):
    def test_normalizes_and_upserts_isbn13_category_and_ranking(self):
        raw = {
            'isbn': '1234567890',
            'isbn13': '9781234567890',
            'itemId': 42,
            'mallType': 'BOOK',
            'title': '  정규화 도서  ',
            'author': '저자',
            'categoryId': 777,
            'categoryName': '국내도서>소설/시/희곡>한국소설',
            'pubDate': '2026-06-22',
            'bestRank': 2,
        }

        normalized = normalize_aladin_item(raw)
        self.assertEqual(normalized['isbn'], '9781234567890')
        self.assertEqual(normalized['title'], '정규화 도서')

        first = upsert_aladin_items([raw], list_type='Bestseller')
        raw['title'] = '수정된 도서명'
        second = upsert_aladin_items([raw], list_type='Bestseller')

        self.assertEqual(first.created, 1)
        self.assertEqual(first.rankings, 1)
        self.assertEqual(second.updated, 1)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, '수정된 도서명')
        self.assertEqual(BookRanking.objects.count(), 1)
        self.assertEqual(Book.objects.get().categories.get().depth2, '한국소설')

    def test_skips_item_without_isbn13(self):
        result = upsert_aladin_items([{'isbn': '1234567890', 'title': 'ISBN10 전용'}])
        self.assertEqual(result.skipped, 1)
        self.assertFalse(Book.objects.exists())

    def test_skips_non_numeric_isbn13(self):
        result = upsert_aladin_items([{'isbn13': 'K982130876', 'title': '알라딘 전용 코드'}])
        self.assertEqual(result.skipped, 1)
        self.assertFalse(Book.objects.exists())


class LoadAladinFixtureCommandTests(TestCase):
    def test_fixture_uses_idempotent_sync_service(self):
        output = StringIO()
        call_command('load_aladin_books', period_start='2026-06-22', stdout=output)
        first_count = Book.objects.count()
        call_command('load_aladin_books', period_start='2026-06-22', stdout=output)

        self.assertGreater(first_count, 0)
        self.assertEqual(Book.objects.count(), first_count)
        self.assertEqual(BookRanking.objects.count(), first_count)


class BookmarkAPITests(APITestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_user(
            username='bookmark-user', email='bookmark@example.com', nickname='찜 사용자', password='pw',
        )
        self.book = Book.objects.create(isbn='9781111111111', title='찜할 책')

    def test_bookmark_is_authenticated_and_idempotent(self):
        self.assertEqual(self.client.post(f'/api/v1/books/{self.book.isbn}/bookmark').status_code, 401)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(f'/api/v1/books/{self.book.isbn}/bookmark').status_code, 201)
        self.assertEqual(self.client.post(f'/api/v1/books/{self.book.isbn}/bookmark').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/users/me/bookmarks').data['count'], 1)
        self.assertEqual(self.client.delete(f'/api/v1/books/{self.book.isbn}/bookmark').status_code, 204)
        self.assertEqual(self.client.get('/api/v1/users/me/bookmarks').data['count'], 0)


class FakeEmbeddingClient:
    def __init__(self):
        self.calls = 0

    def embed(self, texts):
        self.calls += 1
        return {
            'model': 'text-embedding-test', 'dimensions': 2,
            'vectors': [[1.0, index / 10] for index, _ in enumerate(texts)],
        }


class TextAwareEmbeddingClient:
    def __init__(self):
        self.calls = 0
        self.lock = Lock()

    def embed(self, texts):
        with self.lock:
            self.calls += 1
        vectors = []
        for text in texts:
            title = next(line for line in text.splitlines() if line.startswith('제목: '))
            vectors.append([float(title.rsplit(' ', 1)[-1]), 0.0])
        return {
            'model': 'text-embedding-test', 'dimensions': 2,
            'vectors': vectors,
        }


@override_settings(
    OPENAI_EMBEDDING_MODEL='text-embedding-test',
    OPENAI_EMBEDDING_DIMENSIONS=2,
)
class BookEmbeddingTests(TestCase):
    def test_embedding_sync_is_content_hash_idempotent(self):
        books = [
            Book.objects.create(isbn=f'97833333333{index:02d}', title=f'임베딩 도서 {index}', description='AI와 사회')
            for index in range(1, 3)
        ]
        client = FakeEmbeddingClient()
        first = sync_book_embeddings(books, ai_client=client, batch_size=2)
        refreshed = list(Book.objects.filter(id__in=[book.id for book in books]).prefetch_related('embedding', 'category_links__category'))
        second = sync_book_embeddings(refreshed, ai_client=client, batch_size=2)
        self.assertEqual((first.created, first.updated, first.skipped), (2, 0, 0))
        self.assertEqual(second.skipped, 2)
        self.assertEqual(client.calls, 1)
        self.assertEqual(BookEmbedding.objects.count(), 2)

    def test_embedding_sync_can_parallelize_batch_api_calls(self):
        books = [
            Book.objects.create(isbn=f'97833333334{index:02d}', title=f'임베딩 도서 {index}')
            for index in range(1, 4)
        ]
        client = TextAwareEmbeddingClient()

        result = sync_book_embeddings(books, ai_client=client, batch_size=1, max_workers=2)

        self.assertEqual((result.created, result.updated, result.skipped), (3, 0, 0))
        self.assertEqual(client.calls, 3)
        vectors_by_isbn = {
            item.book.isbn: item.vector
            for item in BookEmbedding.objects.select_related('book')
        }
        self.assertEqual(vectors_by_isbn['9783333333401'], [1.0, 0.0])
        self.assertEqual(vectors_by_isbn['9783333333402'], [2.0, 0.0])
        self.assertEqual(vectors_by_isbn['9783333333403'], [3.0, 0.0])

    def test_cosine_similarity(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)


class BookAIAnalysisAPITests(APITestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_user(
            username='analysis-user', email='analysis@example.com', nickname='분석 사용자', password='pw',
        )
        self.book = Book.objects.create(
            isbn='9784444444444', title='분석할 책', description='AI와 독서에 관한 책', sales_point=100,
        )

    @patch('books.views.AIServiceClient')
    def test_analysis_requires_auth_and_caches_gpt_result(self, client_class):
        client_class.return_value.analyze_book.return_value = {
            'sales_reason': 'AI 관심 증가와 연결됩니다.',
            'review_summary': '리뷰 본문이 없어 평가 경향을 단정할 수 없습니다.',
            'model': 'gpt-5.4-mini',
        }
        url = f'/api/v1/books/{self.book.isbn}/ai-analysis/generate'
        self.assertEqual(self.client.post(url, {'review_excerpts': []}, format='json').status_code, 401)
        self.assertEqual(self.client.get(f'/api/v1/books/{self.book.isbn}/ai-analysis').data['status'], 'not_started')
        self.client.force_authenticate(self.user)
        created = self.client.post(url, {'review_excerpts': []}, format='json')
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.data['status'], 'completed')
        self.assertEqual(created.data['model'], 'gpt-5.4-mini')
        client_class.return_value.analyze_book.reset_mock()
        cached = self.client.post(url, {'review_excerpts': []}, format='json')
        self.assertEqual(cached.status_code, 200)
        client_class.return_value.analyze_book.assert_not_called()

        client_class.return_value.analyze_book.return_value = {
            'sales_reason': '강제 갱신된 분석입니다.',
            'review_summary': '리뷰 없이 갱신했습니다.',
            'model': 'gpt-5.4-mini',
        }
        refreshed = self.client.post(url, {'review_excerpts': [], 'force': True}, format='json')
        self.assertEqual(refreshed.status_code, 200)
        self.assertEqual(refreshed.data['sales_reason'], '강제 갱신된 분석입니다.')
        client_class.return_value.analyze_book.assert_called_once()


class AladinCatalogTests(TestCase):
    def test_load_book_category_ids_filters_domestic_depth(self):
        csv_path = Path(__file__).resolve().parents[2] / 'aladin_Category_CID_20210927 (1).csv'
        categories = load_book_category_ids(csv_path, min_depth=4)
        self.assertGreater(len(categories), 1000)
        self.assertTrue(all(depth >= 4 for depth, _, _ in categories))

    def test_raw_items_to_fixture_rows_filters_by_pub_date(self):
        rows = raw_items_to_fixture_rows([
            {
                'isbn13': '9781111111111',
                'title': '최근 도서',
                'pubDate': '2026-01-01',
                'categoryName': '국내도서>소설',
            },
            {
                'isbn13': '9782222222222',
                'title': '오래된 도서',
                'pubDate': '2020-01-01',
                'categoryName': '국내도서>소설',
            },
        ], cutoff=date(2025, 6, 23))
        self.assertEqual(rows.collected, 1)
        self.assertEqual(rows.fixture_rows[0]['fields']['isbn'], '9781111111111')

    def test_build_recent_books_catalog_deduplicates_across_pages(self):
        item = {
            'isbn13': '9783333333333',
            'title': '신간 A',
            'pubDate': '2026-05-01',
            'categoryName': '국내도서>에세이',
            'salesPoint': 100,
        }

        class FakeClient:
            def item_list(self, **kwargs):
                return {'item': [item]}

        with patch('books.aladin_catalog.load_book_category_ids', return_value=[(4, 123, '에세이')]):
            result = build_recent_books_catalog(
                client=FakeClient(),
                category_csv=Path('unused.csv'),
                since_days=365,
                query_types=('ItemNewAll',),
                max_calls=10,
                pages_per_query=2,
                sleep_seconds=0,
            )

        self.assertEqual(result.collected, 1)
        self.assertEqual(result.api_calls, 2)
        self.assertEqual(result.fixture_rows[0]['fields']['title'], '신간 A')

    def test_build_recent_books_catalog_skips_invalid_category_errors(self):
        from books.clients import AladinAPIError

        class FlakyClient:
            def __init__(self):
                self.calls = 0

            def item_list(self, **kwargs):
                self.calls += 1
                if kwargs.get('category_id') == 999:
                    raise AladinAPIError('invalid category')
                return {'item': [{
                    'isbn13': '9785555555555',
                    'title': '유효 카테고리 도서',
                    'pubDate': '2026-05-01',
                    'categoryName': '국내도서>에세이',
                }]}

        with patch('books.aladin_catalog.load_book_category_ids', return_value=[
            (4, 999, '무효'),
            (4, 1000, '유효'),
        ]):
            result = build_recent_books_catalog(
                client=FlakyClient(),
                category_csv=Path('unused.csv'),
                since_days=365,
                query_types=('ItemNewAll',),
                max_calls=10,
                pages_per_query=1,
                sleep_seconds=0,
            )

        self.assertEqual(result.collected, 1)
        self.assertEqual(result.skipped_api_errors, 1)

    def test_sort_by_recent_publication_orders_newest_first(self):
        ordered = sort_by_recent_publication([
            {'isbn': '9781111111111', 'pub_date': date(2024, 1, 1), 'sales_point': 10},
            {'isbn': '9782222222222', 'pub_date': date(2026, 6, 1), 'sales_point': 1},
            {'isbn': '9783333333333', 'pub_date': None, 'sales_point': 99},
        ])
        self.assertEqual([item['isbn'] for item in ordered], [
            '9782222222222',
            '9781111111111',
            '9783333333333',
        ])

    def test_build_list_type_catalog_limits_to_target_count_by_pub_date(self):
        class FakeClient:
            def item_list(self, **kwargs):
                category_id = kwargs.get('category_id')
                return {'item': [{
                    'isbn13': f'9781000000{category_id:03d}',
                    'title': f'도서 {category_id}',
                    'pubDate': f'2026-0{(category_id % 9) + 1}-01',
                    'categoryName': '국내도서>에세이',
                    'salesPoint': category_id,
                }]}

        with patch('books.aladin_catalog.load_book_category_ids', return_value=[
            (4, index, f'분야 {index}') for index in range(1, 8)
        ]):
            result = build_list_type_catalog(
                client=FakeClient(),
                category_csv=Path('unused.csv'),
                query_type='Bestseller',
                target_count=3,
                max_calls=20,
                pages_per_query=1,
                sleep_seconds=0,
            )

        self.assertEqual(result.collected, 3)
        pub_dates = [row['fields']['pub_date'] for row in result.fixture_rows]
        self.assertEqual(pub_dates, sorted(pub_dates, reverse=True))

    def test_merge_fixture_files_prefers_latest_path_order(self):
        first = normalized_to_fixture_row(normalize_aladin_item({
            'isbn13': '9784444444444',
            'title': '첫 fixture',
            'pubDate': '2026-01-01',
        }))
        second = normalized_to_fixture_row(normalize_aladin_item({
            'isbn13': '9784444444444',
            'title': '두번째 fixture',
            'pubDate': '2026-02-01',
        }))
        with tempfile.TemporaryDirectory() as tempdir:
            base = Path(tempdir) / 'base.json'
            extra = Path(tempdir) / 'extra.json'
            write_fixture_file([first], base)
            write_fixture_file([second], extra)
            merged = merge_fixture_files(base, extra)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['fields']['title'], '두번째 fixture')
