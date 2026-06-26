import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

const refreshClient = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

let interceptorsConfigured = false
let refreshPromise = null

const isAuthEndpoint = (url = '') => (
  url.includes('/auth/login')
  || url.includes('/auth/register')
  || url.includes('/auth/token/refresh')
)

export const setupAuthInterceptors = (authStore) => {
  if (interceptorsConfigured) return
  interceptorsConfigured = true

  api.interceptors.request.use((config) => {
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      const shouldRefresh = error.response?.status === 401
        && originalRequest
        && !originalRequest._retry
        && !isAuthEndpoint(originalRequest.url)
        && authStore.refreshToken

      if (!shouldRefresh) {
        return Promise.reject(error)
      }

      originalRequest._retry = true

      try {
        if (!refreshPromise) {
          refreshPromise = refreshClient
            .post('/auth/token/refresh', { refresh: authStore.refreshToken })
            .then(({ data }) => {
              authStore.updateTokens({
                access: data.access,
                refresh: data.refresh || authStore.refreshToken,
              })
              return data.access
            })
            .finally(() => {
              refreshPromise = null
            })
        }

        const accessToken = await refreshPromise
        originalRequest.headers.Authorization = `Bearer ${accessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        authStore.logout()
        return Promise.reject(refreshError)
      }
    },
  )
}

export default api
