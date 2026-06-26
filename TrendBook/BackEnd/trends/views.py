import hmac
import threading
import time
from datetime import timedelta

from django.conf import settings
from django.db import close_old_connections
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.models import AIJob
from recommendations.models import NewsRecommendation, Recommendation
from recommendations.serializers import RecommendationSerializer

from .ai_client import AIServiceError
from .clients import TrendProviderError
from .models import SyncRun, TrendBatch, TrendTopic, TrendTopicNews, WeatherSnapshot
from .serializers import (
    TrendTopicDetailSerializer,
    TrendTopicListSerializer,
    WeatherSnapshotSerializer,
)
from .services import (
    ACTIVE_DISCOVER_CATEGORIES,
    complete_article_recommendation_job,
    complete_recommendation_job,
    complete_trend_job,
    current_weather_snapshot_by_coordinates,
    start_article_recommendation_generation,
    start_recommendation_generation,
    start_trend_generation,
    refresh_discover_cache,
    sync_sources,
)


DISCOVER_REFRESH_LOCK_KEY = 'discover_refresh'
REFRESH_RUNNING_TIMEOUT = timedelta(hours=2)
REFRESH_POLL_INTERVAL_SECONDS = 2
REFRESH_MAX_WAIT_SECONDS = 600


def _latest_public_batch():
    return TrendBatch.objects.filter(
        status=TrendBatch.Status.COMPLETED,
        is_legacy=False,
    ).order_by('-published_at').first()


def _topic_queryset():
    return TrendTopic.objects.select_related('batch').prefetch_related(
        Prefetch('article_links', queryset=TrendTopicNews.objects.select_related('article').order_by('rank')),
        Prefetch(
            'article_links__book_recommendations',
            queryset=NewsRecommendation.objects.select_related('book').order_by('-relevance_score'),
        ),
        Prefetch('recommendations', queryset=Recommendation.objects.select_related('book').order_by('-relevance_score')),
        'ai_jobs',
    )


def _refresh_message(phase):
    return {
        'queued': '트렌드 갱신을 준비 중입니다.',
        'collecting': '도서, 임베딩, 뉴스와 날씨를 수집 중입니다.',
        'generating': 'AI가 새 트렌드 주제를 생성 중입니다.',
        'publishing': '새 트렌드 캐시를 발행 중입니다.',
        'completed': '트렌드 갱신이 완료되었습니다.',
        'failed': '트렌드 갱신에 실패했습니다.',
    }.get(phase, '트렌드 갱신 상태를 확인 중입니다.')


def _merge_refresh_metadata(run, **updates):
    metadata = {**(run.metadata or {}), **updates}
    SyncRun.objects.filter(pk=run.pk).update(metadata=metadata)
    return metadata


def _complete_refresh_run(run, *, status_value, phase, error_message=''):
    now = timezone.now()
    metadata = _merge_refresh_metadata(run, phase=phase, message=_refresh_message(phase))
    SyncRun.objects.filter(pk=run.pk).update(
        status=status_value,
        finished_at=now,
        next_run_after=now + timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS),
        error_message=error_message[:2000],
        metadata=metadata,
    )


def _finalize_refresh_run_from_job(run):
    if not run or run.status != SyncRun.Status.RUNNING:
        return run
    trend_job_id = (run.metadata or {}).get('trend_job_id')
    if not trend_job_id:
        return run
    job = AIJob.objects.filter(id=trend_job_id, kind=AIJob.Kind.TREND).first()
    if not job:
        return run
    if job.status == AIJob.Status.COMPLETED:
        _complete_refresh_run(run, status_value=SyncRun.Status.COMPLETED, phase='completed')
        run.refresh_from_db()
    elif job.status == AIJob.Status.FAILED:
        _complete_refresh_run(
            run,
            status_value=SyncRun.Status.FAILED,
            phase='failed',
            error_message=job.error_message or 'AI 트렌드 생성에 실패했습니다.',
        )
        run.refresh_from_db()
    return run


def _refresh_status_payload(run):
    if not run:
        return {
            'status': 'idle',
            'phase': 'queued',
            'message': '트렌드 갱신 대기 중입니다.',
            'trend_job_id': None,
            'error': None,
            'started_at': None,
            'finished_at': None,
        }

    run = _finalize_refresh_run_from_job(run)
    metadata = run.metadata or {}
    trend_job_id = metadata.get('trend_job_id')
    phase = metadata.get('phase') or 'queued'
    status_value = 'idle'
    error = None

    if run.status == SyncRun.Status.RUNNING:
        if trend_job_id:
            status_value = 'processing'
            phase = 'generating'
        else:
            status_value = 'running'
            phase = phase if phase in {'queued', 'collecting'} else 'collecting'
    elif run.status == SyncRun.Status.COMPLETED:
        status_value = 'completed'
        phase = 'completed'
    elif run.status == SyncRun.Status.FAILED:
        status_value = 'failed'
        phase = 'failed'
        error = run.error_message or metadata.get('error') or '트렌드 갱신에 실패했습니다.'

    return {
        'status': status_value,
        'phase': phase,
        'message': metadata.get('message') or _refresh_message(phase),
        'trend_job_id': trend_job_id,
        'error': error,
        'started_at': run.started_at,
        'finished_at': run.finished_at,
    }


def _wait_for_trend_job(run_id, trend_job_id):
    deadline = time.monotonic() + REFRESH_MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        close_old_connections()
        run = SyncRun.objects.filter(pk=run_id).first()
        job = AIJob.objects.filter(id=trend_job_id, kind=AIJob.Kind.TREND).first()
        if not run or not job:
            return
        if job.status == AIJob.Status.COMPLETED:
            _complete_refresh_run(run, status_value=SyncRun.Status.COMPLETED, phase='completed')
            return
        if job.status == AIJob.Status.FAILED:
            _complete_refresh_run(
                run,
                status_value=SyncRun.Status.FAILED,
                phase='failed',
                error_message=job.error_message or 'AI 트렌드 생성에 실패했습니다.',
            )
            return
        time.sleep(REFRESH_POLL_INTERVAL_SECONDS)

    run = SyncRun.objects.filter(pk=run_id).first()
    if run:
        _complete_refresh_run(
            run,
            status_value=SyncRun.Status.FAILED,
            phase='failed',
            error_message='AI 트렌드 생성 대기 시간이 초과되었습니다.',
        )


def _run_discover_refresh_background(run_id, *, city=None, news_display=None):
    close_old_connections()
    try:
        run = SyncRun.objects.get(pk=run_id)
        metadata = _merge_refresh_metadata(
            run,
            phase='collecting',
            message=_refresh_message('collecting'),
        )
        SyncRun.objects.filter(pk=run.pk).update(metadata=metadata)

        result = refresh_discover_cache(city=city, news_display=news_display)
        trend_job_id = result.get('trend_job_id')
        metadata = {
            **result,
            'trend_job_id': trend_job_id,
            'phase': 'generating',
            'message': _refresh_message('generating'),
        }
        SyncRun.objects.filter(pk=run.pk).update(error_message='', metadata=metadata)
        if trend_job_id:
            _wait_for_trend_job(run.pk, trend_job_id)
        else:
            _complete_refresh_run(
                run,
                status_value=SyncRun.Status.FAILED,
                phase='failed',
                error_message='트렌드 AI 작업 ID가 생성되지 않았습니다.',
            )
    except Exception as exc:
        SyncRun.objects.filter(pk=run_id).update(
            status=SyncRun.Status.FAILED,
            finished_at=timezone.now(),
            next_run_after=timezone.now() + timedelta(seconds=settings.TREND_REFRESH_INTERVAL_SECONDS),
            error_message=str(exc)[:2000],
            metadata={'phase': 'failed', 'message': _refresh_message('failed'), 'error': str(exc)[:2000]},
        )
    finally:
        close_old_connections()


def _launch_refresh_thread(run_id, *, city=None, news_display=None):
    thread = threading.Thread(
        target=_run_discover_refresh_background,
        kwargs={'run_id': run_id, 'city': city, 'news_display': news_display},
        name='trendbook-manual-discover-refresh',
        daemon=True,
    )
    thread.start()


def _latest_refresh_run():
    return SyncRun.objects.filter(lock_key=DISCOVER_REFRESH_LOCK_KEY).first()


class TrendListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        batch = _latest_public_batch()
        if not batch:
            return Response(
                {'code': 'TREND_CACHE_EMPTY', 'detail': '사용 가능한 트렌드 캐시가 없습니다.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        topics = _topic_queryset().filter(
            batch=batch,
            category__in=ACTIVE_DISCOVER_CATEGORIES,
        ).annotate(news_count=Count('article_links'))
        weather = WeatherSnapshot.objects.first()
        is_stale = not batch.published_at or batch.published_at < timezone.now() - timedelta(hours=3)
        article_job = batch.ai_jobs.filter(
            kind=AIJob.Kind.ARTICLE_RECOMMENDATION,
        ).order_by('-created_at').first()
        return Response({
            'batch_id': batch.id,
            'published_at': batch.published_at,
            'is_stale': is_stale,
            'weather': WeatherSnapshotSerializer(weather).data if weather else None,
            'article_recommendation': {
                'status': article_job.status if article_job else 'not_started',
                'job_id': str(article_job.id) if article_job else None,
                'error': (
                    article_job.error_message
                    if article_job and article_job.status == AIJob.Status.FAILED
                    else None
                ),
            },
            'results': TrendTopicListSerializer(topics, many=True).data,
        })


class CurrentWeatherView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response(
                {'code': 'INVALID_COORDINATES', 'detail': 'lat/lon 좌표가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            return Response(
                {'code': 'INVALID_COORDINATES', 'detail': 'lat/lon 좌표 범위가 올바르지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            snapshot = current_weather_snapshot_by_coordinates(lat=lat, lon=lon)
        except TrendProviderError as exc:
            return Response(
                {'code': 'WEATHER_UNAVAILABLE', 'detail': str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(WeatherSnapshotSerializer(snapshot).data)


class TrendDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, topic_id):
        topic = get_object_or_404(
            _topic_queryset(), id=topic_id,
            batch__status=TrendBatch.Status.COMPLETED, batch__is_legacy=False,
            category__in=ACTIVE_DISCOVER_CATEGORIES,
        )
        return Response(TrendTopicDetailSerializer(topic).data)


class TrendSyncView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            display = int(request.data.get('news_display') or settings.DISCOVER_NEWS_SEARCH_DISPLAY)
        except (TypeError, ValueError):
            return Response({'code': 'INVALID_NEWS_DISPLAY', 'detail': 'news_display는 정수여야 합니다.'}, status=400)
        if not 1 <= display <= 100:
            return Response({'code': 'INVALID_NEWS_DISPLAY', 'detail': 'news_display는 1~10이어야 합니다.'}, status=400)
        try:
            result = refresh_discover_cache(city=request.data.get('city'), news_display=display)
        except (ValueError, AIServiceError) as exc:
            return Response({
                'code': 'TREND_JOB_UNAVAILABLE', 'detail': str(exc),
                'source_errors': [],
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        source_result = result['sources']
        return Response({
            'job_id': result['trend_job_id'], 'status': AIJob.Status.PROCESSING,
            'news_created': source_result['news_created'],
            'news_updated': source_result['news_updated'],
            'source_errors': source_result['errors'],
        }, status=status.HTTP_202_ACCEPTED)


class TrendRefreshView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            display = int(request.data.get('news_display') or settings.DISCOVER_NEWS_SEARCH_DISPLAY)
        except (TypeError, ValueError):
            return Response({'code': 'INVALID_NEWS_DISPLAY', 'detail': 'news_display는 정수여야 합니다.'}, status=400)
        if not 1 <= display <= 100:
            return Response({'code': 'INVALID_NEWS_DISPLAY', 'detail': 'news_display는 1~100이어야 합니다.'}, status=400)

        now = timezone.now()
        stale_cutoff = now - REFRESH_RUNNING_TIMEOUT
        run, _ = SyncRun.objects.get_or_create(lock_key=DISCOVER_REFRESH_LOCK_KEY)
        run = _finalize_refresh_run_from_job(run)
        claimed = SyncRun.objects.filter(pk=run.pk).exclude(
            status=SyncRun.Status.RUNNING,
            started_at__gte=stale_cutoff,
        ).update(
            status=SyncRun.Status.RUNNING,
            started_at=now,
            finished_at=None,
            error_message='',
            metadata={
                'phase': 'queued',
                'message': _refresh_message('queued'),
                'requested_by': request.user.id,
            },
        )
        if claimed:
            run.refresh_from_db()
            _launch_refresh_thread(run.pk, city=request.data.get('city'), news_display=display)
        else:
            run.refresh_from_db()
        return Response(_refresh_status_payload(run), status=status.HTTP_202_ACCEPTED)


class TrendRefreshStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(_refresh_status_payload(_latest_refresh_run()))


class ArticleRecommendationGenerateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        batch = _latest_public_batch()
        if not batch:
            return Response(
                {'code': 'TREND_CACHE_EMPTY', 'detail': '사용 가능한 트렌드 캐시가 없습니다.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            job, already_complete = start_article_recommendation_generation(batch)
        except (ValueError, AIServiceError) as exc:
            return Response({'code': 'ARTICLE_RECOMMENDATION_UNAVAILABLE', 'detail': str(exc)}, status=503)
        if already_complete:
            return Response({'status': 'completed'})
        return Response({'job_id': str(job.id), 'status': job.status}, status=202)


class RecommendationGenerateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, topic_id):
        topic = get_object_or_404(
            _topic_queryset(), id=topic_id,
            batch__status=TrendBatch.Status.COMPLETED, batch__is_legacy=False,
        )
        try:
            job, cached = start_recommendation_generation(topic)
        except (ValueError, AIServiceError) as exc:
            return Response({'code': 'RECOMMENDATION_UNAVAILABLE', 'detail': str(exc)}, status=503)
        if cached is not None:
            return Response({'status': 'completed', 'results': RecommendationSerializer(cached, many=True).data})
        return Response({'job_id': str(job.id), 'status': job.status}, status=202)


class AIJobStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, job_id):
        job = get_object_or_404(AIJob, id=job_id)
        data = {
            'job_id': str(job.id), 'kind': job.kind, 'status': job.status,
            'error': job.error_message or None,
            'created_at': job.created_at, 'finished_at': job.finished_at,
        }
        if job.status == AIJob.Status.COMPLETED and job.topic_id:
            data['results'] = RecommendationSerializer(
                job.topic.recommendations.select_related('book').all(), many=True,
            ).data
        return Response(data)


class AIJobCallbackView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        provided = request.headers.get('X-Internal-Secret', '')
        if not hmac.compare_digest(provided, settings.INTERNAL_AI_SECRET):
            return Response({'detail': 'Invalid internal service credential.'}, status=401)
        job = get_object_or_404(AIJob.objects.select_related('batch', 'topic'), id=job_id)
        if job.status == AIJob.Status.COMPLETED:
            return Response({'job_id': str(job.id), 'status': job.status})
        try:
            if request.data.get('status') == 'failed':
                now = timezone.now()
                job.status = AIJob.Status.FAILED
                job.error_message = str(request.data.get('error') or 'AI 작업이 실패했습니다.')[:1000]
                job.finished_at = now
                job.save(update_fields=['status', 'error_message', 'finished_at'])
                if job.kind == AIJob.Kind.TREND and job.batch_id:
                    job.batch.status = TrendBatch.Status.FAILED
                    job.batch.error_message = job.error_message
                    job.batch.save(update_fields=['status', 'error_message', 'updated_at'])
                return Response({'job_id': str(job.id), 'status': job.status})
            if job.kind == AIJob.Kind.TREND:
                complete_trend_job(job, request.data.get('topics') or [])
            elif job.kind == AIJob.Kind.ARTICLE_RECOMMENDATION:
                complete_article_recommendation_job(job, request.data.get('article_recommendations') or [])
            else:
                complete_recommendation_job(job, request.data.get('recommendations') or [])
        except (KeyError, TypeError, ValueError) as exc:
            now = timezone.now()
            job.status = AIJob.Status.FAILED
            job.error_message = str(exc)
            job.finished_at = now
            job.save(update_fields=['status', 'error_message', 'finished_at'])
            if job.kind == AIJob.Kind.TREND and job.batch_id:
                job.batch.status = TrendBatch.Status.FAILED
                job.batch.error_message = str(exc)
                job.batch.save(update_fields=['status', 'error_message', 'updated_at'])
            return Response({'code': 'INVALID_AI_RESULT', 'detail': str(exc)}, status=400)
        return Response({'job_id': str(job.id), 'status': AIJob.Status.COMPLETED})
