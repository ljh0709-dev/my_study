from rest_framework import serializers

from books.serializers import BookListSerializer

from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    topic_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recommendation
        fields = (
            'id', 'topic_id', 'book', 'reason', 'relevance_score',
            'retrieval_score', 'embedding_model', 'created_at',
        )
