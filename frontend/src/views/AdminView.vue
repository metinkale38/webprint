<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import api from '@/api/client'
import { apiErrorMessage } from '@/api/errors'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import { usePrintersStore } from '@/stores/printers'
import type { PrintJob, Printer, User } from '@/types'

type Tab = 'printers' | 'users' | 'jobs'

const tabs: { id: Tab; label: string }[] = [
  { id: 'printers', label: 'Drucker' },
  { id: 'users', label: 'Nutzer' },
  { id: 'jobs', label: 'Aufträge' },
]

const printers = usePrintersStore()
const tab = ref<Tab>('printers')
const users = ref<User[]>([])
const jobs = ref<PrintJob[]>([])
const error = ref('')
const message = ref('')
const busy = ref(false)

const showPrinterForm = ref(false)
const editingPrinterId = ref<number | null>(null)
const printerForm = reactive({
  name: '',
  device_uri: '',
  protocol: 'ipp',
  location: '',
  model: '',
  driver_mode: 'everywhere',
  enabled: true,
})

const showUserForm = ref(false)
const editingUserId = ref<number | null>(null)
const userForm = reactive({
  username: '',
  password: '',
  display_name: '',
  role: 'user' as 'admin' | 'user',
  active: true,
})

onMounted(() => {
  void loadAll()
})

async function loadAll(): Promise<void> {
  await Promise.all([printers.fetch(), loadUsers(), loadJobs()])
}

function resetMessages(): void {
  error.value = ''
  message.value = ''
}

async function loadUsers(): Promise<void> {
  try {
    const { data } = await api.get<User[]>('/users')
    users.value = data
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Nutzer konnten nicht geladen werden.')
  }
}

async function loadJobs(): Promise<void> {
  try {
    const { data } = await api.get<PrintJob[]>('/jobs', { params: { all_jobs: true } })
    jobs.value = data
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Aufträge konnten nicht geladen werden.')
  }
}

async function scan(): Promise<void> {
  resetMessages()
  busy.value = true
  try {
    const { data } = await api.post<{ printers: unknown[]; created: number; updated: number }>(
      '/printers/scan',
    )
    await printers.fetch()
    message.value = `${data.printers.length} gefunden, ${data.created} neu, ${data.updated} aktualisiert.`
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Scan fehlgeschlagen.')
  } finally {
    busy.value = false
  }
}

async function refreshStatuses(): Promise<void> {
  resetMessages()
  busy.value = true
  try {
    const { data } = await api.post<{ updated: number }>('/printers/refresh')
    await printers.fetch()
    message.value = `${data.updated} Druckerstatus aktualisiert.`
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Statusaktualisierung fehlgeschlagen.')
  } finally {
    busy.value = false
  }
}

function newPrinter(): void {
  resetMessages()
  editingPrinterId.value = null
  Object.assign(printerForm, {
    name: '',
    device_uri: '',
    protocol: 'ipp',
    location: '',
    model: '',
    driver_mode: 'everywhere',
    enabled: true,
  })
  showPrinterForm.value = true
}

function editPrinter(printer: Printer): void {
  resetMessages()
  editingPrinterId.value = printer.id
  Object.assign(printerForm, {
    name: printer.name,
    device_uri: printer.device_uri,
    protocol: printer.protocol,
    location: printer.location,
    model: printer.model,
    driver_mode: printer.driver_mode,
    enabled: printer.enabled,
  })
  showPrinterForm.value = true
}

async function savePrinter(): Promise<void> {
  resetMessages()
  try {
    if (editingPrinterId.value === null) {
      await api.post('/printers', { ...printerForm })
      message.value = 'Drucker angelegt.'
    } else {
      await api.patch(`/printers/${editingPrinterId.value}`, { ...printerForm })
      message.value = 'Drucker aktualisiert.'
    }
    showPrinterForm.value = false
    await printers.fetch()
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Drucker konnte nicht gespeichert werden.')
  }
}

async function deletePrinter(printer: Printer): Promise<void> {
  if (!window.confirm(`Drucker "${printer.name}" wirklich löschen?`)) {
    return
  }
  resetMessages()
  try {
    await api.delete(`/printers/${printer.id}`)
    await printers.fetch()
    message.value = 'Drucker gelöscht.'
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Drucker konnte nicht gelöscht werden.')
  }
}

function newUser(): void {
  resetMessages()
  editingUserId.value = null
  Object.assign(userForm, {
    username: '',
    password: '',
    display_name: '',
    role: 'user',
    active: true,
  })
  showUserForm.value = true
}

function editUser(user: User): void {
  resetMessages()
  editingUserId.value = user.id
  Object.assign(userForm, {
    username: user.username,
    password: '',
    display_name: user.display_name,
    role: user.role,
    active: user.active,
  })
  showUserForm.value = true
}

async function saveUser(): Promise<void> {
  resetMessages()
  try {
    if (editingUserId.value === null) {
      await api.post('/users', {
        username: userForm.username,
        password: userForm.password,
        display_name: userForm.display_name,
        role: userForm.role,
        active: userForm.active,
      })
      message.value = 'Nutzer angelegt.'
    } else {
      const payload: Record<string, unknown> = {
        display_name: userForm.display_name,
        role: userForm.role,
        active: userForm.active,
      }
      if (userForm.password) {
        payload.password = userForm.password
      }
      await api.patch(`/users/${editingUserId.value}`, payload)
      message.value = 'Nutzer aktualisiert.'
    }
    showUserForm.value = false
    await loadUsers()
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Nutzer konnte nicht gespeichert werden.')
  }
}

async function deleteUser(user: User): Promise<void> {
  if (!window.confirm(`Nutzer "${user.username}" wirklich löschen?`)) {
    return
  }
  resetMessages()
  try {
    await api.delete(`/users/${user.id}`)
    await loadUsers()
    message.value = 'Nutzer gelöscht.'
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Nutzer konnte nicht gelöscht werden.')
  }
}

async function cancelJob(job: PrintJob): Promise<void> {
  if (!window.confirm(`Auftrag "${job.filename}" abbrechen?`)) {
    return
  }
  resetMessages()
  try {
    await api.post(`/jobs/${job.id}/cancel`)
    await loadJobs()
    message.value = 'Auftrag abgebrochen.'
  } catch (reason: any) {
    error.value = apiErrorMessage(reason, 'Auftrag konnte nicht abgebrochen werden.')
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' })
}

function printerStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    idle: 'Bereit',
    printing: 'Druckt',
    disabled: 'Deaktiviert',
    offline: 'Offline',
    unknown: 'Unbekannt',
  }
  return labels[status] ?? status
}
</script>

<template>
  <section class="space-y-5">
    <header>
      <h1 class="text-2xl font-bold">Administration</h1>
      <p class="mt-1 text-sm text-slate-500">Drucker, Nutzer und Aufträge verwalten.</p>
    </header>

    <div class="grid grid-cols-3 gap-1 rounded-xl bg-white p-1 ring-1 ring-slate-200">
      <button
        v-for="item in tabs"
        :key="item.id"
        type="button"
        class="min-h-10 rounded-lg px-3 text-sm font-medium transition"
        :class="tab === item.id ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-50'"
        @click="tab = item.id"
      >
        {{ item.label }}
      </button>
    </div>

    <div aria-live="polite" class="space-y-2">
      <p v-if="message" class="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700" role="status">
        {{ message }}
      </p>
      <p v-if="error" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{{ error }}</p>
    </div>

    <template v-if="tab === 'printers'">
      <div class="flex flex-wrap gap-2">
        <button type="button" class="btn-primary px-3 py-2 text-sm" :disabled="busy" @click="scan">
          Scannen
        </button>
        <button type="button" class="btn-secondary px-3 py-2 text-sm" :disabled="busy" @click="refreshStatuses">
          Status aktualisieren
        </button>
        <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="newPrinter">
          Neuer Drucker
        </button>
      </div>

      <form v-if="showPrinterForm" class="card space-y-3" @submit.prevent="savePrinter">
        <h2 class="font-semibold">{{ editingPrinterId === null ? 'Neuer Drucker' : 'Drucker bearbeiten' }}</h2>
        <label class="block">
          <span class="field-label">Name</span>
          <input v-model="printerForm.name" class="field-input" required />
        </label>
        <label class="block">
          <span class="field-label">Geräte-URI</span>
          <input
            v-model="printerForm.device_uri"
            class="field-input"
            placeholder="ipp://192.168.1.50/ipp/print"
            required
          />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="field-label">Protokoll</span>
            <select v-model="printerForm.protocol" class="field-input">
              <option value="ipp">IPP</option>
              <option value="ipps">IPPS</option>
              <option value="lpd">LPD</option>
              <option value="socket">Socket</option>
              <option value="dnssd">DNS-SD</option>
              <option value="cups-pdf">CUPS-PDF</option>
            </select>
          </label>
          <label class="block">
            <span class="field-label">Treibermodus</span>
            <input v-model="printerForm.driver_mode" class="field-input" />
          </label>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="field-label">Standort</span>
            <input v-model="printerForm.location" class="field-input" />
          </label>
          <label class="block">
            <span class="field-label">Modell</span>
            <input v-model="printerForm.model" class="field-input" />
          </label>
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="printerForm.enabled" type="checkbox" class="h-4 w-4" />
          Aktiv
        </label>
        <div class="flex gap-2">
          <button type="submit" class="btn-primary flex-1 px-3 py-2 text-sm">Speichern</button>
          <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="showPrinterForm = false">
            Abbrechen
          </button>
        </div>
      </form>

      <p v-if="printers.items.length === 0" class="card text-sm text-slate-500">
        Keine Drucker eingerichtet.
      </p>
      <div v-else class="space-y-3">
        <article v-for="printer in printers.items" :key="printer.id" class="card space-y-2">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate font-semibold">{{ printer.name }}</p>
              <p class="truncate text-xs text-slate-500">{{ printer.device_uri }}</p>
              <p class="mt-1 text-xs text-slate-500">
                {{ printer.location || 'Kein Standort' }} · {{ printer.model || 'Kein Modell' }}
              </p>
            </div>
            <span class="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">
              {{ printerStatusLabel(printer.status) }}
            </span>
          </div>
          <div class="flex gap-3 text-sm">
            <button type="button" class="font-medium text-brand-600" @click="editPrinter(printer)">
              Bearbeiten
            </button>
            <button type="button" class="font-medium text-red-600" @click="deletePrinter(printer)">
              Löschen
            </button>
          </div>
        </article>
      </div>
    </template>

    <template v-else-if="tab === 'users'">
      <button type="button" class="btn-primary px-3 py-2 text-sm" @click="newUser">Neuer Nutzer</button>

      <form v-if="showUserForm" class="card space-y-3" @submit.prevent="saveUser">
        <h2 class="font-semibold">{{ editingUserId === null ? 'Neuer Nutzer' : 'Nutzer bearbeiten' }}</h2>
        <label class="block">
          <span class="field-label">Benutzername</span>
          <input
            v-model="userForm.username"
            class="field-input"
            autocapitalize="none"
            :disabled="editingUserId !== null"
            required
          />
        </label>
        <label class="block">
          <span class="field-label">{{ editingUserId === null ? 'Passwort' : 'Neues Passwort (optional)' }}</span>
          <input
            v-model="userForm.password"
            class="field-input"
            type="password"
            autocomplete="new-password"
            :required="editingUserId === null"
          />
        </label>
        <label class="block">
          <span class="field-label">Anzeigename</span>
          <input v-model="userForm.display_name" class="field-input" />
        </label>
        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="field-label">Rolle</span>
            <select v-model="userForm.role" class="field-input">
              <option value="user">Nutzer</option>
              <option value="admin">Admin</option>
            </select>
          </label>
          <label class="flex items-end gap-2 pb-3 text-sm">
            <input v-model="userForm.active" type="checkbox" class="h-4 w-4" />
            Aktiv
          </label>
        </div>
        <div class="flex gap-2">
          <button type="submit" class="btn-primary flex-1 px-3 py-2 text-sm">Speichern</button>
          <button type="button" class="btn-secondary px-3 py-2 text-sm" @click="showUserForm = false">
            Abbrechen
          </button>
        </div>
      </form>

      <p v-if="users.length === 0" class="card text-sm text-slate-500">Keine Nutzer gefunden.</p>
      <div v-else class="space-y-3">
        <article v-for="user in users" :key="user.id" class="card flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="truncate font-semibold">{{ user.display_name || user.username }}</p>
            <p class="truncate text-xs text-slate-500">@{{ user.username }} · {{ user.role === 'admin' ? 'Admin' : 'Nutzer' }}</p>
          </div>
          <div class="flex shrink-0 gap-3 text-sm">
            <button type="button" class="font-medium text-brand-600" @click="editUser(user)">Bearbeiten</button>
            <button type="button" class="font-medium text-red-600" @click="deleteUser(user)">Löschen</button>
          </div>
        </article>
      </div>
    </template>

    <template v-else>
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold">Alle Aufträge</h2>
        <button type="button" class="text-sm font-medium text-brand-600" @click="loadJobs">Aktualisieren</button>
      </div>

      <p v-if="jobs.length === 0" class="card text-sm text-slate-500">Noch keine Aufträge vorhanden.</p>
      <div v-else class="space-y-3">
        <article v-for="job in jobs" :key="job.id" class="card space-y-2">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate font-semibold">{{ job.filename }}</p>
              <p class="mt-0.5 text-xs text-slate-500">
                {{ job.user_name }} · {{ job.printer_name }} · {{ formatDate(job.created_at) }}
              </p>
            </div>
            <JobStatusBadge :status="job.status" />
          </div>
          <div class="flex items-center justify-between text-xs text-slate-500">
            <span>{{ job.pages }} Seite{{ job.pages === 1 ? '' : 'n' }} · {{ job.copies }} Kopie{{ job.copies === 1 ? '' : 'n' }}</span>
            <button
              v-if="['queued', 'processing'].includes(job.status)"
              type="button"
              class="font-medium text-red-600"
              @click="cancelJob(job)"
            >
              Abbrechen
            </button>
          </div>
        </article>
      </div>
    </template>

    <RouterLink to="/stats" class="card block text-center font-medium text-brand-700">
      Zur Statistik
    </RouterLink>
  </section>
</template>
