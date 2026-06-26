from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from books.models import Book
from recommendations.models import Recommendation
from trends.models import (
    NewsArticle, NewsCategory, TrendBatch, TrendTopic, TrendTopicNews, WeatherSnapshot,
)


DEMO_TOPICS = [
    ('AI가 바꾸는 일과 배움', NewsCategory.TECH, ['AI', '일자리', '교육']),
    ('고물가 시대의 생활 경제', NewsCategory.ECONOMY, ['물가', '소비', '경제']),
    ('기후와 도시의 새로운 선택', NewsCategory.SOCIETY, ['기후', '도시', '환경']),
    ('세계 질서와 우리의 시선', NewsCategory.WORLD, ['국제', '외교', '세계']),
    ('콘텐츠가 만드는 새로운 취향', NewsCategory.CULTURE, ['문화', '콘텐츠', '취향']),
]


class Command(BaseCommand):
    help = '외부 API 키 없이 발표 가능한 도서·트렌드·추천 데모 캐시를 구성합니다.'

    @transaction.atomic
    def handle(self, *args, **options):
        call_command('load_aladin_books', verbosity=0)
        books = list(Book.objects.filter(adult=False).order_by('-sales_point', 'id')[:25])
        if len(books) < 5:
            raise CommandError('데모 추천에 사용할 도서가 최소 5권 필요합니다.')

        now = timezone.now()
        articles = []
        for topic_index, (topic_title, category, _) in enumerate(DEMO_TOPICS, start=1):
            for article_index in range(1, 4):
                url = f'https://demo.local/news/{topic_index}-{article_index}'
                article, _ = NewsArticle.objects.update_or_create(
                    cache_key=NewsArticle.make_cache_key(url),
                    defaults={
                        'title': f'{topic_title} 관련 뉴스 {article_index}',
                        'summary': f'{topic_title}의 현재 맥락을 설명하는 데모 뉴스 요약입니다.',
                        'category': category, 'source': 'TrendBook Demo', 'source_url': url,
                        'published_at': now - timedelta(minutes=topic_index * article_index * 5),
                    },
                )
                articles.append(article)

        WeatherSnapshot.objects.update_or_create(
            location='구미', observed_at=now.replace(second=0, microsecond=0),
            defaults={'condition': '맑음', 'temperature_c': 24, 'feels_like_c': 24, 'humidity': 55, 'wind_speed': 1.4, 'weather_code': 800, 'icon': '01d'},
        )
        TrendBatch.objects.filter(is_legacy=False, topics__title__startswith='[데모]').distinct().delete()
        batch = TrendBatch.objects.create(
            status=TrendBatch.Status.COMPLETED, source_started_at=now, published_at=now,
        )
        for index, (title, category, keywords) in enumerate(DEMO_TOPICS, start=1):
            topic = TrendTopic.objects.create(
                batch=batch, title=f'[데모] {title}',
                summary=f'{title}를 최근 뉴스와 함께 읽고 더 깊게 탐색할 책을 제안합니다.',
                category=category, keywords=keywords, rank=index,
            )
            linked = articles[(index - 1) * 3:index * 3]
            TrendTopicNews.objects.bulk_create([
                TrendTopicNews(topic=topic, article=article, rank=rank, is_primary=rank == 1)
                for rank, article in enumerate(linked, start=1)
            ])
            selected = books[(index - 1) * 5:index * 5] or books[:5]
            Recommendation.objects.bulk_create([
                Recommendation(
                    topic=topic, book=book,
                    reason=f'{title}의 뉴스 맥락을 {book.category_name or "도서"} 관점에서 확장해 줍니다.',
                    relevance_score=0.95 - rank * 0.06,
                )
                for rank, book in enumerate(selected[:5])
            ])
        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: books={Book.objects.count()}, news={len(articles)}, topics=5, recommendations=25'
        ))
