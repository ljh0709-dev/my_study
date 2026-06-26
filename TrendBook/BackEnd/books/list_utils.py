from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from .models import Book, BookRanking

BOOK_LIST_PAGE_SIZE = 12
BOOK_LIST_LOOKBACK_DAYS = 14


def get_recent_cutoff():
    return timezone.localdate() - timedelta(days=BOOK_LIST_LOOKBACK_DAYS)


def apply_book_list_filters(queryset, params):
    section = (params.get('section') or 'all').strip().lower()
    ordering = (params.get('ordering') or 'popular').strip().lower()
    cutoff = get_recent_cutoff()

    if section == 'bestseller':
        ranked_book_ids = BookRanking.objects.filter(
            list_type=BookRanking.ListType.BESTSELLER,
            period_start__gte=cutoff,
        ).values_list('book_id', flat=True)
        queryset = queryset.filter(id__in=ranked_book_ids)
    elif section == 'new':
        queryset = queryset.filter(pub_date__gte=cutoff)
    elif section == 'recommended':
        ranked_book_ids = BookRanking.objects.filter(
            list_type=BookRanking.ListType.EDITOR_CHOICE,
            period_start__gte=cutoff,
        ).values_list('book_id', flat=True)
        queryset = queryset.filter(id__in=ranked_book_ids)
    elif section not in {'all', ''}:
        return queryset.none()

    if ordering == 'newest':
        queryset = queryset.order_by('-pub_date', '-sales_point', 'id')
    elif ordering == 'oldest':
        queryset = queryset.order_by('pub_date', '-sales_point', 'id')
    elif ordering == 'popular':
        queryset = queryset.order_by('-sales_point', 'id')
    else:
        return queryset.none()

    return queryset.distinct()
