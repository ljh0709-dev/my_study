import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { setupAuthInterceptors } from './api/axios'
import { useAuthStore } from './stores/auth'
import './assets/styles.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

const authStore = useAuthStore(pinia)
authStore.initialize()
setupAuthInterceptors(authStore)

app.use(router)

app.mount('#app')
