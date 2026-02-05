import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import LoginPage from '@/pages/auth/LoginPage.vue'
import ChatPage from '@/pages/chat/ChatPage.vue'
import HistoryPage from '@/pages/history/HistoryPage.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next({ name: 'login' })
  }

  if (to.name === 'login' && isAuthenticated.value) {
    return next({ name: 'chat' })
  }

  return next()
})

export default router
