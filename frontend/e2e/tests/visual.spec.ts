import { expect, test } from '@playwright/test'

import {
  adminUser,
  mockGlobalLists,
  sampleStatsOverview,
  sampleUserStats,
  samplePrinterStats,
} from './helpers'

test('Login visuell', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: {} }))
  await page.route('**/api/auth/refresh', (route) => route.fulfill({ status: 401, json: {} }))

  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Anmelden' })).toBeVisible()

  await expect(page).toHaveScreenshot('login.png', { fullPage: true })
})

test('Drucken visuell', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: adminUser }))
  await mockGlobalLists(page)

  await page.goto('/print')
  await expect(page.getByRole('heading', { name: 'Drucken' })).toBeVisible()

  await expect(page).toHaveScreenshot('print.png', { fullPage: true })
})

test('Admin visuell', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: adminUser }))
  await mockGlobalLists(page)
  await page.route('**/api/printers/scan', (route) =>
    route.fulfill({ json: { printers: [], created: 0, updated: 0 } }),
  )
  await page.route('**/api/printers/refresh', (route) => route.fulfill({ json: { updated: 2 } }))

  await page.goto('/admin')
  await expect(page.getByRole('heading', { name: 'Administration' })).toBeVisible()

  await expect(page).toHaveScreenshot('admin.png', { fullPage: true })
})

test('Statistik visuell', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: adminUser }))
  await page.route('**/api/stats/overview**', (route) =>
    route.fulfill({ json: sampleStatsOverview }),
  )
  await page.route('**/api/stats/users**', (route) => route.fulfill({ json: sampleUserStats }))
  await page.route('**/api/stats/printers**', (route) =>
    route.fulfill({ json: samplePrinterStats }),
  )

  await page.goto('/stats')
  await expect(page.getByRole('heading', { name: 'Statistik' })).toBeVisible()

  await expect(page).toHaveScreenshot('stats.png', { fullPage: true })
})
