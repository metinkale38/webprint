<script setup lang="ts">
import { onMounted, ref } from 'vue'

import api from '@/api/client'
import { usePrintersStore } from '@/stores/printers'
import type { User } from '@/types'

const printers = usePrintersStore()
const users = ref<User[]>([])
const scanMessage = ref('')
const error = ref('')

onMounted(() => {
  void printers.fetch()
  void loadUsers()
})

async function loadUsers(): Promise<void> {
  try {
    const { data } = await api.get<User[]>('/users')
    users.value = data
  } catch (reason: any) {
    error.value = reason?.response?.data?.detail ?? 'Nutzer konnten nicht geladen werden.'
  }
}

async function scan(): Promise<void> {
  scanMessage.value = ''
  error.value = ''
  try {
    const found = await printers.scan()
    scanMessage.value = `${found} neue Drucker gefunden.`
  } catch (reason: any) {
    error.value = reason?.response?.data?.detail ?? 'Scan fehlgeschlagen.'
  }
}
</script>

<template>
  <section class="space-y-5">
    <header>
      <h1 class="text-2xl font-bold">Administration</h1>
      <p class="mt-1 text-sm text-slate-500">Drucker und Nutzer verwalten.</p>
    </header>

    <p v-if="error" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{{ error }}</p>

    <section class="card space-y-3">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold">Drucker</h2>
        <button type="button" class="btn-primary px-3 py-2 text-sm" @click="scan">Scannen</button>
      </div>
      <p v-if="scanMessage" class="text-sm text-emerald-700" role="status">{{ scanMessage }}</p>
      <p v-if="printers.items.length === 0" class="text-sm text-slate-500">Keine Drucker eingerichtet.</p>
      <ul v-else class="divide-y divide-slate-100">
        <li v-for="printer in printers.items" :key="printer.id" class="flex items-center justify-between gap-3 py-2">
          <div class="min-w-0">
            <p class="truncate font-medium">{{ printer.name }}</p>
            <p class="truncate text-xs text-slate-500">{{ printer.device_uri }}</p>
          </div>
          <span class="text-xs text-slate-500">{{ printer.status }}</span>
        </li>
      </ul>
    </section>

    <section class="card space-y-3">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold">Nutzer</h2>
        <button type="button" class="text-sm font-medium text-brand-600" @click="loadUsers">Aktualisieren</button>
      </div>
      <p v-if="users.length === 0" class="text-sm text-slate-500">Keine Nutzer gefunden.</p>
      <ul v-else class="divide-y divide-slate-100">
        <li v-for="user in users" :key="user.id" class="flex items-center justify-between gap-3 py-2">
          <div>
            <p class="font-medium">{{ user.display_name || user.username }}</p>
            <p class="text-xs text-slate-500">@{{ user.username }}</p>
          </div>
          <span class="rounded-full px-2 py-1 text-xs font-medium" :class="user.role === 'admin' ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-600'">
            {{ user.role === 'admin' ? 'Admin' : 'Nutzer' }}
          </span>
        </li>
      </ul>
    </section>

    <RouterLink to="/stats" class="card block text-center font-medium text-brand-700">
      Zur Statistik
    </RouterLink>
  </section>
</template>
