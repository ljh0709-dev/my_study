from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from books.models import Book
from trends.models import TrendTopic, TrendTopicNews


class Recommendation(models.Model):
    topic = models.ForeignKey(
        TrendTopic,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='트렌드 주제',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='도서',
    )
    reason = models.TextField('추천 사유')
    relevance_score = models.DecimalField(
        '관련도', max_digits=4, decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    retrieval_score = models.DecimalField(
        '벡터 검색 유사도', max_digits=6, decimal_places=5, default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
    )
    embedding_model = models.CharField('임베딩 모델', max_length=100, blank=True, default='')
    created_at = models.DateTimeField('생성 일시', auto_now_add=True)

    class Meta:
        db_table = 'recommendation'
        verbose_name = '추천'
        verbose_name_plural = '추천 목록'
        ordering = ('-relevance_score', '-retrieval_score', 'id')
        constraints = [
            models.UniqueConstraint(fields=['topic', 'book'], name='uq_recommendation_topic_book'),
        ]

    @property
    def ai_recommend_reason(self):
        return self.reason

    def __str__(self):
        return f'{self.topic.title} → {self.book.title}'


class NewsRecommendation(models.Model):
    topic_news = models.ForeignKey(
        TrendTopicNews,
        on_delete=models.CASCADE,
        related_name='book_recommendations',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='news_recommendations',
    )
    reason = models.TextField()
    relevance_score = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )
    retrieval_score = models.DecimalField(
        max_digits=6,
        decimal_places=5,
        default=0,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
    )
    embedding_model = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'news_recommendation'
        ordering = ('topic_news__rank', '-relevance_score', '-retrieval_score', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=['topic_news', 'book'],
                name='uq_news_recommendation_link_book',
            ),
        ]

    def __str__(self):
        return f'{self.topic_news.article.title} -> {self.book.title}'
