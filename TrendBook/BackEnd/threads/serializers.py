from rest_framework import serializers

from accounts.serializers import UserSerializer
from books.models import Book
from books.serializers import BookListSerializer

from .models import Comment, ReadingThread, ThreadLike


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at', 'is_owner')
        read_only_fields = ('id', 'author', 'created_at', 'is_owner')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and request.user.pk == obj.author_id)


class ReadingThreadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    book = BookListSerializer(read_only=True)
    book_isbn = serializers.CharField(write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ReadingThread
        fields = (
            'id', 'author', 'book', 'book_isbn', 'title', 'content',
            'comments', 'comment_count', 'like_count', 'is_liked',
            'is_owner', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'author', 'book', 'comments', 'comment_count', 'like_count',
            'is_liked', 'is_owner', 'created_at', 'updated_at',
        )

    def validate_book_isbn(self, value):
        book = Book.objects.filter(isbn=value).order_by('mall_type').first()
        if not book:
            raise serializers.ValidationError('도서를 찾을 수 없습니다.')
        self.context['validated_book'] = book
        return value

    def create(self, validated_data):
        validated_data.pop('book_isbn', None)
        return ReadingThread.objects.create(book=self.context['validated_book'], **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('book_isbn', None)
        return super().update(instance, validated_data)

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if hasattr(obj, 'is_liked'):
            return bool(obj.is_liked)
        return ThreadLike.objects.filter(thread_id=obj.pk, user_id=request.user.id).exists()

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and request.user.pk == obj.author_id)
