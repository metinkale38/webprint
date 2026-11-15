# Release & Deployment

Stand: 2026-11-15 (v0.8.1)

## Voraussetzungen

- Linux-Host mit Docker und Compose
- Port 631 auf dem Host frei (Host-CUPS ggf. stoppen)
- `network_mode: host` (für mDNS und Subnetz-Scan)
- Zielhost im selben Netz wie die Drucker; für andere VLANs `DISCOVERY_SUBNETS` setzen

## Erstinstallation

```bash
git clone <repo> printtool
cd printtool
cp .env.example .env
# ADMIN_PASSWORD, JWT_SECRET, CUPS_PASSWORD und ggf. DISCOVERY_SUBNETS anpassen
docker compose up -d --build
docker compose logs -f app
```

Danach `http://<host-ip>:8000` öffnen und mit den Admin-Zugangsdaten anmelden.

## Drucker einrichten

1. Als Admin unter **Admin → Drucker** „Scannen“ ausführen.
2. Gefundene Drucker prüfen; bei Bedarf Standort/Modell bearbeiten oder deaktivieren.
3. Für nicht gefundene Drucker manuell Geräte-URI eintragen
   (`ipp://…`, `ipps://…`, `lpd://…`, `socket://…`).
4. Testdruck aus der Druck-Ansicht; Auftrag unter **Aufträge** prüfen.

## Virtueller PDF-Drucker (Test)

```bash
# in .env
CUPS_PDF_QUEUE=printtool-pdf
```

```bash
docker compose up -d --build
```

Ausgaben landen im Volume `./cups-pdf` (`/var/spool/cups-pdf`). Ideal für
Abnahme-Tests ohne echten Drucker.

## Daten und Backup

- SQLite: `./data/app.db`
- Uploads: `./uploads/`
- CUPS-Konfiguration/Spool/Logs: benannte Volumes `cups-config`, `cups-spool`, `cups-log`
- Backup: Container stoppen, `data/` und `uploads/` sichern, optional CUPS-Volumes.

## Upgrade

```bash
git pull
docker compose up -d --build
```

Datenbanktabellen werden beim Start per `create_all` ergänzt. Für spätere
Schema-Migrationen ist Alembic vorbereitet.

## Abnahme-Checkliste

```bash
cd backend && .venv/bin/pytest -q
cd ../frontend
npm run build
npm run test
npx playwright test
npx playwright test -c playwright.integration.config.ts
cd ..
docker compose config
```

Manuell auf dem Zielhost:

- [ ] Container startet, `/healthz` antwortet
- [ ] Admin-Login funktioniert
- [ ] Scan findet mindestens einen Drucker oder manueller Drucker wird angelegt
- [ ] Upload + Optionen + Job-Status funktionieren
- [ ] Statistik zählt Seiten/Kopien pro Nutzer und Drucker
- [ ] Neustart: Daten und CUPS-Queues bleiben erhalten

## Bekannte Einschränkungen

- Docker-Build und CUPS-PDF-E2E wurden in der Entwicklungs-Sandbox nicht ausgeführt
  (Docker-Daemon gesperrt). Auf dem Zielhost verifizieren.
- WebKit/Visual-Baselines wurden mit Chromium-Emulation erstellt; CI führt die
  visuellen Tests bewusst nicht aus.
- Treiberpakete (`printer-driver-all`, HPLIP, Gutenprint) vergrößern das Image.
- Farb-/SW-Option ist bei exotischen PPD-Treibern herstellerspezifisch; der
  Fallback deckt `print-color-mode`, `ColorModel` und `OutputMode` ab.
- Kein AirPrint: direkte Drucke außerhalb der WebUI wären nicht zuordenbar.
