<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { apiErrorMessage } from '@/api/errors'
import OptionsSheet from '@/components/OptionsSheet.vue'
import PrinterCard from '@/components/PrinterCard.vue'
import { useAuthStore } from '@/stores/auth'
import { useJobsStore } from '@/stores/jobs'
import { usePrintersStore } from '@/stores/printers'
import type { PrintOptions } from '@/types'

const MAX_FILE_MB = 50
const allowedTypes = new Set(['application/pdf', 'image/jpeg', 'image/png'])
const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png']

const auth = useAuthStore()
const printers = usePrintersStore()
const jobs = useJobsStore()

const file = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const fileError = ref('')
const selectedPrinterId = ref<number | null>(null)
const showOptions = ref(false)
const submitting = ref(false)
const message = ref('')
const error = ref('')
const createdJobId = ref<number | null>(null)

const options = ref<PrintOptions>({
  copies: 1,
  duplex: 'one-sided',
  nup: 1,
  color_mode: 'monochrome',
  page_range: '',
  media: 'A4',
})

const selectedPrinter = computed(
  () => printers.items.find((printer) => printer.id === selectedPrinterId.value) ?? null,
)

const canSubmit = computed(
  () => file.value !== null && selectedPrinter.value !== null && !submitting.value && !fileError.value,
)

const fileSize = computed(() => {
  if (!file.value) return ''
  const kilobytes = file.value.size / 1024
  return kilobytes < 1024
    ? `${Math.round(kilobytes)} KB`
    : `${(kilobytes / 1024).toFixed(1)} MB`
})

const summary = computed(() => {
  const parts = [
    `${options.value.copies} Kopie${options.value.copies === 1 ? '' : 'n'}`,
    options.value.duplex === 'one-sided' ? 'einseitig' : 'doppelseitig',
    `${options.value.nup}-up`,
    options.value.color_mode === 'color' ? 'Farbe' : 'Schwarzweiß',
    options.value.media,
  ]
  if (options.value.page_range.trim()) {
    parts.push(`Seiten ${options.value.page_range.trim()}`)
  }
  return parts.join(' · ')
})

onMounted(() => {
  void printers.fetch()
})

function validateFile(candidate: File): string {
  const name = candidate.name.toLowerCase()
  const typeOk =
    allowedTypes.has(candidate.type) || allowedExtensions.some((extension) => name.endsWith(extension))
  if (!typeOk) {
    return 'Nur PDF, JPG oder PNG erlaubt.'
  }
  if (candidate.size > MAX_FILE_MB * 1024 * 1024) {
    return `Die Datei ist größer als ${MAX_FILE_MB} MB.`
  }
  return ''
}

function onFile(event: Event): void {
  const target = event.target as HTMLInputElement
  const candidate = target.files?.[0] ?? null
  message.value = ''
  error.value = ''
  createdJobId.value = null

  if (candidate === null) {
    file.value = null
    fileError.value = ''
    return
  }

  const validationError = validateFile(candidate)
  if (validationError) {
    file.value = null
    fileError.value = validationError
    target.value = ''
    return
  }

  file.value = candidate
  fileError.value = ''
}

async function submit(): Promise<void> {
  if (!file.value || !selectedPrinter.value) return
  submitting.value = true
  message.value = ''
  error.value = ''
  createdJobId.value = null
  try {
    const form = new FormData()
    form.append('file', file.value)
    form.append('printer_id', String(selectedPrinter.value.id))
    form.append('copies', String(options.value.copies))
    form.append('duplex', options.value.duplex)
    form.append('nup', String(options.value.nup))
    form.append('color_mode', options.value.color_mode)
    form.append('page_range', options.value.page_range)
    form.append('media', options.value.media)

    const job = await jobs.submit(form)
    createdJobId.value = job.id
    message.value = `Auftrag #${job.id} wurde erstellt.`
    file.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Auftrag konnte nicht erstellt werden.')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="space-y-5">
    <header>
      <h1 class="text-2xl font-bold">Drucken</h1>
      <p class="mt-1 text-sm text-slate-500">Datei wählen, Drucker aussuchen, Optionen prüfen.</p>
    </header>

    <label class="card block cursor-pointer border-2 border-dashed border-slate-200">
      <span class="field-label">Datei</span>
      <span class="btn-secondary w-full">Datei auswählen</span>
      <input
        ref="fileInput"
        class="sr-only"
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
        @change="onFile"
      />
      <p class="mt-2 text-xs text-slate-500">PDF, JPG oder PNG · max. {{ MAX_FILE_MB }} MB</p>
      <p v-if="file" class="mt-2 break-all text-sm font-medium text-brand-700">
        {{ file.name }} <span class="font-normal text-slate-500">({{ fileSize }})</span>
      </p>
      <p v-if="fileError" class="mt-2 text-sm text-red-700" role="alert">{{ fileError }}</p>
    </label>

    <section>
      <div class="mb-2 flex items-center justify-between">
        <h2 class="text-lg font-semibold">Drucker</h2>
        <button type="button" class="text-sm font-medium text-brand-600" @click="printers.fetch()">
          Aktualisieren
        </button>
      </div>

      <p v-if="printers.loading" class="card text-sm text-slate-500">Drucker werden geladen…</p>
      <p v-else-if="printers.error" class="card text-sm text-red-700" role="alert">{{ printers.error }}</p>
      <div v-else-if="printers.items.length === 0" class="card space-y-2 text-sm text-slate-500">
        <p>Noch keine Drucker eingerichtet.</p>
        <RouterLink v-if="auth.isAdmin" to="/admin" class="font-medium text-brand-600">
          Als Admin Drucker suchen und hinzufügen
        </RouterLink>
      </div>
      <div v-else class="space-y-3">
        <PrinterCard
          v-for="printer in printers.items"
          :key="printer.id"
          :printer="printer"
          :selected="printer.id === selectedPrinterId"
          @select="selectedPrinterId = printer.id"
        />
      </div>
    </section>

    <section class="card">
      <div class="flex items-center justify-between gap-3">
        <div class="min-w-0">
          <h2 class="font-semibold">Optionen</h2>
          <p class="mt-1 text-sm text-slate-500">{{ summary }}</p>
          <p class="mt-1 text-xs text-slate-500">
            {{ selectedPrinter ? selectedPrinter.name : 'Kein Drucker gewählt' }}
          </p>
        </div>
        <button type="button" class="btn-secondary shrink-0 px-3 py-2 text-sm" @click="showOptions = true">
          Ändern
        </button>
      </div>
    </section>

    <div aria-live="polite" class="space-y-2">
      <p v-if="message" class="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700" role="status">
        {{ message }}
        <RouterLink v-if="createdJobId" to="/jobs" class="ml-1 font-semibold underline">
          Zu meinen Aufträgen
        </RouterLink>
      </p>
      <p v-if="error" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{{ error }}</p>
    </div>

    <button class="btn-primary w-full" type="button" :disabled="!canSubmit" @click="submit">
      {{ submitting ? 'Wird gesendet…' : 'Druckauftrag senden' }}
    </button>

    <p class="text-center text-xs text-slate-500">
      Der Auftrag wird deinem angemeldeten Konto zugeordnet.
    </p>

    <OptionsSheet v-model="showOptions" v-model:options="options" />
  </section>
</template>
