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
| `DISCOVERY_SUBNETS` | Kommagetrennte Subnetze für den aktiven Scan |
| `DISCOVERY_INTERVAL` | Scan-Intervall in Sekunden |
| `COOKIE_SECURE` | `true` hinter HTTPS |
| `CUPS_ADMIN` / `CUPS_PASSWORD` | Optionaler CUPS-WebUI-Zugang |

## Architektur & Agenten

- `docs/architecture.md`: Komponenten, Datenmodell, API, Druckoptionen
- `docs/agent-workflow.md`: Agent-Rollen, Ablauf, Commit-Regeln
- `AGENTS.md`: verbindliche Projektregeln
- `.opencode/agent/*.md`: Agent-Definitionen (alle `deepseek/deepseek-flash`)

## Status

M0: Repo, Agent-Doku, Backend-/Frontend-Scaffold, Docker-/Playwright-Gerüst.
Nächste Meilensteine: CUPS/Discovery, Druckjobs, Admin-UI, E2E/visuelle Tests.
