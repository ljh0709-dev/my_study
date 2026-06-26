<template>
  <section class="page">
    <ToastNotification :message="toast.message" :variant="toast.variant" />

    <header class="page-header">
      <p class="eyebrow">MY LIBRARY</p>
      <h1>{{ user.nickname || '회원' }}의 서재</h1>
    </header>

    <div class="layout">
      <section class="panel profile-card">
        <h2>프로필</h2>
        <form @submit.prevent="updateProfile">
          <label>
            이메일
            <input :value="user.email" disabled>
          </label>
          <label>
            닉네임
            <input v-model="profile.nickname" required>
          </label>
          <label>
            추가할 관심 카테고리
            <select v-model="selectedDepth1">
              <option value="">카테고리를 선택하세요</option>
              <option
                v-for="category in availableDepthCategories"
                :key="category.depth1"
                :value="category.depth1"
              >
                {{ category.depth1 }}
              </option>
            </select>
          </label>
          <div class="form-actions">
            <button class="secondary" type="button" @click="appendKeywords">카테고리 추가</button>
            <button class="primary" type="submit" :disabled="saving">
              {{ saving ? '저장 중…' : '프로필 저장' }}
            </button>
          </div>
        </form>

        <div v-if="keywords.length" class="keyword-section">
          <h3>관심 카테고리</h3>
          <div class="keyword-pills">
            <span v-for="keyword in keywords" :key="keyword" class="keyword-pill">
              {{ categoryLabel(keyword) }}
              <button class="keyword-remove" type="button" :aria-label="`${categoryLabel(keyword)} 카테고리 삭제`" @click="removeKeyword(keyword)">×</button>
            </span>
          </div>
        </div>

        <div class="danger-zone">
          <button class="danger" :disabled="deleting" @click="withdraw">
            {{ deleting ? '탈퇴 처리 중…' : '회원 탈퇴' }}
          </button>
        </div>
      </section>

      <section class="panel">
        <div class="section-title">
          <h2>찜한 도서</h2>
          <button
            v-if="bookmarks.length >= 4"
            class="text-button"
            type="button"
            @click="showAllBookmarks = !showAllBookmarks"
          >
            {{ showAllBookmarks ? '접기' : '더보기' }}
          </button>
        </div>
        <p v-if="loading" class="empty">불러오는 중…</p>
        <p v-else-if="!bookmarks.length" class="empty">아직 찜한 도서가 없습니다.</p>
        <div v-else class="card-grid">
          <router-link v-for="item in displayedBookmarks" :key="item.id" :to="`/books/${item.book.isbn}`" class="media-card">
            <img :src="item.book.cover_img || placeholder" :alt="item.book.title">
            <div>
              <strong>{{ item.book.title }}</strong>
              <small>{{ item.book.author || '저자 미상' }}</small>
            </div>
          </router-link>
        </div>
      </section>

      <section class="panel">
        <h2>내가 작성한 도서 리뷰</h2>
        <p v-if="loading" class="empty">불러오는 중…</p>
        <p v-else-if="!myReviews.length" class="empty">아직 작성한 도서 리뷰가 없습니다.</p>
        <div v-else class="review-groups">
          <div v-for="group in groupedReviews" :key="group.isbn" class="review-group">
            <article v-for="review in visibleReviewsForGroup(group)" :key="review.id" class="review-card">
              <router-link :to="`/threads/${review.id}`" class="media-card review-link">
                <img :src="review.book.cover_img || placeholder" :alt="review.book.title">
                <div>
                  <strong>{{ review.title }}</strong>
                  <small>{{ review.book.title }}</small>
                </div>
              </router-link>
              <button class="delete-review" type="button" @click="removeReview(review.id)">삭제</button>
            </article>
            <button
              v-if="group.reviews.length > 1"
              class="text-button group-more"
              type="button"
              @click="toggleReviewGroup(group.isbn)"
            >
              {{ isReviewGroupExpanded(group.isbn) ? '접기' : `더보기 (${group.reviews.length - 1}개)` }}
            </button>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>관심 카테고리 기반 추천 도서</h2>
        <p v-if="!keywords.length" class="empty">관심 카테고리를 등록하면 맞춤 도서를 추천해 드립니다.</p>
        <p v-else-if="recommendationsLoading" class="empty">추천 도서를 불러오는 중…</p>
        <p v-else-if="!recommendedBooks.length" class="empty">카테고리에 맞는 추천 도서를 찾지 못했습니다.</p>
        <div v-else class="card-grid">
          <router-link v-for="book in recommendedBooks" :key="book.isbn" :to="`/books/${book.isbn}`" class="media-card">
            <img :src="book.cover_img || placeholder" :alt="book.title">
            <div>
              <span v-if="book.recommendation_category" class="recommendation-category">{{ book.recommendation_category }}</span>
              <strong>{{ book.title }}</strong>
              <small>{{ book.author || '저자 미상' }}</small>
              <small v-if="book.recommendation_reason" class="recommendation-reason">{{ book.recommendation_reason }}</small>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import ToastNotification from '../components/ToastNotification.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user || {})
const profile = ref({ nickname: '', preferred_genres: '' })
const selectedDepth1 = ref('')
const categories = ref([])
const bookmarks = ref([])
const myReviews = ref([])
const recommendedBooks = ref([])
const loading = ref(true)
const recommendationsLoading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const showAllBookmarks = ref(false)
const expandedReviewGroups = ref(new Set())
const toast = ref({ message: '', variant: 'success' })
const placeholder = 'https://via.placeholder.com/55x80?text=Book'

const BOOKMARK_PREVIEW_LIMIT = 3

const parseKeywords = (value) => (
  (value || '')
    .split(/[,，|]+/)
    .map((keyword) => keyword.trim())
    .filter(Boolean)
)

const keywords = computed(() => parseKeywords(profile.value.preferred_genres))
const serializeKeywords = (items) => [...new Set(items)].join(', ')
const depthCategories = computed(() => {
  const seen = new Set()
  return categories.value
    .filter((category) => category.depth1)
    .filter((category) => {
      if (seen.has(category.depth1)) return false
      seen.add(category.depth1)
      return true
    })
    .map((category) => ({ depth1: category.depth1 }))
})
const availableDepthCategories = computed(() => (
  depthCategories.value.filter((category) => !keywords.value.map(categoryLabel).includes(category.depth1))
))

const displayedBookmarks = computed(() => (
  showAllBookmarks.value || bookmarks.value.length < 4
    ? bookmarks.value
    : bookmarks.value.slice(0, BOOKMARK_PREVIEW_LIMIT)
))

const groupedReviews = computed(() => {
  const groups = new Map()
  for (const review of myReviews.value) {
    const isbn = review.book?.isbn || `review-${review.id}`
    if (!groups.has(isbn)) {
      groups.set(isbn, { isbn, reviews: [] })
    }
    groups.get(isbn).reviews.push(review)
  }
  return [...groups.values()]
})

const showToast = (message, variant = 'success') => {
  toast.value = { message: '', variant }
  requestAnimationFrame(() => {
    toast.value = { message, variant }
  })
}

const categoryLabel = (depth1) => {
  const legacyCategory = categories.value.find((item) => String(item.cid) === String(depth1))
  return legacyCategory?.depth1 || depth1
}

const appendKeywords = () => {
  if (!selectedDepth1.value) return
  profile.value.preferred_genres = serializeKeywords([...keywords.value.map(categoryLabel), selectedDepth1.value])
  selectedDepth1.value = ''
}

const persistKeywords = async () => {
  await authStore.updateMe({ nickname: profile.value.nickname, preferred_genres: profile.value.preferred_genres })
  await loadRecommendations()
}

const removeKeyword = async (keyword) => {
  profile.value.preferred_genres = serializeKeywords(keywords.value.filter((item) => item !== keyword))
  try {
    await persistKeywords()
    showToast('관심 키워드를 삭제했습니다.')
  } catch {
    showToast('키워드를 삭제하지 못했습니다.', 'error')
  }
}

const isReviewGroupExpanded = (isbn) => expandedReviewGroups.value.has(isbn)

const toggleReviewGroup = (isbn) => {
  const next = new Set(expandedReviewGroups.value)
  if (next.has(isbn)) next.delete(isbn)
  else next.add(isbn)
  expandedReviewGroups.value = next
}

const visibleReviewsForGroup = (group) => (
  isReviewGroupExpanded(group.isbn) ? group.reviews : [group.reviews[0]]
)

const loadRecommendations = async () => {
  const keywordList = keywords.value
  if (!keywordList.length) { recommendedBooks.value = []; return }
  recommendationsLoading.value = true
  try {
    const { data } = await api.get('/users/me/category-recommendations')
    recommendedBooks.value = Array.isArray(data) ? data : []
  } catch { recommendedBooks.value = [] }
  finally { recommendationsLoading.value = false }
}

const loadCategories = async () => {
  const { data } = await api.get('/categories', { params: { mall_type: 'BOOK' } })
  categories.value = Array.isArray(data) ? data : []
}

const load = async () => {
  loading.value = true
  try {
    await authStore.fetchMe()
    profile.value = { nickname: user.value.nickname || '', preferred_genres: user.value.preferred_genres || '' }
    const [, bookmarkResponse, reviewResponse] = await Promise.all([
      loadCategories(),
      api.get('/users/me/bookmarks'),
      api.get('/threads', { params: { mine: 1 } }),
    ])
    bookmarks.value = bookmarkResponse.data.results || []
    myReviews.value = reviewResponse.data.results || []
    await loadRecommendations()
  } finally { loading.value = false }
}

const updateProfile = async () => {
  saving.value = true
  try {
    appendKeywords()
    await authStore.updateMe(profile.value)
    showToast('프로필을 저장했습니다.')
    await loadRecommendations()
  } catch {
    showToast('저장하지 못했습니다.', 'error')
  } finally { saving.value = false }
}

const withdraw = async () => {
  if (!window.confirm('정말 탈퇴하시겠습니까? 작성한 리뷰, 찜 목록 등 모든 데이터가 삭제됩니다.')) return
  deleting.value = true
  try { await authStore.deleteMe(); router.push({ name: 'Discover' }) }
  catch { showToast('회원 탈퇴에 실패했습니다.', 'error') }
  finally { deleting.value = false }
}

const removeReview = async (reviewId) => {
  if (!window.confirm('도서 리뷰를 삭제할까요?')) return
  await api.delete(`/threads/${reviewId}`)
  myReviews.value = myReviews.value.filter((review) => review.id !== reviewId)
}

onMounted(load)
</script>

<style scoped>
.page { max-width: 1080px; margin: auto; padding: 24px var(--space-margin-mobile) 48px; }
@media (min-width: 768px) { .page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.eyebrow { font: var(--text-label-sm); letter-spacing: var(--ls-label); color: var(--color-primary); text-transform: uppercase; }
.page-header h1 { font: 300 clamp(1.8rem, 5vw, 2.5rem)/1.2 var(--font-headline); letter-spacing: var(--ls-headline); color: var(--color-primary); margin: 6px 0 24px; }

.layout { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }

.panel {
  background: var(--color-surface-container-lowest);
  padding: 24px;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(196, 198, 204, 0.2);
}

.panel h2 { margin: 0 0 16px; font: 400 1.15rem/1.3 var(--font-body); color: var(--color-on-surface); }
.panel h3 { margin: 20px 0 10px; font-size: .92rem; color: var(--color-on-surface-variant); font-weight: 400; }

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.section-title h2 { margin: 0; }

.text-button {
  border: 0;
  background: transparent;
  color: var(--color-primary);
  font-size: 0.84rem;
  font-weight: 400;
  cursor: pointer;
  padding: 4px 0;
  transition: opacity var(--transition-fast);
}

.text-button:hover { opacity: 0.75; }

.profile-card label { display: grid; gap: 7px; margin: 14px 0; color: var(--color-on-surface-variant); font-weight: 300; font-size: 0.88rem; }
.profile-card input,
.profile-card select { border: 1px solid var(--color-outline-variant); border-radius: var(--radius-md); padding: 10px 12px; background: var(--color-surface-container-lowest); }

.form-actions { display: flex; gap: 8px; margin-top: 8px; }

.primary, .secondary, .danger {
  border: 0;
  border-radius: var(--radius-full);
  padding: 10px 16px;
  font-weight: 400;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.primary { background: var(--color-primary); color: var(--color-on-primary); }
.primary:hover { background: var(--color-primary-container); }
.secondary { border: 1px solid var(--color-outline-variant); background: var(--color-surface-container-lowest); color: var(--color-on-surface-variant); }
.secondary:hover { border-color: var(--color-primary); color: var(--color-primary); }
.danger { background: var(--color-error-container); color: var(--color-on-error-container); }
.danger:hover { background: #fecaca; }

.danger-zone { margin-top: 24px; padding-top: 18px; border-top: 1px solid rgba(196, 198, 204, 0.2); }

.keyword-pills { display: flex; flex-wrap: wrap; gap: 8px; }

.keyword-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 6px 8px 6px 14px;
  background: var(--color-surface-container-low);
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  font-size: .88rem;
  font-weight: 400;
  color: var(--color-primary);
}

.keyword-remove {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  border: 0;
  border-radius: 50%;
  background: var(--color-surface-container-lowest);
  color: var(--color-primary);
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.keyword-remove:hover { background: var(--color-primary); color: var(--color-on-primary); }

.card-grid { display: grid; gap: 12px; }

.review-groups { display: grid; gap: 16px; }

.review-group { display: grid; gap: 12px; }

.group-more { justify-self: start; margin-top: -4px; }

.media-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: inherit;
  background: var(--color-surface-container-low);
  transition: all var(--transition-fast);
}

.media-card:hover { border-color: var(--color-outline-variant); }
.media-card img { width: 50px; height: 72px; object-fit: cover; border-radius: var(--radius-sm); flex-shrink: 0; }
.media-card strong, .media-card small { display: block; }
.media-card strong { font-size: .92rem; font-weight: 400; line-height: 1.4; color: var(--color-on-surface); }
.media-card small { color: var(--color-on-surface-variant); margin-top: 5px; font-size: 0.78rem; }

.recommendation-category {
  display: inline-flex;
  width: fit-content;
  margin-bottom: 6px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--color-surface-container-lowest);
  color: var(--color-primary);
  border: 1px solid var(--color-outline-variant);
  font-size: 0.7rem;
  font-weight: 500;
}

.recommendation-reason {
  line-height: 1.35;
}

.review-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-lg);
  background: var(--color-surface-container-low);
}

.review-card .media-card { flex: 1; min-width: 0; padding: 0; border: 0; background: transparent; }

.delete-review {
  flex: 0 0 auto;
  border: 0;
  border-radius: var(--radius-md);
  padding: 6px 10px;
  background: var(--color-error-container);
  color: var(--color-on-error-container);
  font-weight: 400;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.delete-review:hover { background: #fecaca; }

.empty { color: var(--color-on-surface-variant); font-weight: 300; }

@media (max-width: 820px) {
  .layout { grid-template-columns: 1fr; }
  .review-card { flex-direction: column; }
}
</style>
