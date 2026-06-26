import json
import unittest

import httpx

from ai_service.app.openai_adapter import (
    OpenAIAdapter,
    _build_single_article_recommendation_schema,
    _repair_trend_topics,
)
from pydantic import ValidationError

from ai_service.app.schemas import (
    ArticleRecommendationJobRequest,
    TrendGenerationOutput,
    TrendJobRequest,
    TrendTopicOutput,
)


class OpenAIAdapterTests(unittest.TestCase):
    def test_responses_api_uses_gpt_54_mini_and_strict_schema(self):
        categories = ['TECH_SCIENCE', 'BUSINESS', 'ARTS_CULTURE']
        topics = [
            {
                'title': f'주제 {rank}', 'summary': '검증 가능한 요약', 'category': category,
                'keywords': ['AI', '기술'], 'rank': rank,
                'article_ids': [1, 2, 3],
            }
            for rank, category in enumerate(categories, start=1)
        ]

        def handler(request):
            payload = json.loads(request.content)
            self.assertEqual(payload['model'], 'gpt-5.4-mini')
            self.assertEqual(payload['text']['format']['type'], 'json_schema')
            self.assertTrue(payload['text']['format']['strict'])
            return httpx.Response(200, json={
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps({'topics': topics})}]}],
            })

        adapter = OpenAIAdapter(
            api_key='test-key', base_url='https://api.openai.test/v1',
            transport=httpx.MockTransport(handler),
        )
        articles = []
        for offset, category in enumerate(categories):
            for local_index in range(1, 4):
                article_id = offset * 3 + local_index
                articles.append({
                    'id': article_id,
                    'title': f'뉴스 {article_id}',
                    'summary': '요약',
                    'category': category,
                    'published_at': '2026-06-22T00:00:00Z',
                })
        request = TrendJobRequest.model_validate({
            'job_id': 'job',
            'articles': articles,
            'callback_url': 'http://localhost/callback',
        })
        result = adapter.generate_trends(request)
        self.assertEqual(len(result.topics), 3)

    def test_repair_trend_topics_normalizes_mismatched_sections(self):
        categories = ['TECH_SCIENCE', 'BUSINESS', 'ARTS_CULTURE']
        ids_by_category = {
            category: [index * 3 + offset for offset in range(1, 4)]
            for index, category in enumerate(categories)
        }
        topics = [
            {
                'title': f'Topic {rank}', 'summary': 'Summary', 'category': 'TECH_SCIENCE',
                'keywords': ['news', 'books'], 'rank': rank,
                'article_ids': [1, 2, 3],
            }
            for rank in range(1, 4)
        ]
        repaired = _repair_trend_topics(TrendGenerationOutput.model_validate({'topics': topics}), ids_by_category)
        self.assertEqual([item.category for item in repaired.topics], categories)
        self.assertEqual([item.rank for item in repaired.topics], [1, 2, 3])
        self.assertEqual(repaired.topics[1].article_ids, [4, 5, 6])

    def test_trend_generation_repairs_article_ids_by_section(self):
        categories = ['TECH_SCIENCE', 'BUSINESS', 'ARTS_CULTURE']
        topics = [
            {
                'title': f'Topic {rank}', 'summary': 'Summary', 'category': category,
                'keywords': ['news', 'books'], 'rank': rank,
                'article_ids': [1, 2, 3],
            }
            for rank, category in enumerate(categories, start=1)
        ]

        def handler(request):
            return httpx.Response(200, json={
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps({'topics': topics})}]}],
            })

        adapter = OpenAIAdapter(
            api_key='test-key', base_url='https://api.openai.test/v1',
            transport=httpx.MockTransport(handler),
        )
        articles = []
        for offset, category in enumerate(categories):
            for local_index in range(1, 4):
                article_id = offset * 3 + local_index
                articles.append({
                    'id': article_id,
                    'title': f'News {article_id}',
                    'summary': 'Summary',
                    'category': category,
                    'published_at': '2026-06-22T00:00:00Z',
                })
        result = adapter.generate_trends(TrendJobRequest.model_validate({
            'job_id': 'job',
            'articles': articles,
            'callback_url': 'http://localhost/callback',
        }))
        for index, topic in enumerate(result.topics):
            self.assertEqual(topic.article_ids, [index * 3 + 1, index * 3 + 2, index * 3 + 3])

    def test_trend_topic_output_rejects_inactive_categories(self):
        with self.assertRaises(ValidationError):
            TrendTopicOutput.model_validate({
                'title': '주제', 'summary': '요약', 'category': 'SPORTS',
                'keywords': ['news', 'books'], 'rank': 1, 'article_ids': [1, 2, 3],
            })
        with self.assertRaises(ValidationError):
            TrendTopicOutput.model_validate({
                'title': '주제', 'summary': '요약', 'category': 'ENTERTAINMENT',
                'keywords': ['news', 'books'], 'rank': 1, 'article_ids': [1, 2, 3],
            })

    def test_trend_topic_output_rejects_rank_outside_active_sections(self):
        with self.assertRaises(ValidationError):
            TrendTopicOutput.model_validate({
                'title': '주제', 'summary': '요약', 'category': 'TECH_SCIENCE',
                'keywords': ['news', 'books'], 'rank': 4, 'article_ids': [1, 2, 3],
            })

    def test_trend_generation_output_requires_exactly_three_topics(self):
        with self.assertRaises(ValidationError):
            TrendGenerationOutput.model_validate({'topics': []})
        with self.assertRaises(ValidationError):
            TrendGenerationOutput.model_validate({
                'topics': [
                    {
                        'title': f'Topic {rank}', 'summary': 'Summary', 'category': 'TECH_SCIENCE',
                        'keywords': ['news', 'books'], 'rank': rank, 'article_ids': [1, 2, 3],
                    }
                    for rank in range(1, 5)
                ],
            })

    def test_single_article_recommendation_schema_constrains_isbn(self):
        schema = _build_single_article_recommendation_schema(
            ['9780000000001', '9780000000002', '9780000000003'],
            3,
        )
        recommendation_schema = schema['properties']['recommendations']
        self.assertEqual(recommendation_schema['minItems'], 3)
        self.assertEqual(recommendation_schema['maxItems'], 3)
        self.assertEqual(
            recommendation_schema['items']['properties']['isbn']['enum'],
            ['9780000000001', '9780000000002', '9780000000003'],
        )

    def test_generate_article_recommendations_accepts_candidate_isbns(self):
        payload = {
            'recommendations': [
                {'isbn': '9780000000001', 'reason': '첫 번째 추천', 'relevance_score': 0.9},
                {'isbn': '9780000000002', 'reason': '두 번째 추천', 'relevance_score': 0.8},
                {'isbn': '9780000000003', 'reason': '세 번째 추천', 'relevance_score': 0.7},
            ],
        }

        def handler(request):
            sent_schema = json.loads(request.content)['text']['format']['schema']
            self.assertEqual(
                sent_schema['properties']['recommendations']['items']['properties']['isbn']['enum'],
                ['9780000000001', '9780000000002', '9780000000003'],
            )
            return httpx.Response(200, json={
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(payload)}]}],
            })

        adapter = OpenAIAdapter(
            api_key='test-key', base_url='https://api.openai.test/v1',
            transport=httpx.MockTransport(handler),
        )
        request = ArticleRecommendationJobRequest.model_validate({
            'job_id': 'job',
            'recommendations_per_article': 3,
            'articles': [{
                'topic_news_id': 1,
                'article': {'id': 1, 'title': '뉴스 1', 'summary': '요약'},
                'topic': {
                    'id': 1, 'title': 'AI', 'summary': '요약', 'category': 'TECH_SCIENCE',
                    'keywords': ['AI'],
                },
                'candidates': [
                    {'isbn': '9780000000001', 'title': '도서 1', 'retrieval_score': 0.9},
                    {'isbn': '9780000000002', 'title': '도서 2', 'retrieval_score': 0.8},
                    {'isbn': '9780000000003', 'title': '도서 3', 'retrieval_score': 0.7},
                ],
            }],
            'callback_url': 'http://localhost/callback',
        })
        result = adapter.generate_article_recommendations(request)
        self.assertEqual(len(result.article_recommendations[0].recommendations), 3)

    def test_embeddings_api_preserves_input_order(self):
        def handler(request):
            payload = json.loads(request.content)
            self.assertEqual(payload['model'], 'text-embedding-3-small')
            self.assertEqual(payload['dimensions'], 768)
            return httpx.Response(200, json={
                'data': [
                    {'index': 1, 'embedding': [0.0, 1.0] + [0.0] * 766},
                    {'index': 0, 'embedding': [1.0, 0.0] + [0.0] * 766},
                ],
            })

        adapter = OpenAIAdapter(
            api_key='test-key', base_url='https://api.openai.test/v1',
            transport=httpx.MockTransport(handler),
        )
        vectors = adapter.embed(['첫째', '둘째'])
        self.assertEqual(len(vectors[0]), 768)
        self.assertEqual(vectors[0][:2], [1.0, 0.0])
        self.assertEqual(vectors[1][:2], [0.0, 1.0])
