from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from ai.models import AIJob
from books.models import Book, BookEmbedding
from books.services import BookSyncResult
from recommendations.models import NewsRecommendation, Recommendation

from .models import NewsArticle, NewsCategory, SyncRun, TrendBatch, TrendTopic, TrendTopicNews, WeatherSnapshot
from .recommendation_utils import filter_recommendation_records
from .scheduler import run_refresh_if_due
from .serializers import WeatherSnapshotSerializer
from .services import (
    DISCOVER_SECTIONS,
    NEWS_QUERIES,
    collect_news,
    collect_weather,
    complete_article_recommendation_job,
    complete_trend_job,
    current_weather_snapshot_by_coordinates,
    refresh_discover_cache,
    start_article_recommendation_generation,
)
from .weather_utils import normalize_weather_condition


class FakeNewsClient:
    def __init__(self, published_at):
        self.published_at = published_at

    def search(self, query, display=10):
        return {'items': [{
            'title': f'<b>{query}</b>', 'description': '뉴스 &amp; 요약',
            'originallink': f'https://example.com/{query}',
            'pubDate': self.published_at.strftime('%a, %d %b %Y %H:%M:%S %z'),
        }]}


class FakeWeatherClient:
    def current(self, city=None):
        return {
            'name': city or 'Gumi', 'dt': int(timezone.now().timestamp()),
            'weather': [{'id': 800, 'description': '맑음', 'icon': '01d'}],
            'main': {'temp': 23.5, 'feels_like': 23.0, 'humidity': 50}, 'wind': {'speed': 1.2},
        }

    def current_by_coordinates(self, lat, lon):
        return {
            'name': 'Current Location', 'dt': int(timezone.now().timestamp()),
            'weather': [{'id': 804, 'description': '온흐림', 'icon': '04d'}],
            'main': {'temp': 19.5, 'feels_like': 19.0, 'humidity': 70}, 'wind': {'speed': 2.2},
        }


class SourceCollectionTests(TestCase):
    def test_news_is_recent_normalized_unique_and_discover_sections(self):
        now = timezone.now()
        first = collect_news(FakeNewsClient(now), now=now)
        second = collect_news(FakeNewsClient(now), now=now)
        self.assertEqual(first.news_created, 15)
        self.assertEqual(second.news_updated, 15)
        self.assertEqual(set(NewsArticle.objects.values_list('category', flat=True)), set(NEWS_QUERIES))
        self.assertNotIn('<b>', NewsArticle.objects.first().title)

    @override_settings(DISCOVER_NEWS_LOOKBACK_HOURS=24)
    def test_old_news_is_filtered_and_weather_is_separate(self):
        now = timezone.now()
        result = collect_news(FakeNewsClient(now - timedelta(hours=25)), now=now)
        self.assertEqual(result.news_created, 0)
        collect_weather(FakeWeatherClient(), city='Gumi', now=now)
        self.assertEqual(WeatherSnapshot.objects.count(), 1)
        self.assertEqual(NewsArticle.objects.count(), 0)

    def test_weather_can_be_collected_by_coordinates(self):
        snapshot = collect_weather(FakeWeatherClient(), lat=36.1, lon=128.3)
        self.assertEqual(snapshot.location, 'Current Location')
        self.assertEqual(snapshot.condition, '흐림')

    def test_current_weather_snapshot_by_coordinates_is_not_cached_globally(self):
        snapshot = current_weather_snapshot_by_coordinates(FakeWeatherClient(), lat=36.1, lon=128.3)

        self.assertEqual(snapshot.location, 'Current Location')
        self.assertEqual(snapshot.condition, '흐림')
        self.assertEqual(WeatherSnapshot.objects.count(), 0)


class CurrentWeatherViewTests(APITestCase):
    @patch('trends.views.current_weather_snapshot_by_coordinates')
    def test_current_weather_uses_request_coordinates(self, collect):
        snapshot = WeatherSnapshot(
            location='Current Location',
            observed_at=timezone.now(),
            condition='온흐림',
            temperature_c=19.5,
        )
        collect.return_value = snapshot

        response = self.client.get('/api/v1/weather/current', {'lat': '36.1', 'lon': '128.3'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['condition'], '흐림')
        self.assertEqual(response.data['location'], 'Current Location')
        collect.assert_called_once_with(lat=36.1, lon=128.3)

    def test_current_weather_rejects_invalid_coordinates(self):
        response = self.client.get('/api/v1/weather/current', {'lat': '100', 'lon': '128.3'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'INVALID_COORDINATES')


class TrendPublicationTests(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.articles = []
        index = 1
        for category in NewsCategory.values:
            for _ in range(3):
                self.articles.append(NewsArticle.objects.create(
                    title=f'뉴스 {index}', summary='요약', category=category,
                    source='example.com', source_url=f'https://example.com/{index}',
                    cache_key=NewsArticle.make_cache_key(f'https://example.com/{index}'), published_at=now,
                ))
                index += 1
        self.batch = TrendBatch.objects.create()
        self.job = AIJob.objects.create(
            kind=AIJob.Kind.TREND, batch=self.batch,
            request_payload={'articles': [
                {'id': article.id, 'category': article.category}
                for article in self.articles
            ]},
        )

    def payload(self):
        payload = []
        for section in DISCOVER_SECTIONS:
            articles = [
                article.id
                for article in self.articles
                if article.category == section['category']
            ]
            payload.append({
                'title': f"주제 {section['rank']}", 'summary': '요약', 'category': section['category'],
                'keywords': ['AI', '뉴스'], 'rank': section['rank'], 'article_ids': articles,
            })
        return payload

    def test_atomic_publication_and_discover_contract(self):
        complete_trend_job(self.job, self.payload())
        response = self.client.get('/api/v1/trends')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['results'][0]['news_count'], 3)
        self.assertEqual(len(response.data['results'][0]['news']), 3)

    def test_invalid_ai_result_does_not_publish_batch(self):
        with self.assertRaises(ValueError):
            complete_trend_job(self.job, self.payload()[:2])
        self.batch.refresh_from_db()
        self.assertNotEqual(self.batch.status, TrendBatch.Status.COMPLETED)

    def test_empty_cache_returns_503(self):
        self.assertEqual(self.client.get('/api/v1/trends').status_code, 503)

    def test_trend_callback_does_not_start_article_recommendations_inline(self):
        from rest_framework.test import APIClient

        with patch('trends.views.start_article_recommendation_generation') as starter:
            response = APIClient().post(
                f'/api/v1/internal/ai/jobs/{self.job.id}/complete',
                {'status': 'completed', 'topics': self.payload()},
                format='json',
                HTTP_X_INTERNAL_SECRET=settings.INTERNAL_AI_SECRET,
            )

        self.assertEqual(response.status_code, 200)
        starter.assert_not_called()
        self.job.refresh_from_db()
        self.batch.refresh_from_db()
        self.assertEqual(self.job.status, AIJob.Status.COMPLETED)
        self.assertEqual(self.batch.status, TrendBatch.Status.COMPLETED)


class ArticleRecommendationPublicationTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.batch = TrendBatch.objects.create(status=TrendBatch.Status.COMPLETED, published_at=now)
        self.topic = TrendTopic.objects.create(
            batch=self.batch,
            title='AI 동향',
            summary='요약',
            category=NewsCategory.TECH_SCIENCE,
            keywords=['AI', '기술'],
            rank=1,
        )
        self.article = NewsArticle.objects.create(
            title='뉴스 1', summary='요약', category=NewsCategory.TECH_SCIENCE,
            source='example.com', source_url='https://example.com/article',
            cache_key=NewsArticle.make_cache_key('https://example.com/article'), published_at=now,
        )
        self.link = TrendTopicNews.objects.create(
            topic=self.topic,
            article=self.article,
            rank=1,
            is_primary=True,
        )
        self.books = [
            Book.objects.create(isbn=f'978555555555{index}', title=f'도서 {index}')
            for index in range(1, 4)
        ]
        self.job = AIJob.objects.create(
            kind=AIJob.Kind.ARTICLE_RECOMMENDATION,
            batch=self.batch,
            request_payload={
                'recommendations_per_article': 3,
                'articles': [{
                    'topic_news_id': self.link.id,
                    'candidates': [
                        {
                            'isbn': book.isbn,
                            'book_id': book.id,
                            'retrieval_score': 0.9,
                            'embedding_model': 'test-embedding',
                        }
                        for book in self.books
                    ],
                }],
            },
        )

    def test_article_recommendation_callback_publishes_three_books(self):
        complete_article_recommendation_job(self.job, [{
            'topic_news_id': self.link.id,
            'recommendations': [
                {'isbn': book.isbn, 'reason': f'{book.title} 추천', 'relevance_score': 0.8}
                for book in self.books
            ],
        }])
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, AIJob.Status.COMPLETED)
        self.assertEqual(NewsRecommendation.objects.filter(topic_news=self.link).count(), 3)

    def test_article_recommendation_retry_endpoint_starts_new_job(self):
        from rest_framework.test import APIClient

        self.job.status = AIJob.Status.FAILED
        self.job.error_message = 'failed once'
        self.job.finished_at = timezone.now()
        self.job.save(update_fields=['status', 'error_message', 'finished_at'])

        with patch('trends.views.start_article_recommendation_generation') as starter:
            new_job = AIJob.objects.create(
                kind=AIJob.Kind.ARTICLE_RECOMMENDATION,
                batch=self.batch,
                status=AIJob.Status.PROCESSING,
            )
            starter.return_value = (new_job, False)
            response = APIClient().post('/api/v1/trends/article-recommendations/generate')

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data['job_id'], str(new_job.id))

    def test_failed_ai_callback_marks_job_failed_without_400(self):
        from rest_framework.test import APIClient

        response = APIClient().post(
            f'/api/v1/internal/ai/jobs/{self.job.id}/complete',
            {'status': 'failed', 'error': '뉴스별 추천 ISBN 검증에 실패했습니다.'},
            format='json',
            HTTP_X_INTERNAL_SECRET=settings.INTERNAL_AI_SECRET,
        )
        self.assertEqual(response.status_code, 200)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, AIJob.Status.FAILED)
        self.assertIn('ISBN', self.job.error_message)

    def test_failed_trend_callback_marks_batch_failed(self):
        from rest_framework.test import APIClient

        trend_job = AIJob.objects.create(
            kind=AIJob.Kind.TREND,
            batch=self.batch,
            status=AIJob.Status.PROCESSING,
        )
        response = APIClient().post(
            f'/api/v1/internal/ai/jobs/{trend_job.id}/complete',
            {'status': 'failed', 'error': '트렌드 구조 의미 검증에 두 번 실패했습니다.'},
            format='json',
            HTTP_X_INTERNAL_SECRET=settings.INTERNAL_AI_SECRET,
        )
        self.assertEqual(response.status_code, 200)
        trend_job.refresh_from_db()
        self.batch.refresh_from_db()
        self.assertEqual(trend_job.status, AIJob.Status.FAILED)
        self.assertEqual(self.batch.status, TrendBatch.Status.FAILED)


class ArticleRecommendationEmbeddingTests(TestCase):
    @override_settings(OPENAI_EMBEDDING_MODEL='test-embedding', OPENAI_EMBEDDING_DIMENSIONS=2)
    def test_article_recommendation_batches_query_embeddings(self):
        now = timezone.now()
        batch = TrendBatch.objects.create(status=TrendBatch.Status.COMPLETED, published_at=now)
        topic = TrendTopic.objects.create(
            batch=batch,
            title='AI 동향',
            summary='요약',
            category=NewsCategory.TECH_SCIENCE,
            keywords=['AI', '기술'],
            rank=1,
        )
        for index in range(2):
            article = NewsArticle.objects.create(
                title=f'뉴스 {index + 1}', summary='요약', category=NewsCategory.TECH_SCIENCE,
                source='example.com', source_url=f'https://example.com/article-{index}',
                cache_key=NewsArticle.make_cache_key(f'https://example.com/article-{index}'), published_at=now,
            )
            TrendTopicNews.objects.create(topic=topic, article=article, rank=index + 1, is_primary=index == 0)
        books = [
            Book.objects.create(isbn=f'978444444444{index}', title=f'도서 {index}', sales_point=2000)
            for index in range(1, 4)
        ]
        for index, book in enumerate(books, start=1):
            BookEmbedding.objects.create(
                book=book,
                vector=[1.0, index / 10],
                model='test-embedding',
                dimensions=2,
                content_hash=f'hash-{index}',
            )

        class FakeClient:
            def __init__(self):
                self.embed_calls = []
                self.submitted_payload = None

            def embed(self, texts):
                self.embed_calls.append(texts)
                return {
                    'model': 'test-embedding',
                    'dimensions': 2,
                    'vectors': [[1.0, 0.0] for _ in texts],
                }

            def submit(self, kind, payload):
                self.submitted_payload = payload
                return {'job_id': payload['job_id'], 'status': 'accepted'}

        client = FakeClient()
        job, cached = start_article_recommendation_generation(batch, ai_client=client)

        self.assertFalse(cached)
        self.assertEqual(job.status, AIJob.Status.PROCESSING)
        self.assertEqual(len(client.embed_calls), 1)
        self.assertEqual(len(client.embed_calls[0]), 2)
        self.assertEqual(len(client.submitted_payload['articles']), 2)


class RefreshDiscoverEmbeddingScopeTests(TestCase):
    @patch('trends.services.start_trend_generation')
    @patch('trends.services.sync_sources')
    @patch('trends.services.sync_book_embeddings')
    @patch('trends.services.sync_aladin_list')
    def test_refresh_only_embeds_books_touched_by_aladin_refresh(
        self, sync_aladin, sync_embeddings, sync_sources_mock, start_trend,
    ):
        touched = Book.objects.create(isbn='9787777777771', title='갱신된 도서', sales_point=2000)
        untouched = Book.objects.create(isbn='9787777777772', title='기존 도서', sales_point=2000)
        sync_aladin.return_value = BookSyncResult(updated=1, rankings=1, book_ids={touched.id})
        sync_sources_mock.return_value = type('SourceResult', (), {
            'news_created': 0,
            'news_updated': 0,
            'news_skipped': 0,
            'weather_saved': True,
            'errors': [],
        })()
        start_trend.return_value = type('TrendJob', (), {'id': 'job-id'})()
        sync_embeddings.return_value = type('EmbeddingResult', (), {
            'created': 1,
            'updated': 0,
            'skipped': 0,
        })()

        refresh_discover_cache()

        embedded_books = sync_embeddings.call_args.args[0]
        self.assertEqual([book.id for book in embedded_books], [touched.id])
        self.assertNotIn(untouched.id, [book.id for book in embedded_books])
        self.assertEqual(sync_embeddings.call_args.kwargs['batch_size'], 100)


class WeatherNormalizationTests(TestCase):
    def test_known_weather_typo_is_replaced(self):
        self.assertEqual(normalize_weather_condition('튼구름'), '구름 많음')
        self.assertEqual(normalize_weather_condition('온흐림'), '흐림')
        self.assertEqual(normalize_weather_condition('맑음'), '맑음')

    def test_weather_snapshot_serializer_normalizes_condition(self):
        snapshot = WeatherSnapshot.objects.create(
            location='Gumi',
            observed_at=timezone.now(),
            condition='온흐림',
            temperature_c=21.5,
        )
        data = WeatherSnapshotSerializer(snapshot).data
        self.assertEqual(data['condition'], '흐림')


class RecommendationFilterTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.batch = TrendBatch.objects.create(status=TrendBatch.Status.COMPLETED, published_at=now)
        self.topic = TrendTopic.objects.create(
            batch=self.batch,
            title='AI 동향',
            summary='요약',
            category=NewsCategory.TECH_SCIENCE,
            keywords=['AI'],
            rank=1,
        )
        self.books = [
            Book.objects.create(
                isbn=f'978666666666{index}',
                title=f'도서 {index}',
                sales_point=sales_point,
            )
            for index, sales_point in enumerate([5000, 4000, 3000, 2000, 1500, 1000, 999], start=1)
        ]

    def test_filter_recommendation_records_limits_and_filters_sales_point(self):
        records = [
            Recommendation(
                topic=self.topic,
                book=book,
                reason='추천',
                relevance_score=1 - index * 0.05,
            )
            for index, book in enumerate(self.books)
        ]
        filtered = filter_recommendation_records(records)
        self.assertEqual(len(filtered), 5)
        self.assertEqual(
            [record.book.sales_point for record in filtered],
            [5000, 4000, 3000, 2000, 1500],
        )

    def test_filter_recommendation_records_deduplicates_isbn(self):
        duplicate_book = self.books[0]
        records = [
            Recommendation(topic=self.topic, book=duplicate_book, reason='1', relevance_score=0.9),
            Recommendation(topic=self.topic, book=duplicate_book, reason='2', relevance_score=0.8),
            Recommendation(topic=self.topic, book=self.books[1], reason='3', relevance_score=0.7),
        ]
        filtered = filter_recommendation_records(records, limit=5)
        self.assertEqual(len(filtered), 2)
        self.assertEqual({record.book.isbn for record in filtered}, {
            duplicate_book.isbn,
            self.books[1].isbn,
        })


class SchedulerLockTests(TestCase):
    @patch('trends.scheduler.refresh_discover_cache')
    def test_running_lock_skips_duplicate_refresh(self, refresh):
        SyncRun.objects.create(
            lock_key='discover_refresh',
            status=SyncRun.Status.RUNNING,
            started_at=timezone.now(),
        )
        self.assertFalse(run_refresh_if_due(force=True))
        refresh.assert_not_called()


class TrendRefreshViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='refresh-user',
            email='refresh@example.com',
            nickname='Refresh',
            password='pass1234',
        )

    def test_refresh_requires_authentication(self):
        response = self.client.post('/api/v1/trends/refresh')

        self.assertIn(response.status_code, (401, 403))

    @patch('trends.views._launch_refresh_thread')
    def test_authenticated_refresh_starts_background_run(self, launch):
        self.client.force_authenticate(self.user)

        response = self.client.post('/api/v1/trends/refresh')

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data['status'], 'running')
        self.assertEqual(response.data['phase'], 'queued')
        launch.assert_called_once()
        run = SyncRun.objects.get(lock_key='discover_refresh')
        self.assertEqual(run.status, SyncRun.Status.RUNNING)
        self.assertEqual(run.metadata['requested_by'], self.user.id)

    @patch('trends.views._launch_refresh_thread')
    def test_running_refresh_is_reused_without_duplicate_launch(self, launch):
        SyncRun.objects.create(
            lock_key='discover_refresh',
            status=SyncRun.Status.RUNNING,
            started_at=timezone.now(),
            metadata={'phase': 'collecting', 'message': '도서, 임베딩, 뉴스와 날씨를 수집 중입니다.'},
        )
        self.client.force_authenticate(self.user)

        response = self.client.post('/api/v1/trends/refresh')

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data['status'], 'running')
        self.assertEqual(response.data['phase'], 'collecting')
        launch.assert_not_called()

    @patch('trends.views._wait_for_trend_job')
    @patch('trends.views.refresh_discover_cache')
    def test_background_refresh_stores_trend_job_id(self, refresh_cache, wait_for_job):
        from trends.views import _run_discover_refresh_background

        batch = TrendBatch.objects.create()
        job = AIJob.objects.create(kind=AIJob.Kind.TREND, batch=batch, status=AIJob.Status.PROCESSING)
        refresh_cache.return_value = {'trend_job_id': str(job.id), 'sources': {'news_created': 1}}
        run = SyncRun.objects.create(
            lock_key='discover_refresh',
            status=SyncRun.Status.RUNNING,
            started_at=timezone.now(),
        )

        _run_discover_refresh_background(run.id, news_display=30)

        run.refresh_from_db()
        self.assertEqual(run.metadata['trend_job_id'], str(job.id))
        self.assertEqual(run.metadata['phase'], 'generating')
        wait_for_job.assert_called_once_with(run.id, str(job.id))

    def test_status_marks_completed_when_trend_job_completed(self):
        batch = TrendBatch.objects.create(status=TrendBatch.Status.COMPLETED, published_at=timezone.now())
        job = AIJob.objects.create(
            kind=AIJob.Kind.TREND,
            batch=batch,
            status=AIJob.Status.COMPLETED,
            finished_at=timezone.now(),
        )
        SyncRun.objects.create(
            lock_key='discover_refresh',
            status=SyncRun.Status.RUNNING,
            started_at=timezone.now(),
            metadata={'phase': 'generating', 'trend_job_id': str(job.id)},
        )
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/trends/refresh/status')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['phase'], 'completed')
        run = SyncRun.objects.get(lock_key='discover_refresh')
        self.assertEqual(run.status, SyncRun.Status.COMPLETED)

    def test_status_marks_failed_when_trend_job_failed_and_keeps_public_batch(self):
        public_batch = TrendBatch.objects.create(
            status=TrendBatch.Status.COMPLETED,
            published_at=timezone.now() - timedelta(minutes=5),
        )
        failed_batch = TrendBatch.objects.create(status=TrendBatch.Status.FAILED)
        job = AIJob.objects.create(
            kind=AIJob.Kind.TREND,
            batch=failed_batch,
            status=AIJob.Status.FAILED,
            error_message='boom',
            finished_at=timezone.now(),
        )
        SyncRun.objects.create(
            lock_key='discover_refresh',
            status=SyncRun.Status.RUNNING,
            started_at=timezone.now(),
            metadata={'phase': 'generating', 'trend_job_id': str(job.id)},
        )
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/v1/trends/refresh/status')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['phase'], 'failed')
        self.assertEqual(response.data['error'], 'boom')
        public_batch.refresh_from_db()
        self.assertEqual(public_batch.status, TrendBatch.Status.COMPLETED)
