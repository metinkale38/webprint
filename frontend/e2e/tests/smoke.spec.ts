import { expect, test } from '@playwright/test'

test('Login-Seite ist erreichbar', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: {} }))

  await page.goto('/login')

  await expect(page.getByRole('heading', { name: 'Anmelden' })).toBeVisible()
  await expect(page.getByLabel('Benutzername')).toBeVisible()
  await expect(page.getByLabel('Passwort')).toBeVisible()
})
