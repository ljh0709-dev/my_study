import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai_service.app.config import settings
from ai_service.app.main import app
from ai_service.app.schemas import BookAnalysisResponse


class FastAPIServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.headers = {'X-Internal-Secret': settings.internal_ai_secret}

    def test_health_exposes_provider_contract_without_secret(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['service'], 'trendbook-ai')
        self.assertEqual(response.json()['model'], 'gpt-5.4-mini')
        self.assertIn('provider_configured', response.json())

    def test_internal_endpoints_require_secret(self):
        self.assertEqual(self.client.post('/internal/v1/recommendations', json=self.recommendation_payload()).status_code, 401)
        self.assertEqual(self.client.post('/internal/v1/article-recommendations', json=self.article_recommendation_payload()).status_code, 401)
        self.assertEqual(self.client.post('/internal/v1/trends', json=self.trend_payload()).status_code, 401)
        self.assertEqual(self.client.post('/internal/v1/embeddings', json={'texts': ['a']}).status_code, 401)

    @patch('ai_service.app.main.process_recommendation_job')
    def test_recommendation_job_accepts_structured_payload(self, processor):
        response = self.client.post('/internal/v1/recommendations', headers=self.headers, json=self.recommendation_payload())
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {'job_id': 'job-rec', 'status': 'accepted'})
        processor.assert_called_once()

    @patch('ai_service.app.main.process_trend_job')
    def test_trend_job_accepts_structured_payload(self, processor):
        response = self.client.post('/internal/v1/trends', headers=self.headers, json=self.trend_payload())
        self.assertEqual(response.status_code, 202)
        processor.assert_called_once()

    @patch('ai_service.app.main.process_article_recommendation_job')
    def test_article_recommendation_job_accepts_structured_payload(self, processor):
        response = self.client.post('/internal/v1/article-recommendations', headers=self.headers, json=self.article_recommendation_payload())
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {'job_id': 'job-article-rec', 'status': 'accepted'})
        processor.assert_called_once()

    @patch('ai_service.app.main.OpenAIAdapter')
    def test_embedding_endpoint_returns_provider_vectors(self, adapter_class):
        adapter_class.return_value.embed.return_value = [[0.1, 0.2], [0.3, 0.4]]
        response = self.client.post('/internal/v1/embeddings', headers=self.headers, json={'texts': ['a', 'b']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['vectors'], [[0.1, 0.2], [0.3, 0.4]])

    @patch('ai_service.app.main.OpenAIAdapter')
    def test_book_analysis_endpoint_uses_gpt_adapter(self, adapter_class):
        adapter_class.return_value.analyze_book.return_value = BookAnalysisResponse(
            sales_reason='관심 요인', review_summary='리뷰 본문이 없어 경향을 단정할 수 없습니다.', model='gpt-5.4-mini',
        )
        response = self.client.post('/internal/v1/book-analysis', headers=self.headers, json={
            'isbn': '9780000000001', 'title': '테스트 도서', 'review_excerpts': [],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['model'], 'gpt-5.4-mini')

    @staticmethod
    def trend_payload():
        categories = ['TECH_SCIENCE', 'BUSINESS', 'ARTS_CULTURE']
        articles = []
        for offset, category in enumerate(categories):
            for local_index in range(1, 4):
                article_id = offset * 3 + local_index
                articles.append({
                    'id': article_id,
                    'title': f'뉴스 {article_id}',
                    'summary': '요약',
                    'category': category,
                    'published_at': '2026-06-22T09:00:00+09:00',
                })
        return {
            'job_id': 'job-trend',
            'articles': articles,
            'callback_url': 'http://127.0.0.1:8000/api/v1/internal/ai/jobs/00000000-0000-0000-0000-000000000001/complete',
        }

    @staticmethod
    def recommendation_payload():
        return {
            'job_id': 'job-rec',
            'trend': {
                'id': 1, 'title': 'AI 기술 동향', 'summary': '생성형 AI 뉴스가 증가한다.', 'category': 'TECH_SCIENCE',
                'news': [{'id': index, 'title': f'뉴스 {index}', 'summary': '요약'} for index in range(1, 4)],
            },
            'weather': {'location': '구미', 'condition': '맑음', 'temperature_c': 24.5},
            'candidates': [
                {'isbn': f'978000000000{index}', 'title': f'도서 {index}', 'categories': ['과학'], 'retrieval_score': 0.95 - index * 0.05}
                for index in range(1, 6)
            ],
            'callback_url': 'http://127.0.0.1:8000/api/v1/internal/ai/jobs/00000000-0000-0000-0000-000000000002/complete',
        }

    @staticmethod
    def article_recommendation_payload():
        return {
            'job_id': 'job-article-rec',
            'recommendations_per_article': 3,
            'articles': [{
                'topic_news_id': 1,
                'article': {'id': 1, 'title': '뉴스 1', 'summary': '요약', 'source': 'example.com'},
                'topic': {
                    'id': 1, 'title': 'AI 동향', 'summary': '요약', 'category': 'TECH_SCIENCE',
                    'keywords': ['AI', '기술'],
                },
                'candidates': [
                    {'isbn': f'978000000000{index}', 'title': f'도서 {index}', 'categories': ['과학'], 'retrieval_score': 0.95 - index * 0.05}
                    for index in range(1, 4)
                ],
            }],
            'callback_url': 'http://127.0.0.1:8000/api/v1/internal/ai/jobs/00000000-0000-0000-0000-000000000003/complete',
        }


if __name__ == '__main__':
    unittest.main()
