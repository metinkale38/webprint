<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { apiErrorMessage } from '@/api/errors'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import { useJobsStore } from '@/stores/jobs'

const jobs = useJobsStore()
const actionError = ref('')
let refreshTimer: number | undefined

function hasActiveJobs(): boolean {
  return jobs.items.some((job) => ['queued', 'processing'].includes(job.status))
}

onMounted(() => {
  void jobs.fetch()
  refreshTimer = window.setInterval(() => {
    if (hasActiveJobs()) {
      void jobs.fetch(false, true)
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer !== undefined) {
    window.clearInterval(refreshTimer)
  }
})

function formatDate(value: string): string {
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
}

async function cancel(id: number): Promise<void> {
  if (!window.confirm('Druckauftrag wirklich abbrechen?')) {
    return
  }
  try {
    await jobs.cancel(id)
    actionError.value = ''
  } catch (reason: any) {
    actionError.value = apiErrorMessage(reason, 'Auftrag konnte nicht abgebrochen werden.')
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

    <p v-if="actionError" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
      {{ actionError }}
    </p>

    <p v-if="jobs.loading" class="card text-sm text-slate-500">Aufträge werden geladen…</p>
    <p v-else-if="jobs.error" class="card text-sm text-red-700" role="alert">{{ jobs.error }}</p>
    <div v-else-if="jobs.items.length === 0" class="card space-y-2 text-sm text-slate-500">
      <p>Noch keine Aufträge vorhanden.</p>
      <RouterLink to="/print" class="font-medium text-brand-600">Jetzt etwas drucken</RouterLink>
    </div>

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
