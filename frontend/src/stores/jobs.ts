import { defineStore } from 'pinia'

import api from '@/api/client'
import type { PrintJob } from '@/types'

interface JobsState {
  items: PrintJob[]
  loading: boolean
  error: string
}

export const useJobsStore = defineStore('jobs', {
  state: (): JobsState => ({
    items: [],
    loading: false,
    error: '',
  }),
  actions: {
    async fetch(all = false, silent = false): Promise<void> {
      if (!silent) {
        this.loading = true
      }
      this.error = ''
      try {
        const { data } = await api.get<PrintJob[]>('/jobs', { params: { all_jobs: all } })
        this.items = data
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? 'Aufträge konnten nicht geladen werden'
      } finally {
        this.loading = false
      }
    },
    async submit(form: FormData): Promise<PrintJob> {
      const { data } = await api.post<PrintJob>('/jobs', form)
      this.items.unshift(data)
      return data
    },
    async cancel(id: number): Promise<PrintJob> {
      const { data } = await api.post<PrintJob>(`/jobs/${id}/cancel`)
      const index = this.items.findIndex((job) => job.id === id)
      if (index >= 0) {
        this.items[index] = data
      }
      return data
    },
  },
})
