from django.urls import path

from .views import (
    AIJobCallbackView,
    AIJobStatusView,
    ArticleRecommendationGenerateView,
    CurrentWeatherView,
    RecommendationGenerateView,
    TrendDetailView,
    TrendListView,
    TrendRefreshStatusView,
    TrendRefreshView,
    TrendSyncView,
)


app_name = 'trends'

urlpatterns = [
    path('trends', TrendListView.as_view(), name='list'),
    path('trends/today', TrendListView.as_view(), name='today'),
    path('weather/current', CurrentWeatherView.as_view(), name='weather-current'),
    path('trends/refresh', TrendRefreshView.as_view(), name='refresh'),
    path('trends/refresh/status', TrendRefreshStatusView.as_view(), name='refresh-status'),
    path('trends/sync', TrendSyncView.as_view(), name='sync'),
    path('trends/article-recommendations/generate', ArticleRecommendationGenerateView.as_view(), name='generate-article-recommendations'),
    path('trends/<int:topic_id>', TrendDetailView.as_view(), name='detail'),
    path('trends/<int:topic_id>/recommendations/generate', RecommendationGenerateView.as_view(), name='generate-recommendations'),
    path('ai/jobs/<uuid:job_id>', AIJobStatusView.as_view(), name='job-status'),
    path('internal/ai/jobs/<uuid:job_id>/complete', AIJobCallbackView.as_view(), name='job-callback'),
]
