import { expect, test } from '@playwright/test'

import { adminUser, sampleJobs, samplePrinters } from './helpers'

test('Druckauftrag mit Optionen über die UI erstellen', async ({ page }) => {
  let postedBody = ''

  await page.route('**/api/auth/me', (route) => route.fulfill({ json: adminUser }))
  await page.route('**/api/printers', (route) => route.fulfill({ json: samplePrinters }))
  await page.route('**/api/jobs**', async (route) => {
    if (route.request().method() === 'POST') {
      postedBody = route.request().postDataBuffer()?.toString('utf8') ?? ''
      await route.fulfill({ status: 201, json: sampleJobs[0] })
      return
    }
    await route.fulfill({ json: sampleJobs })
  })

  await page.goto('/print')

  await expect(page.getByRole('heading', { name: 'Drucken' })).toBeVisible()
  await page.getByRole('button', { name: /Büro-Drucker/ }).click()
  await page.setInputFiles('input[type="file"]', {
    name: 'test.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4\n%%EOF'),
  })

  await page.getByRole('button', { name: 'Ändern' }).click()
  await page.getByLabel('Kopien').fill('3')
  await page.getByLabel('Doppelseitig').selectOption('two-sided-long-edge')
  await page.getByRole('button', { name: 'Fertig' }).click()

  await page.getByRole('button', { name: 'Druckauftrag senden' }).click()

  await expect(page.getByText('Auftrag #42 wurde erstellt.')).toBeVisible()
  expect(postedBody).toMatch(/name="copies"\r\n\r\n3/)
  expect(postedBody).toMatch(/name="duplex"\r\n\r\ntwo-sided-long-edge/)

  await page.getByRole('link', { name: 'Zu meinen Aufträgen' }).click()
  await expect(page.getByRole('heading', { name: 'Meine Aufträge' })).toBeVisible()
  await expect(page.getByText('angebot.pdf')).toBeVisible()
  await expect(page.getByText('Fertig')).toBeVisible()
})
