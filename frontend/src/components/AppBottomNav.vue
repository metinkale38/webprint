<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const items = [
  { to: '/print', label: 'Drucken', admin: false },
  { to: '/jobs', label: 'Aufträge', admin: false },
  { to: '/stats', label: 'Statistik', admin: true },
  { to: '/admin', label: 'Admin', admin: true },
]
</script>

<template>
  <nav
    class="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white/95 backdrop-blur"
    aria-label="Hauptnavigation"
  >
    <div class="mx-auto flex max-w-2xl items-stretch justify-around">
      <template v-for="item in items" :key="item.to">
        <RouterLink
          v-if="!item.admin || auth.isAdmin"
          :to="item.to"
          class="flex min-h-14 flex-1 flex-col items-center justify-center gap-1 text-xs font-medium text-slate-500"
          active-class="text-brand-600"
        >
          <span
            class="h-1.5 w-1.5 rounded-full bg-current transition-opacity"
            :class="$route.path === item.to ? 'opacity-100' : 'opacity-0'"
          />
          {{ item.label }}
        </RouterLink>
      </template>
    </div>
  </nav>
</template>
