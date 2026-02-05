import { computed } from 'vue'

import { useAuthStore } from '@/stores/modules/auth'
import { setAuthToken } from '@/utils/request'

const STORAGE_KEYS = {
  token: 'infograph:auth-token',
  user: 'infograph:auth-user',
}

const isBrowser = typeof window !== 'undefined'

const readStoredToken = () => {
  if (!isBrowser) return null
  return window.localStorage.getItem(STORAGE_KEYS.token)
}

const readStoredUser = () => {
  if (!isBrowser) return null
  const raw = window.localStorage.getItem(STORAGE_KEYS.user)
  if (!raw) return null

  try {
    return JSON.parse(raw)
  } catch (error) {
    window.localStorage.removeItem(STORAGE_KEYS.user)
    return null
  }
}

const writeStoredToken = (token) => {
  if (!isBrowser) return
  if (!token) {
    window.localStorage.removeItem(STORAGE_KEYS.token)
    return
  }
  window.localStorage.setItem(STORAGE_KEYS.token, token)
}

const writeStoredUser = (user) => {
  if (!isBrowser) return
  if (!user) {
    window.localStorage.removeItem(STORAGE_KEYS.user)
    return
  }

  window.localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user))
}

let initialized = false

const initializeAuthStore = (store) => {
  if (initialized) return

  const token = readStoredToken()
  if (token) {
    const user = readStoredUser()
    store.setAuth({ user, token })
    setAuthToken(token)
  } else {
    setAuthToken(null)
  }

  initialized = true
}

export const useAuth = () => {
  const store = useAuthStore()
  initializeAuthStore(store)

  const login = (user, token) => {
    store.setAuth({ user, token })
    writeStoredUser(user)
    writeStoredToken(token)
    setAuthToken(token)
  }

  const logout = () => {
    store.clearAuth()
    writeStoredUser(null)
    writeStoredToken(null)
    setAuthToken(null)
  }

  return {
    user: computed(() => store.user),
    token: computed(() => store.token),
    isAuthenticated: computed(() => store.isAuthenticated),
    login,
    logout,
  }
}

export const getStoredToken = () => readStoredToken()
