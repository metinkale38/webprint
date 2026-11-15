import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { Accept: 'application/json' },
})

const NO_REFRESH = ['/auth/login', '/auth/refresh', '/auth/logout']
let refreshPromise: Promise<void> | null = null

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryableConfig | undefined
    const status = error.response?.status
    const url = config?.url ?? ''
    const skipRefresh = NO_REFRESH.some((path) => url.startsWith(path))

    if (status === 401 && config && !config._retry && !skipRefresh) {
      config._retry = true
      try {
        refreshPromise ??= api
          .post('/auth/refresh')
          .then(() => undefined)
          .finally(() => {
            refreshPromise = null
          })
        await refreshPromise
        return api(config)
      } catch {
        // Sitzung wirklich abgelaufen; unten wird auf den Login umgeleitet.
      }
    }

    if (status === 401 && !skipRefresh && !window.location.pathname.startsWith('/login')) {
      window.location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export default api
