<script setup lang="ts">
import type { Printer } from '@/types'

defineProps<{
  printer: Printer
  selected?: boolean
}>()

defineEmits<{
  select: []
}>()

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    idle: 'Bereit',
    printing: 'Druckt',
    disabled: 'Deaktiviert',
    offline: 'Offline',
    unknown: 'Unbekannt',
  }
  return labels[status] ?? status
}

function statusClass(status: string): string {
  if (status === 'idle') return 'bg-emerald-100 text-emerald-700'
  if (status === 'printing') return 'bg-blue-100 text-blue-700'
  if (status === 'offline') return 'bg-slate-200 text-slate-600'
  return 'bg-amber-100 text-amber-700'
}
</script>

<template>
  <button
    type="button"
    class="card w-full text-left transition"
    :class="selected ? 'ring-2 ring-brand-500' : 'hover:ring-slate-300'"
    @click="$emit('select')"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="truncate font-semibold">{{ printer.name }}</p>
        <p class="mt-0.5 truncate text-sm text-slate-500">
          {{ printer.location || printer.model || printer.device_uri }}
        </p>
      </div>
      <span
        class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium"
        :class="statusClass(printer.status)"
      >
        {{ statusLabel(printer.status) }}
      </span>
    </div>
  </button>
</template>
