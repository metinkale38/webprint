import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig, devices } from '@playwright/test'

const backendDir = fileURLToPath(new URL('../backend', import.meta.url))
const runId = `${Date.now()}`
const dbPath = path.join(os.tmpdir(), `printtool-e2e-${runId}.db`)
const uploadDir = path.join(os.tmpdir(), `printtool-e2e-uploads-${runId}`)
const backendCommand =
  process.env.PRINTTOOL_BACKEND_CMD ??
  '.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000'

export default defineConfig({
  testDir: './e2e/integration',
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: backendCommand,
      cwd: backendDir,
      url: 'http://127.0.0.1:8000/healthz',
      reuseExistingServer: false,
      timeout: 60_000,
      env: {
        PATH: process.env.PATH ?? '',
        HOME: process.env.HOME ?? '',
        DATABASE_URL: `sqlite:///${dbPath}`,
        UPLOAD_DIR: uploadDir,
        ADMIN_USERNAME: 'admin',
        ADMIN_PASSWORD: 'e2e-password',
        JWT_SECRET: 'e2e-secret-with-at-least-32-characters',
        COOKIE_SECURE: 'false',
        DISCOVERY_ENABLED: 'false',
        JOB_SYNC_ENABLED: 'false',
        PYTHONUNBUFFERED: '1',
      },
    },
    {
      command: 'npm run dev',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
  projects: [{ name: 'integration-chrome', use: { ...devices['Desktop Chrome'] } }],
})
