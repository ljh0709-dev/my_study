import uuid

from django.db import models
from django.db.models import Q

from books.models import Book
from trends.models import TrendBatch, TrendTopic


class AIJob(models.Model):
    class Kind(models.TextChoices):
        TREND = 'trend', '트렌드 생성'
        RECOMMENDATION = 'recommendation', '추천 생성'
        ARTICLE_RECOMMENDATION = 'article_recommendation', 'Article recommendation'

    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        PROCESSING = 'processing', '처리 중'
        COMPLETED = 'completed', '완료'
        FAILED = 'failed', '실패'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=30, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    batch = models.ForeignKey(
        TrendBatch, on_delete=models.CASCADE, related_name='ai_jobs', blank=True, null=True,
    )
    topic = models.ForeignKey(
        TrendTopic, on_delete=models.CASCADE, related_name='ai_jobs', blank=True, null=True,
    )
    request_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'ai_job'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['topic'],
                condition=Q(
                    kind='recommendation', status__in=['pending', 'processing'], topic__isnull=False,
                ),
                name='uq_active_recommendation_job',
            ),
        ]


class AISummary(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        COMPLETED = 'completed', '완료'
        FAILED = 'failed', '실패'

    book = models.OneToOneField(
        Book, on_delete=models.CASCADE, related_name='ai_summary', verbose_name='도서',
    )
    sales_reason = models.TextField('판매 인기 요인', blank=True, null=True)
    review_summary = models.TextField('리뷰 요약', blank=True, null=True)
    model = models.CharField('생성 모델', max_length=100, blank=True, default='')
    source_hash = models.CharField('입력 데이터 해시', max_length=64, blank=True, default='', db_index=True)
    review_source_count = models.PositiveSmallIntegerField('리뷰 발췌 수', default=0)
    status = models.CharField('상태', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        db_table = 'ai_summary'
        verbose_name = 'AI 요약'
        verbose_name_plural = 'AI 요약 목록'

    def __str__(self):
        return f'AI 요약: {self.book.title} ({self.get_status_display()})'
