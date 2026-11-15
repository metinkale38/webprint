import type { Page } from '@playwright/test'

export const adminUser = {
  id: 1,
  username: 'admin',
  display_name: 'Administrator',
  role: 'admin',
  active: true,
}

export const regularUser = {
  id: 2,
  username: 'max',
  display_name: 'Max Mustermann',
  role: 'user',
  active: true,
}

export const samplePrinters = [
  {
    id: 1,
    name: 'Büro-Drucker',
    slug: 'buero-drucker',
    device_uri: 'ipp://192.0.2.10/ipp/print',
    protocol: 'ipp',
    model: 'HP LaserJet',
    location: '1. OG',
    driver_mode: 'everywhere',
    auto_discovered: true,
    enabled: true,
    status: 'idle',
    capabilities: {},
  },
  {
    id: 2,
    name: 'Werkstatt',
    slug: 'werkstatt',
    device_uri: 'ipp://192.0.2.11/ipp/print',
    protocol: 'ipp',
    model: 'Brother',
    location: 'EG',
    driver_mode: 'everywhere',
    auto_discovered: true,
    enabled: true,
    status: 'printing',
    capabilities: {},
  },
]

export const sampleUsers = [adminUser, regularUser]

export const sampleJobs = [
  {
    id: 42,
    user_id: 2,
    printer_id: 1,
    user_name: 'max',
    printer_name: 'Büro-Drucker',
    filename: 'angebot.pdf',
    options: {},
    pages: 4,
    copies: 2,
    color_mode: 'monochrome',
    duplex: 'two-sided-long-edge',
    status: 'completed',
    created_at: '2026-11-15T10:30:00Z',
  },
  {
    id: 43,
    user_id: 1,
    printer_id: 2,
    user_name: 'admin',
    printer_name: 'Werkstatt',
    filename: 'plan.png',
    options: {},
    pages: 1,
    copies: 1,
    color_mode: 'color',
    duplex: 'one-sided',
    status: 'processing',
    created_at: '2026-11-15T11:00:00Z',
  },
]

export const sampleStatsOverview = {
  jobs: 12,
  pages: 48,
  copies: 60,
  color_jobs: 3,
  monochrome_jobs: 9,
  printers: 2,
  users: 2,
}

export const sampleUserStats = [
  { label: 'admin', jobs: 5, pages: 20, copies: 25 },
  { label: 'max', jobs: 7, pages: 28, copies: 35 },
]

export const samplePrinterStats = [
  { label: 'Büro-Drucker', jobs: 8, pages: 32, copies: 40 },
  { label: 'Werkstatt', jobs: 4, pages: 16, copies: 20 },
]

export async function mockLoggedOut(page: Page): Promise<void> {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: {} }))
  await page.route('**/api/auth/refresh', (route) => route.fulfill({ status: 401, json: {} }))
}

export async function mockLoggedIn(page: Page, user = adminUser): Promise<void> {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: user }))
}

export async function mockGlobalLists(page: Page): Promise<void> {
  await page.route('**/api/printers', (route) => route.fulfill({ json: samplePrinters }))
  await page.route('**/api/users', (route) => route.fulfill({ json: sampleUsers }))
  await page.route('**/api/jobs**', (route) => route.fulfill({ json: sampleJobs }))
}
