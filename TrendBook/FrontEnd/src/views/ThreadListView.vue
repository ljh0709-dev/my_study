<template>
  <section class="page">
    <header class="page-header">
      <p class="eyebrow">BOOK REVIEWS</p>
      <h1>도서 리뷰</h1>
      <p class="intro">책에서 시작된 생각을 도서별로 모아봅니다.</p>
    </header>

    <form class="review-tools" @submit.prevent="applyFilters">
      <label class="search-field">
        <span>검색</span>
        <input v-model="searchInput" type="search" placeholder="도서명, 저자, 리뷰 제목/내용 검색">
      </label>
      <label class="sort-field">
        <span>정렬</span>
        <select v-model="ordering" @change="applyFilters">
          <option value="latest">최신순</option>
          <option value="likes">좋아요순</option>
          <option value="comments">댓글순</option>
        </select>
      </label>
      <button class="btn-filter" type="submit">검색</button>
      <button v-if="hasActiveFilters" class="btn-reset" type="button" @click="resetFilters">초기화</button>
    </form>

    <div v-if="loading" class="state">불러오는 중...</div>
    <div v-else-if="!reviewGroups.length" class="state">{{ emptyMessage }}</div>

    <div v-else class="review-groups">
      <article v-for="group in reviewGroups" :key="group.book.isbn" class="book-review-group">
        <div class="review-card-layout">
          <aside class="book-summary">
            <router-link :to="`/books/${group.book.isbn}`" class="book-cover-link">
              <img :src="group.book.cover_img || placeholder" :alt="group.book.title" @error="usePlaceholder">
            </router-link>
            <div class="book-info">
              <span class="badge">{{ group.reviews.length }}개 리뷰</span>
              <h2 class="book-title" :title="group.book.title">{{ group.book.title }}</h2>
              <p class="book-author" :title="group.book.author || '저자 미상'">{{ group.book.author || '저자 미상' }}</p>
            </div>
          </aside>

          <div class="reviews-pane">
            <div class="review-preview-list">
              <router-link v-for="thread in group.previewReviews" :key="thread.id" :to="`/threads/${thread.id}`" class="review-preview">
                <div class="review-copy">
                  <small>{{ thread.author.nickname }}</small>
                  <strong :title="thread.title">{{ thread.title }}</strong>
                  <p>{{ previewContent(thread.content) }}</p>
                </div>
                <div class="meta">
                  <span>댓글 {{ thread.comment_count || 0 }}</span>
                  <span>좋아요 {{ thread.like_count || 0 }}</span>
                </div>
              </router-link>
            </div>

            <router-link
              v-if="group.reviews.length >= previewLimit"
              :to="{ name: 'BookReviews', params: { bookId: group.book.isbn } }"
              class="btn-more"
            >더보기</router-link>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const router = useRouter()
const threads = ref([])
const loading = ref(true)
const searchInput = ref(typeof route.query.q === 'string' ? route.query.q : '')
const ordering = ref(['latest', 'likes', 'comments'].includes(route.query.ordering) ? route.query.ordering : 'latest')
const previewLimit = 2
const placeholder = 'https://via.placeholder.com/120x172?text=Book'
const usePlaceholder = (event) => { event.target.src = placeholder }

const previewContent = (content = '') => {
  if (content.length <= 120) return content
  return `${content.slice(0, 120)}...`
}

const reviewGroups = computed(() => {
  const grouped = new Map()
  for (const thread of threads.value) {
    const isbn = thread.book?.isbn
    if (!isbn) continue
    if (!grouped.has(isbn)) {
      grouped.set(isbn, { book: thread.book, reviews: [], previewReviews: [] })
    }
    grouped.get(isbn).reviews.push(thread)
  }
  return Array.from(grouped.values()).map((group) => ({
    ...group,
    previewReviews: group.reviews.slice(0, previewLimit),
  }))
})

const hasActiveFilters = computed(() => Boolean(searchInput.value.trim()) || ordering.value !== 'latest')
const emptyMessage = computed(() => (
  hasActiveFilters.value
    ? '검색 조건에 맞는 도서 리뷰가 없습니다.'
    : '아직 등록된 도서 리뷰가 없습니다.'
))

const fetchThreads = async () => {
  loading.value = true
  try {
    const params = {}
    if (route.query.book) params.book_isbn = route.query.book
    const query = typeof route.query.q === 'string' ? route.query.q.trim() : ''
    if (query) params.q = query
    const currentOrdering = ['latest', 'likes', 'comments'].includes(route.query.ordering)
      ? route.query.ordering
      : 'latest'
    params.ordering = currentOrdering
    threads.value = (await api.get('/threads', { params })).data.results || []
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  await router.push({
    name: 'Threads',
    query: {
      ...route.query,
      q: searchInput.value.trim() || undefined,
      ordering: ordering.value === 'latest' ? undefined : ordering.value,
    },
  })
}

const resetFilters = async () => {
  searchInput.value = ''
  ordering.value = 'latest'
  await router.push({
    name: 'Threads',
    query: {
      ...route.query,
      q: undefined,
      ordering: undefined,
    },
  })
}

watch(
  () => route.query,
  async (query) => {
    searchInput.value = typeof query.q === 'string' ? query.q : ''
    ordering.value = ['latest', 'likes', 'comments'].includes(query.ordering) ? query.ordering : 'latest'
    await fetchThreads()
  },
)

onMounted(async () => {
  await fetchThreads()
})
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: 24px var(--space-margin-mobile); }
@media (min-width: 768px) { .page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.page-header { margin-bottom: 24px; }
.eyebrow { margin: 0 0 6px; font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary); text-transform: uppercase; }
.page-header h1 { margin: 0; font: 300 clamp(1.8rem, 5vw, 2.4rem)/1.2 var(--font-headline); letter-spacing: var(--ls-headline); color: var(--color-primary); }
.intro { color: var(--color-on-surface-variant); font-weight: 300; margin: 8px 0 0; }

.review-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px auto auto;
  gap: 10px;
  align-items: end;
  margin: 0 0 18px;
}

.search-field,
.sort-field {
  display: grid;
  gap: 6px;
  min-width: 0;
  color: var(--color-on-surface-variant);
  font-size: .78rem;
  font-weight: 400;
}

.search-field input,
.sort-field select {
  width: 100%;
  min-width: 0;
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  background: var(--color-surface-container-lowest);
  color: var(--color-on-surface);
  padding: 10px 14px;
  font: 300 .9rem/1.2 var(--font-body);
}

.search-field input:focus,
.sort-field select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(75, 91, 109, .12);
}

.btn-filter,
.btn-reset {
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  padding: 10px 16px;
  background: var(--color-surface-container-lowest);
  color: var(--color-primary);
  font-size: .86rem;
  cursor: pointer;
}

.btn-filter {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-on-primary);
}

.btn-reset:hover,
.btn-filter:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.state { padding: 36px; text-align: center; background: var(--color-surface-container-lowest); border: 1px solid rgba(196, 198, 204, 0.2); border-radius: var(--radius-xl); color: var(--color-on-surface-variant); font-weight: 300; }

.review-groups { display: grid; gap: 16px; }

.book-review-group {
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.review-card-layout {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  gap: 28px;
  padding: 22px;
  align-items: start;
}

.book-summary {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.book-cover-link {
  display: block;
  flex: 0 0 auto;
}

.book-cover-link img {
  width: 120px;
  height: 172px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-surface-container);
  box-shadow: var(--shadow-card);
}

.book-info, .reviews-pane, .review-copy { min-width: 0; }

.badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border-radius: var(--radius-full);
  padding: 5px 10px;
  font-size: .72rem;
  font-weight: 400;
  background: var(--color-surface-container-low);
  color: var(--color-primary);
  margin-bottom: 8px;
}

.book-title {
  margin: 0 0 8px;
  font: 400 1.15rem/1.35 var(--font-body);
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  margin: 0;
  color: var(--color-on-surface-variant);
  font-weight: 300;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.review-preview-list {
  display: grid;
  gap: 10px;
  min-width: 0;
  max-width: 100%;
}

.review-preview {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  padding: 14px;
  border: 1px solid rgba(196, 198, 204, 0.15);
  border-radius: var(--radius-lg);
  color: inherit;
  text-decoration: none;
  background: var(--color-surface-container-low);
  transition: border-color var(--transition-fast), box-shadow var(--transition-normal), transform var(--transition-fast);
}

.review-preview:hover {
  border-color: var(--color-outline-variant);
  box-shadow: var(--shadow-card);
  transform: translateY(-1px);
}

.review-preview small, .review-preview p { color: var(--color-on-surface-variant); font-weight: 300; }

.review-copy {
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-preview strong {
  display: block;
  margin: 4px 0;
  max-width: 100%;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
  font-weight: 400;
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.review-preview p {
  margin: 0;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  flex: 0 0 auto;
  color: var(--color-primary);
  font-size: .8rem;
  font-weight: 400;
}

.btn-more {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--color-outline-variant);
  background: var(--color-surface-container-lowest);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  padding: 8px 14px;
  font-size: .86rem;
  font-weight: 400;
  text-decoration: none;
  margin-top: 12px;
  transition: all var(--transition-fast);
}

.btn-more:hover { border-color: var(--color-primary); }

@media (max-width: 720px) {
  .review-tools { grid-template-columns: 1fr; }
  .review-card-layout { grid-template-columns: 1fr; }
  .book-summary { grid-template-columns: 96px minmax(0, 1fr); }
  .book-cover-link img { width: 96px; height: 136px; }
  .review-preview { align-items: flex-start; flex-direction: column; }
}
</style>
