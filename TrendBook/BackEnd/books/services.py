from dataclasses import dataclass, field
from datetime import datetime

from django.db import transaction
from django.utils.timezone import localdate

from .models import AladinCategory, Book, BookCategory, BookRanking, MallType


ALADIN_LIST_TYPES = {
    'Bestseller': BookRanking.ListType.BESTSELLER,
    'ItemNewAll': BookRanking.ListType.ITEM_NEW_ALL,
    'ItemNewSpecial': BookRanking.ListType.ITEM_NEW_SPECIAL,
    'ItemEditorChoice': BookRanking.ListType.EDITOR_CHOICE,
    'BlogBest': BookRanking.ListType.BLOG_BEST,
}


@dataclass
class BookSyncResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    rankings: int = 0
    book_ids: set[int] = field(default_factory=set)


def _date(value):
    try:
        return datetime.strptime(value or '', '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def normalize_aladin_item(raw, default_mall_type=MallType.BOOK):
    """검색·상세·리스트 응답을 하나의 내부 도서 형식으로 변환한다."""
    isbn13 = str(raw.get('isbn13') or '').replace('-', '').strip()
    if len(isbn13) != 13 or not isbn13.isdigit():
        candidate = str(raw.get('isbn') or '').replace('-', '').strip()
        isbn13 = candidate if len(candidate) == 13 and candidate.isdigit() else ''
    if not isbn13:
        return None

    mall_type = str(raw.get('mallType') or default_mall_type).upper()
    if mall_type not in MallType.values:
        mall_type = default_mall_type

    return {
        'isbn': isbn13,
        'mall_type': mall_type,
        'isbn10': (str(raw.get('isbn') or '').strip() or None) if raw.get('isbn13') else None,
        'aladin_item_id': raw.get('itemId') or None,
        'title': str(raw.get('title') or '').strip(),
        'author': str(raw.get('author') or '').strip(),
        'publisher': str(raw.get('publisher') or '').strip(),
        'cover_img': str(raw.get('cover') or '').strip(),
        'description': str(raw.get('description') or '').strip(),
        'category_id': raw.get('categoryId') or None,
        'category_name': str(raw.get('categoryName') or '').strip(),
        'aladin_link': str(raw.get('link') or '').replace('&amp;', '&').strip(),
        'pub_date': _date(raw.get('pubDate')),
        'price_sales': raw.get('priceSales') or None,
        'price_standard': raw.get('priceStandard') or None,
        'sales_point': raw.get('salesPoint') or None,
        'customer_review_rank': raw.get('customerReviewRank'),
        'stock_status': str(raw.get('stockStatus') or '').strip(),
        'adult': bool(raw.get('adult', False)),
        'fixed_price': bool(raw.get('fixedPrice', False)),
        'best_rank': raw.get('bestRank'),
    }


def _upsert_category(book, normalized):
    category_id = normalized['category_id']
    category_name = normalized['category_name']
    if not category_id or not category_name:
        return None

    parts = [part.strip() for part in category_name.split('>') if part.strip()]
    mall_labels = {label for _, label in MallType.choices}
    if parts and parts[0] in mall_labels:
        parts.pop(0)
    parts = parts[:5]
    defaults = {
        'name': parts[-1] if parts else category_name,
        'mall_type': normalized['mall_type'],
        **{f'depth{i}': parts[i - 1] if len(parts) >= i else '' for i in range(1, 6)},
    }
    category, _ = AladinCategory.objects.update_or_create(cid=category_id, defaults=defaults)
    BookCategory.objects.filter(book=book, is_primary=True).exclude(category=category).update(
        is_primary=False,
    )
    BookCategory.objects.update_or_create(
        book=book, category=category, defaults={'is_primary': True},
    )
    return category


@transaction.atomic
def upsert_aladin_items(items, default_mall_type=MallType.BOOK, list_type=None,
                        period_start=None, category_id=None):
    result = BookSyncResult()
    ranking_type = ALADIN_LIST_TYPES.get(list_type)
    period_start = period_start or localdate()

    for raw in items:
        normalized = normalize_aladin_item(raw, default_mall_type)
        if normalized is None or not normalized['title']:
            result.skipped += 1
            continue

        category_value = normalized.pop('category_id')
        best_rank = normalized.pop('best_rank')
        category_name = normalized['category_name']
        isbn = normalized.pop('isbn')
        mall_type = normalized.pop('mall_type')
        book, created = Book.objects.update_or_create(
            isbn=isbn,
            mall_type=mall_type,
            defaults=normalized,
        )
        normalized_for_category = {
            'category_id': category_value,
            'category_name': category_name,
            'mall_type': mall_type,
        }
        _upsert_category(book, normalized_for_category)
        result.created += int(created)
        result.updated += int(not created)
        result.book_ids.add(book.id)

        rank = best_rank if isinstance(best_rank, int) and best_rank > 0 else None
        if ranking_type and rank:
            ranking_category = None
            if category_id:
                ranking_category = AladinCategory.objects.filter(cid=category_id).first()
            BookRanking.objects.update_or_create(
                book=book,
                category=ranking_category,
                list_type=ranking_type,
                period_start=period_start,
                defaults={'rank': rank},
            )
            result.rankings += 1
    return result


def sync_aladin_list(client, query_type='Bestseller', mall_type=MallType.BOOK,
                     category_id=None, max_results=50, period_start=None):
    payload = client.item_list(
        query_type=query_type,
        mall_type=mall_type,
        category_id=category_id,
        max_results=max_results,
    )
    return upsert_aladin_items(
        payload.get('item', []),
        default_mall_type=mall_type,
        list_type=query_type,
        period_start=period_start,
        category_id=category_id,
    )
