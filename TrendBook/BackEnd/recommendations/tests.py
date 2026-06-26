from django.test import TestCase
from django.utils import timezone

from books.models import Book, BookEmbedding
from trends.models import NewsArticle, NewsCategory, TrendBatch, TrendTopic, TrendTopicNews
from trends.services import complete_recommendation_job, start_recommendation_generation


class AcceptingAIClient:
    def submit(self, kind, payload):
        return {'job_id': payload['job_id'], 'status': 'accepted'}

    def embed(self, texts):
        return {'model': 'test-embedding', 'dimensions': 2, 'vectors': [[1.0, 0.0] for _ in texts]}


class RecommendationJobTests(TestCase):
    def setUp(self):
        batch = TrendBatch.objects.create(status=TrendBatch.Status.COMPLETED, published_at=timezone.now())
        self.topic = TrendTopic.objects.create(
            batch=batch, title='AI와 독서', summary='뉴스 맥락', category=NewsCategory.TECH_SCIENCE,
            keywords=['AI'], rank=1,
        )
        for rank in range(1, 4):
            url = f'https://example.com/news/{rank}'
            article = NewsArticle.objects.create(
                title=f'뉴스 {rank}', summary='요약', category=NewsCategory.TECH_SCIENCE,
                source='example.com', source_url=url,
                cache_key=NewsArticle.make_cache_key(url), published_at=timezone.now(),
            )
            TrendTopicNews.objects.create(topic=self.topic, article=article, rank=rank, is_primary=rank == 1)
        self.books = [
            Book.objects.create(
                isbn=f'97822222222{index:02d}', title=f'AI 도서 {index}',
                description='AI 기술과 사회를 설명하는 책', sales_point=2000 - index,
            ) for index in range(1, 7)
        ]
        for index, book in enumerate(self.books, start=1):
            BookEmbedding.objects.create(
                book=book, vector=[1.0, index / 100], model='test-embedding',
                dimensions=2, content_hash=f'{index:064d}',
            )

    def test_active_job_and_completed_recommendations_are_reused(self):
        client = AcceptingAIClient()
        first_job, cached = start_recommendation_generation(self.topic, ai_client=client)
        second_job, _ = start_recommendation_generation(self.topic, ai_client=client)
        self.assertIsNone(cached)
        self.assertEqual(first_job.id, second_job.id)

        outputs = [
            {'isbn': item['isbn'], 'reason': '뉴스 맥락과 직접 연결됩니다.', 'relevance_score': 0.9 - index * 0.05}
            for index, item in enumerate(first_job.request_payload['candidates'][:5])
        ]
        complete_recommendation_job(first_job, outputs)
        job, cached = start_recommendation_generation(self.topic, ai_client=client)
        self.assertIsNone(job)
        self.assertEqual(len(cached), 5)

    def test_candidate_outside_allowlist_is_rejected(self):
        job, _ = start_recommendation_generation(self.topic, ai_client=AcceptingAIClient())
        outputs = [
            {'isbn': item['isbn'], 'reason': '추천 사유', 'relevance_score': 0.8}
            for item in job.request_payload['candidates'][:4]
        ]
        outputs.append({'isbn': '9789999999999', 'reason': '잘못된 후보', 'relevance_score': 0.8})
        with self.assertRaises(ValueError):
            complete_recommendation_job(job, outputs)
