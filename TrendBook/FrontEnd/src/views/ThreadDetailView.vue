<template>
  <section class="page">
    <div v-if="loading" class="panel state">불러오는 중…</div>
    <template v-else-if="thread">
      <router-link to="/threads" class="back">← 도서 리뷰</router-link>

      <router-link :to="`/books/${thread.book.isbn}`" class="panel book-banner">
        <img :src="bookCover" :alt="thread.book.title" @error="usePlaceholder">
        <div class="book-meta">
          <span class="eyebrow">REVIEWED BOOK</span>
          <h2>{{ thread.book.title }}</h2>
          <p class="book-author">{{ thread.book.author || '저자 미상' }}</p>
          <p v-if="thread.book.category_name" class="book-category">{{ thread.book.category_name }}</p>
          <span class="view-book">도서 상세 보기 →</span>
        </div>
      </router-link>

      <article class="panel article">
        <small>{{ thread.author.nickname }} · {{ formatDate(thread.created_at) }}</small>
        <form v-if="isEditing" class="edit-form" @submit.prevent="saveThread">
          <label>
            제목
            <input v-model="editForm.title" maxlength="200" required>
          </label>
          <label>
            내용
            <textarea v-model="editForm.content" rows="8" required></textarea>
          </label>
          <p v-if="editError" class="error">{{ editError }}</p>
          <div class="edit-actions">
            <button class="primary" type="submit" :disabled="editSaving">{{ editSaving ? '저장 중…' : '저장' }}</button>
            <button class="ghost" type="button" :disabled="editSaving" @click="cancelEdit">취소</button>
          </div>
        </form>
        <template v-else>
          <h1>{{ thread.title }}</h1>
          <p>{{ thread.content }}</p>
          <div class="actions">
            <div class="action-left">
              <button v-if="auth.isAuthenticated" class="like" :class="{ active: thread.is_liked }" :disabled="likeSaving" @click="toggleLike">
                {{ thread.is_liked ? '♥ 좋아요 취소' : '♡ 좋아요' }} {{ thread.like_count || 0 }}
              </button>
              <span v-else class="like-count">좋아요 {{ thread.like_count || 0 }}</span>
              <button v-if="thread.is_owner" class="secondary" type="button" @click="startEdit">수정</button>
            </div>
            <button v-if="thread.is_owner" class="danger" type="button" @click="removeThread">삭제</button>
          </div>
        </template>
      </article>
      <section class="panel">
        <h2>댓글 {{ thread.comments.length }}</h2>
        <form v-if="auth.isAuthenticated" @submit.prevent="addComment">
          <textarea v-model="comment" rows="3" required placeholder="생각을 남겨보세요"></textarea>
          <button class="primary">댓글 작성</button>
        </form>
        <p v-else class="login-hint">댓글을 쓰려면 로그인해 주세요.</p>
        <div v-for="item in thread.comments" :key="item.id" class="comment">
          <div>
            <strong>{{ item.author.nickname }}</strong>
            <p>{{ item.content }}</p>
          </div>
          <button v-if="item.is_owner" class="comment-delete" type="button" @click="removeComment(item.id)">삭제</button>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const thread = ref(null)
const loading = ref(true)
const likeSaving = ref(false)
const isEditing = ref(false)
const editSaving = ref(false)
const editError = ref('')
const editForm = ref({ title: '', content: '' })
const comment = ref('')
const placeholder = 'https://via.placeholder.com/120x172?text=Book'
const bookCover = computed(() => thread.value?.book?.cover_img || placeholder)
const usePlaceholder = (event) => { event.target.src = placeholder }
const formatDate = (value) => (
  value
    ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
    : '-'
)

const load = async () => {
  loading.value = true
  try { thread.value = (await api.get(`/threads/${route.params.threadId}`)).data }
  finally { loading.value = false }
}

const toggleLike = async () => {
  if (!thread.value || likeSaving.value) return
  likeSaving.value = true
  try {
    const response = thread.value.is_liked
      ? await api.delete(`/threads/${thread.value.id}/like`)
      : await api.post(`/threads/${thread.value.id}/like`)
    thread.value.like_count = response.data.like_count
    thread.value.is_liked = response.data.is_liked
  } finally { likeSaving.value = false }
}

const startEdit = () => {
  if (!thread.value) return
  editForm.value = {
    title: thread.value.title,
    content: thread.value.content,
  }
  editError.value = ''
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editError.value = ''
}

const saveThread = async () => {
  if (!thread.value || editSaving.value) return
  editSaving.value = true
  editError.value = ''
  try {
    const { data } = await api.patch(`/threads/${thread.value.id}`, editForm.value)
    thread.value = data
    isEditing.value = false
  } catch (e) {
    editError.value = e.response?.data?.detail || '도서 리뷰를 수정하지 못했습니다.'
  } finally {
    editSaving.value = false
  }
}

const addComment = async () => {
  await api.post(`/threads/${thread.value.id}/comments`, { content: comment.value })
  comment.value = ''
  await load()
}

const removeComment = async (id) => { await api.delete(`/comments/${id}`); await load() }

const removeThread = async () => {
  if (confirm('도서 리뷰를 삭제할까요?')) {
    await api.delete(`/threads/${thread.value.id}`)
    router.push('/threads')
  }
}

onMounted(load)
</script>

<style scoped>
.page { max-width: 780px; margin: auto; padding: 24px var(--space-margin-mobile); }
@media (min-width: 768px) { .page { padding-left: var(--space-margin-desktop); padding-right: var(--space-margin-desktop); } }

.page > a.back { text-decoration: none; color: var(--color-on-surface-variant); font-weight: 300; }
.back:hover { color: var(--color-primary); }

.book-banner {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 22px;
  align-items: center;
  text-decoration: none;
  color: inherit;
  transition: border-color var(--transition-fast), box-shadow var(--transition-normal);
}

.book-banner:hover {
  border-color: var(--color-outline-variant);
  box-shadow: var(--shadow-card);
}

.book-banner img {
  width: 120px;
  height: 172px;
  object-fit: cover;
  border-radius: var(--radius-md);
  background: var(--color-surface-container);
  box-shadow: var(--shadow-card);
}

.book-meta { min-width: 0; }

.eyebrow {
  display: block;
  margin: 0 0 8px;
  font: var(--text-label-sm);
  letter-spacing: var(--ls-label);
  color: var(--color-primary);
  text-transform: uppercase;
}

.book-meta h2 {
  margin: 0 0 10px;
  font: 400 clamp(1.2rem, 3vw, 1.5rem)/1.35 var(--font-body);
  color: var(--color-on-surface);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author, .book-category {
  margin: 0 0 6px;
  color: var(--color-on-surface-variant);
  font-weight: 300;
  line-height: 1.5;
}

.view-book {
  display: inline-block;
  margin-top: 10px;
  font-size: .88rem;
  font-weight: 400;
  color: var(--color-primary);
}

.panel {
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  padding: 26px;
  border-radius: var(--radius-xl);
  margin: 18px 0;
}

.article h1 { font: 300 clamp(1.6rem, 4vw, 2.2rem)/1.2 var(--font-headline); letter-spacing: var(--ls-headline); color: var(--color-primary); margin: 12px 0 16px; }
.article > p { white-space: pre-wrap; line-height: 1.9; font-weight: 300; color: var(--color-on-surface-variant); }
.article small { color: var(--color-on-surface-variant); font-weight: 300; }

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  margin-top: 16px;
}

.action-left {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.like, .primary, .secondary, .ghost, .danger {
  border: 0;
  border-radius: var(--radius-full);
  padding: 9px 16px;
  font-weight: 400;
  font-size: 0.88rem;
  transition: all var(--transition-fast);
}

.like { background: var(--color-surface-container-low); color: var(--color-primary); }
.like.active { background: var(--color-error-container); color: var(--color-on-error-container); }
.like:disabled { opacity: .6; cursor: not-allowed; }
.like-count { color: var(--color-on-surface-variant); font-size: .9rem; font-weight: 300; }
.primary { background: var(--color-primary); color: var(--color-on-primary); }
.primary:hover { background: var(--color-primary-container); }
.secondary { background: var(--color-surface-container-low); color: var(--color-on-surface-variant); }
.secondary:hover { color: var(--color-primary); }
.ghost { background: transparent; color: var(--color-on-surface-variant); }
.danger { background: var(--color-error-container); color: var(--color-on-error-container); }

.edit-form {
  display: grid;
  gap: 16px;
  margin-top: 18px;
}

.edit-form label {
  display: grid;
  gap: 8px;
  color: var(--color-on-surface-variant);
  font-weight: 300;
  font-size: 0.88rem;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
}

.edit-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.error { color: var(--color-error); font-size: 0.88rem; margin: 0; }

.panel h2 { font: 400 1.15rem/1.3 var(--font-body); color: var(--color-on-surface); margin: 0 0 16px; }
.login-hint { color: var(--color-on-surface-variant); font-weight: 300; }

.comment {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  border-top: 1px solid rgba(196, 198, 204, 0.2);
  padding: 15px 0;
}

.comment strong { font-weight: 400; color: var(--color-on-surface); }
.comment p { margin: 6px 0; font-weight: 300; color: var(--color-on-surface-variant); }

.comment-delete {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: var(--color-error);
  font-size: .82rem;
  font-weight: 400;
  padding: 4px 2px;
  cursor: pointer;
}

.comment-delete:hover { text-decoration: underline; }

.state { text-align: center; color: var(--color-on-surface-variant); font-weight: 300; }

@media (max-width: 560px) {
  .book-banner { grid-template-columns: 96px minmax(0, 1fr); gap: 16px; }
  .book-banner img { width: 96px; height: 136px; }
}
</style>
