from datetime import date

from django.core.management.base import BaseCommand, CommandError

from books.clients import AladinAPIError, AladinClient
from books.models import MallType
from books.services import ALADIN_LIST_TYPES, sync_aladin_list


class Command(BaseCommand):
    help = '알라딘 상품 리스트를 조회해 도서·카테고리·순위를 동기화합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--query-type', choices=ALADIN_LIST_TYPES, default='Bestseller')
        parser.add_argument('--mall-type', choices=MallType.values, default=MallType.BOOK)
        parser.add_argument('--category-id', type=int)
        parser.add_argument('--max-results', type=int, default=50)
        parser.add_argument('--period-start')

    def handle(self, *args, **options):
        try:
            period_start = date.fromisoformat(options['period_start']) if options['period_start'] else None
        except ValueError as exc:
            raise CommandError('--period-start는 YYYY-MM-DD 형식이어야 합니다.') from exc
        try:
            result = sync_aladin_list(
                AladinClient(),
                query_type=options['query_type'],
                mall_type=options['mall_type'],
                category_id=options['category_id'],
                max_results=options['max_results'],
                period_start=period_start,
            )
        except AladinAPIError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f'created={result.created}, updated={result.updated}, '
            f'skipped={result.skipped}, rankings={result.rankings}'
        ))
