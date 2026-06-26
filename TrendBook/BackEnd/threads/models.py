from django.conf import settings
from django.db import models

from books.models import Book


class ReadingThread(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reading_threads',
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='reading_threads')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reading_thread'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class ThreadLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thread_likes',
    )
    thread = models.ForeignKey(
        ReadingThread,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'thread_like'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'thread'],
                name='uq_thread_like_user_thread',
            ),
        ]

    def __str__(self):
        return f'{self.user_id} likes {self.thread_id}'


class Comment(models.Model):
    thread = models.ForeignKey(ReadingThread, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='thread_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'thread_comment'
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.author}: {self.content[:30]}'
