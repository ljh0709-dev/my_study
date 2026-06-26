import { defineStore } from 'pinia'
import api from '../api/axios'

const STORAGE_KEY = 'trendbook_auth_state'

const emptyAuthState = () => ({
  accessToken: null,
  refreshToken: null,
  user: null,
})

export const useAuthStore = defineStore('auth', {
  state: emptyAuthState,

  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken || state.refreshToken),
  },

  actions: {
    initialize() {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return

      try {
        const data = JSON.parse(raw)
        this.accessToken = data.accessToken || null
        this.refreshToken = data.refreshToken || null
        this.user = data.user || null
      } catch (error) {
        console.error('인증 상태를 복원하지 못했습니다.', error)
        this.logout()
      }
    },

    persist() {
      if (!this.accessToken && !this.refreshToken) {
        localStorage.removeItem(STORAGE_KEY)
        return
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        accessToken: this.accessToken,
        refreshToken: this.refreshToken,
        user: this.user,
      }))
    },

    updateTokens({ access, refresh }) {
      this.accessToken = access || null
      this.refreshToken = refresh || null
      this.persist()
    },

    async login(credentials) {
      const { data } = await api.post('/auth/login', credentials)
      this.accessToken = data.access
      this.refreshToken = data.refresh
      this.user = data.user
      this.persist()
      return this.user
    },

    async signup(userData) {
      const { data } = await api.post('/auth/register', userData)
      return data
    },

    async fetchMe() {
      const { data } = await api.get('/users/me')
      this.user = data
      this.persist()
      return this.user
    },

    async updateMe(profile) {
      const { data } = await api.patch('/users/me', profile)
      this.user = data
      this.persist()
      return this.user
    },

    async deleteMe() {
      await api.delete('/users/me')
      this.logout()
    },

    logout() {
      Object.assign(this, emptyAuthState())
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
