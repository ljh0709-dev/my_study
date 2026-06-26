from django.urls import path

from .views import (
    BestsellerListView, BookDetailView, BookListView, BookmarkView,
    BookAIAnalysisGenerateView, BookAIAnalysisView, CategoryListView,
    MyBookmarkListView, MyCategoryRecommendationView,
)


app_name = 'books'

urlpatterns = [
    path('books', BookListView.as_view(), name='book-list'),
    path('books/<str:isbn>', BookDetailView.as_view(), name='book-detail'),
    path('categories', CategoryListView.as_view(), name='category-list'),
    path('bestsellers', BestsellerListView.as_view(), name='bestseller-list'),
    path('books/<str:isbn>/bookmark', BookmarkView.as_view(), name='bookmark'),
    path('books/<str:isbn>/ai-analysis', BookAIAnalysisView.as_view(), name='ai-analysis'),
    path('books/<str:isbn>/ai-analysis/generate', BookAIAnalysisGenerateView.as_view(), name='ai-analysis-generate'),
    path('users/me/bookmarks', MyBookmarkListView.as_view(), name='my-bookmarks'),
    path('users/me/category-recommendations', MyCategoryRecommendationView.as_view(), name='my-category-recommendations'),
]
