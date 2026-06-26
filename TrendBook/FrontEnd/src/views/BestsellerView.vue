<template>
  <section class="bestseller-page">
    <div class="bestseller-header">
      <div class="header-content">
        <p class="eyebrow">BESTSELLERS</p>
        <h1>베스트셀러</h1>
        <p class="subtitle">최근 주간 인기 도서</p>
      </div>
    </div>

    <div class="category-filter">
      <button
        v-for="category in categories"
        :key="category"
        :class="['filter-btn', { active: selectedCategory === category }]"
        @click="selectedCategory = category"
      >
        {{ category }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>베스트셀러를 불러오는 중...</p>
    </div>

    <div v-if="error && !loading" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button class="primary" @click="fetchBestsellers">다시 시도</button>
    </div>

    <div v-if="filteredBooks.length > 0" class="bestsellers-grid">
      <article
        v-for="(book, index) in filteredBooks"
        :key="book.isbn"
        class="bestseller-item"
        @click="goToBookDetail(book.isbn)"
      >
        <div class="rank-badge">{{ index + 1 }}</div>
        <div class="book-cover">
          <img
            :src="book.cover || 'https://via.placeholder.com/160x240?text=No+Cover'"
            :alt="book.title"
            @error="(e) => (e.target.src = 'https://via.placeholder.com/160x240?text=No+Cover')"
          />
        </div>
        <div class="book-info">
          <h2 class="book-title">{{ book.title }}</h2>
          <p class="book-author">{{ book.author }}</p>
          <p class="book-publisher">{{ book.publisher }}</p>
          <div class="book-stats">
            <span class="rating" v-if="book.rating">★ {{ book.rating }}</span>
            <span class="sales-point">판매지수 {{ formatNumber(book.salesPoint) }}</span>
          </div>
          <div class="book-price">
            <span class="price-sales">{{ formatNumber(book.priceSales) }}원</span>
            <span v-if="book.priceStandard" class="price-standard">정가 {{ formatNumber(book.priceStandard) }}원</span>
          </div>
        </div>
      </article>
    </div>

    <div v-if="!loading && filteredBooks.length === 0" class="empty-state">
      <p>현재 보유한 베스트셀러가 없습니다.</p>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const books = ref([])
const selectedCategory = ref('전체')

const categories = computed(() => {
  const cats = new Set(['전체'])
  books.value.forEach((book) => {
    if (book.category && book.category.trim() !== '') cats.add(book.category)
  })
  return Array.from(cats)
})

const filteredBooks = computed(() => {
  if (selectedCategory.value === '전체') return books.value
  return books.value.filter((book) => book.category === selectedCategory.value)
})

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('ko-KR').format(num)
}

const fetchBestsellers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/bestsellers')
    let booksData = response.data
    if (booksData && typeof booksData === 'object' && !Array.isArray(booksData)) {
      booksData = booksData.results || booksData.data || []
    }
    if (!Array.isArray(booksData)) booksData = []
    const processedBooks = booksData
      .filter((ranking) => ranking.book?.isbn && ranking.book?.title)
      .map((ranking) => ({ ...ranking.book, rank: ranking.rank }))
      .map((book) => ({
        isbn: book.isbn ?? book.isbn13,
        title: book.title,
        author: book.author || '저자 미상',
        publisher: book.publisher || '출판사 정보 없음',
        cover: book.cover_img ?? book.cover,
        rating: book.customer_review_rank ?? 0,
        salesPoint: book.sales_point ?? 0,
        priceSales: book.price_sales ?? 0,
        priceStandard: book.price_standard ?? 0,
        category: book.category_name || '기타',
      }))
      .slice(0, 50)
    books.value = processedBooks
    if (books.value.length === 0) error.value = '베스트셀러 데이터를 찾을 수 없습니다.'
  } catch (err) {
    error.value = `베스트셀러를 불러올 수 없습니다. 오류: ${err.message}`
    books.value = []
  } finally {
    loading.value = false
  }
}

const goToBookDetail = (isbn) => {
  router.push({ name: 'BookDetail', params: { bookId: isbn } })
}

onMounted(() => { fetchBestsellers() })
</script>

<style scoped>
.bestseller-page { max-width: 1200px; margin: 0 auto; padding: 24px var(--space-margin-mobile); }
@media (min-width: 768px) { .bestseller-page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.bestseller-header { margin-bottom: 24px; }
.eyebrow { font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary); text-transform: uppercase; margin: 0 0 4px; }
.header-content h1 { font: 300 clamp(1.8rem, 4vw, 2.4rem)/1.2 var(--font-headline); letter-spacing: var(--ls-headline); color: var(--color-primary); margin: 0 0 8px; }
.subtitle { color: var(--color-on-surface-variant); margin: 0; font-weight: 300; }

/* Filters */
.category-filter { display: flex; gap: 10px; margin-bottom: 28px; flex-wrap: wrap; }
.filter-btn {
  padding: 8px 16px;
  background: var(--color-surface-container-lowest);
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 300;
  color: var(--color-on-surface-variant);
  transition: all var(--transition-fast);
}
.filter-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.filter-btn.active { background: var(--color-primary); color: var(--color-on-primary); border-color: var(--color-primary); font-weight: 400; }

/* States */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 24px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  color: var(--color-on-surface-variant);
  font-weight: 300;
}
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-surface-container-high); border-top-color: var(--color-primary); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-message { color: var(--color-error); margin: 0 0 16px; }

/* Grid */
.bestsellers-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 768px) { .bestsellers-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .bestsellers-grid { grid-template-columns: repeat(3, 1fr); } }

.bestseller-item {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
}
.bestseller-item:hover { box-shadow: var(--shadow-card-hover); border-color: var(--color-outline-variant); transform: translateY(-3px); }

.rank-badge {
  position: absolute;
  top: 12px; right: 12px;
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: 50%;
  font-weight: 400;
  font-size: 0.88rem;
  box-shadow: var(--shadow-sm);
}

.book-cover { width: 100%; height: 240px; background: var(--color-surface-container); border-radius: var(--radius-md); overflow: hidden; margin-bottom: 16px; }
.book-cover img { width: 100%; height: 100%; object-fit: cover; }

.book-info { flex: 1; }
.book-title { margin: 0 0 4px; font: 400 1rem/1.4 var(--font-body); color: var(--color-on-surface); }
.book-author { margin: 0 0 2px; font-size: 0.82rem; color: var(--color-on-surface-variant); font-weight: 300; }
.book-publisher { margin: 0 0 10px; font-size: 0.78rem; color: var(--color-outline); font-weight: 300; }

.book-stats { display: flex; gap: 12px; margin-bottom: 12px; font-size: 0.82rem; }
.rating { color: var(--color-warning); font-weight: 400; }
.sales-point { color: var(--color-primary); font-weight: 300; }

.book-price { display: flex; gap: 8px; align-items: center; margin-top: auto; padding-top: 12px; border-top: 1px solid rgba(196, 198, 204, 0.15); }
.price-sales { font: 400 1rem/1 var(--font-body); color: var(--color-on-surface); }
.price-standard { font-size: 0.78rem; color: var(--color-outline); text-decoration: line-through; }
</style>
