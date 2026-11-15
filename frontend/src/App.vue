<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppBottomNav from '@/components/AppBottomNav.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  if (!auth.initialized) {
    void auth.fetchMe()
  }
})

async function logout(): Promise<void> {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-dvh bg-slate-100 text-slate-900">
    <header
      v-if="auth.isAuthenticated"
      class="mx-auto flex w-full max-w-2xl items-center justify-between gap-3 px-4 pt-4"
    >
      <div class="min-w-0">
        <p class="text-xs font-semibold uppercase tracking-wide text-brand-600">PrintTool</p>
        <p class="truncate text-sm text-slate-500">
          {{ auth.user?.display_name || auth.user?.username }}
        </p>
      </div>
      <button type="button" class="text-sm font-medium text-slate-500 hover:text-slate-800" @click="logout">
        Abmelden
      </button>
    </header>

    <main class="mx-auto w-full max-w-2xl px-4 pb-28 pt-4">
      <RouterView />
    </main>
    <AppBottomNav v-if="auth.isAuthenticated" />
  </div>
</template>
