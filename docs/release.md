# Release & Deployment

Stand: 2026-11-15 (v0.8.1)

## Voraussetzungen

- Linux-Host mit Docker und Compose
- Port 631 auf dem Host frei (Host-CUPS ggf. stoppen)
- `network_mode: host` (für mDNS und Subnetz-Scan)
- Zielhost im selben Netz wie die Drucker; für andere VLANs `DISCOVERY_SUBNETS` setzen
- Für HTTPS: laufendes Traefik mit externem Docker-Netz `traefik` und Certresolver
  (Name in `TRAEFIK_CERT_RESOLVER`, Default `myresolver`)

## Erstinstallation

```bash
git clone <repo> printtool
cd printtool
cp .env.example .env
# HOST, ADMIN_PASSWORD, JWT_SECRET, CUPS_PASSWORD und ggf. DISCOVERY_SUBNETS anpassen
docker network create traefik   # falls das externe Netz noch nicht existiert
docker compose up -d --build
docker compose logs -f app
```

Danach `https://<HOST>` über Traefik öffnen (oder direkt `http://<host-ip>:8000`)
und mit den Admin-Zugangsdaten anmelden.

## Traefik / HTTPS

Die App bleibt im Host-Netz, damit CUPS/mDNS funktionieren. Der zusätzliche
Service `printtool-proxy` (Caddy) hängt im externen `traefik`-Netz und leitet an
`host.docker.internal:8000` weiter. Die Traefik-Labels liegen auf dem Proxy.

- `HOST` ist die öffentliche Domain (`Host(...)`-Regel).
- `TRAEFIK_CERT_RESOLVER` muss dem Certresolver in der Traefik-Konfiguration entsprechen.
- Bei HTTPS `COOKIE_SECURE=true` setzen; für direkten HTTP-Zugriff auf Port 8000 `false`.
- Router/Service heißen `printtool`, der EntryPoint ist `websecure`, der interne
  Service-Port ist `8080`.
- Das externe Netz muss existieren: `docker network create traefik`.
- Ohne Traefik ist die App weiterhin direkt unter `http://<host-ip>:8000` erreichbar;
  der Proxy läuft dann ohne Nutzen mit.

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

Ausgaben landen im Volume `./volumes/cups-pdf` (`/var/spool/cups-pdf`). Ideal für
Abnahme-Tests ohne echten Drucker.

## Daten und Backup

- SQLite: `./volumes/data/app.db`
- Uploads: `./volumes/uploads/`
- CUPS-Konfiguration/Spool/Logs: `./volumes/cups/{config,spool,log}`
- PDF-Ausgaben (Test): `./volumes/cups-pdf/`
- Backup: Container stoppen und `./volumes/` komplett sichern.

Beim ersten Start wird ein leeres `./volumes/cups/config` automatisch mit den
CUPS-Standarddateien aus dem Image befüllt; bestehende Konfiguration bleibt
erhalten.

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
