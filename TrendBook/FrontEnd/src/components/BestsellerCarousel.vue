<template>
  <div class="bestseller-section">
    <div class="section-header">
      <h2 class="section-title">베스트셀러</h2>
      <p class="section-subtitle">실시간 인기 도서</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>베스트셀러를 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-if="hasError && !isLoading" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchBestsellers">다시 시도</button>
    </div>

    <!-- 베스트셀러 회전목마 -->
    <div v-if="!isLoading && !hasError && books.length > 0" class="carousel-container">
      <button 
        class="carousel-btn carousel-btn-left"
        @click="previousPage"
        :disabled="currentPage === 0"
        aria-label="이전 페이지"
      >
        <span class="arrow">‹</span>
      </button>

      <div class="carousel-track">
        <div class="books-grid">
          <article
            v-for="(book, index) in currentPageBooks"
            :key="`${book.isbn}-${index}`"
            class="book-card"
            @click="goToBookDetail(book.isbn)"
          >
            <div class="rank-badge">{{ currentPage * itemsPerPage + index + 1 }}</div>
            <div class="book-cover">
              <img
                :src="book.cover || 'https://via.placeholder.com/160x240?text=No+Cover'"
                :alt="book.title"
                @error="(e) => (e.target.src = 'https://via.placeholder.com/160x240?text=No+Cover')"
                class="cover-image"
              />
            </div>
            <div class="book-info">
              <h3 class="book-title">{{ truncateTitle(book.title) }}</h3>
              <p class="book-author">{{ truncateAuthor(book.author) }}</p>
              <div class="book-rating" v-if="book.rating">
                <span class="star">⭐</span>
                <span class="rating-value">{{ book.rating }}</span>
              </div>
              <div class="book-price">
                {{ formatNumber(book.priceSales) }}원
              </div>
            </div>
          </article>
        </div>
      </div>

      <button 
        class="carousel-btn carousel-btn-right"
        @click="nextPage"
        :disabled="currentPage >= maxPage"
        aria-label="다음 페이지"
      >
        <span class="arrow">›</span>
      </button>

    </div>
    <!-- 페이지 인디케이터 -->
    <div class="carousel-indicator">
      <div class="page-dots">
        <button
          v-for="(_, index) in totalPages"
          :key="index"
          class="dot"
          :class="{ active: currentPage === index }"
          @click="goToPage(index)"
          :aria-label="`페이지 ${index + 1}`"
          ></button>
        </div>
    </div>

    <!-- 빈 상태 -->
    <div v-if="!isLoading && !hasError && books.length === 0" class="empty-state">
      <p>현재 베스트셀러가 없습니다.</p>
    </div>

    <!-- 전체 보기 버튼 -->
    <div v-if="books.length > 0" class="view-all-section">
      <router-link to="/bestsellers" class="view-all-btn">
        전체 베스트셀러 보기 →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()

const books = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(0)
const itemsPerPage = ref(4) // 기본값: 4개

const isLoading = computed(() => loading.value)
const hasError = computed(() => error.value !== null)

// 총 페이지 수
const totalPages = computed(() => {
  return Math.ceil(books.value.length / itemsPerPage.value)
})

// 최대 페이지
const maxPage = computed(() => {
  return Math.max(0, totalPages.value - 1)
})

// 현재 페이지의 도서
const currentPageBooks = computed(() => {
  const start = currentPage.value * itemsPerPage.value
  const end = start + itemsPerPage.value
  return books.value.slice(start, end)
})

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('ko-KR').format(num)
}

const truncateTitle = (title, length = 25) => {
  if (!title) return ''
  return title.length > length ? title.substring(0, length) + '...' : title
}

const truncateAuthor = (author, length = 20) => {
  if (!author) return '저자 미상'
  return author.length > length ? author.substring(0, length) + '...' : author
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
    if (!Array.isArray(booksData)) {
      booksData = []
    }

    const processedBooks = booksData
      .filter((ranking) => ranking.book?.isbn && ranking.book?.title)
      .map((ranking) => ranking.book)
      .filter((book) => book.isbn && book.title)
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
      .sort((a, b) => (b.salesPoint || 0) - (a.salesPoint || 0))
      .slice(0, 100) // 최대 100개
    
    books.value = processedBooks
    currentPage.value = 0

    if (books.value.length === 0) {
      error.value = '베스트셀러 데이터를 찾을 수 없습니다.'
    }
  } catch (err) {
    error.value = `베스트셀러를 불러올 수 없습니다. 오류: ${err.message}`
    console.error('Fetch bestsellers error:', err)
    books.value = []
  } finally {
    loading.value = false
  }
}

const previousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < maxPage.value) {
    currentPage.value++
  }
}

const goToPage = (pageIndex) => {
  if (pageIndex >= 0 && pageIndex <= maxPage.value) {
    currentPage.value = pageIndex
  }
}

const goToBookDetail = (isbn) => {
  router.push({
    name: 'BookDetail',
    params: { bookId: isbn },
  })
}

onMounted(() => {
  fetchBestsellers()
  
  // 반응형: 화면 크기에 따라 itemsPerPage 조정
  const handleResize = () => {
    if (window.innerWidth < 768) {
      itemsPerPage.value = 2
    } else if (window.innerWidth < 1024) {
      itemsPerPage.value = 3
    } else {
      itemsPerPage.value = 4
    }
    currentPage.value = 0
  }
  
  handleResize()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.bestseller-section {
  margin-bottom: 80px;
}

.section-header {
  margin-bottom: 32px;
}

.section-title {
  font: 300 32px/1.2 var(--font-headline);
  letter-spacing: -0.02em;
  margin: 0 0 8px;
  color: var(--color-on-surface);
}

.section-subtitle {
  font: 300 16px/1.6 var(--font-body);
  color: var(--color-on-surface-variant);
  margin: 0;
}

/* 회전목마 컨테이너 */
.carousel-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.carousel-track {
  flex: 1;
  overflow: hidden;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 도서 카드 */
.book-card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface-container-lowest);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-outline-variant);
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal), transform var(--transition-normal);
  position: relative;
  box-shadow: var(--shadow-card);
}

.book-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-4px);
}

.rank-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 28px;
  height: 28px;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font: 600 13px/1 var(--font-body);
  z-index: 1;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.book-cover {
  position: relative;
  width: 100%;
  padding-top: 145%;
  overflow: hidden;
  background: var(--color-surface-container-low);
}

.cover-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.book-card:hover .cover-image {
  transform: scale(1.03);
}

.book-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: var(--color-surface-container-lowest);
}

.book-title {
  font: 600 15px/1.4 var(--font-body);
  margin: 0 0 6px;
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  font: 300 13px/1.4 var(--font-body);
  color: var(--color-on-surface-variant);
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
  font-size: 0.8rem;
}

.star {
  font-size: 0.9rem;
}

.rating-value {
  color: var(--color-warning, #d97706);
  font-weight: 600;
}

.book-price {
  font: 600 14px/1.4 var(--font-body);
  color: var(--color-primary);
}

/* 회전목마 버튼 */
.carousel-btn {
  width: 44px;
  height: 44px;
  border: 1px solid var(--color-outline-variant);
  background: var(--color-surface-container-lowest);
  border-radius: var(--radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--color-on-surface-variant);
  transition: all var(--transition-fast);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.carousel-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-surface-container-low);
  color: var(--color-primary);
  transform: scale(1.05);
}

.carousel-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.arrow {
  font-weight: 300;
  line-height: 1;
}

/* 페이지 인디케이터 */
.carousel-indicator {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.page-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--color-outline-variant);
  border: none;
  cursor: pointer;
  transition: all var(--transition-normal);
  padding: 0;
}

.dot:hover {
  background: var(--color-outline);
}

.dot.active {
  background: var(--color-primary);
  width: 24px;
  border-radius: var(--radius-sm);
}

/* 로딩, 에러, 빈 상태 */
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 24px;
  background: var(--color-surface-container-low);
  border-radius: var(--radius-lg);
  color: var(--color-on-surface-variant);
  border: 1px solid var(--color-outline-variant);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-surface-container-high);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state p {
  color: var(--color-error);
  margin: 0 0 16px;
}

.retry-btn {
  padding: 8px 20px;
  background: var(--color-error);
  color: var(--color-on-error);
  border: none;
  border-radius: var(--radius-full);
  font: 600 14px/1.4 var(--font-body);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.retry-btn:hover {
  background: #93000a;
}

/* 전체 보기 버튼 */
.view-all-section {
  text-align: center;
  margin-top: 24px;
}

.view-all-btn {
  display: inline-block;
  padding: 10px 24px;
  background: var(--color-surface-container-lowest);
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  text-decoration: none;
  border-radius: var(--radius-full);
  font: 300 15px/1.4 var(--font-body);
  transition: all var(--transition-normal);
  cursor: pointer;
}

.view-all-btn:hover {
  background: var(--color-primary);
  color: var(--color-on-primary);
  transform: translateX(4px);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .books-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .carousel-btn {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }
}

@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .carousel-btn {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }

  .book-card:hover {
    transform: translateY(-2px);
  }
}

@media (max-width: 512px) {
  .books-grid {
    grid-template-columns: 1fr;
  }

  .carousel-container {
    gap: 12px;
  }
}
</style>
