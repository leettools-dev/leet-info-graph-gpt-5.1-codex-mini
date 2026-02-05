<script setup>
import { ref, onMounted } from 'vue'
import { logger } from '@/lib/utils'
import { useRouter } from 'vue-router'

const router = useRouter()
const backendStatus = ref('Checking...')

onMounted(async () => {
  logger.debug('App: script setup')
  const { checkHealth } = await import('@/api/health')
  try {
    await checkHealth()
    backendStatus.value = 'Backend Connected'
  } catch (error) {
    backendStatus.value = 'Backend Unreachable'
  }
})

const navigate = (path) => {
  router.push(path)
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <header class="border-b border-slate-800 p-4 flex items-center justify-between">
      <div class="text-2xl font-semibold">Research Infograph Assistant</div>
      <div class="text-sm">{{ backendStatus }}</div>
    </header>

    <nav class="bg-slate-900 p-4 flex gap-4">
      <button class="btn-primary" @click="navigate('/login')">Login</button>
      <button class="btn-primary" @click="navigate('/chat')">Chat</button>
      <button class="btn-primary" @click="navigate('/history')">History</button>
    </nav>

    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>
