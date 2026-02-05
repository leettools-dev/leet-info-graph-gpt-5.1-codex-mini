import { defineStore } from 'pinia'

import {
  createSession as apiCreateSession,
  deleteSession as apiDeleteSession,
  listSessions as apiListSessions,
} from '@/api/session'

export const useSessionStore = defineStore('session', {
  state: () => ({
    sessions: [],
    loading: false,
    error: null,
  }),
  getters: {
    hasSessions: (state) => state.sessions.length > 0,
  },
  actions: {
    async fetchSessions() {
      if (this.loading) return
      this.loading = true
      this.error = null
      try {
        const items = await apiListSessions()
        this.sessions = items
      } catch (error) {
        this.error = error
      } finally {
        this.loading = false
      }
    },
    async createSession(prompt) {
      this.error = null
      try {
        const session = await apiCreateSession({ prompt })
        this.sessions.unshift(session)
        return session
      } catch (error) {
        this.error = error
        throw error
      }
    },
    async deleteSession(sessionId) {
      this.error = null
      try {
        await apiDeleteSession(sessionId)
        this.sessions = this.sessions.filter((session) => session.session_id !== sessionId)
      } catch (error) {
        this.error = error
        throw error
      }
    },
    clearSessions() {
      this.sessions = []
    },
  },
})
