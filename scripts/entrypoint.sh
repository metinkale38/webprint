#!/usr/bin/env bash
set -euo pipefail

mkdir -p /run/cups /var/spool/cups /var/log/cups /app/data /app/uploads

cupsd

for _ in $(seq 1 30); do
  if [ -S /run/cups/cups.sock ]; then
    break
  fi
  sleep 1
done

cupsctl --remote-admin --remote-any --share-printers >/dev/null 2>&1 || true

if [ -n "${CUPS_ADMIN:-}" ] && [ -n "${CUPS_PASSWORD:-}" ]; then
  if ! id "${CUPS_ADMIN}" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "${CUPS_ADMIN}" || true
  fi
  echo "${CUPS_ADMIN}:${CUPS_PASSWORD}" | chpasswd || true
  usermod -aG lpadmin "${CUPS_ADMIN}" 2>/dev/null || true
fi

cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
APP_PID=$!

cleanup() {
  kill "${APP_PID}" 2>/dev/null || true
  cupsctl --stop-daemon >/dev/null 2>&1 || true
  wait "${APP_PID}" 2>/dev/null || true
  exit 0
}

trap cleanup SIGTERM SIGINT

wait "${APP_PID}"
