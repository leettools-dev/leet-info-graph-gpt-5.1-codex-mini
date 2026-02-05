import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    setAuth(payload) {
      this.user = payload.user
      this.token = payload.token
    },
    clearAuth() {
      this.user = null
      this.token = null
    },
  },
})
