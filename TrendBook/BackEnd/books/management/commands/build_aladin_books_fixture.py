from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import localdate

from books.aladin_catalog import (
    build_recent_books_catalog,
    default_category_csv_path,
    finalize_catalog_rows,
    load_build_state,
    merge_fixture_files,
    save_build_state,
    write_fixture_file,
)
from books.clients import AladinAPIError, AladinClient
from books.models import MallType
from books.services import upsert_aladin_items


class Command(BaseCommand):
    help = (
        '알라딘 ItemList API로 최근 1년 국내도서를 카테고리별 수집해 fixture를 만들고 '
        '선택적으로 DB에 적재합니다. 일일 5000회 호출 한도를 고려해 --max-calls로 제한합니다.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=Path,
            default=Path('books/fixtures/books_recent_1y.json'),
            help='생성할 fixture 경로 (기본: books/fixtures/books_recent_1y.json)',
        )
        parser.add_argument(
            '--merge-into',
            type=Path,
            default=Path('books/fixtures/books.json'),
            help='기존 fixture와 ISBN 기준 병합해 저장할 경로',
        )
        parser.add_argument(
            '--checkpoint',
            type=Path,
            default=Path('books/fixtures/.aladin_build_checkpoint.json'),
            help='중간 저장/재개용 체크포인트 경로',
        )
        parser.add_argument('--category-csv', type=Path, help='알라딘 카테고리 CSV 경로')
        parser.add_argument('--since-days', type=int, default=365, help='포함할 최근 출간 일수')
        parser.add_argument('--min-depth', type=int, default=3, help='수집할 국내도서 카테고리 최소 depth')
        parser.add_argument('--max-calls', type=int, default=4500, help='이번 실행에서 사용할 API 호출 상한')
        parser.add_argument('--pages-per-query', type=int, default=4, help='카테고리·리스트당 최대 페이지(1~4)')
        parser.add_argument(
            '--query-types',
            default='ItemNewAll,ItemNewSpecial,Bestseller',
            help='쉼표로 구분한 ItemList QueryType 목록',
        )
        parser.add_argument('--sleep', type=float, default=0.05, help='API 호출 간 대기(초)')
        parser.add_argument('--period-start', help='베스트셀러 집계 기준일(YYYY-MM-DD)')
        parser.add_argument('--resume', action='store_true', help='체크포인트가 있으면 이어서 수집합니다.')
        parser.add_argument(
            '--load',
            action='store_true',
            help='fixture 생성 후 upsert_aladin_items로 DB에 적재합니다.',
        )
        parser.add_argument(
            '--skip-merge',
            action='store_true',
            help='--merge-into 병합 파일을 만들지 않습니다.',
        )

    def handle(self, *args, **options):
        books_root = Path(__file__).resolve().parents[3]
        category_csv = (options.get('category_csv') or default_category_csv_path()).expanduser().resolve()
        output_path = self._resolve_path(books_root, options['output'])
        merge_into = self._resolve_path(books_root, options['merge_into'])
        checkpoint_path = self._resolve_path(books_root, options['checkpoint'])

        query_types = tuple(
            item.strip()
            for item in str(options['query_types']).split(',')
            if item.strip()
        )
        if not query_types:
            raise CommandError('--query-types에 최소 1개 QueryType이 필요합니다.')

        try:
            period_start = (
                date.fromisoformat(options['period_start'])
                if options.get('period_start')
                else localdate()
            )
        except ValueError as exc:
            raise CommandError('--period-start는 YYYY-MM-DD 형식이어야 합니다.') from exc

        start_category_index = 0
        initial_rows: list[dict] = []
        if options['resume']:
            state = load_build_state(checkpoint_path)
            if state:
                start_category_index = int(state.get('next_category_index') or 0)
                initial_rows = state.get('fixture_rows') or []
                self.stdout.write(
                    f'체크포인트 재개: 카테고리 index {start_category_index}, '
                    f'누적 {len(initial_rows)}권'
                )

        def persist_checkpoint(result, next_category_index, collected_by_isbn):
            rows = finalize_catalog_rows(collected_by_isbn)
            write_fixture_file(rows, output_path)
            save_build_state(checkpoint_path, {
                'next_category_index': next_category_index,
                'api_calls': result.api_calls,
                'since_days': options['since_days'],
                'fixture_rows': rows,
            })

        def on_progress(result, depth, category_id, category_name, category_added, total_collected):
            if category_added:
                self.stdout.write(
                    f'  CID {category_id} (depth {depth}, {category_name}): '
                    f'+{category_added}권, 누적 {total_collected}권, 호출 {result.api_calls}회'
                )

        self.stdout.write(
            f'알라딘 최근 {options["since_days"]}일 도서 수집 시작 '
            f'(max_calls={options["max_calls"]}, min_depth={options["min_depth"]})'
        )
        try:
            build_result = build_recent_books_catalog(
                client=AladinClient(timeout=12.0),
                category_csv=category_csv,
                since_days=options['since_days'],
                query_types=query_types,
                min_depth=options['min_depth'],
                max_calls=options['max_calls'],
                pages_per_query=options['pages_per_query'],
                sleep_seconds=options['sleep'],
                start_category_index=start_category_index,
                initial_rows=initial_rows,
                checkpoint_callback=persist_checkpoint,
                progress_callback=on_progress,
            )
        except FileNotFoundError as exc:
            raise CommandError(str(exc)) from exc

        write_fixture_file(build_result.fixture_rows, output_path)
        save_build_state(checkpoint_path, {
            'next_category_index': build_result.categories_scanned,
            'api_calls': build_result.api_calls,
            'since_days': options['since_days'],
            'fixture_rows': build_result.fixture_rows,
            'completed': True,
        })

        merged_count = len(build_result.fixture_rows)
        if not options['skip_merge']:
            merged_rows = merge_fixture_files(merge_into, output_path)
            write_fixture_file(merged_rows, merge_into)
            merged_count = len(merged_rows)

        self.stdout.write(self.style.SUCCESS(
            '수집 완료: '
            f'fixture={len(build_result.fixture_rows)}권, '
            f'API 호출={build_result.api_calls}, '
            f'카테고리={build_result.categories_scanned}, '
            f'제외(기간外)={build_result.skipped_not_recent}, '
            f'제외(무효)={build_result.skipped_invalid}, '
            f'API 스킵={build_result.skipped_api_errors}'
        ))
        self.stdout.write(f'  저장: {output_path}')
        if not options['skip_merge']:
            self.stdout.write(f'  병합 저장: {merge_into} ({merged_count}권)')

        if options['load']:
            self._load_fixture_rows(build_result.fixture_rows, period_start)

    @staticmethod
    def _resolve_path(books_root: Path, path: Path) -> Path:
        path = Path(path).expanduser()
        return path if path.is_absolute() else books_root / path

    def _load_fixture_rows(self, rows, period_start):
        raw_books = []
        for index, row in enumerate(rows, start=1):
            fields = row.get('fields', row)
            raw_books.append({
                'isbn13': fields.get('isbn'),
                'isbn': fields.get('isbn10'),
                'itemId': fields.get('aladin_item_id'),
                'mallType': fields.get('mall_type', MallType.BOOK),
                'title': fields.get('title'),
                'author': fields.get('author'),
                'publisher': fields.get('publisher'),
                'cover': fields.get('cover_img'),
                'description': fields.get('description'),
                'categoryName': fields.get('category_name'),
                'link': fields.get('aladin_link'),
                'pubDate': fields.get('pub_date'),
                'priceSales': fields.get('price_sales'),
                'priceStandard': fields.get('price_standard'),
                'salesPoint': fields.get('sales_point'),
                'customerReviewRank': fields.get('customer_review_rank'),
                'stockStatus': fields.get('stock_status'),
                'adult': fields.get('adult', False),
                'fixedPrice': fields.get('fixed_price', False),
                'bestRank': index,
            })
        load_result = upsert_aladin_items(
            raw_books,
            default_mall_type=MallType.BOOK,
            list_type='ItemNewAll',
            period_start=period_start,
        )
        self.stdout.write(self.style.SUCCESS(
            f'DB 적재: created={load_result.created}, updated={load_result.updated}, '
            f'skipped={load_result.skipped}, rankings={load_result.rankings}'
        ))