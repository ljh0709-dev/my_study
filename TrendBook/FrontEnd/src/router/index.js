import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import ProfileView from '../views/ProfileView.vue'
import BookListView from '../views/BookListView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import BookReviewsView from '../views/BookReviewsView.vue'
import DiscoverView from '../views/DiscoverView.vue'
import TrendDetailView from '../views/TrendDetailView.vue'

import ThreadListView from '../views/ThreadListView.vue'
import ThreadFormView from '../views/ThreadFormView.vue'
import ThreadDetailView from '../views/ThreadDetailView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: { name: 'Discover' },
    },
    {
      path: '/discover',
      name: 'Discover',
      component: DiscoverView,
    },
    {
      path: '/discover/:trendId',
      name: 'TrendDetail',
      component: TrendDetailView,
      props: true,
    },
    {
      path: '/bestsellers',
      redirect: { name: 'BookList', query: { section: 'bestseller' } },
    },
    {
      path: '/books',
      name: 'BookList',
      component: BookListView,
    },
    {
      path: '/books/:bookId/reviews',
      name: 'BookReviews',
      component: BookReviewsView,
      props: true,
    },
    {
      path: '/books/:bookId',
      name: 'BookDetail',
      component: BookDetailView,
      props: true,
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: '/signup',
      name: 'Signup',
      component: SignupView,
      meta: { guestOnly: true },
    },
    {
      path: '/mypage',
      alias: ['/profile', '/manage'],
      name: 'Profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/threads',
      name: 'Threads',
      component: ThreadListView,
    },
    {
      path: '/threads/new',
      name: 'ThreadCreate',
      component: ThreadFormView,
      meta: { requiresAuth: true },
    },
    {
      path: '/threads/:threadId',
      name: 'ThreadDetail',
      component: ThreadDetailView,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/discover',
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: 'Discover' }
  }
})

export default router
