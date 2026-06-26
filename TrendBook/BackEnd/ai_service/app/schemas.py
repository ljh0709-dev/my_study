from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class NewsCandidate(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=500)
    summary: str = Field(default='', max_length=2000)
    category: str = Field(min_length=1, max_length=20)
    published_at: datetime


class TrendJobRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=64)
    articles: list[NewsCandidate] = Field(min_length=9, max_length=60)
    callback_url: HttpUrl


class TrendTopicOutput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=700)
    category: Literal['TECH_SCIENCE', 'BUSINESS', 'ARTS_CULTURE']
    keywords: list[str] = Field(min_length=2, max_length=6)
    rank: int = Field(ge=1, le=3)
    article_ids: list[int] = Field(min_length=3, max_length=3)


class TrendGenerationOutput(BaseModel):
    topics: list[TrendTopicOutput] = Field(min_length=3, max_length=3)


class NewsContext(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=500)
    summary: str = Field(default='', max_length=2000)


class TrendContext(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=20)
    news: list[NewsContext] = Field(min_length=3, max_length=5)


class WeatherContext(BaseModel):
    location: str = Field(min_length=1, max_length=100)
    condition: str = Field(min_length=1, max_length=100)
    temperature_c: float


class BookCandidate(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    title: str = Field(min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=4000)
    categories: list[str] = Field(default_factory=list, max_length=8)
    sales_point: int | None = Field(default=None, ge=0)
    rank: int | None = Field(default=None, ge=1)
    retrieval_score: float = Field(ge=-1, le=1)


class RecommendationJobRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=64)
    trend: TrendContext
    weather: WeatherContext | None = None
    candidates: list[BookCandidate] = Field(min_length=5, max_length=20)
    callback_url: HttpUrl


class RecommendationOutput(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    reason: str = Field(min_length=1, max_length=700)
    relevance_score: float = Field(ge=0, le=1)


class RecommendationGenerationOutput(BaseModel):
    recommendations: list[RecommendationOutput] = Field(min_length=5, max_length=5)


class ArticleTopicContext(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=20)
    keywords: list[str] = Field(default_factory=list, max_length=8)


class ArticleNewsContext(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=500)
    summary: str = Field(default='', max_length=2000)
    source: str | None = Field(default=None, max_length=150)


class ArticleRecommendationContext(BaseModel):
    topic_news_id: int
    article: ArticleNewsContext
    topic: ArticleTopicContext
    candidates: list[BookCandidate] = Field(min_length=3, max_length=10)


class ArticleRecommendationJobRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=64)
    articles: list[ArticleRecommendationContext] = Field(min_length=1, max_length=15)
    recommendations_per_article: int = Field(default=3, ge=1, le=5)
    callback_url: HttpUrl


class ArticleRecommendationGroup(BaseModel):
    topic_news_id: int
    recommendations: list[RecommendationOutput] = Field(min_length=1, max_length=5)


class ArticleRecommendationGenerationOutput(BaseModel):
    article_recommendations: list[ArticleRecommendationGroup] = Field(min_length=1, max_length=15)


class EmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=100)


class EmbeddingResponse(BaseModel):
    model: str
    dimensions: int
    vectors: list[list[float]]


class BookAnalysisRequest(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    title: str = Field(min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    categories: list[str] = Field(default_factory=list, max_length=8)
    sales_point: int | None = Field(default=None, ge=0)
    customer_review_rank: float | None = Field(default=None, ge=0, le=10)
    review_excerpts: list[str] = Field(default_factory=list, max_length=30)


class BookAnalysisResponse(BaseModel):
    sales_reason: str = Field(min_length=1, max_length=1000)
    review_summary: str = Field(min_length=1, max_length=1200)
    model: str


class JobAcceptedResponse(BaseModel):
    job_id: str
    status: Literal['accepted'] = 'accepted'


class HealthResponse(BaseModel):
    status: Literal['ok'] = 'ok'
    service: str
    environment: str
    model: str
    embedding_model: str
    provider_configured: bool
