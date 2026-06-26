<template>
  <section class="reviews-page">
    <router-link :to="`/books/${bookId}`" class="back">← 도서 상세로</router-link>

    <header class="page-header">
      <p class="eyebrow">BOOK REVIEWS</p>
      <h1>{{ bookTitle }}의 도서 리뷰</h1>
      <p>총 {{ totalCount }}개의 리뷰</p>
    </header>

    <div class="review-toolbar">
      <label>
        정렬
        <select v-model="ordering" @change="changeOrdering">
          <option value="latest">최신순</option>
          <option value="likes">좋아요순</option>
          <option value="comments">댓글 많은 순</option>
        </select>
      </label>
    </div>

    <div v-if="loading" class="state">리뷰를 불러오는 중입니다…</div>
    <div v-else-if="!reviews.length" class="state">아직 등록된 도서 리뷰가 없습니다.</div>
    <div v-else class="review-list">
      <router-link
        v-for="review in reviews"
        :key="review.id"
        :to="`/threads/${review.id}`"
        class="review-card"
      >
        <img :src="review.book.cover_img || placeholder" :alt="review.book.title">
        <div class="review-body">
          <small>{{ review.author.nickname }} · {{ formatDate(review.created_at) }}</small>
          <h2>{{ review.title }}</h2>
          <p>{{ review.content }}</p>
          <div class="meta">
            <span>댓글 {{ review.comment_count || 0 }}</span>
            <span>좋아요 {{ review.like_count || 0 }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <nav v-if="totalPages > 1" class="pagination">
      <button :disabled="page <= 1" @click="goToPage(1)">처음</button>
      <button :disabled="page <= 1" @click="goToPage(page - 1)">이전</button>
      <button v-for="pageNumber in pageNumbers" :key="pageNumber" :class="{ active: pageNumber === page }" @click="goToPage(pageNumber)">{{ pageNumber }}</button>
      <button :disabled="page >= totalPages" @click="goToPage(page + 1)">다음</button>
      <button :disabled="page >= totalPages" @click="goToPage(totalPages)">끝</button>
    </nav>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const bookId = computed(() => route.params.bookId)
const reviews = ref([])
const bookTitle = ref('도서')
const totalCount = ref(0)
const totalPages = ref(1)
const page = ref(1)
const loading = ref(true)
const ordering = ref('latest')
const placeholder = 'https://via.placeholder.com/80x112?text=Book'

const pageNumbers = computed(() => {
  const numbers = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let current = start; current <= end; current += 1) {
    numbers.push(current)
  }
  return numbers
})

const formatDate = (value) => (
  value
    ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
    : '-'
)

const loadBook = async () => {
  try {
    const { data } = await api.get(`/books/${bookId.value}`)
    bookTitle.value = data.title
  } catch {
    bookTitle.value = '도서'
  }
}

const loadReviews = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/threads', {
      params: { book_isbn: bookId.value, page: page.value, ordering: ordering.value },
    })
    reviews.value = data.results || []
    totalCount.value = data.count || reviews.value.length
    totalPages.value = Math.max(1, Math.ceil(totalCount.value / 10))
  } finally {
    loading.value = false
  }
}

const changeOrdering = async () => {
  page.value = 1
  await loadReviews()
}

const goToPage = async (nextPage) => {
  if (nextPage < 1 || nextPage > totalPages.value || nextPage === page.value) return
  page.value = nextPage
  await loadReviews()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(bookId, async () => {
  page.value = 1
  ordering.value = 'latest'
  await Promise.all([loadBook(), loadReviews()])
})

onMounted(async () => {
  await Promise.all([loadBook(), loadReviews()])
})
</script>

<style scoped>
.reviews-page { max-width: 900px; margin: auto; padding: 24px var(--space-margin-mobile) 48px; }
@media (min-width: 768px) { .reviews-page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.back { display: inline-block; margin-bottom: 18px; color: var(--color-on-surface-variant); text-decoration: none; font-weight: 300; }
.back:hover { color: var(--color-primary); }

.page-header { margin-bottom: 24px; }
.eyebrow { font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary); text-transform: uppercase; }
.page-header h1 { margin: 6px 0; font: 300 clamp(1.6rem, 4vw, 2rem)/1.3 var(--font-headline); color: var(--color-primary); }
.page-header p { color: var(--color-on-surface-variant); font-weight: 300; }

.review-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.review-toolbar label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-on-surface-variant);
  font-size: 0.88rem;
  font-weight: 300;
  white-space: nowrap;
}

.review-toolbar select {
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--color-surface-container-lowest);
  color: var(--color-on-surface);
}

.review-list { display: grid; gap: 14px; }

.review-card {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  gap: 18px;
  padding: 20px;
  border-radius: var(--radius-xl);
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  color: inherit;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.review-card:hover { border-color: var(--color-outline-variant); box-shadow: var(--shadow-card); }
.review-card img { width: 80px; height: 112px; object-fit: cover; border-radius: var(--radius-md); }
.review-body {
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.review-card small, .review-card p { color: var(--color-on-surface-variant); font-weight: 300; }
.review-card h2,
.review-card p {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.review-card h2 {
  margin: 8px 0;
  font: 400 1.1rem/1.4 var(--font-body);
  color: var(--color-on-surface);
  -webkit-line-clamp: 2;
}
.review-card p {
  -webkit-line-clamp: 3;
}

.meta { display: flex; gap: 12px; margin-top: 10px; font-size: .82rem; color: var(--color-primary); font-weight: 400; }

.state { padding: 36px; text-align: center; background: var(--color-surface-container-lowest); border-radius: var(--radius-xl); color: var(--color-on-surface-variant); font-weight: 300; }

.pagination { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 28px; }
.pagination button {
  min-width: 42px; padding: 8px 12px;
  border: 1px solid var(--color-outline-variant); border-radius: var(--radius-md);
  background: var(--color-surface-container-lowest); color: var(--color-on-surface-variant);
  font-weight: 300; font-size: 0.88rem; transition: all var(--transition-fast);
}
.pagination button:hover:not(:disabled) { border-color: var(--color-primary); color: var(--color-primary); }
.pagination button.active { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary); }
.pagination button:disabled { opacity: .4; cursor: not-allowed; }

@media (max-width: 640px) {
  .review-card {
    grid-template-columns: 64px minmax(0, 1fr);
    gap: 12px;
    padding: 16px;
  }

  .review-card img {
    width: 64px;
    height: 92px;
  }

  .review-toolbar {
    justify-content: flex-start;
  }
}
</style>
