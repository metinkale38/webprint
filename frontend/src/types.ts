export interface User {
  id: number
  username: string
  display_name: string
  role: 'admin' | 'user'
  active: boolean
}

export interface Printer {
  id: number
  name: string
  slug: string
  device_uri: string
  protocol: string
  model: string
  location: string
  driver_mode: string
  auto_discovered: boolean
  enabled: boolean
  status: string
  capabilities: Record<string, unknown>
  last_seen?: string | null
}

export interface PrintOptions {
  copies: number
  duplex: 'one-sided' | 'two-sided-long-edge' | 'two-sided-short-edge'
  nup: 1 | 2 | 4 | 6 | 9 | 16
  color_mode: 'color' | 'monochrome'
  page_range: string
  media: string
}

export interface PrintJob {
  id: number
  user_id: number
  printer_id: number
  filename: string
  options: Record<string, unknown>
  pages: number
  copies: number
  color_mode: string
  duplex: string
  status: string
  cups_job_id?: string | null
  error?: string | null
  created_at: string
  started_at?: string | null
  finished_at?: string | null
}

export interface StatsRow {
  label: string
  jobs: number
  pages: number
  copies: number
}

export interface StatsOverview {
  jobs: number
  pages: number
  copies: number
  color_jobs: number
  monochrome_jobs: number
  printers: number
  users: number
}
