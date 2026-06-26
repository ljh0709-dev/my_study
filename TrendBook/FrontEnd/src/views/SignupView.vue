<template>
  <section class="page-shell">
    <div class="auth-card">
      <h1>회원가입</h1>
      <p>이메일과 닉네임으로 TrendBook 계정을 만들어보세요.</p>

      <div v-if="alertMessage" class="alert">{{ alertMessage }}</div>

      <form @submit.prevent="submitSignup">
        <div class="form-field">
          <label for="email">이메일</label>
          <input id="email" v-model="email" type="email" autocomplete="email" required />
        </div>
        <div class="form-field">
          <label for="nickname">닉네임</label>
          <input id="nickname" v-model="nickname" type="text" required />
        </div>
        <div class="form-field">
          <label for="password">비밀번호</label>
          <input id="password" v-model="password" type="password" autocomplete="new-password" required />
        </div>
        <div class="form-field">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input id="passwordConfirm" v-model="passwordConfirm" type="password" autocomplete="new-password" required />
        </div>

        <button class="primary" type="submit" :disabled="submitting">
          {{ submitting ? '가입 중...' : '가입하기' }}
        </button>
      </form>

      <p class="text-center footer-text">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const alertMessage = ref('')
const submitting = ref(false)

const submitSignup = async () => {
  alertMessage.value = ''
  if (password.value !== passwordConfirm.value) {
    alertMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  submitting.value = true
  try {
    await authStore.signup({
      email: email.value,
      nickname: nickname.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    router.push({ name: 'Login' })
  } catch (error) {
    const errors = error.response?.data
    const firstMessage = errors && typeof errors === 'object'
      ? Object.values(errors).flat()[0]
      : null
    alertMessage.value = firstMessage || '회원가입에 실패했습니다. 정보를 확인해 주세요.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-shell { display: grid; place-items: center; min-height: 72vh; padding: 24px var(--space-margin-mobile); }

.auth-card {
  width: min(520px, 100%);
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
