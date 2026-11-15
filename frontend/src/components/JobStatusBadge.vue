<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const label = computed(() => {
  const labels: Record<string, string> = {
    queued: 'Wartet',
    processing: 'In Bearbeitung',
    completed: 'Fertig',
    cancelled: 'Abgebrochen',
    failed: 'Fehlgeschlagen',
  }
  return labels[props.status] ?? props.status
})

const classes = computed(() => {
  if (props.status === 'completed') return 'bg-emerald-100 text-emerald-700'
  if (props.status === 'processing') return 'bg-blue-100 text-blue-700'
  if (props.status === 'failed') return 'bg-red-100 text-red-700'
  if (props.status === 'cancelled') return 'bg-slate-200 text-slate-600'
  return 'bg-amber-100 text-amber-700'
})
</script>

<template>
  <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="classes">{{ label }}</span>
</template>
