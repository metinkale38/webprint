import { expect, test } from '@playwright/test'

const admin = {
  id: 1,
  username: 'admin',
  display_name: 'Administrator',
  role: 'admin',
  active: true,
}

const printers = [
  {
    id: 1,
    name: 'Testdrucker',
    slug: 'testdrucker',
    device_uri: 'ipp://192.0.2.10/ipp/print',
    protocol: 'ipp',
    model: 'PDF-Drucker',
    location: 'Erdgeschoss',
    driver_mode: 'everywhere',
    auto_discovered: false,
    enabled: true,
    status: 'idle',
    capabilities: {},
  },
]

test.beforeEach(async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: admin }))
  await page.route('**/api/printers', (route) => route.fulfill({ json: printers }))
  await page.route('**/api/jobs', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 201,
        json: {
          id: 42,
          user_id: 1,
          printer_id: 1,
          filename: 'test.pdf',
          options: {},
          pages: 1,
          copies: 1,
          color_mode: 'monochrome',
          duplex: 'one-sided',
          status: 'queued',
          created_at: new Date().toISOString(),
        },
      })
      return
    }
    await route.fulfill({ json: [] })
  })
})

test('Druckauftrag über die UI erstellen', async ({ page }) => {
  await page.goto('/print')

  await expect(page.getByRole('heading', { name: 'Drucken' })).toBeVisible()
  await page.getByRole('button', { name: /Testdrucker/ }).click()
  await page.setInputFiles('input[type="file"]', {
    name: 'test.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4\n%%EOF'),
  })
  await page.getByRole('button', { name: 'Druckauftrag senden' }).click()

  await expect(page.getByText('Auftrag #42 wurde erstellt.')).toBeVisible()
})
