from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class MallType(models.TextChoices):
    """TrendBook에서 지원하는 알라딘 상품 몰."""

    BOOK = 'BOOK', '국내도서'
    FOREIGN = 'FOREIGN', '외국도서'
    EBOOK = 'EBOOK', '전자책'


class AladinCategory(models.Model):
    """알라딘 CID와 최대 5단계 분류 경로를 보존하는 카테고리 마스터."""

    cid = models.PositiveIntegerField('알라딘 CID', primary_key=True)
    name = models.CharField('카테고리명', max_length=100)
    mall_type = models.CharField(
        '몰 유형',
        max_length=10,
        choices=MallType.choices,
        db_index=True,
    )
    depth1 = models.CharField('1단계', max_length=100)
    depth2 = models.CharField('2단계', max_length=100, blank=True, default='')
    depth3 = models.CharField('3단계', max_length=100, blank=True, default='')
    depth4 = models.CharField('4단계', max_length=100, blank=True, default='')
    depth5 = models.CharField('5단계', max_length=100, blank=True, default='')
    is_active = models.BooleanField('사용 여부', default=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        db_table = 'aladin_category'
        verbose_name = '알라딘 카테고리'
        verbose_name_plural = '알라딘 카테고리 목록'
        indexes = [
            models.Index(fields=['mall_type', 'name'], name='idx_category_mall_name'),
            models.Index(fields=['mall_type', 'depth1'], name='idx_category_mall_d1'),
        ]

    @property
    def path(self):
        return ' > '.join(
            depth
            for depth in (self.depth1, self.depth2, self.depth3, self.depth4, self.depth5)
            if depth
        )

    def __str__(self):
        return f'[{self.get_mall_type_display()}] {self.path}'


class Book(models.Model):
    """
    알라딘 API에서 수집한 도서 마스터.

    기존 URL 및 관계 호환을 위해 ``isbn`` 필드명을 유지하되 ISBN13을 우선 저장한다.
    가격·판매지수처럼 변하는 값은 최신 캐시를 보관하고, 순위 이력은 BookRanking에 저장한다.
    """

    isbn = models.CharField('ISBN13', max_length=20)
    isbn10 = models.CharField('ISBN10', max_length=10, blank=True, null=True)
    aladin_item_id = models.PositiveBigIntegerField(
        '알라딘 상품 ID',
        unique=True,
        blank=True,
        null=True,
    )
    mall_type = models.CharField(
        '몰 유형',
        max_length=10,
        choices=MallType.choices,
        default=MallType.BOOK,
        db_index=True,
    )
    title = models.CharField('도서명', max_length=255)
    author = models.CharField('저자', max_length=500, blank=True, null=True)
    publisher = models.CharField('출판사', max_length=255, blank=True, null=True)
    cover_img = models.URLField('표지 URL', max_length=500, blank=True, null=True)
    description = models.TextField('줄거리', blank=True, null=True)
    category_name = models.CharField(
        '대표 카테고리명',
        max_length=100,
        blank=True,
        null=True,
        help_text='API 응답 표시용 캐시. 정식 관계는 categories를 사용합니다.',
    )
    categories = models.ManyToManyField(
        AladinCategory,
        through='BookCategory',
        related_name='books',
        blank=True,
    )
    aladin_link = models.URLField('알라딘 링크', max_length=500, blank=True, null=True)
    pub_date = models.DateField('출판일', blank=True, null=True)
    price_sales = models.PositiveIntegerField('판매가', blank=True, null=True)
    price_standard = models.PositiveIntegerField('정가', blank=True, null=True)
    sales_point = models.PositiveBigIntegerField('판매지수', blank=True, null=True)
    customer_review_rank = models.DecimalField(
        '회원 리뷰 평점',
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    stock_status = models.CharField('재고 상태', max_length=100, blank=True, default='')
    adult = models.BooleanField('성인 등급', default=False)
    fixed_price = models.BooleanField('도서 정가제 대상', default=False)
    cached_at = models.DateTimeField('최초 캐싱 시점', auto_now_add=True)
    updated_at = models.DateTimeField('최종 갱신 시점', auto_now=True)

    class Meta:
        db_table = 'book'
        verbose_name = '도서'
        verbose_name_plural = '도서 목록'
        indexes = [
            models.Index(fields=['title'], name='idx_book_title'),
            models.Index(fields=['mall_type', 'pub_date'], name='idx_book_mall_pubdate'),
            models.Index(fields=['-sales_point'], name='idx_book_sales_point'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['isbn', 'mall_type'],
                name='uq_book_isbn_malltype',
            ),
        ]

    def __str__(self):
        return f'{self.title} ({self.isbn})'


class BookCategory(models.Model):
    """도서가 속한 복수의 알라딘 카테고리를 연결한다."""

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='category_links',
        verbose_name='도서',
    )
    category = models.ForeignKey(
        AladinCategory,
        on_delete=models.PROTECT,
        related_name='book_links',
        verbose_name='카테고리',
    )
    is_primary = models.BooleanField('대표 카테고리 여부', default=False)
    created_at = models.DateTimeField('연결일', auto_now_add=True)

    class Meta:
        db_table = 'book_category'
        verbose_name = '도서 카테고리'
        verbose_name_plural = '도서 카테고리 목록'
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'category'],
                name='uq_book_category',
            ),
            models.UniqueConstraint(
                fields=['book'],
                condition=Q(is_primary=True),
                name='uq_book_primary_category',
            ),
        ]

    def __str__(self):
        return f'{self.book} → {self.category}'


class BookRanking(models.Model):
    """베스트셀러 등 알라딘 상품 리스트의 시점별 순위를 저장한다."""

    class ListType(models.TextChoices):
        BESTSELLER = 'BESTSELLER', '베스트셀러'
        ITEM_NEW_ALL = 'ITEM_NEW_ALL', '신간 전체'
        ITEM_NEW_SPECIAL = 'ITEM_NEW_SPECIAL', '주목할 만한 신간'
        EDITOR_CHOICE = 'EDITOR_CHOICE', '편집자 추천'
        BLOG_BEST = 'BLOG_BEST', '블로거 베스트셀러'

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='rankings',
        verbose_name='도서',
    )
    category = models.ForeignKey(
        AladinCategory,
        on_delete=models.PROTECT,
        related_name='rankings',
        verbose_name='조회 카테고리',
        blank=True,
        null=True,
    )
    list_type = models.CharField('리스트 유형', max_length=20, choices=ListType.choices)
    rank = models.PositiveIntegerField('순위')
    period_start = models.DateField('집계 기준일')
    fetched_at = models.DateTimeField('수집 시점', auto_now_add=True)

    class Meta:
        db_table = 'book_ranking'
        verbose_name = '도서 순위'
        verbose_name_plural = '도서 순위 이력'
        ordering = ('-period_start', 'rank')
        indexes = [
            models.Index(
                fields=['list_type', 'category', '-period_start', 'rank'],
                name='idx_ranking_lookup',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(rank__gte=1),
                name='ck_book_ranking_positive',
            ),
            models.UniqueConstraint(
                fields=['book', 'category', 'list_type', 'period_start'],
                condition=Q(category__isnull=False),
                name='uq_book_ranking_category',
            ),
            models.UniqueConstraint(
                fields=['book', 'list_type', 'period_start'],
                condition=Q(category__isnull=True),
                name='uq_book_ranking_all',
            ),
        ]

    def __str__(self):
        return f'{self.period_start} {self.get_list_type_display()} {self.rank}위 - {self.book}'


class BookBookmark(models.Model):
    """사용자와 도서의 찜 N:M 중개 테이블."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='사용자',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='도서',
    )
    created_at = models.DateTimeField('찜한 일시', auto_now_add=True)

    class Meta:
        db_table = 'book_bookmark'
        verbose_name = '찜'
        verbose_name_plural = '찜 목록'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='uq_bookmark_user_book',
            ),
        ]

    def __str__(self):
        return f'{self.user} → {self.book}'


class BookEmbedding(models.Model):
    """도서 설명 기반 임베딩 캐시. SQLite MVP에서는 JSON 벡터로 보존한다."""

    book = models.OneToOneField(
        Book, on_delete=models.CASCADE, related_name='embedding', verbose_name='도서',
    )
    vector = models.JSONField('임베딩 벡터')
    model = models.CharField('임베딩 모델', max_length=100)
    dimensions = models.PositiveIntegerField('차원')
    content_hash = models.CharField('입력 콘텐츠 해시', max_length=64, db_index=True)
    embedded_at = models.DateTimeField('생성 시각', auto_now=True)

    class Meta:
        db_table = 'book_embedding'
        verbose_name = '도서 임베딩'
        verbose_name_plural = '도서 임베딩 목록'

    def __str__(self):
        return f'{self.book} ({self.model}, {self.dimensions}d)'
