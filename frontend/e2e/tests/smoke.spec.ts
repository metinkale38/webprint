import { expect, test } from '@playwright/test'

import { mockLoggedOut } from './helpers'

test('Login-Seite ist erreichbar', async ({ page }) => {
  await mockLoggedOut(page)

  await page.goto('/login')

  await expect(page.getByRole('heading', { name: 'Anmelden' })).toBeVisible()
  await expect(page.getByLabel('Benutzername')).toBeVisible()
  await expect(page.getByLabel('Passwort')).toBeVisible()
})
