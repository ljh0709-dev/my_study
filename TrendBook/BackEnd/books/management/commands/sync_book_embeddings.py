from django.core.management.base import BaseCommand, CommandError

from books.embeddings import sync_book_embeddings
from books.models import Book
from trends.ai_client import AIServiceClient, AIServiceError


class Command(BaseCommand):
    help = '도서 메타데이터 임베딩을 FastAPI/OpenAI로 생성하거나 갱신합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--batch-size', type=int, default=50)
        parser.add_argument('--max-workers', type=int, default=1)
        parser.add_argument('--limit', type=int)
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        if not 1 <= batch_size <= 100:
            raise CommandError('--batch-size는 1~100이어야 합니다.')
        max_workers = options['max_workers']
        if not 1 <= max_workers <= 8:
            raise CommandError('--max-workers는 1~8이어야 합니다.')
        queryset = Book.objects.filter(adult=False).prefetch_related(
            'category_links__category', 'embedding',
        ).order_by('id')
        if options.get('limit'):
            queryset = queryset[:max(1, options['limit'])]
        try:
            result = sync_book_embeddings(
                list(queryset), ai_client=AIServiceClient(timeout=90),
                batch_size=batch_size, force=options['force'], max_workers=max_workers,
            )
        except (AIServiceError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f'Book embeddings ready: created={result.created}, updated={result.updated}, skipped={result.skipped}'
        ))
