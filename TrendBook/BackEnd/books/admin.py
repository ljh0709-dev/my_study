from django.contrib import admin

from .models import AladinCategory, Book, BookBookmark, BookCategory, BookEmbedding, BookRanking


class BookCategoryInline(admin.TabularInline):
    model = BookCategory
    extra = 0
    autocomplete_fields = ('category',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'isbn',
        'mall_type',
        'author',
        'publisher',
        'price_sales',
        'sales_point',
        'updated_at',
    )
    search_fields = ('title', 'isbn', 'isbn10', 'author', 'publisher')
    list_filter = ('mall_type', 'adult', 'fixed_price')
    ordering = ('-updated_at',)
    inlines = (BookCategoryInline,)


@admin.register(AladinCategory)
class AladinCategoryAdmin(admin.ModelAdmin):
    list_display = ('cid', 'name', 'mall_type', 'path', 'is_active')
    search_fields = ('=cid', 'name', 'depth1', 'depth2', 'depth3', 'depth4', 'depth5')
    list_filter = ('mall_type', 'is_active', 'depth1')
    ordering = ('mall_type', 'depth1', 'depth2', 'depth3', 'depth4', 'depth5')


@admin.register(BookRanking)
class BookRankingAdmin(admin.ModelAdmin):
    list_display = ('period_start', 'list_type', 'category', 'rank', 'book', 'fetched_at')
    list_filter = ('list_type', 'period_start')
    search_fields = ('book__title', 'book__isbn', 'category__name')
    raw_id_fields = ('book', 'category')
    ordering = ('-period_start', 'rank')


@admin.register(BookBookmark)
class BookBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'book')


@admin.register(BookEmbedding)
class BookEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('book', 'model', 'dimensions', 'embedded_at')
    search_fields = ('book__title', 'book__isbn', 'content_hash')
    readonly_fields = ('vector', 'content_hash', 'embedded_at')
    raw_id_fields = ('book',)
