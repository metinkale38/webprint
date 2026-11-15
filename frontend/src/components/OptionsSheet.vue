<script setup lang="ts">
import type { PrintOptions } from '@/types'

const open = defineModel<boolean>({ required: true })
const options = defineModel<PrintOptions>('options', { required: true })

function update<K extends keyof PrintOptions>(key: K, value: PrintOptions[K]): void {
  options.value = { ...options.value, [key]: value } as PrintOptions
}

function setCopies(event: Event): void {
  update('copies', Math.max(1, Number((event.target as HTMLInputElement).value) || 1))
}

function setDuplex(event: Event): void {
  update('duplex', (event.target as HTMLSelectElement).value as PrintOptions['duplex'])
}

function setNup(event: Event): void {
  update('nup', Number((event.target as HTMLSelectElement).value) as PrintOptions['nup'])
}

function setColorMode(event: Event): void {
  update('color_mode', (event.target as HTMLSelectElement).value as PrintOptions['color_mode'])
}

function setPageRange(event: Event): void {
  update('page_range', (event.target as HTMLInputElement).value)
}

function setMedia(event: Event): void {
  update('media', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-end bg-slate-900/40" @click.self="open = false">
    <section class="safe-bottom max-h-[85dvh] w-full overflow-y-auto rounded-t-3xl bg-white p-4 shadow-xl">
      <div class="mx-auto mb-4 h-1.5 w-12 rounded-full bg-slate-300" />
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold">Druckoptionen</h2>
        <button type="button" class="btn-secondary min-h-9 px-3 py-1.5 text-sm" @click="open = false">
          Fertig
        </button>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <label class="block">
          <span class="field-label">Kopien</span>
          <input
            class="field-input"
            type="number"
            min="1"
            max="99"
            :value="options.copies"
            @input="setCopies"
          />
        </label>

        <label class="block">
          <span class="field-label">Papier</span>
          <select class="field-input" :value="options.media" @change="setMedia">
            <option value="A4">A4</option>
            <option value="A5">A5</option>
            <option value="Letter">Letter</option>
            <option value="Legal">Legal</option>
          </select>
        </label>

        <label class="block">
          <span class="field-label">Doppelseitig</span>
          <select class="field-input" :value="options.duplex" @change="setDuplex">
            <option value="one-sided">Nein</option>
            <option value="two-sided-long-edge">Ja, lange Kante</option>
            <option value="two-sided-short-edge">Ja, kurze Kante</option>
          </select>
        </label>

        <label class="block">
          <span class="field-label">Seiten pro Blatt</span>
          <select class="field-input" :value="options.nup" @change="setNup">
            <option :value="1">1</option>
            <option :value="2">2</option>
            <option :value="4">4</option>
            <option :value="6">6</option>
            <option :value="9">9</option>
            <option :value="16">16</option>
          </select>
        </label>

        <label class="block">
          <span class="field-label">Farbe</span>
          <select class="field-input" :value="options.color_mode" @change="setColorMode">
            <option value="monochrome">Schwarzweiß</option>
            <option value="color">Farbe</option>
          </select>
        </label>

        <label class="block">
          <span class="field-label">Seitenbereich</span>
          <input
            class="field-input"
            type="text"
            inputmode="numeric"
            placeholder="z. B. 1-5,8"
            :value="options.page_range"
            @input="setPageRange"
          />
        </label>
      </div>
    </section>
  </div>
</template>
