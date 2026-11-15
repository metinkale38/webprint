# PrintTool

Mobiler Druckserver für Netzwerkdrucker: CUPS im Docker-Container, FastAPI-Backend,
Vue-3-WebUI (mobile-first, deutsch) und lokale Benutzerverwaltung.

## Screenshots

| Login | Drucken | Administration | Statistik |
|---|---|---|---|
| <img src="frontend/e2e/tests/__screenshots__/mobile-iphone/login.png" alt="Login" width="180" /> | <img src="frontend/e2e/tests/__screenshots__/mobile-iphone/print.png" alt="Drucken" width="180" /> | <img src="frontend/e2e/tests/__screenshots__/mobile-iphone/admin.png" alt="Administration" width="180" /> | <img src="frontend/e2e/tests/__screenshots__/mobile-iphone/stats.png" alt="Statistik" width="180" /> |

## Funktionen (Zielbild)

- Automatische Druckerkennung per mDNS/Bonjour und Subnetz-Scan
- Drucken aus der WebUI: PDF/JPG/PNG hochladen, Drucker wählen, Optionen setzen
- Optionen: Kopien, Seitenbereich, Doppelseitig, N-up, Farbe/Schwarzweiß, Papier
- Benutzerverwaltung: Admin und Nutzer; nur Admins legen Nutzer und Drucker an
- Statistik pro Nutzer und Drucker (Seiten, Kopien, Farbe/SW, Zeitraum)
- AirPrint bewusst deaktiviert, damit alle Aufträge einem Nutzer zugeordnet werden

## Schnellstart (Docker)

```bash
cp .env.example .env
# HOST, ADMIN_PASSWORD, JWT_SECRET und TRAEFIK_CERT_RESOLVER anpassen
docker network create traefik   # falls das externe Traefik-Netz noch nicht existiert
docker compose up -d --build
```

Danach `https://<HOST>` über Traefik öffnen; direkt erreichbar bleibt
`http://<host-ip>:8000`. CUPS läuft im Host-Netzwerk auf Port 631; dieser Port
muss auf dem Host frei sein (ggf. Host-CUPS stoppen).

## Traefik / HTTPS

Die App bleibt für CUPS/mDNS im Host-Netz. Ein schlanker Caddy-Proxy
(`printtool-proxy`) hängt im externen `traefik`-Netz und leitet an
`host.docker.internal:8000` weiter; die Traefik-Labels sitzen auf diesem Proxy.

- `HOST` in `.env` = öffentliche Domain
- `TRAEFIK_CERT_RESOLVER` = Name des Certresolvers in der Traefik-Konfiguration
- Externes Docker-Netz `traefik` muss existieren
- Router/Service: `printtool`, EntryPoint `websecure`, Service-Port `8080`
- Für HTTPS `COOKIE_SECURE=true` setzen
- Ohne Traefik bleibt die App direkt unter `http://<host-ip>:8000` erreichbar

## Entwicklung

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Frontend (Node.js erforderlich):

```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
npm run test
npx playwright test
npx playwright test -c playwright.integration.config.ts
```

Die gemockten Playwright-Tests und visuellen Screenshot-Baselines liegen unter
`frontend/e2e/`. Details: `docs/testing.md`.

## Konfiguration

Siehe `.env.example`. Wichtige Variablen:

| Variable | Zweck |
|---|---|
| `HOST` | Öffentliche Domain für den Traefik-Router |
| `TRAEFIK_CERT_RESOLVER` | Certresolver-Name in Traefik (Default `myresolver`) |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin-Bootstrap beim ersten Start |
| `JWT_SECRET` | Signatur der Session-Cookies (min. 32 Zeichen) |
| `DATABASE_URL` | SQLite-Pfad, im Container `sqlite:////app/data/app.db` |
| `UPLOAD_DIR` | Upload-Verzeichnis, im Container `/app/uploads` |
| `UPLOAD_MAX_MB` | Maximale Uploadgröße |
| `DISCOVERY_ENABLED` | Periodische Druckererkennung ein/aus |
| `DISCOVERY_MDNS` | mDNS/Bonjour-Erkennung ein/aus |
| `DISCOVERY_SNMP` | SNMP-Anreicherung ein/aus (benötigt `snmpget`) |
| `DISCOVERY_SUBNETS` | Kommagetrennte Subnetze für den aktiven Scan |
| `DISCOVERY_INTERVAL` | Scan-Intervall in Sekunden |
| `SNMP_COMMUNITY` | SNMP-Community (Default `public`) |
| `JOB_SYNC_ENABLED` | CUPS-Jobstatus periodisch in die DB übernehmen |
| `JOB_SYNC_INTERVAL` | Intervall des Job-Status-Syncs in Sekunden |
| `COOKIE_SECURE` | `true` hinter HTTPS |
| `CUPS_ADMIN` / `CUPS_PASSWORD` | Optionaler CUPS-WebUI-Zugang |
| `CUPS_PDF_QUEUE` | Optionaler virtueller PDF-Drucker (z. B. `printtool-pdf` für E2E) |

## Architektur & Agenten

- `docs/architecture.md`: Komponenten, Datenmodell, API, Druckoptionen
- `docs/testing.md`: Test-Pyramide, Playwright, visuelle Tests, CUPS-PDF
- `docs/release.md`: Deployment, Backup, Abnahme-Checkliste
- `docs/agent-workflow.md`: Agent-Rollen, Ablauf, Commit-Regeln
- `AGENTS.md`: verbindliche Projektregeln
- `.opencode/agent/*.md`: Agent-Definitionen (alle `deepseek/deepseek-flash`)

## Status

**v0.8.1 – Release-Kandidat.** Alle geplanten Meilensteine sind umgesetzt:

- M0–M2: Repo/Agent-Doku, CUPS-Grundlage, API-Härtung und CRUD
- M3–M4: Discovery (mDNS/Subnetz/SNMP), Auto-Queues, Job-Status-Sync
- M5–M6: Mobile UI, Session-Refresh, Admin-UI, Statistik mit Zeitraumfilter
- M7: Playwright-E2E, visuelle Baselines, echter Integrationslauf
- M8: Changelog, Release-Doku, CI-Workflow

Offen vor Produktivbetrieb: Docker-Build und CUPS-PDF-E2E auf dem Zielhost
verifizieren (in der Sandbox war der Docker-Daemon gesperrt).
