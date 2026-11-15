import { defineStore } from 'pinia'

import api from '@/api/client'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  initialized: boolean
  loading: boolean
  error: string
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    initialized: false,
    loading: false,
    error: '',
  }),
  getters: {
    isAuthenticated: (state): boolean => state.user !== null,
    isAdmin: (state): boolean => state.user?.role === 'admin',
  },
  actions: {
    async login(username: string, password: string): Promise<boolean> {
      this.loading = true
      this.error = ''
      try {
        const { data } = await api.post<User>('/auth/login', { username, password })
        this.user = data
        this.initialized = true
        return true
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? 'Anmeldung fehlgeschlagen'
        return false
      } finally {
        this.loading = false
      }
    },
    async fetchMe(): Promise<void> {
      try {
        const { data } = await api.get<User>('/auth/me')
        this.user = data
      } catch {
        this.user = null
      } finally {
        this.initialized = true
      }
    },
    async logout(): Promise<void> {
      try {
        await api.post('/auth/logout')
      } finally {
        this.user = null
        this.initialized = true
      }
    },
  },
})
