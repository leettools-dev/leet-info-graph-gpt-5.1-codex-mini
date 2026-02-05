<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useSessionStore } from '@/stores/modules/session'
import { useAuth } from '@/composables/useAuth'
import { logger } from '@/lib/utils'

const router = useRouter()
const sessionStore = useSessionStore()
const { user } = useAuth()

const feedback = ref('')
const isDeleting = ref(false)

const sessions = computed(() => sessionStore.sessions)
const isLoading = computed(() => sessionStore.loading)
const hasError = computed(() => Boolean(sessionStore.error))
const errorMessage = computed(() => sessionStore.error?.message ?? '')

const displayName = computed(() => user.value?.name ?? 'Researcher')

const formatTimestamp = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

onMounted(async () => {
  try {
    await sessionStore.fetchSessions()
  } catch (error) {
    logger.debug('HistoryPage: fetchSessions failed', error)
  }
})

const handleViewSession = (sessionId) => {
  router.push({ name: 'sessionDetail', params: { sessionId } })
}

const handleDeleteSession = async (sessionId) => {
  if (isDeleting.value) return
  isDeleting.value = true
  feedback.value = 'Removing session...'
  try {
    await sessionStore.deleteSession(sessionId)
    feedback.value = 'Session removed'
  } catch (error) {
    logger.debug('HistoryPage: deleteSession failed', error)
    feedback.value = 'Unable to remove session. Please try again.'
  } finally {
    isDeleting.value = false
    if (typeof window !== 'undefined') {
      window.setTimeout(() => {
        feedback.value = ''
      }, 2500)
    }
  }
}
</script>

<template>
  <div class="p-8 rounded-lg bg-slate-900 shadow-lg max-w-4xl mx-auto space-y-6">
    <header class="space-y-2">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-slate-400">Sessions for {{ displayName }}</p>
          <h1 class="text-3xl font-semibold">Research History</h1>
        </div>
        <span class="text-xs text-slate-400">{{ sessions.length }} stored</span>
      </div>
      <div v-if="feedback" class="text-sm text-sky-400" role="status">{{ feedback }}</div>
      <div v-if="hasError" class="text-sm text-rose-400" role="alert">{{ errorMessage }}</div>
    </header>

    <section>
      <div v-if="isLoading" class="text-sm text-slate-400">Loading sessions...</div>
      <div v-else-if="!sessions.length" class="space-y-2 text-slate-400">
        <p>No sessions yet.</p>
        <p>Return to the chat page to create a new research prompt.</p>
      </div>
      <ul v-else class="space-y-4">
        <li
          v-for="session in sessions"
          :key="session.session_id"
          class="rounded border border-slate-800 bg-slate-950 p-4 space-y-2"
        >
          <div class="flex items-center justify-between gap-4">
            <div class="space-y-1">
              <p class="text-sm text-slate-400">Status: {{ session.status }}</p>
              <p class="text-base font-medium">{{ session.prompt }}</p>
              <p class="text-xs text-slate-500">Created {{ formatTimestamp(session.created_at) }}</p>
            </div>
            <div class="flex gap-2">
              <button
                class="btn-primary"
                type="button"
                @click="handleViewSession(session.session_id)"
                aria-label="View session details"
              >
                View
              </button>
              <button
                class="btn-primary border-rose-500 text-rose-400"
                type="button"
                :disabled="isDeleting"
                @click="handleDeleteSession(session.session_id)"
                aria-label="Delete session"
              >
                Delete
              </button>
            </div>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>
