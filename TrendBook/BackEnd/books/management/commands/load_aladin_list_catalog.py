import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import localdate

from books.aladin_catalog import (
    CATALOG_LIST_TYPES,
    DEFAULT_CATALOG_PER_LIST,
    build_list_type_catalog,
    default_category_csv_path,
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
        '알라딘 ItemList API로 베스트셀러·신간·추천도서를 카테고리별 수집해 '
        '최근 출판 순으로 DB에 적재합니다. 리스트 유형당 기본 3000권입니다.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--per-list',
            type=int,
            default=DEFAULT_CATALOG_PER_LIST,
            help='리스트 유형당 적재할 도서 수 (기본: 3000)',
        )
        parser.add_argument(
            '--list-types',
            default=','.join(query_type for query_type, _ in CATALOG_LIST_TYPES),
            help='쉼표로 구분한 ItemList QueryType (Bestseller, ItemNewAll, ItemEditorChoice)',
        )
        parser.add_argument('--category-csv', type=Path, help='알라딘 카테고리 CSV 경로')
        parser.add_argument('--min-depth', type=int, default=3, help='수집할 국내도서 카테고리 최소 depth')
        parser.add_argument(
            '--max-calls-per-list',
            type=int,
            default=1600,
            help='리스트 유형당 API 호출 상한 (3유형 합계 일 5000회 한도 고려)',
        )
        parser.add_argument('--pages-per-query', type=int, default=4, help='카테고리당 최대 페이지(1~4)')
        parser.add_argument('--sleep', type=float, default=0.05, help='API 호출 간 대기(초)')
        parser.add_argument('--period-start', help='순위 집계 기준일(YYYY-MM-DD)')
        parser.add_argument(
            '--output-dir',
            type=Path,
            default=Path('books/fixtures'),
            help='유형별 fixture 저장 디렉터리',
        )
        parser.add_argument(
            '--checkpoint',
            type=Path,
            default=Path('books/fixtures/.aladin_list_catalog_checkpoint.json'),
            help='중간 저장/재개용 체크포인트 경로',
        )
        parser.add_argument('--resume', action='store_true', help='체크포인트가 있으면 이어서 수집합니다.')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='API 수집만 하고 DB 적재는 생략합니다.',
        )

    def handle(self, *args, **options):
        books_root = Path(__file__).resolve().parents[3]
        category_csv = (options.get('category_csv') or default_category_csv_path()).expanduser().resolve()
        output_dir = self._resolve_path(books_root, options['output_dir'])
        checkpoint_path = self._resolve_path(books_root, options['checkpoint'])

        list_types = tuple(
            item.strip()
            for item in str(options['list_types']).split(',')
            if item.strip()
        )
        if not list_types:
            raise CommandError('--list-types에 최소 1개 QueryType이 필요합니다.')

        try:
            period_start = (
                date.fromisoformat(options['period_start'])
                if options.get('period_start')
                else localdate()
            )
        except ValueError as exc:
            raise CommandError('--period-start는 YYYY-MM-DD 형식이어야 합니다.') from exc

        progress_fixture_path = output_dir / 'aladin_list_catalog_progress.json'
        checkpoint = load_build_state(checkpoint_path) if options['resume'] else None
        completed_types = set((checkpoint or {}).get('completed_types') or [])
        resume_query_type = (checkpoint or {}).get('current_query_type')
        resume_category_index = int((checkpoint or {}).get('next_category_index') or 0)
        resume_rows = self._load_progress_rows(checkpoint, progress_fixture_path)
        resume_api_calls = int((checkpoint or {}).get('api_calls') or 0)

        client = AladinClient(timeout=12.0)
        totals = {'created': 0, 'updated': 0, 'skipped': 0, 'rankings': 0, 'books': 0}

        for query_type in list_types:
            if query_type in completed_types:
                self.stdout.write(f'[{query_type}] 체크포인트 완료 항목 — 건너뜀')
                continue

            start_index = resume_category_index if query_type == resume_query_type else 0
            initial_rows = resume_rows if query_type == resume_query_type else []
            initial_api_calls = resume_api_calls if query_type == resume_query_type else 0

            def persist_checkpoint(result, next_category_index, collected_by_isbn, active_query_type):
                from books.aladin_catalog import finalize_catalog_rows

                metadata = {
                    'current_query_type': active_query_type,
                    'next_category_index': next_category_index,
                    'api_calls': result.api_calls,
                    'completed_types': sorted(completed_types),
                }
                try:
                    if result.api_calls % 100 == 0:
                        rows = finalize_catalog_rows(collected_by_isbn)
                        write_fixture_file(rows, progress_fixture_path)
                    save_build_state(checkpoint_path, metadata)
                except OSError as exc:
                    self.stdout.write(self.style.WARNING(
                        f'  체크포인트 저장 실패(무시하고 계속): {exc}'
                    ))

            def on_progress(result, active_query_type, depth, category_id, category_name, category_added, total_collected):
                if category_added:
                    self.stdout.write(
                        f'  [{active_query_type}] CID {category_id} (depth {depth}, {category_name}): '
                        f'+{category_added}권, 누적 {total_collected}권, 호출 {result.api_calls}회'
                    )

            self.stdout.write(
                f'[{query_type}] 수집 시작 (목표 {options["per_list"]}권, '
                f'max_calls={options["max_calls_per_list"]})'
            )
            try:
                build_result = build_list_type_catalog(
                    client=client,
                    category_csv=category_csv,
                    query_type=query_type,
                    target_count=options['per_list'],
                    min_depth=options['min_depth'],
                    max_calls=options['max_calls_per_list'],
                    pages_per_query=options['pages_per_query'],
                    sleep_seconds=options['sleep'],
                    start_category_index=start_index,
                    initial_rows=initial_rows,
                    initial_api_calls=initial_api_calls,
                    checkpoint_callback=persist_checkpoint,
                    checkpoint_every_calls=100,
                    progress_callback=on_progress,
                )
            except FileNotFoundError as exc:
                raise CommandError(str(exc)) from exc
            except AladinAPIError as exc:
                raise CommandError(str(exc)) from exc

            output_path = output_dir / f'books_{query_type.lower()}_recent.json'
            write_fixture_file(build_result.fixture_rows, output_path)

            self.stdout.write(self.style.SUCCESS(
                f'[{query_type}] 수집 완료: {build_result.collected}권, '
                f'API 호출={build_result.api_calls}, '
                f'카테고리={build_result.categories_scanned}, '
                f'제외(무효)={build_result.skipped_invalid}, '
                f'API 스킵={build_result.skipped_api_errors}'
            ))
            self.stdout.write(f'  fixture 저장: {output_path}')

            if not options['dry_run']:
                load_result = self._load_fixture_rows(
                    build_result.fixture_rows,
                    query_type=query_type,
                    period_start=period_start,
                )
                totals['created'] += load_result.created
                totals['updated'] += load_result.updated
                totals['skipped'] += load_result.skipped
                totals['rankings'] += load_result.rankings
                totals['books'] += load_result.created + load_result.updated
                self.stdout.write(self.style.SUCCESS(
                    f'[{query_type}] DB 적재: created={load_result.created}, '
                    f'updated={load_result.updated}, skipped={load_result.skipped}, '
                    f'rankings={load_result.rankings}'
                ))

            completed_types.add(query_type)
            resume_query_type = None
            resume_category_index = 0
            resume_rows = []
            resume_api_calls = 0
            if progress_fixture_path.is_file():
                progress_fixture_path.unlink()
            save_build_state(checkpoint_path, {
                'completed_types': sorted(completed_types),
                'completed': len(completed_types) == len(list_types),
            })

        merged_path = output_dir / 'books.json'
        per_list_paths = [
            output_dir / f'books_{query_type.lower()}_recent.json'
            for query_type in list_types
        ]
        merged_rows = merge_fixture_files(*per_list_paths)
        write_fixture_file(merged_rows, merged_path)
        self.stdout.write(f'  통합 fixture 저장: {merged_path} ({len(merged_rows)}권)')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('dry-run 모드 — DB 적재를 생략했습니다.'))
        else:
            self.stdout.write(self.style.SUCCESS(
                '전체 DB 적재 완료: '
                f'books={totals["books"]}, created={totals["created"]}, '
                f'updated={totals["updated"]}, skipped={totals["skipped"]}, '
                f'rankings={totals["rankings"]}'
            ))

    @staticmethod
    def _load_progress_rows(checkpoint, progress_fixture_path: Path) -> list[dict]:
        if progress_fixture_path.is_file():
            with progress_fixture_path.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        if checkpoint:
            return checkpoint.get('fixture_rows') or []
        return []

    @staticmethod
    def _resolve_path(books_root: Path, path: Path) -> Path:
        path = Path(path).expanduser()
        return path if path.is_absolute() else books_root / path

    @staticmethod
    def _load_fixture_rows(rows, *, query_type, period_start):
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
        return upsert_aladin_items(
            raw_books,
            default_mall_type=MallType.BOOK,
            list_type=query_type,
            period_start=period_start,
        )