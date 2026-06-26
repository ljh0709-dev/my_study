<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link class="navbar-brand" to="/discover">
        <img :src="logoUrl" alt="TrendBook" class="brand-logo" />
      </router-link>

      <nav class="nav-links">
        <router-link class="nav-link" to="/discover">Discover</router-link>
        <router-link class="nav-link" to="/books">Catalog</router-link>
        <router-link class="nav-link" to="/threads">Reviews</router-link>
      </nav>

      <div class="nav-actions">
        <template v-if="isAuthenticated">
          <router-link class="nav-icon-btn" to="/mypage" title="마이페이지">
            <span class="material-symbols-outlined">account_circle</span>
          </router-link>
          <button class="btn-logout" type="button" @click="logout">로그아웃</button>
        </template>
        <template v-else>
          <router-link class="nav-link" to="/login">로그인</router-link>
          <router-link class="btn-signup" to="/signup">회원가입</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/auth'
import logoUrl from '../assets/Logo.png'

const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

const logout = () => {
  authStore.logout()
  router.push({ name: 'Discover' })
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1020;
  background: rgba(249, 249, 248, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(196, 198, 204, 0.3);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 var(--space-margin-mobile);
  height: 64px;
}

@media (min-width: 768px) {
  .navbar-inner {
    padding: 0 var(--space-margin-desktop);
  }
}

@media (max-width: 640px) {
  .navbar-inner {
    height: auto;
    padding: 10px 16px;
    flex-wrap: wrap;
    row-gap: 6px;
  }

  .navbar-brand {
    order: 1;
  }

  .nav-actions {
    order: 2;
  }
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-logo {
  display: block;
  height: 24px;
  width: auto;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .brand-logo {
    height: 32px;
  }
}

/* Nav links */
.nav-links {
  display: flex;
  gap: 14px;
  align-items: center;
}

@media (min-width: 768px) {
  .nav-links {
    gap: 32px;
  }
}

@media (max-width: 640px) {
  .nav-links {
    order: 3;
    width: 100%;
    justify-content: space-around;
    border-top: 1px solid rgba(196, 198, 204, 0.2);
    padding-top: 4px;
    margin-top: 2px;
  }
}

.nav-link {
  font: 300 13px/1.6 var(--font-body);
  color: rgba(67, 71, 76, 0.7);
  text-decoration: none;
  padding: 14px 0;
  border-bottom: 2px solid transparent;
  transition: color var(--transition-normal), border-color var(--transition-normal);
  white-space: nowrap;
}

@media (min-width: 768px) {
  .nav-link {
    font-size: 16px;
    padding: 20px 0;
  }
}

@media (max-width: 640px) {
  .nav-link {
    padding: 6px 0;
  }
}

.nav-link:hover {
  color: var(--color-primary);
}

.nav-link.router-link-exact-active,
.nav-link.router-link-active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* Actions */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.nav-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-on-surface-variant);
  transition: color var(--transition-fast);
  text-decoration: none;
}

.nav-icon-btn:hover {
  color: var(--color-primary);
}

.btn-logout {
  background: var(--color-surface-container-lowest);
  border: 1px solid var(--color-outline-variant);
  border-radius: var(--radius-full);
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--color-on-surface-variant);
  transition: all var(--transition-fast);
}

@media (min-width: 768px) {
  .btn-logout {
    padding: 6px 14px;
    font-size: 0.82rem;
  }
}

.btn-logout:hover {
  background: var(--color-error-container);
  border-color: var(--color-error-container);
  color: var(--color-on-error-container);
}

.btn-signup {
  display: inline-flex;
  align-items: center;
  background: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: var(--radius-full);
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 400;
  text-decoration: none;
  transition: background var(--transition-fast);
  white-space: nowrap;
}

@media (min-width: 768px) {
  .btn-signup {
    padding: 6px 16px;
    font-size: 0.82rem;
  }
}

.btn-signup:hover {
  background: var(--color-primary-container);
  color: var(--color-on-primary);
}
</style>
