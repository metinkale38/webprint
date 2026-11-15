<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')

async function submit(): Promise<void> {
  const success = await auth.login(username.value.trim(), password.value)
  if (success) {
    await router.push({ name: 'print' })
  }
}
</script>

<template>
  <section class="mx-auto mt-8 max-w-md">
    <div class="mb-6 text-center">
      <p class="text-sm font-semibold uppercase tracking-wide text-brand-600">PrintTool</p>
      <h1 class="mt-2 text-3xl font-bold">Anmelden</h1>
      <p class="mt-2 text-sm text-slate-500">Melde dich an, um Dokumente zu drucken.</p>
    </div>

    <form class="card space-y-4" @submit.prevent="submit">
      <label class="block">
        <span class="field-label">Benutzername</span>
        <input
          v-model="username"
          class="field-input"
          autocomplete="username"
          autocapitalize="none"
          required
        />
      </label>

      <label class="block">
        <span class="field-label">Passwort</span>
        <input
          v-model="password"
          class="field-input"
          type="password"
          autocomplete="current-password"
          required
        />
      </label>

      <p v-if="auth.error" class="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
        {{ auth.error }}
      </p>

      <button class="btn-primary w-full" type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Anmelden…' : 'Anmelden' }}
      </button>
    </form>
  </section>
</template>
