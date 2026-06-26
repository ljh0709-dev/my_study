<template>
  <section class="page-shell">
    <div class="auth-card">
      <h1>로그인</h1>
      <p>TrendBook에 로그인하고 추천 서비스를 시작하세요.</p>

      <div v-if="alertMessage" class="alert">{{ alertMessage }}</div>

      <form @submit.prevent="submitLogin">
        <div class="form-field">
          <label for="email">이메일</label>
          <input id="email" v-model="email" type="email" autocomplete="email" required />
        </div>

        <div class="form-field">
          <label for="password">비밀번호</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" required />
        </div>

        <button class="primary" type="submit" :disabled="submitting">
          {{ submitting ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <p class="text-center footer-text">
        아직 계정이 없으신가요?
        <router-link to="/signup">회원가입</router-link>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const alertMessage = ref('')
const submitting = ref(false)

const submitLogin = async () => {
  alertMessage.value = ''
  submitting.value = true
  try {
    await authStore.login({ email: email.value, password: password.value })
    await router.push(typeof route.query.redirect === 'string' ? route.query.redirect : { name: 'Discover' })
  } catch (error) {
    alertMessage.value = error.response?.data?.detail
      || '로그인에 실패했습니다. 이메일과 비밀번호를 확인해 주세요.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-shell { display: grid; place-items: center; min-height: 72vh; padding: 24px var(--space-margin-mobile); }

.auth-card {
  width: min(480px, 100%);
  background: var(--color-surface-container-lowest);
  border: 1px solid rgba(196, 198, 204, 0.2);
  border-radius: var(--radius-xl);
  padding: 36px;
}

.auth-card h1 {
  font: 300 2rem/1.2 var(--font-headline);
  letter-spacing: var(--ls-headline);
  color: var(--color-primary);
  margin: 0 0 8px;
}

.auth-card > p { color: var(--color-on-surface-variant); font-weight: 300; margin: 0 0 24px; }

.footer-text { margin-top: 20px; font-size: 0.88rem; color: var(--color-on-surface-variant); }
.footer-text a { color: var(--color-primary); text-decoration: underline; text-underline-offset: 3px; }

button:disabled { cursor: wait; opacity: 0.55; }
</style>
