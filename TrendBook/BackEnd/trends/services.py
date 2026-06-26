import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone as dt_timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from ai.models import AIJob
from books.clients import AladinClient
from books.embeddings import cosine_similarity, sync_book_embeddings
from books.models import Book, BookEmbedding, BookRanking, MallType
from books.services import sync_aladin_list
from recommendations.models import NewsRecommendation, Recommendation

from .ai_client import AIServiceClient, AIServiceError
from .clients import NaverNewsClient, OpenWeatherClient, TrendProviderError
from .recommendation_utils import book_meets_recommendation_threshold
from .weather_utils import normalize_weather_condition
from .models import (
    NewsArticle,
    NewsCategory,
    TrendBatch,
    TrendTopic,
    TrendTopicNews,
    WeatherSnapshot,
)


TAG_PATTERN = re.compile(r'<[^>]+>')
NEWS_QUERIES = {
    NewsCategory.TECH_SCIENCE: ('AI', '반도체', '과학기술', '우주', '테크'),
    NewsCategory.BUSINESS: ('경제', '증시', '기업', '금융', '부동산'),
    NewsCategory.ARTS_CULTURE: ('문화', '예술', '공연', '전시', '출판'),
}

DISCOVER_SECTIONS = [
    {'category': NewsCategory.TECH_SCIENCE, 'label': '테크 & 과학', 'rank': 1},
    {'category': NewsCategory.BUSINESS, 'label': '비즈니스', 'rank': 2},
    {'category': NewsCategory.ARTS_CULTURE, 'label': '예술 & 문화', 'rank': 3},
]

ACTIVE_DISCOVER_CATEGORIES = {section['category'] for section in DISCOVER_SECTIONS}


@dataclass
class SourceSyncResult:
    news_created: int = 0
    news_updated: int = 0
    news_skipped: int = 0
    weather_saved: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self):
        return self.news_created + self.news_updated + int(self.weather_saved)


def clean_text(value):
    return html.unescape(TAG_PATTERN.sub('', value or '')).strip()


def normalize_news_item(raw, category, now=None):
    link = str(raw.get('originallink') or raw.get('link') or '').strip()
    if not link:
        return None
    try:
        published_at = parsedate_to_datetime(raw.get('pubDate', ''))
    except (TypeError, ValueError, OverflowError):
        return None
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=dt_timezone.utc)
    source = urlparse(link).netloc.removeprefix('www.') or 'Naver News'
    return {
        'cache_key': NewsArticle.make_cache_key(link),
        'title': clean_text(raw.get('title')),
        'summary': clean_text(raw.get('description')),
        'category': category,
        'source': source,
        'source_url': link,
        'published_at': published_at,
    }


def collect_news(news_client=None, display=None, now=None):
    news_client = news_client or NaverNewsClient()
    now = now or timezone.now()
    display = display or settings.DISCOVER_NEWS_SEARCH_DISPLAY
    cutoff = now - timedelta(hours=settings.DISCOVER_NEWS_LOOKBACK_HOURS)
    result = SourceSyncResult()
    seen_urls = set()

    for category, queries in NEWS_QUERIES.items():
        for query in queries:
            try:
                payload = news_client.search(query, display=max(1, min(display, 100)))
            except TrendProviderError as exc:
                result.errors.append(f'{category}/{query}: {exc}')
                continue
            for raw in payload.get('items', []):
                values = normalize_news_item(raw, category, now=now)
                if (
                    not values
                    or not values['title']
                    or values['published_at'] < cutoff
                    or values['source_url'] in seen_urls
                ):
                    result.news_skipped += 1
                    continue
                seen_urls.add(values['source_url'])
                cache_key = values.pop('cache_key')
                _, created = NewsArticle.objects.update_or_create(cache_key=cache_key, defaults=values)
                result.news_created += int(created)
                result.news_updated += int(not created)
    return result


def collect_weather(weather_client=None, city=None, lat=None, lon=None, now=None):
    weather_client = weather_client or OpenWeatherClient()
    now = now or timezone.now()
    if lat is not None and lon is not None:
        payload = weather_client.current_by_coordinates(lat, lon)
    else:
        payload = weather_client.current(city)
    weather = (payload.get('weather') or [{}])[0]
    main = payload.get('main') or {}
    wind = payload.get('wind') or {}
    location = str(payload.get('name') or city or settings.OPENWEATHER_CITY)
    observed_at = datetime.fromtimestamp(payload.get('dt'), tz=dt_timezone.utc) if payload.get('dt') else now
    snapshot, _ = WeatherSnapshot.objects.update_or_create(
        location=location,
        observed_at=observed_at.replace(second=0, microsecond=0),
        defaults={
            'condition': normalize_weather_condition(clean_text(weather.get('description'))),
            'temperature_c': main.get('temp'),
            'feels_like_c': main.get('feels_like'),
            'humidity': main.get('humidity'),
            'wind_speed': wind.get('speed'),
            'weather_code': weather.get('id'),
            'icon': str(weather.get('icon') or ''),
        },
    )
    return snapshot


def current_weather_snapshot_by_coordinates(weather_client=None, lat=None, lon=None, now=None):
    weather_client = weather_client or OpenWeatherClient()
    now = now or timezone.now()
    payload = weather_client.current_by_coordinates(lat, lon)
    weather = (payload.get('weather') or [{}])[0]
    main = payload.get('main') or {}
    wind = payload.get('wind') or {}
    location = str(payload.get('name') or '현재 위치')
    observed_at = datetime.fromtimestamp(payload.get('dt'), tz=dt_timezone.utc) if payload.get('dt') else now
    return WeatherSnapshot(
        location=location,
        observed_at=observed_at.replace(second=0, microsecond=0),
        condition=normalize_weather_condition(clean_text(weather.get('description'))),
        temperature_c=main.get('temp'),
        feels_like_c=main.get('feels_like'),
        humidity=main.get('humidity'),
        wind_speed=wind.get('speed'),
        weather_code=weather.get('id'),
        icon=str(weather.get('icon') or ''),
    )


def sync_sources(news_client=None, weather_client=None, city=None, news_display=None, now=None):
    result = collect_news(news_client, display=news_display, now=now)
    try:
        collect_weather(weather_client, city=city, now=now)
        result.weather_saved = True
    except TrendProviderError as exc:
        result.errors.append(f'WEATHER: {exc}')
    return result


def _callback_url(job):
    base = settings.PUBLIC_API_BASE_URL.rstrip('/')
    return f'{base}/api/v1/internal/ai/jobs/{job.id}/complete'


def start_trend_generation(ai_client=None, now=None):
    now = now or timezone.now()
    articles = []
    if False and len(articles) < 15:
        raise ValueError('신뢰할 수 있는 3개 주제를 만들려면 최근 24시간 뉴스가 최소 9건 필요합니다.')

    recent = NewsArticle.objects.filter(
        published_at__gte=now - timedelta(hours=settings.DISCOVER_NEWS_LOOKBACK_HOURS),
    )
    per_section_limit = max(settings.DISCOVER_NEWS_PER_SECTION, 12)
    articles = []
    shortages = []
    for section in DISCOVER_SECTIONS:
        rows = list(recent.filter(
            category=section['category'],
        ).order_by('-published_at')[:per_section_limit])
        if len(rows) < settings.DISCOVER_NEWS_PER_SECTION:
            shortages.append(f"{section['label']} {len(rows)}/{settings.DISCOVER_NEWS_PER_SECTION}")
        articles.extend(rows)
    if shortages:
        raise ValueError(
            f'최근 {settings.DISCOVER_NEWS_LOOKBACK_HOURS}시간 뉴스가 섹션별 최소 3건 필요합니다: '
            + ', '.join(shortages)
            + '. DISCOVER_NEWS_SEARCH_DISPLAY 값을 늘리거나 잠시 후 다시 시도하세요.'
        )

    batch = TrendBatch.objects.create(status=TrendBatch.Status.PENDING, source_started_at=now)
    job = AIJob.objects.create(kind=AIJob.Kind.TREND, batch=batch)
    payload = {
        'job_id': str(job.id),
        'articles': [
            {
                'id': article.id, 'title': article.title, 'summary': article.summary,
                'category': article.category, 'published_at': article.published_at.isoformat(),
            }
            for article in articles
        ],
        'callback_url': _callback_url(job),
    }
    job.request_payload = payload
    job.save(update_fields=['request_payload'])
    try:
        (ai_client or AIServiceClient()).submit('trend', payload)
    except AIServiceError as exc:
        job.status = AIJob.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at'])
        batch.status = TrendBatch.Status.FAILED
        batch.error_message = str(exc)
        batch.save(update_fields=['status', 'error_message', 'updated_at'])
        raise
    job.status = AIJob.Status.PROCESSING
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])
    batch.status = TrendBatch.Status.PROCESSING
    batch.save(update_fields=['status', 'updated_at'])
    return job


def _validate_topics(job, topics):
    if len(topics) != len(DISCOVER_SECTIONS):
        raise ValueError('트렌드 주제는 정확히 3개여야 합니다.')
    allowed_ids = {item['id'] for item in job.request_payload.get('articles', [])}
    article_categories = {
        item['id']: item.get('category')
        for item in job.request_payload.get('articles', [])
    }
    ranks = {item.get('rank') for item in topics}
    expected_ranks = {section['rank'] for section in DISCOVER_SECTIONS}
    if ranks != expected_ranks:
        raise ValueError('트렌드 순위는 1~3을 한 번씩 사용해야 합니다.')
    expected_categories = {section['category'] for section in DISCOVER_SECTIONS}
    if {item.get('category') for item in topics} != expected_categories:
        raise ValueError('Discover topics must cover all configured sections exactly once.')
    for item in topics:
        if not str(item.get('title') or '').strip() or not str(item.get('summary') or '').strip():
            raise ValueError('주제 제목과 요약은 비어 있을 수 없습니다.')
        article_ids = item.get('article_ids') or []
        if len(article_ids) != settings.DISCOVER_NEWS_PER_SECTION or len(article_ids) != len(set(article_ids)):
            raise ValueError('주제별 서로 다른 기사 3~5개가 필요합니다.')
        if not set(article_ids) <= allowed_ids:
            raise ValueError('입력에 없던 기사 ID가 포함되었습니다.')
        if item.get('category') not in NewsCategory.values:
            raise ValueError('지원하지 않는 트렌드 분야입니다.')


        if any(article_categories.get(article_id) != item.get('category') for article_id in article_ids):
            raise ValueError('Topic articles must belong to the same Discover section.')


@transaction.atomic
def complete_trend_job(job, topics):
    if job.kind != AIJob.Kind.TREND or not job.batch_id:
        raise ValueError('트렌드 생성 작업이 아닙니다.')
    _validate_topics(job, topics)
    article_ids = {article_id for item in topics for article_id in item['article_ids']}
    articles = {article.id: article for article in NewsArticle.objects.filter(id__in=article_ids)}
    if set(articles) != article_ids:
        raise ValueError('삭제되었거나 존재하지 않는 기사가 포함되었습니다.')

    job.batch.topics.all().delete()
    for item in sorted(topics, key=lambda value: value['rank']):
        topic = TrendTopic.objects.create(
            batch=job.batch,
            title=str(item['title']).strip(),
            summary=str(item['summary']).strip(),
            category=item['category'],
            keywords=[str(value).strip() for value in item.get('keywords', []) if str(value).strip()][:8],
            rank=item['rank'],
        )
        TrendTopicNews.objects.bulk_create([
            TrendTopicNews(topic=topic, article=articles[article_id], rank=index, is_primary=index == 1)
            for index, article_id in enumerate(item['article_ids'], start=1)
        ])
    now = timezone.now()
    job.status = AIJob.Status.COMPLETED
    job.finished_at = now
    job.error_message = ''
    job.save(update_fields=['status', 'finished_at', 'error_message'])
    job.batch.status = TrendBatch.Status.COMPLETED
    job.batch.published_at = now
    job.batch.error_message = ''
    job.batch.save(update_fields=['status', 'published_at', 'error_message', 'updated_at'])


def _retrieval_query(topic):
    article_context = '\n'.join(
        f'- {link.article.title}: {link.article.summary}'
        for link in topic.article_links.select_related('article').all()
    )
    return (
        f'트렌드: {topic.title}\n요약: {topic.summary}\n'
        f'키워드: {", ".join(topic.keywords)}\n관련 뉴스:\n{article_context}'
    )[:8000]


def select_book_candidates(topic, limit=20, ai_client=None):
    ai_client = ai_client or AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS)
    response = ai_client.embed([_retrieval_query(topic)])
    vectors = response.get('vectors') or []
    query_vector = vectors[0] if len(vectors) == 1 else None
    model = str(response.get('model') or '')
    dimensions = int(response.get('dimensions') or 0)
    if not query_vector or len(query_vector) != dimensions or not model:
        raise ValueError('트렌드 질의 임베딩 응답이 올바르지 않습니다.')

    embeddings = list(BookEmbedding.objects.filter(
        book__adult=False, model=model, dimensions=dimensions,
    ).select_related('book').prefetch_related(
        'book__category_links__category',
        Prefetch('book__rankings', queryset=BookRanking.objects.order_by('-period_start', 'rank')),
    ))
    if len(embeddings) < 5:
        raise ValueError('도서 임베딩이 부족합니다. python manage.py sync_book_embeddings를 먼저 실행하세요.')

    ranked = []
    for embedding in embeddings:
        similarity = cosine_similarity(query_vector, embedding.vector)
        book = embedding.book
        sales_score = min((book.sales_point or 0) / 100000, 1)
        rank_values = [ranking.rank for ranking in book.rankings.all()]
        rank_score = 1 / min(rank_values) if rank_values else 0
        book._retrieval_score = similarity
        book._embedding_model = model
        book._hybrid_score = similarity * 0.9 + sales_score * 0.07 + rank_score * 0.03
        ranked.append(book)
    ranked.sort(key=lambda book: book._hybrid_score, reverse=True)
    unique = []
    seen_isbns = set()
    for book in ranked:
        if book.isbn in seen_isbns:
            continue
        if not book_meets_recommendation_threshold(book):
            continue
        seen_isbns.add(book.isbn)
        unique.append(book)
        if len(unique) == limit:
            break
    return unique


def start_recommendation_generation(topic, ai_client=None):
    cached = list(topic.recommendations.select_related('book').all())
    if len(cached) == 5:
        return None, cached
    active = topic.ai_jobs.filter(
        kind=AIJob.Kind.RECOMMENDATION,
        status__in=[AIJob.Status.PENDING, AIJob.Status.PROCESSING],
    ).first()
    if active:
        return active, None
    ai_client = ai_client or AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS)
    candidates = select_book_candidates(topic, ai_client=ai_client)
    if len(candidates) < 5:
        raise ValueError('추천 생성을 위한 도서 후보가 최소 5권 필요합니다.')

    job = AIJob.objects.create(kind=AIJob.Kind.RECOMMENDATION, topic=topic)
    weather = WeatherSnapshot.objects.first()
    payload = {
        'job_id': str(job.id),
        'trend': {
            'id': topic.id, 'title': topic.title, 'summary': topic.summary,
            'category': topic.category,
            'news': [
                {'id': link.article_id, 'title': link.article.title, 'summary': link.article.summary}
                for link in topic.article_links.select_related('article').all()
            ],
        },
        'weather': ({
            'location': weather.location,
            'condition': weather.condition or '정보 없음',
            'temperature_c': weather.temperature_c,
        } if weather and weather.temperature_c is not None else None),
        'candidates': [
            {
                'isbn': book.isbn, 'title': book.title, 'author': book.author,
                'book_id': book.id,
                'description': book.description,
                'categories': [link.category.path for link in book.category_links.all()],
                'sales_point': book.sales_point,
                'rank': min([ranking.rank for ranking in book.rankings.all()], default=None),
                'retrieval_score': round(book._retrieval_score, 6),
                'embedding_model': book._embedding_model,
            }
            for book in candidates
        ],
        'callback_url': _callback_url(job),
    }
    job.request_payload = payload
    job.save(update_fields=['request_payload'])
    try:
        ai_client.submit('recommendation', payload)
    except AIServiceError as exc:
        job.status = AIJob.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at'])
        raise
    job.status = AIJob.Status.PROCESSING
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])
    return job, None


@transaction.atomic
def complete_recommendation_job(job, recommendations):
    if job.kind != AIJob.Kind.RECOMMENDATION or not job.topic_id:
        raise ValueError('추천 생성 작업이 아닙니다.')
    if len(recommendations) != 5:
        raise ValueError('추천 결과는 정확히 5권이어야 합니다.')
    allowed = {item['isbn'] for item in job.request_payload.get('candidates', [])}
    isbns = [item.get('isbn') for item in recommendations]
    if len(set(isbns)) != 5 or not set(isbns) <= allowed:
        raise ValueError('후보 외 ISBN 또는 중복 ISBN이 포함되었습니다.')
    candidate_ids = {
        item['isbn']: item.get('book_id')
        for item in job.request_payload.get('candidates', [])
        if item.get('isbn') in isbns
    }
    books_by_id = {
        book.id: book for book in Book.objects.filter(id__in=[value for value in candidate_ids.values() if value])
    }
    books = {
        isbn: books_by_id[book_id]
        for isbn, book_id in candidate_ids.items()
        if book_id in books_by_id
    }
    candidate_metadata = {
        item['isbn']: item
        for item in job.request_payload.get('candidates', [])
        if item.get('isbn') in isbns
    }
    if set(books) != set(isbns):
        raise ValueError('존재하지 않는 도서가 포함되었습니다.')
    for isbn in isbns:
        if not book_meets_recommendation_threshold(books[isbn]):
            raise ValueError('판매지수가 기준 미만인 도서가 포함되었습니다.')
    for item in recommendations:
        score = float(item.get('relevance_score', -1))
        reason = str(item.get('reason') or '').strip()
        if not 0 <= score <= 1 or not reason:
            raise ValueError('추천 사유와 0~1 관련도가 필요합니다.')

    job.topic.recommendations.all().delete()
    Recommendation.objects.bulk_create([
        Recommendation(
            topic=job.topic, book=books[item['isbn']], reason=str(item['reason']).strip(),
            relevance_score=item['relevance_score'],
            retrieval_score=candidate_metadata[item['isbn']].get('retrieval_score', 0),
            embedding_model=candidate_metadata[item['isbn']].get('embedding_model', ''),
        )
        for item in recommendations
    ])
    job.status = AIJob.Status.COMPLETED
    job.finished_at = timezone.now()
    job.error_message = ''
    job.save(update_fields=['status', 'finished_at', 'error_message'])


def _rank_books_for_query(query, limit=10, ai_client=None):
    ai_client = ai_client or AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS)
    response = ai_client.embed([query[:8000]])
    vectors = response.get('vectors') or []
    query_vector = vectors[0] if len(vectors) == 1 else None
    model = str(response.get('model') or '')
    dimensions = int(response.get('dimensions') or 0)
    return _rank_books_from_vector(query_vector, model, dimensions, limit=limit)


def _rank_books_from_vector(query_vector, model, dimensions, limit=10, embeddings=None):
    if not query_vector or len(query_vector) != dimensions or not model:
        raise ValueError('Invalid embedding response for article recommendation query.')

    if embeddings is None:
        embeddings = list(BookEmbedding.objects.filter(
            book__adult=False, model=model, dimensions=dimensions,
        ).select_related('book').prefetch_related(
            'book__category_links__category',
            Prefetch('book__rankings', queryset=BookRanking.objects.order_by('-period_start', 'rank')),
        ))
    if len(embeddings) < settings.DISCOVER_BOOK_RECS_PER_NEWS:
        raise ValueError('Book embeddings are not ready. Run sync_book_embeddings first.')

    ranked = []
    for embedding in embeddings:
        similarity = cosine_similarity(query_vector, embedding.vector)
        book = embedding.book
        sales_score = min((book.sales_point or 0) / 100000, 1)
        rank_values = [ranking.rank for ranking in book.rankings.all()]
        rank_score = 1 / min(rank_values) if rank_values else 0
        book._retrieval_score = similarity
        book._embedding_model = model
        book._hybrid_score = similarity * 0.9 + sales_score * 0.07 + rank_score * 0.03
        ranked.append(book)
    ranked.sort(key=lambda book: book._hybrid_score, reverse=True)

    unique = []
    seen_isbns = set()
    for book in ranked:
        if book.isbn in seen_isbns:
            continue
        if not book_meets_recommendation_threshold(book):
            continue
        seen_isbns.add(book.isbn)
        unique.append(book)
        if len(unique) == limit:
            break
    return unique


def _rank_books_for_queries(queries, limit=10, ai_client=None):
    ai_client = ai_client or AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS)
    response = ai_client.embed([query[:8000] for query in queries])
    vectors = response.get('vectors') or []
    model = str(response.get('model') or '')
    dimensions = int(response.get('dimensions') or 0)
    if len(vectors) != len(queries) or dimensions <= 0 or not model:
        raise ValueError('Invalid embedding response for article recommendation queries.')

    embeddings = list(BookEmbedding.objects.filter(
        book__adult=False, model=model, dimensions=dimensions,
    ).select_related('book').prefetch_related(
        'book__category_links__category',
        Prefetch('book__rankings', queryset=BookRanking.objects.order_by('-period_start', 'rank')),
    ))
    if len(embeddings) < settings.DISCOVER_BOOK_RECS_PER_NEWS:
        raise ValueError('Book embeddings are not ready. Run sync_book_embeddings first.')

    return [
        _rank_books_from_vector(vector, model, dimensions, limit=limit, embeddings=embeddings)
        for vector in vectors
    ]


def _article_retrieval_query(topic_news):
    topic = topic_news.topic
    article = topic_news.article
    return (
        f'Discover section: {topic.category}\n'
        f'Topic: {topic.title}\n'
        f'Topic summary: {topic.summary}\n'
        f'Keywords: {", ".join(topic.keywords)}\n'
        f'News title: {article.title}\n'
        f'News summary: {article.summary}'
    )


def start_article_recommendation_generation(batch, ai_client=None):
    links = list(TrendTopicNews.objects.filter(topic__batch=batch).select_related(
        'topic', 'article',
    ).prefetch_related(
        'book_recommendations',
    ).order_by('topic__rank', 'rank'))
    if not links:
        raise ValueError('No Discover news is available for article recommendations.')
    expected = settings.DISCOVER_BOOK_RECS_PER_NEWS
    if all(link.book_recommendations.count() == expected for link in links):
        return None, True

    active = AIJob.objects.filter(
        kind=AIJob.Kind.ARTICLE_RECOMMENDATION,
        batch=batch,
        status__in=[AIJob.Status.PENDING, AIJob.Status.PROCESSING],
    ).first()
    if active:
        return active, False

    ai_client = ai_client or AIServiceClient(timeout=settings.AI_SERVICE_TIMEOUT_SECONDS)
    article_payloads = []
    ranked_candidates = _rank_books_for_queries(
        [_article_retrieval_query(link) for link in links],
        limit=10,
        ai_client=ai_client,
    )
    for link, candidates in zip(links, ranked_candidates):
        if len(candidates) < expected:
            raise ValueError('Not enough book candidates for article recommendations.')
        article_payloads.append({
            'topic_news_id': link.id,
            'article': {
                'id': link.article_id,
                'title': link.article.title,
                'summary': link.article.summary,
                'source': link.article.source,
            },
            'topic': {
                'id': link.topic_id,
                'title': link.topic.title,
                'summary': link.topic.summary,
                'category': link.topic.category,
                'keywords': link.topic.keywords,
            },
            'candidates': [
                {
                    'isbn': book.isbn,
                    'book_id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'description': book.description,
                    'categories': [item.category.path for item in book.category_links.all()],
                    'sales_point': book.sales_point,
                    'rank': min([ranking.rank for ranking in book.rankings.all()], default=None),
                    'retrieval_score': round(book._retrieval_score, 6),
                    'embedding_model': book._embedding_model,
                }
                for book in candidates
            ],
        })

    job = AIJob.objects.create(kind=AIJob.Kind.ARTICLE_RECOMMENDATION, batch=batch)
    payload = {
        'job_id': str(job.id),
        'articles': article_payloads,
        'recommendations_per_article': expected,
        'callback_url': _callback_url(job),
    }
    job.request_payload = payload
    job.save(update_fields=['request_payload'])
    try:
        ai_client.submit('article_recommendation', payload)
    except AIServiceError as exc:
        job.status = AIJob.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at'])
        raise
    job.status = AIJob.Status.PROCESSING
    job.started_at = timezone.now()
    job.save(update_fields=['status', 'started_at'])
    return job, False


@transaction.atomic
def complete_article_recommendation_job(job, article_recommendations):
    if job.kind != AIJob.Kind.ARTICLE_RECOMMENDATION or not job.batch_id:
        raise ValueError('This is not an article recommendation job.')
    expected_count = int(job.request_payload.get('recommendations_per_article') or settings.DISCOVER_BOOK_RECS_PER_NEWS)
    request_articles = {
        item['topic_news_id']: item
        for item in job.request_payload.get('articles', [])
    }
    if set(request_articles) != {item.get('topic_news_id') for item in article_recommendations}:
        raise ValueError('Article recommendation response must cover all requested news.')

    topic_news_by_id = {
        item.id: item
        for item in TrendTopicNews.objects.filter(id__in=request_articles.keys()).select_related('topic', 'article')
    }
    if set(topic_news_by_id) != set(request_articles):
        raise ValueError('Article recommendation response references missing news.')

    all_book_ids = set()
    candidate_by_link = {}
    for link_id, item in request_articles.items():
        candidates = {
            candidate['isbn']: candidate
            for candidate in item.get('candidates', [])
        }
        candidate_by_link[link_id] = candidates
        all_book_ids.update(
            candidate.get('book_id')
            for candidate in candidates.values()
            if candidate.get('book_id')
        )
    books_by_id = {book.id: book for book in Book.objects.filter(id__in=all_book_ids)}

    for item in article_recommendations:
        link_id = item.get('topic_news_id')
        rows = item.get('recommendations') or []
        isbns = [row.get('isbn') for row in rows]
        if len(rows) != expected_count or len(set(isbns)) != expected_count:
            raise ValueError('Each news item must have exactly three different book recommendations.')
        if not set(isbns) <= set(candidate_by_link[link_id]):
            raise ValueError('Article recommendation used a book outside the candidate set.')
        for row in rows:
            score = float(row.get('relevance_score', -1))
            if not 0 <= score <= 1 or not str(row.get('reason') or '').strip():
                raise ValueError('Article recommendation score and reason are required.')

    NewsRecommendation.objects.filter(topic_news_id__in=request_articles.keys()).delete()
    rows_to_create = []
    for item in article_recommendations:
        link_id = item['topic_news_id']
        for row in item['recommendations']:
            candidate = candidate_by_link[link_id][row['isbn']]
            book = books_by_id.get(candidate.get('book_id'))
            if not book:
                raise ValueError('Article recommendation references a missing book.')
            rows_to_create.append(NewsRecommendation(
                topic_news=topic_news_by_id[link_id],
                book=book,
                reason=str(row['reason']).strip(),
                relevance_score=row['relevance_score'],
                retrieval_score=candidate.get('retrieval_score', 0),
                embedding_model=candidate.get('embedding_model', ''),
            ))
    NewsRecommendation.objects.bulk_create(rows_to_create)
    job.status = AIJob.Status.COMPLETED
    job.finished_at = timezone.now()
    job.error_message = ''
    job.save(update_fields=['status', 'finished_at', 'error_message'])


def refresh_discover_cache(city=None, news_display=None):
    from books.models import Book

    book_results = {}
    touched_book_ids = set()
    client = AladinClient()
    for query_type in settings.ALADIN_REFRESH_LISTS:
        result = sync_aladin_list(
            client,
            query_type=query_type,
            mall_type=MallType.BOOK,
            max_results=50,
        )
        book_results[query_type] = {
            'created': result.created,
            'updated': result.updated,
            'skipped': result.skipped,
            'rankings': result.rankings,
        }
        touched_book_ids.update(result.book_ids)

    books = list(Book.objects.filter(id__in=touched_book_ids, adult=False).prefetch_related(
        'category_links__category', 'embedding',
    ).order_by('id'))
    embedding_result = sync_book_embeddings(
        books,
        ai_client=AIServiceClient(timeout=90),
        batch_size=100,
        max_workers=settings.BOOK_EMBEDDING_MAX_WORKERS,
    ) if books else None
    source_result = sync_sources(
        city=city,
        news_display=news_display or settings.DISCOVER_NEWS_SEARCH_DISPLAY,
    )
    trend_job = start_trend_generation()
    return {
        'books': book_results,
        'embeddings': None if embedding_result is None else {
            'created': embedding_result.created,
            'updated': embedding_result.updated,
            'skipped': embedding_result.skipped,
        },
        'sources': {
            'news_created': source_result.news_created,
            'news_updated': source_result.news_updated,
            'news_skipped': source_result.news_skipped,
            'weather_saved': source_result.weather_saved,
            'errors': source_result.errors,
        },
        'trend_job_id': str(trend_job.id),
    }
