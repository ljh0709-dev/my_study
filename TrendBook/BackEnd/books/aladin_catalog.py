from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from django.utils.timezone import localdate

from .clients import AladinAPIError, AladinClient
from .models import MallType
from .services import normalize_aladin_item


DEFAULT_CATEGORY_CSV = 'aladin_Category_CID_20210927 (1).csv'
DEFAULT_QUERY_TYPES = ('ItemNewAll', 'ItemNewSpecial', 'Bestseller')
CATALOG_LIST_TYPES = (
    ('Bestseller', '베스트셀러'),
    ('ItemNewAll', '신간'),
    ('ItemEditorChoice', '추천도서'),
)
DEFAULT_CATALOG_PER_LIST = 3000
MAX_RESULTS_PER_PAGE = 50
MAX_PAGES_PER_QUERY = 4
ALADIN_MAX_RESULTS_PER_QUERY = 200


@dataclass
class CatalogBuildResult:
    api_calls: int = 0
    categories_scanned: int = 0
    collected: int = 0
    skipped_not_recent: int = 0
    skipped_invalid: int = 0
    skipped_api_errors: int = 0
    fixture_rows: list[dict] = field(default_factory=list)


def default_category_csv_path() -> Path:
    return Path(__file__).resolve().parents[2] / DEFAULT_CATEGORY_CSV


def _category_depth(row: dict) -> int:
    for depth in range(5, 0, -1):
        if (row.get(f'{depth}Depth') or '').strip():
            return depth
    return 0


def load_book_category_ids(
    csv_path: Path,
    *,
    min_depth: int = 3,
    mall_label: str = '국내도서',
) -> list[tuple[int, int, str]]:
    if not csv_path.is_file():
        raise FileNotFoundError(f'카테고리 CSV를 찾을 수 없습니다: {csv_path}')

    categories: list[tuple[int, int, str]] = []
    with csv_path.open('r', encoding='utf-8-sig', newline='') as csv_file:
        next(csv_file, None)
        next(csv_file, None)
        reader = csv.DictReader(csv_file)
        for row in reader:
            if (row.get('몰') or '').strip() != mall_label:
                continue
            depth = _category_depth(row)
            if depth < min_depth:
                continue
            try:
                cid = int(row['CID'])
            except (KeyError, TypeError, ValueError):
                continue
            categories.append((depth, cid, (row.get('카테고리명') or '').strip()))

    # 넓은 분야(depth 3~4)를 먼저 훑어 추천 후보 다양성을 확보한다.
    categories.sort(key=lambda item: (item[0], item[1]))
    return categories


def normalized_to_fixture_row(normalized: dict) -> dict:
    return {
        'model': 'books.book',
        'fields': {
            'isbn': normalized['isbn'],
            'isbn10': normalized.get('isbn10'),
            'aladin_item_id': normalized.get('aladin_item_id'),
            'mall_type': normalized.get('mall_type', MallType.BOOK),
            'title': normalized.get('title'),
            'author': normalized.get('author'),
            'publisher': normalized.get('publisher'),
            'cover_img': normalized.get('cover_img'),
            'description': normalized.get('description'),
            'category_name': normalized.get('category_name'),
            'aladin_link': normalized.get('aladin_link'),
            'pub_date': normalized['pub_date'].isoformat() if normalized.get('pub_date') else None,
            'price_sales': normalized.get('price_sales'),
            'price_standard': normalized.get('price_standard'),
            'sales_point': normalized.get('sales_point'),
            'customer_review_rank': normalized.get('customer_review_rank'),
            'stock_status': normalized.get('stock_status') or '',
            'adult': normalized.get('adult', False),
            'fixed_price': normalized.get('fixed_price', False),
        },
    }


def fixture_row_to_normalized(row: dict) -> dict | None:
    fields = row.get('fields', row)
    pub_date = fields.get('pub_date')
    return {
        'isbn': fields.get('isbn'),
        'isbn10': fields.get('isbn10'),
        'aladin_item_id': fields.get('aladin_item_id'),
        'mall_type': fields.get('mall_type', MallType.BOOK),
        'title': fields.get('title'),
        'author': fields.get('author'),
        'publisher': fields.get('publisher'),
        'cover_img': fields.get('cover_img'),
        'description': fields.get('description'),
        'category_name': fields.get('category_name'),
        'aladin_link': fields.get('aladin_link'),
        'pub_date': date.fromisoformat(pub_date) if pub_date else None,
        'price_sales': fields.get('price_sales'),
        'price_standard': fields.get('price_standard'),
        'sales_point': fields.get('sales_point'),
        'customer_review_rank': fields.get('customer_review_rank'),
        'stock_status': fields.get('stock_status') or '',
        'adult': fields.get('adult', False),
        'fixed_price': fields.get('fixed_price', False),
    }


def rows_to_collected_map(rows: list[dict]) -> dict[str, dict]:
    collected: dict[str, dict] = {}
    for row in rows:
        normalized = fixture_row_to_normalized(row)
        if normalized and normalized.get('isbn'):
            collected[normalized['isbn']] = normalized
    return collected


def raw_items_to_fixture_rows(raw_items: list[dict], *, cutoff: date | None = None) -> CatalogBuildResult:
    result = CatalogBuildResult()
    seen_isbns: set[str] = set()

    for raw in raw_items:
        normalized = normalize_aladin_item(raw, default_mall_type=MallType.BOOK)
        if normalized is None or not normalized.get('title'):
            result.skipped_invalid += 1
            continue
        pub_date = normalized.get('pub_date')
        if cutoff and (not pub_date or pub_date < cutoff):
            result.skipped_not_recent += 1
            continue
        isbn = normalized['isbn']
        if isbn in seen_isbns:
            continue
        seen_isbns.add(isbn)
        result.fixture_rows.append(normalized_to_fixture_row(normalized))
        result.collected += 1
    return result


def build_recent_books_catalog(
    *,
    client: AladinClient,
    category_csv: Path,
    since_days: int = 365,
    query_types: tuple[str, ...] = DEFAULT_QUERY_TYPES,
    min_depth: int = 3,
    max_calls: int = 4500,
    pages_per_query: int = MAX_PAGES_PER_QUERY,
    sleep_seconds: float = 0.05,
    start_category_index: int = 0,
    initial_rows: list[dict] | None = None,
    checkpoint_every_calls: int = 25,
    checkpoint_callback=None,
    progress_callback=None,
) -> CatalogBuildResult:
    cutoff = localdate() - timedelta(days=since_days)
    categories = load_book_category_ids(category_csv, min_depth=min_depth)
    pages_per_query = max(1, min(pages_per_query, MAX_PAGES_PER_QUERY))

    collected_by_isbn = rows_to_collected_map(initial_rows or [])
    result = CatalogBuildResult()
    result.api_calls = 0
    start_category_index = max(0, min(start_category_index, len(categories)))

    for index, (depth, category_id, category_name) in enumerate(categories):
        if index < start_category_index:
            continue
        if result.api_calls >= max_calls:
            break
        result.categories_scanned += 1
        category_added = 0

        for query_type in query_types:
            if result.api_calls >= max_calls:
                break
            duplicate_streak = 0

            for page in range(1, pages_per_query + 1):
                if result.api_calls >= max_calls:
                    break

                try:
                    payload = client.item_list(
                        query_type=query_type,
                        mall_type=MallType.BOOK,
                        category_id=category_id,
                        start=page,
                        max_results=MAX_RESULTS_PER_PAGE,
                    )
                except AladinAPIError:
                    result.skipped_api_errors += 1
                    break
                result.api_calls += 1
                if checkpoint_callback and checkpoint_every_calls > 0 and result.api_calls % checkpoint_every_calls == 0:
                    checkpoint_callback(result, index + 1, collected_by_isbn)
                items = payload.get('item') or []
                if not items:
                    break

                page_new = 0
                for raw in items:
                    normalized = normalize_aladin_item(raw, default_mall_type=MallType.BOOK)
                    if normalized is None or not normalized.get('title'):
                        result.skipped_invalid += 1
                        continue
                    pub_date = normalized.get('pub_date')
                    if not pub_date or pub_date < cutoff:
                        result.skipped_not_recent += 1
                        continue

                    isbn = normalized['isbn']
                    if isbn in collected_by_isbn:
                        continue

                    if not normalized.get('category_id'):
                        normalized['category_id'] = category_id
                    if not normalized.get('category_name'):
                        normalized['category_name'] = category_name

                    collected_by_isbn[isbn] = normalized
                    page_new += 1
                    category_added += 1

                if page_new == 0:
                    duplicate_streak += 1
                else:
                    duplicate_streak = 0
                if duplicate_streak >= 2:
                    break
                if page * MAX_RESULTS_PER_PAGE >= ALADIN_MAX_RESULTS_PER_QUERY:
                    break

                if sleep_seconds:
                    time.sleep(sleep_seconds)

        if progress_callback:
            progress_callback(
                result,
                depth,
                category_id,
                category_name,
                category_added,
                len(collected_by_isbn),
            )
        if checkpoint_callback and category_added:
            checkpoint_callback(result, index + 1, collected_by_isbn)

    result.collected = len(collected_by_isbn)
    result.fixture_rows = finalize_catalog_rows(collected_by_isbn)
    return result


def write_fixture_file(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(f'{output_path.suffix}.tmp')
    last_error: OSError | None = None
    for attempt in range(3):
        try:
            with temp_path.open('w', encoding='utf-8') as handle:
                json.dump(rows, handle, ensure_ascii=False, indent=2)
            temp_path.replace(output_path)
            return
        except OSError as exc:
            last_error = exc
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            time.sleep(0.2 * (attempt + 1))
    if last_error is not None:
        raise last_error


def merge_fixture_files(*paths: Path) -> list[dict]:
    merged: dict[str, dict] = {}
    for path in paths:
        if not path.is_file():
            continue
        with path.open('r', encoding='utf-8') as handle:
            rows = json.load(handle)
        for row in rows:
            fields = row.get('fields', row)
            isbn = str(fields.get('isbn') or '').strip()
            if isbn:
                merged[isbn] = row
    return list(merged.values())


def save_build_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f'{path.suffix}.tmp')
    with temp_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def load_build_state(path: Path) -> dict | None:
    if not path.is_file():
        return None
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def sort_by_recent_publication(items: list[dict]) -> list[dict]:
    return sorted(
        items,
        key=lambda row: (row.get('pub_date') or date.min, row.get('sales_point') or 0),
        reverse=True,
    )


def finalize_catalog_rows(collected_by_isbn: dict[str, dict]) -> list[dict]:
    return [
        normalized_to_fixture_row(item)
        for item in sort_by_recent_publication(list(collected_by_isbn.values()))
    ]


def build_list_type_catalog(
    *,
    client: AladinClient,
    category_csv: Path,
    query_type: str,
    target_count: int = DEFAULT_CATALOG_PER_LIST,
    min_depth: int = 3,
    max_calls: int = 2000,
    pages_per_query: int = MAX_PAGES_PER_QUERY,
    sleep_seconds: float = 0.05,
    start_category_index: int = 0,
    initial_rows: list[dict] | None = None,
    initial_api_calls: int = 0,
    checkpoint_callback=None,
    checkpoint_every_calls: int = 25,
    progress_callback=None,
) -> CatalogBuildResult:
    """단일 ItemList QueryType에서 카테고리를 순회하며 최근 출판 순 상위 N권을 수집한다."""
    categories = load_book_category_ids(category_csv, min_depth=min_depth)
    pages_per_query = max(1, min(pages_per_query, MAX_PAGES_PER_QUERY))
    target_count = max(1, target_count)

    collected_by_isbn = rows_to_collected_map(initial_rows or [])
    result = CatalogBuildResult()
    result.api_calls = max(0, initial_api_calls)

    start_category_index = max(0, min(start_category_index, len(categories)))
    for index, (depth, category_id, category_name) in enumerate(categories):
        if index < start_category_index:
            continue
        if result.api_calls >= max_calls:
            break

        result.categories_scanned += 1
        category_added = 0
        duplicate_streak = 0

        for page in range(1, pages_per_query + 1):
            if result.api_calls >= max_calls:
                break

            try:
                payload = client.item_list(
                    query_type=query_type,
                    mall_type=MallType.BOOK,
                    category_id=category_id,
                    start=page,
                    max_results=MAX_RESULTS_PER_PAGE,
                )
            except AladinAPIError:
                result.skipped_api_errors += 1
                break
            result.api_calls += 1
            if checkpoint_callback and checkpoint_every_calls > 0 and result.api_calls % checkpoint_every_calls == 0:
                checkpoint_callback(result, index + 1, collected_by_isbn, query_type)

            items = payload.get('item') or []
            if not items:
                break

            page_new = 0
            for raw in items:
                normalized = normalize_aladin_item(raw, default_mall_type=MallType.BOOK)
                if normalized is None or not normalized.get('title'):
                    result.skipped_invalid += 1
                    continue

                isbn = normalized['isbn']
                if isbn in collected_by_isbn:
                    continue

                if not normalized.get('category_id'):
                    normalized['category_id'] = category_id
                if not normalized.get('category_name'):
                    normalized['category_name'] = category_name

                collected_by_isbn[isbn] = normalized
                page_new += 1
                category_added += 1

            if page_new == 0:
                duplicate_streak += 1
            else:
                duplicate_streak = 0
            if duplicate_streak >= 2:
                break
            if page * MAX_RESULTS_PER_PAGE >= ALADIN_MAX_RESULTS_PER_QUERY:
                break

            if sleep_seconds:
                time.sleep(sleep_seconds)

        if progress_callback:
            progress_callback(
                result,
                query_type,
                depth,
                category_id,
                category_name,
                category_added,
                len(collected_by_isbn),
            )

    recent_items = sort_by_recent_publication(list(collected_by_isbn.values()))[:target_count]
    trimmed = {item['isbn']: item for item in recent_items}
    result.collected = len(trimmed)
    result.fixture_rows = finalize_catalog_rows(trimmed)
    return result