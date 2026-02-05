<template>
  <div class="p-8 rounded-lg bg-slate-900 shadow-lg max-w-md mx-auto">
    <h1 class="text-3xl font-semibold mb-4">Login</h1>
    <p class="text-sm text-slate-400">Sign in with Google to continue.</p>

    <div class="mt-8 flex flex-col gap-3">
      <button
        class="btn-primary w-full"
        @click="handleGoogleSignIn"
        aria-label="Sign in with Google"
      >
        <span class="font-medium">Sign in with Google</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { logger } from '@/lib/utils'

const router = useRouter()
const { login } = useAuth()

const handleGoogleSignIn = async () => {
  logger.debug('LoginPage: handleGoogleSignIn')

  try {
    const fakeUser = {
      user_id: 'user-123',
      email: 'user@example.com',
      name: 'Researcher',
      google_id: 'google-123',
      created_at: Date.now(),
      updated_at: Date.now(),
    }

    const fakeToken = 'fake-jwt-token'

    login(fakeUser, fakeToken)
    router.push({ name: 'chat' })
  } catch (error) {
    logger.debug('LoginPage: sign in failed', error)
  }
}
</script>

