from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status

from .config import settings
from .openai_adapter import OpenAIAPIError, OpenAIAdapter
from .schemas import (
    ArticleRecommendationJobRequest,
    BookAnalysisRequest,
    BookAnalysisResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    HealthResponse,
    JobAcceptedResponse,
    RecommendationJobRequest,
    TrendJobRequest,
)
from .security import require_internal_secret
from .tasks import process_article_recommendation_job, process_recommendation_job, process_trend_job


app = FastAPI(
    title='TrendBook AI Service', version='2.0.0',
    docs_url='/docs' if settings.environment == 'local' else None, redoc_url=None,
)


@app.get('/health', response_model=HealthResponse)
def health():
    return HealthResponse(
        service=settings.service_name,
        environment=settings.environment,
        model=settings.openai_model,
        embedding_model=settings.openai_embedding_model,
        provider_configured=bool(settings.openai_api_key),
    )


@app.post('/internal/v1/trends', response_model=JobAcceptedResponse, status_code=202, dependencies=[Depends(require_internal_secret)])
def create_trend_job(payload: TrendJobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_trend_job, payload)
    return JobAcceptedResponse(job_id=payload.job_id)


@app.post('/internal/v1/recommendations', response_model=JobAcceptedResponse, status_code=202, dependencies=[Depends(require_internal_secret)])
def create_recommendation_job(payload: RecommendationJobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_recommendation_job, payload)
    return JobAcceptedResponse(job_id=payload.job_id)


@app.post('/internal/v1/article-recommendations', response_model=JobAcceptedResponse, status_code=202, dependencies=[Depends(require_internal_secret)])
def create_article_recommendation_job(payload: ArticleRecommendationJobRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_article_recommendation_job, payload)
    return JobAcceptedResponse(job_id=payload.job_id)


@app.post('/internal/v1/embeddings', response_model=EmbeddingResponse, dependencies=[Depends(require_internal_secret)])
def create_embeddings(payload: EmbeddingRequest):
    try:
        vectors = OpenAIAdapter().embed(payload.texts)
    except OpenAIAPIError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return EmbeddingResponse(
        model=settings.openai_embedding_model,
        dimensions=settings.openai_embedding_dimensions,
        vectors=vectors,
    )


@app.post('/internal/v1/book-analysis', response_model=BookAnalysisResponse, dependencies=[Depends(require_internal_secret)])
def create_book_analysis(payload: BookAnalysisRequest):
    try:
        return OpenAIAdapter().analyze_book(payload)
    except OpenAIAPIError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
