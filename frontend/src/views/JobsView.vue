<script setup lang="ts">
import { onMounted } from 'vue'

import JobStatusBadge from '@/components/JobStatusBadge.vue'
import { useJobsStore } from '@/stores/jobs'

const jobs = useJobsStore()

onMounted(() => {
  void jobs.fetch()
})

function formatDate(value: string): string {
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
}

async function cancel(id: number): Promise<void> {
  try {
    await jobs.cancel(id)
  } catch {
    // Der Status bleibt in der Liste sichtbar; Details liefert die API.
  }
}
</script>

<template>
  <section class="space-y-5">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Meine Aufträge</h1>
        <p class="mt-1 text-sm text-slate-500">Zuletzt erstellte Druckaufträge.</p>
      </div>
      <button type="button" class="text-sm font-medium text-brand-600" @click="jobs.fetch()">
        Aktualisieren
      </button>
    </header>

    <p v-if="jobs.loading" class="card text-sm text-slate-500">Aufträge werden geladen…</p>
    <p v-else-if="jobs.error" class="card text-sm text-red-700" role="alert">{{ jobs.error }}</p>
    <p v-else-if="jobs.items.length === 0" class="card text-sm text-slate-500">
      Noch keine Aufträge vorhanden.
    </p>

    <div v-else class="space-y-3">
      <article v-for="job in jobs.items" :key="job.id" class="card space-y-2">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-semibold">{{ job.filename }}</p>
            <p class="mt-0.5 text-sm text-slate-500">
              {{ formatDate(job.created_at) }} · {{ job.pages }} Seite{{ job.pages === 1 ? '' : 'n' }} ·
              {{ job.copies }} Kopie{{ job.copies === 1 ? '' : 'n' }}
            </p>
          </div>
          <JobStatusBadge :status="job.status" />
        </div>
        <div class="flex items-center justify-between gap-3 text-sm text-slate-500">
          <span>{{ job.color_mode === 'color' ? 'Farbe' : 'Schwarzweiß' }} · {{ job.duplex === 'one-sided' ? 'einseitig' : 'doppelseitig' }}</span>
          <button
            v-if="['queued', 'processing'].includes(job.status)"
            type="button"
            class="font-medium text-red-600"
            @click="cancel(job.id)"
          >
            Abbrechen
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
