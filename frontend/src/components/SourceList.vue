<template>
  <section class="space-y-4">
    <h2 class="text-xl font-semibold text-white">Sources</h2>
    <div v-if="loading" class="text-sm text-slate-400">Loading sources...</div>
    <div v-else-if="!sources.length" class="text-sm text-slate-400">No sources yet.</div>
    <div v-else class="space-y-3">
      <SourceCard v-for="source in sources" :key="source.source_id" :source="source" />
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import SourceCard from '@/components/SourceCard.vue'
import { listSources } from '@/api/source'

const props = defineProps({
  sessionId: String,
})

const sources = ref([])
const loading = ref(false)

const loadSources = async () => {
  loading.value = true
  try {
    const data = await listSources(props.sessionId)
    sources.value = data
  } finally {
    loading.value = false
  }
}

loadSources()
</script>
