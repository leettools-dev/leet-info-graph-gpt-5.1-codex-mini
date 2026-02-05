<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getSession } from '@/api/session'
import { logger } from '@/lib/utils'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()

const sessionId = computed(() => route.params.sessionId)
const session = ref(null)
const loading = ref(true)
const error = ref('')

const displayName = computed(() => user.value?.name ?? 'Researcher')

const fetchSession = async () => {
  loading.value = true
  error.value = ''
  try {
    if (!sessionId.value) {
      throw new Error('Missing session id')
    }
    session.value = await getSession(sessionId.value)
  } catch (err) {
    logger.debug('SessionDetailPage: fetchSession failed', err)
    error.value = err?.message ?? 'Unable to load session'
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'history' })
}

const formattedCreatedAt = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(value))
}

onMounted(() => {
  fetchSession()
})
</script>

<template>
  <div class="p-8 rounded-lg bg-slate-900 shadow-lg max-w-3xl mx-auto space-y-6">
    <header class="space-y-2">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-slate-400">Session for {{ displayName }}</p>
          <h1 class="text-3xl font-semibold">Session Details</h1>
        </div>
        <button class="text-sm text-sky-400 hover:underline" @click="goBack">Back to history</button>
      </div>
      <p v-if="loading" class="text-sm text-slate-400">Loading session...</p>
      <p v-if="error" class="text-sm text-rose-400" role="alert">{{ error }}</p>
    </header>

    <section v-if="!loading && session" class="space-y-4">
      <div class="rounded border border-slate-800 bg-slate-950 p-4 space-y-2">
        <p class="text-sm text-slate-400">Status: {{ session.status }}</p>
        <p class="text-base leading-relaxed">{{ session.prompt }}</p>
        <p class="text-xs text-slate-500">Created {{ formattedCreatedAt(session.created_at) }}</p>
      </div>
      <div class="rounded border border-dashed border-slate-700 p-4 bg-slate-950">
        <h2 class="text-lg font-semibold">Insights</h2>
        <p class="text-sm text-slate-400">
          Source extraction and infographic rendering will appear here once they are implemented.
        </p>
      </div>
    </section>
  </div>
</template>
