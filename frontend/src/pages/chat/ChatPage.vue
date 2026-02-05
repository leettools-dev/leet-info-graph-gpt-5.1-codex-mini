<script setup>
import { computed, onMounted, ref } from 'vue'

import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/modules/session'
import { useAuth } from '@/composables/useAuth'
import { logger } from '@/lib/utils'

const sessionStore = useSessionStore()
const prompt = ref('')
const statusMessage = ref('')
const isSubmitting = ref(false)
const router = useRouter()
const { user } = useAuth()

onMounted(() => {
  sessionStore.fetchSessions().catch((error) => {
    logger.debug('ChatPage: fetchSessions failed', error)
  })
})

const handleNewResearch = async () => {
  const trimmed = prompt.value.trim()
  if (!trimmed) {
    statusMessage.value = 'Please enter a prompt to start a new research session.'
    return
  }

  isSubmitting.value = true
  statusMessage.value = 'Creating research session...'

  try {
    const session = await sessionStore.createSession(trimmed)
    statusMessage.value = `Created research session ${session.session_id}`
    prompt.value = ''
    router.push({ name: 'history' })
  } catch (error) {
    logger.debug('ChatPage: createSession failed', error)
    statusMessage.value = 'Unable to create research session. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}

const recentSessions = computed(() => sessionStore.sessions.slice(0, 3))
const isLoadingSessions = computed(() => sessionStore.loading)
const userName = computed(() => user.value?.name ?? 'Researcher')

const feedbackMessage = computed(() => {
  if (statusMessage.value) return statusMessage.value
  if (isLoadingSessions.value) return 'Loading history...'
  return null
})
</script>

<template>
  <div class="p-8 rounded-lg bg-slate-900 shadow-lg max-w-3xl mx-auto space-y-6">
    <div>
      <h1 class="text-3xl font-semibold">Chat</h1>
      <p class="text-sm text-slate-400">Welcome back, {{ userName }}.</p>
    </div>

    <div class="space-y-2">
      <label class="text-sm font-medium" for="prompt-input">New research prompt</label>
      <textarea
        id="prompt-input"
        v-model="prompt"
        rows="4"
        class="w-full rounded border border-slate-700 bg-slate-950 p-3 text-sm focus:ring-2 focus:ring-sky-500"
        placeholder="Describe what you want to explore today"
        aria-label="Research prompt"
      ></textarea>
      <div class="flex items-center justify-between gap-4">
        <button
          class="btn-primary"
          :disabled="isSubmitting"
          @click="handleNewResearch"
          aria-label="Create new research session"
        >
          <span class="font-semibold">New Research</span>
        </button>
        <span class="text-sm text-slate-400" role="status">
          {{ isLoadingSessions ? 'Loading history...' : statusMessage }}
        </span>
      </div>
    </div>

    <section class="space-y-2">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Recent sessions</h2>
        <button class="text-sm text-sky-400 hover:underline" @click="router.push({ name: 'history' })">
          View all
        </button>
      </div>
      <p v-if="!recentSessions.length" class="text-sm text-slate-500">
        You have not created any research sessions yet.
      </p>
      <ul v-else class="space-y-2">
        <li
          v-for="session in recentSessions"
          :key="session.session_id"
          class="rounded border border-slate-800 bg-slate-950 p-4"
        >
          <p class="text-sm text-slate-400">Status: {{ session.status }}</p>
          <p class="text-base font-medium">{{ session.prompt }}</p>
        </li>
      </ul>
    </section>
  </div>
</template>
