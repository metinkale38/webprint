import { expect, test } from '@playwright/test'

const suffix = Date.now().toString(36)

test('Admin richtet Drucker ein, druckt und legt einen Nutzer an', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Benutzername').fill('admin')
  await page.getByLabel('Passwort').fill('e2e-password')
  await page.getByRole('button', { name: 'Anmelden' }).click()
  await expect(page.getByRole('heading', { name: 'Drucken' })).toBeVisible()

  await page.goto('/admin')
  await page.getByRole('button', { name: 'Neuer Drucker' }).click()
  await page.getByLabel('Name').fill(`E2E-Drucker-${suffix}`)
  await page.getByLabel('Geräte-URI').fill('ipp://192.0.2.50/ipp/print')
  await page.getByLabel('Standort').fill('Testraum')
  await page.getByRole('button', { name: 'Speichern' }).click()
  await expect(page.getByText('Drucker angelegt.')).toBeVisible()
  await expect(page.getByText(`E2E-Drucker-${suffix}`)).toBeVisible()

  await page.goto('/print')
  await page.getByRole('button', { name: new RegExp(`E2E-Drucker-${suffix}`) }).click()
  await page.setInputFiles('input[type="file"]', {
    name: 'e2e.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4\n%%EOF\n'),
  })

  await page.getByRole('button', { name: 'Ändern' }).click()
  await page.getByLabel('Kopien').fill('2')
  await page.getByRole('button', { name: 'Fertig' }).click()
  await page.getByRole('button', { name: 'Druckauftrag senden' }).click()
  await expect(page.getByText(/Auftrag #\d+ wurde erstellt/)).toBeVisible()

  await page.getByRole('link', { name: 'Zu meinen Aufträgen' }).click()
  await expect(page.getByRole('heading', { name: 'Meine Aufträge' })).toBeVisible()
  await expect(page.getByText('e2e.pdf')).toBeVisible()
  await expect(page.getByText('Wartet')).toBeVisible()

  await page.goto('/stats')
  await expect(page.getByRole('heading', { name: 'Statistik' })).toBeVisible()
  await expect(page.getByText('Seiten', { exact: true })).toBeVisible()

  await page.goto('/admin')
  await page.getByRole('button', { name: 'Nutzer' }).click()
  await page.getByRole('button', { name: 'Neuer Nutzer' }).click()
  await page.getByLabel('Benutzername').fill(`e2e-user-${suffix}`)
  await page.getByLabel('Passwort').fill('e2e-user-password')
  await page.getByRole('button', { name: 'Speichern' }).click()
  await expect(page.getByText('Nutzer angelegt.')).toBeVisible()
  await expect(page.getByText(`@e2e-user-${suffix}`)).toBeVisible()
})
