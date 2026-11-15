import { expect, test } from '@playwright/test'

import {
  adminUser,
  samplePrinterStats,
  sampleStatsOverview,
  sampleUserStats,
} from './helpers'

test('Statistik zeigt Nutzer-/Druckeransicht und Zeitraumfilter', async ({ page }) => {
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
  await expect(page.getByText('48')).toBeVisible()
  await expect(page.getByText('admin', { exact: true })).toBeVisible()
  await expect(page.getByText('max', { exact: true })).toBeVisible()

  await page.getByRole('button', { name: 'Nach Drucker' }).click()
  await expect(page.getByText('Büro-Drucker')).toBeVisible()
  await expect(page.getByText('Werkstatt')).toBeVisible()

  await page.getByLabel('Von').fill('2026-11-01')
  await page.getByLabel('Bis').fill('2026-11-30')
  await page.getByRole('button', { name: 'Anwenden' }).click()

  await expect(page.getByText('Büro-Drucker')).toBeVisible()
  await page.getByRole('button', { name: 'Zurücksetzen' }).click()
  await expect(page.getByRole('heading', { name: 'Statistik' })).toBeVisible()
})
