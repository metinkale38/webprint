import { expect, test } from '@playwright/test'

import { adminUser, mockGlobalLists, samplePrinters, sampleUsers } from './helpers'

test('Admin-Bereiche zeigen Drucker, Nutzer und Aufträge', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: adminUser }))
  await mockGlobalLists(page)
  await page.route('**/api/printers/scan', (route) =>
    route.fulfill({ json: { printers: [], created: 0, updated: 0 } }),
  )
  await page.route('**/api/printers/refresh', (route) =>
    route.fulfill({ json: { updated: 2 } }),
  )

  await page.goto('/admin')

  await expect(page.getByRole('heading', { name: 'Administration' })).toBeVisible()
  await expect(page.getByText('Büro-Drucker')).toBeVisible()
  await expect(page.getByText('HP LaserJet')).toBeVisible()

  await page.getByRole('button', { name: 'Status aktualisieren' }).click()
  await expect(page.getByText('2 Druckerstatus aktualisiert.')).toBeVisible()

  await page.getByRole('button', { name: 'Neuer Drucker' }).click()
  await expect(page.getByRole('heading', { name: 'Neuer Drucker' })).toBeVisible()
  await page.getByLabel('Name').fill('Neuer Testdrucker')
  await page.getByLabel('Geräte-URI').fill('ipp://192.0.2.99/ipp/print')
  await page.getByRole('button', { name: 'Abbrechen' }).click()

  await page.getByRole('button', { name: 'Nutzer' }).click()
  await expect(page.getByText('@max')).toBeVisible()
  await expect(page.getByText('Max Mustermann')).toBeVisible()

  await page.getByRole('button', { name: 'Neuer Nutzer' }).click()
  await expect(page.getByRole('heading', { name: 'Neuer Nutzer' })).toBeVisible()
  await page.getByLabel('Benutzername').fill('neuer-nutzer')
  await page.getByLabel('Passwort').fill('geheim-123')
  await page.getByRole('button', { name: 'Abbrechen' }).click()

  await page.getByRole('button', { name: 'Aufträge' }).click()
  await expect(page.getByText('angebot.pdf')).toBeVisible()
  await expect(page.getByText('max · Büro-Drucker ·')).toBeVisible()
  await expect(page.getByText('Fertig')).toBeVisible()

  const printerCount = samplePrinters.length
  const userCount = sampleUsers.length
  expect(printerCount).toBe(2)
  expect(userCount).toBe(2)
})
