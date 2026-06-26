from django.urls import path

from .views import (
    CommentDeleteView,
    ThreadCommentListCreateView,
    ThreadDetailView,
    ThreadLikeView,
    ThreadListCreateView,
)


app_name = 'threads'

urlpatterns = [
    path('threads', ThreadListCreateView.as_view(), name='list-create'),
    path('threads/<int:pk>', ThreadDetailView.as_view(), name='detail'),
    path('threads/<int:thread_id>/like', ThreadLikeView.as_view(), name='like'),
    path('threads/<int:thread_id>/comments', ThreadCommentListCreateView.as_view(), name='comments'),
    path('comments/<int:comment_id>', CommentDeleteView.as_view(), name='comment-delete'),
]
