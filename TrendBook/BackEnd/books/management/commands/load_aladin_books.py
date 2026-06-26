import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from books.models import MallType
from books.services import upsert_aladin_items


class Command(BaseCommand):
    help = 'Load the mock Aladin fixture through the production normalization service.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            type=Path,
            help='적재할 fixture 경로. 기본값은 books_recent_1y.json 또는 books.json',
        )
        parser.add_argument(
            '--period-start',
            help='베스트셀러 집계 기준일(YYYY-MM-DD). 기본값은 실행일입니다.',
        )

    def handle(self, *args, **options):
        fixtures_dir = Path(__file__).resolve().parents[3] / 'books' / 'fixtures'
        if options.get('fixture'):
            fixture_path = Path(options['fixture']).expanduser()
            if not fixture_path.is_absolute():
                fixture_path = Path(__file__).resolve().parents[3] / fixture_path
        else:
            recent_fixture = fixtures_dir / 'books_recent_1y.json'
            fixture_path = recent_fixture if recent_fixture.exists() else fixtures_dir / 'books.json'
        if not fixture_path.exists():
            raise CommandError(f'Fixture file not found: {fixture_path}')

        try:
            period_start = (
                date.fromisoformat(options['period_start'])
                if options.get('period_start')
                else None
            )
        except ValueError as exc:
            raise CommandError('--period-start는 YYYY-MM-DD 형식이어야 합니다.') from exc

        try:
            with fixture_path.open('r', encoding='utf-8') as handle:
                fixture_rows = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f'Fixture를 읽을 수 없습니다: {exc}') from exc

        raw_books = []
        for position, row in enumerate(fixture_rows, start=1):
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
                'bestRank': position,
            })

        result = upsert_aladin_items(
            raw_books,
            default_mall_type=MallType.BOOK,
            list_type='Bestseller',
            period_start=period_start,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Loaded {result.created + result.updated} books and {result.rankings} rankings, '
            f'skipped {result.skipped} from {fixture_path.name}'
        ))
