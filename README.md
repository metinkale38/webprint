# PrintTool

Mobiler Druckserver für Netzwerkdrucker: CUPS im Docker-Container, FastAPI-Backend,
Vue-3-WebUI (mobile-first, deutsch) und lokale Benutzerverwaltung.

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
# ADMIN_PASSWORD und JWT_SECRET in .env ändern!
docker compose up -d --build
```

Danach `http://<host-ip>:8000` öffnen und mit den Admin-Zugangsdaten aus `.env`
anmelden. CUPS läuft im Host-Netzwerk auf Port 631; dieser Port muss auf dem Host
frei sein (ggf. Host-CUPS stoppen).

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
```

## Konfiguration

Siehe `.env.example`. Wichtige Variablen:

| Variable | Zweck |
|---|---|
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
- `docs/agent-workflow.md`: Agent-Rollen, Ablauf, Commit-Regeln
- `AGENTS.md`: verbindliche Projektregeln
- `.opencode/agent/*.md`: Agent-Definitionen (alle `deepseek/deepseek-flash`)

## Status

M0: Repo, Agent-Doku, Backend-/Frontend-Scaffold, Docker-/Playwright-Gerüst.
M1: CUPS-Service (Queues, Status, IPP-Probe), Entrypoint und virtueller PDF-Drucker.
M2: API-Härtung (Rate-Limit, Security-Header, Validierung), Nutzer-/Drucker-CRUD, Jobs/Statistik.
M3: Discovery per mDNS, Subnetz-Scan, optionale SNMP-Anreicherung und automatische Queue-Anlage.
M4: Job-Status-Sync mit CUPS, Farboptions-Fallback und Live-Polling der Aufträge.
M5: Session-Refresh, verbesserter Druck-Flow, Auftrags-Polling und Komponenten-Tests.
Nächste Meilensteine: Admin-UI, E2E/visuelle Tests, Release.
