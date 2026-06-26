from rest_framework import serializers

from .models import AISummary


class AISummarySerializer(serializers.ModelSerializer):
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)

    class Meta:
        model = AISummary
        fields = (
            'id', 'book_isbn', 'sales_reason', 'review_summary',
            'status', 'model', 'review_source_count', 'created_at', 'updated_at',
        )

