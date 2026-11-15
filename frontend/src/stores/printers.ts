import { defineStore } from 'pinia'

import api from '@/api/client'
import type { Printer } from '@/types'

interface PrintersState {
  items: Printer[]
  loading: boolean
  error: string
}

export const usePrintersStore = defineStore('printers', {
  state: (): PrintersState => ({
    items: [],
    loading: false,
    error: '',
  }),
  actions: {
    async fetch(): Promise<void> {
      this.loading = true
      this.error = ''
      try {
        const { data } = await api.get<Printer[]>('/printers')
        this.items = data
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? 'Drucker konnten nicht geladen werden'
      } finally {
        this.loading = false
      }
    },
    async scan(): Promise<number> {
      const { data } = await api.post<{ printers: unknown[] }>('/printers/scan')
      await this.fetch()
      return data.printers.length
    },
  },
})
