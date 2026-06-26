import logging

import httpx

from .config import settings
from .openai_adapter import OpenAIAdapter
from .schemas import ArticleRecommendationJobRequest, RecommendationJobRequest, TrendJobRequest


logger = logging.getLogger(__name__)


def _callback(url, payload):
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                str(url), json=payload,
                headers={'X-Internal-Secret': settings.internal_ai_secret},
            )
            response.raise_for_status()
    except httpx.HTTPError:
        logger.exception('AI callback failed: %s', url)


def process_trend_job(payload: TrendJobRequest, adapter=None):
    try:
        result = (adapter or OpenAIAdapter()).generate_trends(payload)
        _callback(payload.callback_url, {'status': 'completed', 'topics': [item.model_dump() for item in result.topics]})
    except Exception as exc:  # background boundary: failure must reach Django job state
        logger.exception('Trend generation failed: %s', payload.job_id)
        _callback(payload.callback_url, {'status': 'failed', 'error': str(exc)[:1000]})


def process_recommendation_job(payload: RecommendationJobRequest, adapter=None):
    try:
        result = (adapter or OpenAIAdapter()).generate_recommendations(payload)
        _callback(payload.callback_url, {
            'status': 'completed',
            'recommendations': [item.model_dump() for item in result.recommendations],
        })
    except Exception as exc:
        logger.exception('Recommendation generation failed: %s', payload.job_id)
        _callback(payload.callback_url, {'status': 'failed', 'error': str(exc)[:1000]})


def process_article_recommendation_job(payload: ArticleRecommendationJobRequest, adapter=None):
    try:
        result = (adapter or OpenAIAdapter()).generate_article_recommendations(payload)
        _callback(payload.callback_url, {
            'status': 'completed',
            'article_recommendations': [
                item.model_dump() for item in result.article_recommendations
            ],
        })
    except Exception as exc:
        logger.exception('Article recommendation generation failed: %s', payload.job_id)
        _callback(payload.callback_url, {'status': 'failed', 'error': str(exc)[:1000]})
