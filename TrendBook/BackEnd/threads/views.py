from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, ReadingThread, ThreadLike
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, ReadingThreadSerializer


def _thread_queryset(request):
    queryset = ReadingThread.objects.select_related('author', 'book').annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True),
    )
    if request.user.is_authenticated:
        queryset = queryset.annotate(
            is_liked=Exists(
                ThreadLike.objects.filter(
                    thread_id=OuterRef('pk'),
                    user_id=request.user.id,
                ),
            ),
        )
    return queryset


class ThreadListCreateView(generics.ListCreateAPIView):
    serializer_class = ReadingThreadSerializer

    def get_permissions(self):
        return [permissions.AllowAny()] if self.request.method == 'GET' else [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = _thread_queryset(self.request)
        mine = self.request.query_params.get('mine')
        if mine in {'1', 'true', 'True'}:
            if not self.request.user.is_authenticated:
                return queryset.none()
            queryset = queryset.filter(author=self.request.user)
        isbn = self.request.query_params.get('book_isbn')
        if isbn:
            queryset = queryset.filter(book__isbn=isbn)
        query = (self.request.query_params.get('q') or '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(book__title__icontains=query)
                | Q(book__author__icontains=query)
                | Q(book__isbn__icontains=query)
                | Q(author__nickname__icontains=query)
            )
        ordering = self.request.query_params.get('ordering')
        ordering_map = {
            'latest': ('-created_at', '-id'),
            'likes': ('-like_count', '-created_at', '-id'),
            'comments': ('-comment_count', '-created_at', '-id'),
        }
        queryset = queryset.order_by(*ordering_map.get(ordering, ordering_map['latest']))
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReadingThreadSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return _thread_queryset(self.request).prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('author')),
        )


class ThreadCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        return [permissions.AllowAny()] if self.request.method == 'GET' else [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Comment.objects.filter(thread_id=self.kwargs['thread_id']).select_related('author')

    def perform_create(self, serializer):
        thread = get_object_or_404(ReadingThread, id=self.kwargs['thread_id'])
        serializer.save(author=self.request.user, thread=thread)


class ThreadLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, thread_id):
        thread = get_object_or_404(ReadingThread, id=thread_id)
        _, created = ThreadLike.objects.get_or_create(user=request.user, thread=thread)
        like_count = thread.likes.count()
        return Response(
            {'like_count': like_count, 'is_liked': True},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, thread_id):
        thread = get_object_or_404(ReadingThread, id=thread_id)
        ThreadLike.objects.filter(user=request.user, thread=thread).delete()
        return Response({'like_count': thread.likes.count(), 'is_liked': False})


class CommentDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.author_id != request.user.id:
            return Response({'detail': '본인 댓글만 삭제할 수 있습니다.'}, status=403)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
