from django.core.management.base import BaseCommand, CommandError

from trends.services import refresh_discover_cache


class Command(BaseCommand):
    help = '네이버 뉴스와 OpenWeather 데이터를 수집해 오늘의 트렌드 캐시를 갱신합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--city')
        parser.add_argument('--news-display', type=int, default=None)

    def handle(self, *args, **options):
        try:
            result = refresh_discover_cache(
                city=options['city'],
                news_display=options['news_display'],
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc
        source = result['sources']
        self.stdout.write(self.style.SUCCESS(
            f"news_created={source['news_created']}, news_updated={source['news_updated']}, "
            f"trend_job_id={result['trend_job_id']}, source_errors={len(source['errors'])}"
        ))
        for error in source['errors']:
            self.stderr.write(self.style.WARNING(error))
