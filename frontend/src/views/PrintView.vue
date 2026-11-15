<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import OptionsSheet from '@/components/OptionsSheet.vue'
import PrinterCard from '@/components/PrinterCard.vue'
import { useJobsStore } from '@/stores/jobs'
import { usePrintersStore } from '@/stores/printers'
import type { PrintOptions } from '@/types'

const printers = usePrintersStore()
const jobs = useJobsStore()

const file = ref<File | null>(null)
const selectedPrinterId = ref<number | null>(null)
const showOptions = ref(false)
const submitting = ref(false)
const message = ref('')
const error = ref('')

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

const canSubmit = computed(() => file.value !== null && selectedPrinter.value !== null && !submitting.value)

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

function onFile(event: Event): void {
  const target = event.target as HTMLInputElement
  file.value = target.files?.[0] ?? null
  message.value = ''
  error.value = ''
}

async function submit(): Promise<void> {
  if (!file.value || !selectedPrinter.value) return
  submitting.value = true
  message.value = ''
  error.value = ''
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
    message.value = `Auftrag #${job.id} wurde erstellt.`
    file.value = null
    const input = document.querySelector<HTMLInputElement>('input[type="file"]')
    if (input) input.value = ''
  } catch (reason: any) {
    error.value = reason?.response?.data?.detail ?? 'Auftrag konnte nicht erstellt werden.'
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

    <label class="card block cursor-pointer">
      <span class="field-label">Datei</span>
      <input
        class="block w-full text-sm"
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
        @change="onFile"
      />
      <p class="mt-2 text-xs text-slate-500">PDF, JPG oder PNG · max. 50 MB</p>
      <p v-if="file" class="mt-2 truncate text-sm font-medium text-brand-700">{{ file.name }}</p>
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
      <p v-else-if="printers.items.length === 0" class="card text-sm text-slate-500">
        Noch keine Drucker eingerichtet. Ein Admin kann Drucker hinzufügen oder scannen.
      </p>
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
        <div>
          <h2 class="font-semibold">Optionen</h2>
          <p class="mt-1 text-sm text-slate-500">{{ summary }}</p>
        </div>
        <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="showOptions = true">
          Ändern
        </button>
      </div>
    </section>

    <p v-if="message" class="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700" role="status">
      {{ message }}
    </p>
    <p v-if="error" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{{ error }}</p>

    <button class="btn-primary w-full" type="button" :disabled="!canSubmit" @click="submit">
      {{ submitting ? 'Wird gesendet…' : 'Druckauftrag senden' }}
    </button>

    <OptionsSheet v-model="showOptions" v-model:options="options" />
  </section>
</template>
