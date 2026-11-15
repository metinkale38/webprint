import { expect, test } from '@playwright/test'

test('Login-Seite visuell', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: {} }))

  await page.goto('/login')

  await expect(page).toHaveScreenshot('login.png', { fullPage: true })
})
