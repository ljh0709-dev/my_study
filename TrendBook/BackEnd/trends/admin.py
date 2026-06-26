from django.contrib import admin

from .models import NewsArticle, TrendBatch, TrendIssue, TrendTopic, TrendTopicNews, WeatherSnapshot


admin.site.register(TrendIssue)
admin.site.register(NewsArticle)
admin.site.register(WeatherSnapshot)
admin.site.register(TrendBatch)
admin.site.register(TrendTopic)
admin.site.register(TrendTopicNews)
