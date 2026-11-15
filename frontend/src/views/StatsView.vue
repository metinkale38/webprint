<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import api from '@/api/client'
import { apiErrorMessage } from '@/api/errors'
import type { StatsOverview, StatsRow } from '@/types'

const overview = ref<StatsOverview | null>(null)
const rows = ref<StatsRow[]>([])
const loading = ref(false)
const error = ref('')

const maxPages = computed(() => Math.max(1, ...rows.value.map((row) => row.pages)))

onMounted(() => {
  void load()
})

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const [overviewResponse, usersResponse] = await Promise.all([
      api.get<StatsOverview>('/stats/overview'),
      api.get<StatsRow[]>('/stats/users'),
    ])
    overview.value = overviewResponse.data
    rows.value = usersResponse.data
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Statistik konnte nicht geladen werden.')
  } finally {
    loading.value = false
  }
}

function exportCsv(): void {
  window.location.assign('/api/stats/export')
}
</script>

<template>
  <section class="space-y-5">
    <header class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold">Statistik</h1>
        <p class="mt-1 text-sm text-slate-500">Druckvolumen pro Nutzer und Drucker.</p>
      </div>
      <button type="button" class="text-sm font-medium text-brand-600" @click="exportCsv">CSV</button>
    </header>

    <p v-if="loading" class="card text-sm text-slate-500">Statistik wird geladen…</p>
    <p v-else-if="error" class="card text-sm text-red-700" role="alert">{{ error }}</p>

    <template v-else-if="overview">
      <div class="grid grid-cols-2 gap-3">
        <div class="card">
          <p class="text-sm text-slate-500">Aufträge</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.jobs }}</p>
        </div>
        <div class="card">
          <p class="text-sm text-slate-500">Seiten</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.pages }}</p>
        </div>
        <div class="card">
          <p class="text-sm text-slate-500">Farbe</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.color_jobs }}</p>
        </div>
        <div class="card">
          <p class="text-sm text-slate-500">Schwarzweiß</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.monochrome_jobs }}</p>
        </div>
        <div class="card">
          <p class="text-sm text-slate-500">Drucker</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.printers }}</p>
        </div>
        <div class="card">
          <p class="text-sm text-slate-500">Nutzer</p>
          <p class="mt-1 text-2xl font-bold">{{ overview.users }}</p>
        </div>
      </div>

      <section>
        <h2 class="mb-2 text-lg font-semibold">Nach Nutzer</h2>
        <p v-if="rows.length === 0" class="card text-sm text-slate-500">Noch keine Druckdaten.</p>
        <div v-else class="space-y-3">
          <article v-for="row in rows" :key="row.label" class="card">
            <div class="flex items-center justify-between text-sm">
              <span class="font-medium">{{ row.label }}</span>
              <span class="text-slate-500">{{ row.pages }} Seiten · {{ row.jobs }} Aufträge</span>
            </div>
            <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div class="h-full rounded-full bg-brand-500" :style="{ width: `${(row.pages / maxPages) * 100}%` }" />
            </div>
          </article>
        </div>
      </section>
    </template>
  </section>
</template>
