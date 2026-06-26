from django.contrib import admin
from .models import AIJob, AISummary


@admin.register(AISummary)
class AISummaryAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'model', 'review_source_count', 'created_at', 'updated_at')
    list_filter = ('status',)
    raw_id_fields = ('book',)


@admin.register(AIJob)
class AIJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'status', 'batch', 'topic', 'created_at', 'finished_at')
    list_filter = ('kind', 'status')
    readonly_fields = ('request_payload',)
