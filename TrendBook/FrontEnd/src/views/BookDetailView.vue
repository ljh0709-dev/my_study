<template>
  <div v-if="loading" class="state">도서 정보를 불러오는 중입니다…</div>
  <main v-else-if="book" class="detail-shell">
    <section class="detail-header">
      <img :src="bookCover" :alt="book.title" @error="usePlaceholder">
      <div class="detail-meta">
        <p class="category">{{ book.category_name || '도서' }}</p><h1>{{ book.title }}</h1>
        <p>{{ book.author || '저자 정보 없음' }} · {{ book.publisher || '출판사 정보 없음' }}</p>
        <p>출간 {{ book.pub_date || '미정' }} · ISBN {{ book.isbn }}</p>
        <p>판매가 {{ formatPrice(book.price_sales) }} · 판매지수 {{ formatNumber(book.sales_point) }} · 평점 {{ book.customer_review_rank ?? '-' }}</p>
        <div class="actions">
          <button v-if="authStore.isAuthenticated" class="primary" :disabled="bookmarkSaving" @click="toggleBookmark">{{ book.is_bookmarked ? '찜 해제' : '찜하기' }}</button>
          <router-link v-else :to="{name:'Login',query:{redirect:route.fullPath}}" class="button">로그인하고 찜하기</router-link>
          <router-link v-if="authStore.isAuthenticated" :to="{name:'ThreadCreate',query:{book:book.isbn}}" class="button">도서 리뷰 쓰기</router-link>
          <a v-if="book.aladin_link" :href="book.aladin_link" target="_blank" rel="noreferrer" class="button">알라딘 ↗</a>
        </div>
      </div>
    </section>

    <section class="content-card"><p class="eyebrow">ABOUT THE BOOK</p><h2>도서 소개</h2><p>{{ book.description || '도서 소개 정보가 없습니다.' }}</p></section>

    <section class="content-card analysis-card">
      <div class="analysis-heading">
        <div><p class="eyebrow">GPT BOOK ANALYSIS</p><h2>AI 도서 분석</h2></div>
        <button v-if="authStore.isAuthenticated" class="primary" :disabled="analysisLoading" @click="generateAnalysis(analysis?.status === 'completed')">{{ analysisLoading ? '분석 중…' : (analysis?.status === 'completed' ? '다시 분석' : '분석 생성') }}</button>
        <router-link v-else-if="!authStore.isAuthenticated && analysis?.status !== 'completed'" :to="{name:'Login',query:{redirect:route.fullPath}}" class="button">로그인하고 분석하기</router-link>
      </div>
      <div v-if="analysisLoading" class="analysis-state">GPT-5.4-mini가 도서 메타데이터를 분석하고 있습니다…</div>
      <div v-else-if="analysis?.status === 'completed'" class="analysis-grid">
        <article><span>관심 요인</span><p>{{ analysis.sales_reason }}</p></article>
      </div>
      <p v-else-if="analysisError" class="analysis-state error">{{ analysisError }}</p>
      <p v-else class="analysis-state">아직 생성된 분석이 없습니다. 리뷰 본문이 없으면 평가 경향을 추측하지 않고 그 한계를 명시합니다.</p>
    </section>

    <section class="content-card">
      <div class="section-title">
        <h2>이 책의 도서 리뷰</h2>
        <router-link v-if="reviewTotal > 4" :to="{ name: 'BookReviews', params: { bookId: book.isbn } }">더보기</router-link>
      </div>
      <div v-if="reviewsLoading" class="analysis-state">리뷰를 불러오는 중입니다…</div>
      <div v-else-if="!previewReviews.length" class="analysis-state">아직 등록된 도서 리뷰가 없습니다. 첫 리뷰를 남겨보세요.</div>
      <div v-else class="review-list">
        <router-link v-for="review in previewReviews" :key="review.id" :to="`/threads/${review.id}`" class="review-card">
          <div>
            <small>{{ review.author.nickname }} · {{ formatReviewDate(review.created_at) }}</small>
            <h3>{{ review.title }}</h3>
            <p>{{ review.content.slice(0, 120) }}</p>
            <div class="review-meta">
              <span>댓글 {{ review.comment_count || 0 }}</span>
              <span>좋아요 {{ review.like_count || 0 }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </section>
  </main>
  <div v-else class="state error">{{ error }}</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const book = ref(null)
const loading = ref(true)
const error = ref('')
const bookmarkSaving = ref(false)
const analysis = ref(null)
const analysisLoading = ref(false)
const analysisError = ref('')
const reviewsLoading = ref(true)
const previewReviews = ref([])
const reviewTotal = ref(0)
const placeholder = 'https://via.placeholder.com/240x360?text=No+Cover'
const bookCover = computed(() => book.value?.cover_img || placeholder)
const formatPrice = (value) => (value == null ? '-' : `${Number(value).toLocaleString()}원`)
const formatNumber = (value) => (value ? Number(value).toLocaleString() : '-')
const formatReviewDate = (value) => (
  value
    ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
    : '-'
)
const usePlaceholder = (event) => { event.target.src = placeholder }

const loadReviews = async () => {
  reviewsLoading.value = true
  try {
    const { data } = await api.get('/threads', {
      params: { book_isbn: route.params.bookId, page: 1 },
    })
    reviewTotal.value = data.count || 0
    previewReviews.value = (data.results || []).slice(0, 4)
  } catch {
    reviewTotal.value = 0
    previewReviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

const loadAnalysis = async () => {
  try {
    analysis.value = (await api.get(`/books/${route.params.bookId}/ai-analysis`)).data
  } catch {
    analysis.value = null
  }
}

const load = async () => {
  loading.value = true
  try {
    book.value = (await api.get(`/books/${route.params.bookId}`)).data
    await Promise.all([loadAnalysis(), loadReviews()])
  } catch (requestError) {
    error.value = requestError.response?.data?.detail || '도서를 찾을 수 없습니다.'
  } finally {
    loading.value = false
  }
}

const toggleBookmark = async () => {
  bookmarkSaving.value = true
  try {
    if (book.value.is_bookmarked) {
      await api.delete(`/books/${book.value.isbn}/bookmark`)
    } else {
      await api.post(`/books/${book.value.isbn}/bookmark`)
    }
    book.value.is_bookmarked = !book.value.is_bookmarked
  } finally {
    bookmarkSaving.value = false
  }
}

const generateAnalysis = async (force = false) => {
  analysisLoading.value = true
  analysisError.value = ''
  try {
    analysis.value = (await api.post(`/books/${book.value.isbn}/ai-analysis/generate`, { review_excerpts: [], force })).data
  } catch (requestError) {
    analysisError.value = requestError.response?.data?.detail || 'AI 분석을 생성하지 못했습니다.'
  } finally {
    analysisLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.detail-shell { max-width: 980px; margin: auto; padding: 24px var(--space-margin-mobile); }
@media (min-width: 768px) { .detail-shell { padding: 24px var(--space-margin-desktop); } }

.detail-header {
  display: grid;
  grid-template-columns: minmax(220px, 300px) 1fr;
  gap: 34px;
  align-items: start;
}

.detail-header > img {
  width: 100%;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}

.detail-meta h1 {
  font: 300 clamp(1.8rem, 5vw, 2.8rem)/1.15 var(--font-headline);
  letter-spacing: var(--ls-headline);
  color: var(--color-primary);
  margin: 8px 0 18px;
}

.detail-meta p { color: var(--color-on-surface-variant); font-weight: 300; margin: 4px 0; }

.category { color: var(--color-primary) !important; font-weight: 600 !important; font-size: 0.82rem; }
.eyebrow { font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary) !important; margin: 0 0 8px !important; text-transform: uppercase; }

.actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 24px; }

.button,
.primary {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-outline-variant);
  text-decoration: none;
  color: var(--color-on-surface);
  background: var(--color-surface-container-lowest);
  font-weight: 300;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.button:hover { border-color: var(--color-primary); color: var(--color-primary); }
.primary { background: var(--color-primary); color: var(--color-on-primary); border: 0; font-weight: 400; }
.primary:hover { background: var(--color-primary-container); }
.primary:disabled { opacity: 0.55; cursor: not-allowed; }

.content-card {
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  padding: 26px;
  margin-top: 22px;
  line-height: 1.75;
  font-weight: 300;
}

.content-card h2 { margin: 0 0 12px; font: 300 1.3rem/1.3 var(--font-headline); color: var(--color-on-surface); }
.content-card p { color: var(--color-on-surface-variant); }

.section-title, .analysis-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.section-title a { color: var(--color-primary); text-decoration: underline; text-underline-offset: 4px; font-weight: 300; font-size: 0.88rem; }

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-top: 15px;
}

.analysis-grid article {
  background: var(--color-surface-container-low);
  border-radius: var(--radius-lg);
  padding: 18px;
}

.analysis-grid span { color: var(--color-primary); font: var(--text-label-sm); letter-spacing: var(--ls-label); text-transform: uppercase; }
.analysis-grid p { color: var(--color-on-surface-variant); font-weight: 300; }
.analysis-grid small { color: var(--color-outline); font-size: 0.78rem; }

.analysis-state {
  padding: 24px;
  background: var(--color-surface-container-low);
  border-radius: var(--radius-lg);
  color: var(--color-on-surface-variant);
  text-align: center;
  font-weight: 300;
}

.analysis-state.error { color: var(--color-error); }

.review-list { display: grid; gap: 12px; margin-top: 12px; }

.review-card {
  display: block;
  padding: 18px;
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: inherit;
  background: var(--color-surface-container-low);
  transition: all var(--transition-fast);
}

.review-card:hover { border-color: var(--color-outline-variant); box-shadow: var(--shadow-card); }
.review-card small, .review-card p { color: var(--color-on-surface-variant); font-weight: 300; }
.review-card h3 { margin: 8px 0; font-weight: 400; font-size: 1rem; }

.review-meta {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  font-size: .82rem;
  color: var(--color-primary);
  font-weight: 400;
}

.state {
  padding: 42px;
  text-align: center;
  background: var(--color-surface-container-lowest);
  border-radius: var(--radius-xl);
  font-weight: 300;
  color: var(--color-on-surface-variant);
}

.error { color: var(--color-error); }

@media (max-width: 720px) {
  .detail-header, .analysis-grid { grid-template-columns: 1fr; }
  .detail-header > img { max-width: 260px; margin: auto; }
  .analysis-heading { align-items: flex-start; flex-direction: column; }
}
</style>
