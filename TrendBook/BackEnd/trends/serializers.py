from rest_framework import serializers

from books.serializers import BookListSerializer
from recommendations.models import NewsRecommendation, Recommendation

from .models import NewsArticle, TrendTopic, TrendTopicNews, WeatherSnapshot
from .recommendation_utils import filter_recommendation_records
from .weather_utils import normalize_weather_condition


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = ('id', 'title', 'summary', 'category', 'source', 'source_url', 'published_at')


class WeatherSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherSnapshot
        fields = (
            'location', 'observed_at', 'condition', 'temperature_c',
            'feels_like_c', 'humidity', 'wind_speed', 'weather_code', 'icon',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['condition'] = normalize_weather_condition(data.get('condition'))
        return data


class TopicArticleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='article.id')
    title = serializers.CharField(source='article.title')
    summary = serializers.CharField(source='article.summary')
    category = serializers.CharField(source='article.category')
    source = serializers.CharField(source='article.source')
    source_url = serializers.URLField(source='article.source_url')
    published_at = serializers.DateTimeField(source='article.published_at')
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = TrendTopicNews
        fields = (
            'id', 'title', 'summary', 'category', 'source', 'source_url',
            'published_at', 'rank', 'is_primary', 'recommendations',
        )

    def get_recommendations(self, obj):
        records = obj.book_recommendations.select_related('book').order_by('-relevance_score')
        return NewsRecommendationBriefSerializer(
            filter_recommendation_records(records, limit=3),
            many=True,
        ).data


class NewsRecommendationBriefSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)

    class Meta:
        model = NewsRecommendation
        fields = (
            'id', 'book', 'reason', 'relevance_score',
            'retrieval_score', 'embedding_model', 'created_at',
        )


class RecommendationBriefSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = (
            'id', 'book', 'reason', 'relevance_score',
            'retrieval_score', 'embedding_model', 'created_at',
        )


class TrendTopicListSerializer(serializers.ModelSerializer):
    representative_news = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    news = serializers.SerializerMethodField()
    news_count = serializers.IntegerField(read_only=True)
    recommendation_status = serializers.SerializerMethodField()

    class Meta:
        model = TrendTopic
        fields = (
            'id', 'title', 'summary', 'category', 'label', 'keywords', 'rank',
            'representative_news', 'news', 'news_count', 'recommendation_status',
        )

    def get_representative_news(self, obj):
        links = list(obj.article_links.all())
        primary = next((link for link in links if link.is_primary), links[0] if links else None)
        return TopicArticleSerializer(primary).data if primary else None

    def get_label(self, obj):
        return obj.get_category_display()

    def get_news(self, obj):
        return TopicArticleSerializer(obj.article_links.all(), many=True).data

    def get_recommendation_status(self, obj):
        links = list(obj.article_links.all())
        if links and all(len(link.book_recommendations.all()) >= 3 for link in links):
            return 'completed'
        job = obj.batch.ai_jobs.filter(kind='article_recommendation').order_by('-created_at').first()
        return job.status if job else 'not_started'


class TrendTopicDetailSerializer(serializers.ModelSerializer):
    related_news = TopicArticleSerializer(source='article_links', many=True, read_only=True)
    recommendations = serializers.SerializerMethodField()
    recommendation_status = serializers.SerializerMethodField()

    class Meta:
        model = TrendTopic
        fields = (
            'id', 'title', 'summary', 'category', 'keywords', 'rank',
            'related_news', 'recommendations', 'recommendation_status',
        )

    def get_recommendations(self, obj):
        records = obj.recommendations.select_related('book').order_by('-relevance_score')
        return RecommendationBriefSerializer(
            filter_recommendation_records(records),
            many=True,
        ).data

    def get_recommendation_status(self, obj):
        if len(self.get_recommendations(obj)) == 5:
            return 'completed'
        job = obj.ai_jobs.order_by('-created_at').first()
        return job.status if job else 'not_started'
