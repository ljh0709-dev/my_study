from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('topic', 'book', 'relevance_score', 'retrieval_score', 'embedding_model', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('topic', 'book')
