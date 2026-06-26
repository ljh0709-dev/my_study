<template>
  <div class="books-page">
    <main class="content">
      <header class="content-header">
        <div>
          <h1>도서 목록</h1>
          <p>베스트셀러, 신간, 추천 도서를 탐색해 보세요.</p>
        </div>
        <div class="search-box">
          <input v-model="searchTerm" placeholder="검색어를 입력하세요..." @keyup.enter="applySearch" />
          <button class="search-btn" @click="applySearch">
            <span class="material-symbols-outlined">search</span>
          </button>
        </div>
      </header>

      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          :class="['tab', { active: activeSection === tab.value }]"
          @click="changeSection(tab.value)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="toolbar">
        <p class="total-count">총 {{ totalCount }}권</p>
        <label class="ordering">
          정렬
          <select v-model="activeOrdering" @change="changeOrdering">
            <option value="popular">인기순</option>
            <option value="newest">최신순</option>
            <option value="oldest">오래된순</option>
          </select>
        </label>
      </div>

      <section class="cards">
        <article v-for="book in books" :key="bookKey(book)" class="card">
          <router-link :to="`/books/${bookRouteId(book)}`" class="card-link">
            <div class="cover-wrap">
              <img
                class="cover"
                :src="bookCover(book)"
                :alt="book.title"
                @error="(e) => (e.target.src = 'https://via.placeholder.com/240x360?text=No+Cover')"
              />
            </div>
            <div class="info">
              <h3 class="title">{{ book.title }}</h3>
              <p class="meta">{{ book.author || '저자 미상' }} · {{ book.publisher || '출판사 미상' }}</p>
              <div class="stats">
                <span class="stat sales">판매지수 {{ formatNumber(book.sales_point) }}</span>
                <span class="stat rating">평점 {{ formatRating(book.customer_review_rank) }}</span>
              </div>
            </div>
          </router-link>
        </article>
      </section>

      <div v-if="!loading && !books.length" class="empty">조건에 맞는 도서가 없습니다.</div>
      <div v-if="loading" class="empty">도서를 불러오는 중입니다...</div>

      <nav v-if="totalPages > 1" class="pagination">
        <button :disabled="currentPage <= 1" @click="goToPage(1)">처음</button>
        <button :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">이전</button>
        <button
          v-for="pageNumber in pageNumbers"
          :key="pageNumber"
          :class="{ active: pageNumber === currentPage }"
          @click="goToPage(pageNumber)"
        >
          {{ pageNumber }}
        </button>
        <button :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">다음</button>
        <button :disabled="currentPage >= totalPages" @click="goToPage(totalPages)">끝</button>
      </nav>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const router = useRouter()
const books = ref([])
const loading = ref(false)
const searchTerm = ref(route.query.q || '')
const appliedSearch = ref(route.query.q || '')
const activeSection = ref(route.query.section || 'bestseller')
const activeOrdering = ref(route.query.ordering || 'popular')
const currentPage = ref(Number(route.query.page) || 1)
const totalCount = ref(0)
const totalPages = ref(1)
const BOOKS_PER_PAGE = 12

const tabs = [
  { value: 'bestseller', label: '베스트셀러' },
  { value: 'new', label: '신간' },
  { value: 'recommended', label: '추천' },
]

const bookRouteId = (book) => book.isbn ?? book.isbn13 ?? book.aladin_item_id
const bookKey = (book) => book.isbn ?? book.aladin_item_id ?? book.title
const bookCover = (book) => book.cover_img ?? book.cover ?? 'https://via.placeholder.com/240x360?text=No+Cover'

const formatNumber = (value) => {
  if (value == null || value === '') return '-'
  return new Intl.NumberFormat('ko-KR').format(Number(value))
}

const formatRating = (value) => {
  if (value == null || value === '') return '-'
  return Number(value).toFixed(1)
}

const pageNumbers = computed(() => {
  const numbers = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let page = start; page <= end; page += 1) {
    numbers.push(page)
  }
  return numbers
})

const syncQuery = () => {
  const query = {}
  if (activeSection.value !== 'bestseller') query.section = activeSection.value
  if (activeOrdering.value !== 'popular') query.ordering = activeOrdering.value
  if (currentPage.value > 1) query.page = String(currentPage.value)
  if (appliedSearch.value) query.q = appliedSearch.value
  router.replace({ name: 'BookList', query })
}

const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      section: activeSection.value,
      ordering: activeOrdering.value,
      page: currentPage.value,
    }
    if (appliedSearch.value) params.q = appliedSearch.value

    const { data } = await api.get('/books', { params })
    books.value = data.results || []
    totalCount.value = data.count || books.value.length
    totalPages.value = Math.max(1, Math.ceil(totalCount.value / BOOKS_PER_PAGE))
  } catch (error) {
    console.error('도서 목록 로드 중 오류 발생', error)
    books.value = []
    totalCount.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

const changeSection = async (section) => {
  if (activeSection.value === section) return
  activeSection.value = section
  currentPage.value = 1
  syncQuery()
  await fetchBooks()
}

const changeOrdering = async () => {
  currentPage.value = 1
  syncQuery()
  await fetchBooks()
}

const applySearch = async () => {
  appliedSearch.value = searchTerm.value.trim()
  currentPage.value = 1
  syncQuery()
  await fetchBooks()
}

const goToPage = async (page) => {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  syncQuery()
  await fetchBooks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(
  () => route.query,
  async (query) => {
    activeSection.value = query.section || 'bestseller'
    activeOrdering.value = query.ordering || 'popular'
    currentPage.value = Number(query.page) || 1
    appliedSearch.value = query.q || ''
    searchTerm.value = query.q || ''
    await fetchBooks()
  },
)

onMounted(fetchBooks)
</script>

<style scoped>
.books-page { min-height: calc(100vh - 88px); }
.content { max-width: var(--container-max); margin: 0 auto; padding: 24px var(--space-margin-mobile); }
@media (min-width: 768px) { .content { padding: 24px var(--space-margin-desktop); } }

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 24px;
}

.content-header h1 {
  margin: 0;
  font: 300 clamp(1.6rem, 4vw, 2.2rem)/1.2 var(--font-headline);
  letter-spacing: var(--ls-headline);
  color: var(--color-primary);
}

.content-header p { margin: 10px 0 0; color: var(--color-on-surface-variant); font-weight: 300; }

.search-box { display: flex; gap: 8px; flex: 0 0 auto; min-width: 280px; }
.search-box input {
  flex: 1;
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  padding: 10px 16px;
  font-size: 0.92rem;
}

.search-btn {
  border: 0;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: var(--color-on-primary);
  padding: 10px 14px;
  display: flex;
  align-items: center;
}

.search-btn .material-symbols-outlined { font-size: 20px; }

/* Tabs */
.tabs { display: flex; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }

.tab {
  border: 1px solid var(--color-outline-variant);
  background: var(--color-surface-container-lowest);
  color: var(--color-on-surface-variant);
  border-radius: var(--radius-full);
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 300;
  font-size: 0.92rem;
  transition: all var(--transition-fast);
}

.tab:hover { border-color: var(--color-primary); color: var(--color-primary); }
.tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 400;
}

/* Toolbar */
.toolbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 18px; }
.total-count { margin: 0; color: var(--color-on-surface); font-weight: 400; font-size: 0.92rem; }
.ordering { display: flex; align-items: center; gap: 8px; color: var(--color-on-surface-variant); font-size: .88rem; font-weight: 300; white-space: nowrap; }
.ordering select {
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--color-surface-container-lowest);
}

/* Cards */
.cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  align-items: stretch;
}

.card {
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast), box-shadow var(--transition-normal), border-color var(--transition-fast);
  padding: 0;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--color-outline-variant);
}

.card-link {
  display: flex;
  flex-direction: column;
  height: 100%;
  text-decoration: none;
  color: inherit;
}

.cover-wrap {
  padding: 16px 16px 0;
  background: var(--color-surface-container-low);
}

.cover {
  display: block;
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-surface-container);
  box-shadow: var(--shadow-md);
}

.info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  padding: 14px 16px 18px;
}

.title {
  margin: 0;
  font: 400 1rem/1.4 var(--font-body);
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  margin: 0;
  color: var(--color-on-surface-variant);
  font-size: 0.82rem;
  font-weight: 300;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stats { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }

.stat {
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-full);
  padding: 4px 8px;
  font-size: 0.72rem;
  font-weight: 400;
  line-height: 1;
}

.stat.sales { background: var(--color-success-bg); color: var(--color-success); }
.stat.rating { background: var(--color-warning-bg); color: var(--color-warning); }
.stat.rating::before { content: '★'; margin-right: 4px; font-size: 0.7rem; }

.empty { padding: 28px; color: var(--color-on-surface-variant); font-weight: 300; text-align: center; }

/* Pagination */
.pagination { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 28px; }

.pagination button {
  min-width: 42px;
  padding: 8px 12px;
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-md);
  background: var(--color-surface-container-lowest);
  color: var(--color-on-surface-variant);
  font-weight: 300;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.pagination button:hover:not(:disabled) { border-color: var(--color-primary); color: var(--color-primary); }
.pagination button.active { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }

/* Responsive */
@media (max-width: 1100px) { .cards { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 960px) {
  .content-header { flex-direction: column; align-items: stretch; }
  .search-box { min-width: 0; width: 100%; }
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 620px) {
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .cover-wrap { padding: 12px 12px 0; }
  .info { padding: 12px; }
  .title { font-size: 0.92rem; }
}
</style>