from rest_framework import serializers

from .models import AladinCategory, Book, BookBookmark, BookCategory, BookRanking


class AladinCategorySerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)

    class Meta:
        model = AladinCategory
        fields = (
            'cid', 'name', 'mall_type', 'path',
            'depth1', 'depth2', 'depth3', 'depth4', 'depth5',
        )


class BookCategorySerializer(serializers.ModelSerializer):
    category = AladinCategorySerializer(read_only=True)

    class Meta:
        model = BookCategory
        fields = ('category', 'is_primary')


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'isbn', 'mall_type', 'title', 'author', 'publisher', 'cover_img',
            'category_name', 'pub_date', 'price_sales', 'price_standard',
            'sales_point', 'customer_review_rank', 'stock_status', 'adult',
        )


class BookDetailSerializer(BookListSerializer):
    categories = BookCategorySerializer(source='category_links', many=True, read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + (
            'isbn10', 'aladin_item_id', 'description', 'categories',
            'aladin_link', 'fixed_price', 'cached_at', 'updated_at', 'is_bookmarked',
        )

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and BookBookmark.objects.filter(user=request.user, book=obj).exists()
        )


class BookRankingSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    category_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = BookRanking
        fields = (
            'id', 'book', 'category_id', 'list_type', 'rank',
            'period_start', 'fetched_at',
        )


class BookBookmarkSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)

    class Meta:
        model = BookBookmark
        fields = ('id', 'book', 'created_at')

