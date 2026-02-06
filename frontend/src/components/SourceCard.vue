<template>
  <article class="p-4 rounded border border-slate-800 bg-slate-950 space-y-2">
    <div class="flex items-center justify-between">
      <h3 class="text-base font-semibold text-white">{{ source.title }}</h3>
      <span class="text-xs text-slate-400">{{ confidenceLabel }}</span>
    </div>
    <p class="text-sm text-slate-400">{{ source.snippet }}</p>
    <a
      :href="source.url"
      target="_blank"
      rel="noreferrer"
      class="text-sm text-sky-400 hover:underline"
    >
      Open source ↗
    </a>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  source: {
    type: Object,
    required: true,
  },
})

const confidenceLabel = computed(() => {
  const confidence = props.source?.confidence ?? 0
  return `${Math.round(confidence * 100)}% confidence`
})
</script>

<style scoped>
</style>
