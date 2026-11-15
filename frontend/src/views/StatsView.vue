<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import api from '@/api/client'
import { apiErrorMessage } from '@/api/errors'
import type { StatsOverview, StatsRow } from '@/types'

type View = 'users' | 'printers'

const overview = ref<StatsOverview | null>(null)
const userRows = ref<StatsRow[]>([])
const printerRows = ref<StatsRow[]>([])
const view = ref<View>('users')
const startDate = ref('')
const endDate = ref('')
const loading = ref(false)
const error = ref('')

const rows = computed(() => (view.value === 'users' ? userRows.value : printerRows.value))
const maxPages = computed(() => Math.max(1, ...rows.value.map((row) => row.pages)))

onMounted(() => {
  void load()
})

function periodParams(): Record<string, string> {
  const params: Record<string, string> = {}
  if (startDate.value) params.start = startDate.value
  if (endDate.value) params.end = endDate.value
  return params
}

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const config = { params: periodParams() }
    const [overviewResponse, usersResponse, printersResponse] = await Promise.all([
      api.get<StatsOverview>('/stats/overview', config),
      api.get<StatsRow[]>('/stats/users', config),
      api.get<StatsRow[]>('/stats/printers', config),
    ])
    overview.value = overviewResponse.data
    userRows.value = usersResponse.data
    printerRows.value = printersResponse.data
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Statistik konnte nicht geladen werden.')
  } finally {
    loading.value = false
  }
}

function resetPeriod(): void {
  startDate.value = ''
  endDate.value = ''
  void load()
}

function exportCsv(): void {
  const query = new URLSearchParams(periodParams()).toString()
  window.location.assign(`/api/stats/export${query ? `?${query}` : ''}`)
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

    <section class="card space-y-3">
      <h2 class="font-semibold">Zeitraum</h2>
      <div class="grid grid-cols-2 gap-3">
        <label class="block">
          <span class="field-label">Von</span>
          <input v-model="startDate" class="field-input" type="date" />
        </label>
        <label class="block">
          <span class="field-label">Bis</span>
          <input v-model="endDate" class="field-input" type="date" />
        </label>
      </div>
      <div class="flex gap-2">
        <button type="button" class="btn-primary flex-1 px-3 py-2 text-sm" @click="load">Anwenden</button>
        <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="resetPeriod">Zurücksetzen</button>
      </div>
    </section>

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

      <section class="space-y-3">
        <div class="grid grid-cols-2 gap-1 rounded-xl bg-white p-1 ring-1 ring-slate-200">
          <button
            type="button"
            class="min-h-10 rounded-lg px-3 text-sm font-medium transition"
            :class="view === 'users' ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-50'"
            @click="view = 'users'"
          >
            Nach Nutzer
          </button>
          <button
            type="button"
            class="min-h-10 rounded-lg px-3 text-sm font-medium transition"
            :class="view === 'printers' ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-50'"
            @click="view = 'printers'"
          >
            Nach Drucker
          </button>
        </div>

        <p v-if="rows.length === 0" class="card text-sm text-slate-500">Keine Druckdaten im Zeitraum.</p>
        <div v-else class="space-y-3">
          <article v-for="row in rows" :key="row.label" class="card">
            <div class="flex items-center justify-between gap-3 text-sm">
              <span class="min-w-0 truncate font-medium">{{ row.label }}</span>
              <span class="shrink-0 text-slate-500">{{ row.pages }} Seiten · {{ row.jobs }} Aufträge</span>
            </div>
            <div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                class="h-full rounded-full bg-brand-500"
                :style="{ width: `${(row.pages / maxPages) * 100}%` }"
              />
            </div>
          </article>
        </div>
      </section>
    </template>
  </section>
</template>
