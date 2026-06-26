import hashlib

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import localdate


class NewsCategory(models.TextChoices):
    TECH_SCIENCE = 'TECH_SCIENCE', 'Tech & Science'
    BUSINESS = 'BUSINESS', 'Business'
    ARTS_CULTURE = 'ARTS_CULTURE', 'Arts & Culture'
    SPORTS = 'SPORTS', 'Sports'
    ENTERTAINMENT = 'ENTERTAINMENT', 'Entertainment'


class TrendIssue(models.Model):
    """이전 Day 2 데이터 보존용 모델. 신규 조회에는 사용하지 않는다."""

    class Category(models.TextChoices):
        POLITICS = 'POLITICS', '정치'
        ECONOMY = 'ECONOMY', '경제'
        TECH = 'TECH', '기술'
        CULTURE = 'CULTURE', '문화'
        WEATHER = 'WEATHER', '날씨'

    title = models.CharField('이슈 제목', max_length=255)
    summary = models.TextField('요약 내용')
    category = models.CharField('카테고리', max_length=20, choices=Category.choices)
    source = models.CharField('수집 출처', max_length=100, blank=True, null=True)
    source_url = models.URLField('원문 URL', max_length=1000, blank=True, default='')
    cache_key = models.CharField(
        '외부 데이터 식별자', max_length=255, unique=True, blank=True, null=True,
    )
    published_at = models.DateTimeField('원문 발행 시각', blank=True, null=True)
    synced_on = models.DateField('동기화 기준일', default=localdate, db_index=True)
    metadata = models.JSONField('부가 정보', blank=True, default=dict)
    created_at = models.DateTimeField('수집 일시', auto_now_add=True)

    class Meta:
        db_table = 'trend_issue'
        verbose_name = '레거시 트렌드 이슈'
        verbose_name_plural = '레거시 트렌드 이슈 목록'
        indexes = [
            models.Index(fields=['category'], name='idx_trend_category'),
            models.Index(fields=['-created_at'], name='idx_trend_created'),
            models.Index(fields=['synced_on', 'category'], name='idx_trend_sync_category'),
        ]

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'


class NewsArticle(models.Model):
    """최근 뉴스 원천. 본문을 저장하지 않고 검색 API가 제공한 요약만 보존한다."""

    title = models.CharField('기사 제목', max_length=500)
    summary = models.TextField('기사 요약', blank=True, default='')
    category = models.CharField('수집 분야', max_length=20, choices=NewsCategory.choices)
    source = models.CharField('언론사/제공자', max_length=150, blank=True, default='')
    source_url = models.URLField('원문 URL', max_length=1000)
    cache_key = models.CharField('원문 URL 해시', max_length=64, unique=True)
    published_at = models.DateTimeField('원문 발행 시각', db_index=True)
    collected_at = models.DateTimeField('수집 시각', auto_now_add=True)
    updated_at = models.DateTimeField('갱신 시각', auto_now=True)

    class Meta:
        db_table = 'news_article'
        ordering = ('-published_at', '-id')
        indexes = [
            models.Index(fields=['category', '-published_at'], name='idx_news_category_pub'),
        ]

    @staticmethod
    def make_cache_key(url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def __str__(self):
        return self.title


class WeatherSnapshot(models.Model):
    location = models.CharField('위치', max_length=100)
    observed_at = models.DateTimeField('관측 기준 시각')
    condition = models.CharField('날씨', max_length=100, blank=True, default='')
    temperature_c = models.FloatField('기온', blank=True, null=True)
    feels_like_c = models.FloatField('체감 기온', blank=True, null=True)
    humidity = models.PositiveSmallIntegerField('습도', blank=True, null=True)
    wind_speed = models.FloatField('풍속', blank=True, null=True)
    weather_code = models.IntegerField('날씨 코드', blank=True, null=True)
    icon = models.CharField('아이콘', max_length=20, blank=True, default='')
    collected_at = models.DateTimeField('수집 시각', auto_now_add=True)

    class Meta:
        db_table = 'weather_snapshot'
        ordering = ('-observed_at', '-id')
        constraints = [
            models.UniqueConstraint(
                fields=['location', 'observed_at'], name='uq_weather_location_observed',
            ),
        ]

    def __str__(self):
        return f'{self.location} {self.observed_at:%Y-%m-%d %H:%M}'


class TrendBatch(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        PROCESSING = 'processing', '처리 중'
        COMPLETED = 'completed', '완료'
        FAILED = 'failed', '실패'

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    source_started_at = models.DateTimeField(default=timezone.now)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    is_legacy = models.BooleanField(default=False, db_index=True)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trend_batch'
        ordering = ('-published_at', '-created_at')

    def __str__(self):
        return f'Batch {self.pk} ({self.status})'


class TrendTopic(models.Model):
    batch = models.ForeignKey(TrendBatch, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    summary = models.TextField()
    category = models.CharField(max_length=20, choices=NewsCategory.choices)
    keywords = models.JSONField(default=list, blank=True)
    rank = models.PositiveSmallIntegerField()
    articles = models.ManyToManyField(
        NewsArticle, through='TrendTopicNews', related_name='topics', blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trend_topic'
        ordering = ('rank', 'id')
        constraints = [
            models.UniqueConstraint(fields=['batch', 'rank'], name='uq_topic_batch_rank'),
            models.CheckConstraint(condition=Q(rank__gte=1) & Q(rank__lte=5), name='ck_topic_rank'),
        ]

    def __str__(self):
        return f'{self.rank}. {self.title}'


class TrendTopicNews(models.Model):
    topic = models.ForeignKey(TrendTopic, on_delete=models.CASCADE, related_name='article_links')
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='topic_links')
    rank = models.PositiveSmallIntegerField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'trend_topic_news'
        ordering = ('rank', 'id')
        constraints = [
            models.UniqueConstraint(fields=['topic', 'article'], name='uq_topic_article'),
            models.UniqueConstraint(fields=['topic', 'rank'], name='uq_topic_article_rank'),
            models.UniqueConstraint(
                fields=['topic'], condition=Q(is_primary=True), name='uq_topic_primary_article',
            ),
            models.CheckConstraint(condition=Q(rank__gte=1) & Q(rank__lte=5), name='ck_topic_article_rank'),
        ]

    def __str__(self):
        return f'{self.topic} -> {self.article}'


class SyncRun(models.Model):
    class Status(models.TextChoices):
        IDLE = 'idle', 'Idle'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        SKIPPED = 'skipped', 'Skipped'

    lock_key = models.CharField(max_length=80, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDLE)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    next_run_after = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, default='')
    metadata = models.JSONField(blank=True, default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sync_run'
        ordering = ('lock_key',)

    def __str__(self):
        return f'{self.lock_key} ({self.status})'
