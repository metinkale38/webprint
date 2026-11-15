# Agent Instructions – PrintTool

Last updated: 2026-11-15

## Projekt

PrintTool ist ein mobiler Druckserver für Netzwerkdrucker:

- Docker-Container mit CUPS + FastAPI + Vue-3-SPA, `network_mode: host`
- Automatische Druckerkennung (mDNS/Bonjour + Subnetz-/SNMP-Scan)
- Lokale Benutzerverwaltung (Admin/Nutzer), Admin-Bootstrap per Env
- Drucken aus der WebUI: Upload (PDF/JPEG/PNG), Drucker wählen, Optionen (Doppelseitig, N-up, Farbe/SW, Kopien, Seiten), Job-Status
- Statistik pro Nutzer und Drucker (Seiten, Kopien, Farb/SW, Zeitraum)
- UI komplett deutsch, mobile-first

## Hard Constraints

- **Kein Nextcloud-Login.** Lokale Benutzer in SQLite, Rollen `admin`/`user`, Argon2id/bcrypt, JWT in HttpOnly-Cookies.
- **Kein AirPrint/Bonjour-Anbindung der Drucker.** Alle Aufträge laufen über die WebUI, damit die Nutzerstatistik lückenlos bleibt.
- **Nur PDF, JPEG, PNG.** Keine Office-Konvertierung.
- **Keine Benutzer-Selbstregistrierung.** Nur Admin legt Nutzer an.
- **UI-Sprache:** Deutsch.
- **Host-Netzwerk ist Pflicht** für Druckerkennung (mDNS/Subnetz). Port 631 auf dem Host frei machen.
- **CUPS im Container**; Treiber: IPP Everywhere + `printer-driver-all`, HPLIP, Gutenprint.
- **Keine Secrets im Repo:** `.env`, `data/`, `uploads/`, `*.db`, CUPS-Spool/Logs sind ignoriert. Der DeepSeek-Key liegt nur in `~/.local/share/opencode/auth.json`.
- **Kein DeepSeek Pro.** Alle Agents verwenden `deepseek/deepseek-flash`; Reasoning-Variante bewusst wählen (`low`/`medium`/`high`). Die kostenlosen opencode-Modelle sind wegen erschöpftem Free-Quota nicht als Default zu verwenden.
- **Keine Produktionsdaten/echten Drucker-Zugangsdaten committen.** Tests verwenden gemockte oder virtuelle PDF-Drucker.

## Architektur (Kurz)

```
Browser (Handy) ──HTTP──> FastAPI ──> SQLite
                            │
                            ├──> CUPS (lp/lpadmin/lpstat/ipptool, localhost:631)
                            └──> Discovery (zeroconf mDNS + TCP/SNMP-Scan)
```

- Backend: FastAPI, SQLAlchemy 2 + Alembic, Pydantic, JWT-Cookies, `zeroconf`, `pypdf`, `Pillow`
- Frontend: Vue 3 + TypeScript + Vite + Tailwind, Pinia, Vue Router
- Prozesse im Container: `cupsd` + Uvicorn (Entrypoint)
- Details: `docs/architecture.md`

## Build / Test-Kommandos

Backend (ab M1):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Frontend (ab M1):

```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
npm run test
npx playwright test
```

Docker:

```bash
docker compose up -d --build
docker compose logs -f app
```

## Git-Workflow

- Eigenes Repo in `printtool/`, Trunk `main`.
- Meilensteine auf Branch `milestone/n-<name>`; kleine, logische Commits.
- Commit-Style: Conventional Commits, Deutsch: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Vor Merge: QA-Review (Backend/Security) + ux-e2e (UI/Workflow) → Merge nach `main` → Tag `v0.x.0`.
- Kein Push/Remote ohne ausdrückliche Anweisung.
- Niemals `.env`, Daten, Uploads, CUPS-Spool oder Keys committen.

## Agent-Matrix

| Agent | Modell | Variante | Aufgabe |
|---|---|---|---|
| `architect` | `deepseek/deepseek-flash` | high | Planung, Recherche, Integration, Review |
| `backend` | `deepseek/deepseek-flash` | high | FastAPI, DB, Auth, CUPS, Discovery, Jobs |
| `frontend` | `deepseek/deepseek-flash` | high | Vue-3 mobile-first UI |
| `devops` | `deepseek/deepseek-flash` | medium | Docker, Compose, CI, Releases |
| `qa` | `deepseek/deepseek-flash` | high | Unit/Integration/API/Security-Tests |
| `ux-e2e` | `deepseek/deepseek-flash` | high | Playwright, visuelle Tests, UI/UX-Review |
| `docs` | `deepseek/deepseek-flash` | low | Doku, Changelog, Release Notes |

Regel: Reasoning-Variante abschwächen, wenn die Aufgabe einfach ist (`docs`, Boilerplate, kleine Fixes). `high` für Implementierung/Review.

## Definition of Done

- Code baut/lintet, Tests grün (Backend `pytest`, Frontend `npm run test`, E2E `npx playwright test` je nach Umfang)
- Neue/ geänderte Funktionen haben Tests
- Doku aktualisiert (README/AGENTS/docs), Commit-Message konventionell
- Keine Secrets, keine debuggten Credentials
- Übergabe an QA/ux-e2e vor Milestone-Merge

## Aktueller Stand

- M0 abgeschlossen: Git-Repo, Agent-Doku, Backend-/Frontend-Scaffold, Docker-/Compose-Gerüst, Playwright-Setup.
- M1 abgeschlossen: CUPS-Service (Queue anlegen/entfernen, Status, IPP-Probe), Entrypoint mit optionalem PDF-Drucker, Compose-Volume `cups-pdf/`.
- Backend: 14 `pytest`-Tests grün; `/healthz` und Admin-Login funktionieren.
- Frontend: TypeScript-Check, Vite-Build und Vitest grün (portables Node im Testlauf).
- Docker-Build in dieser Umgebung noch unverifiziert (Docker-Daemon für `docker run/build` gesperrt); `docker compose config` ist valide.
- Nächste Schritte: M2 API vervollständigen, M3 Discovery, M4 Druckjobs, M5 Frontend-Flows, M6 Admin, M7 QA/E2E, M8 Release.

## Wichtige Dateien

- `AGENTS.md`: diese Datei
- `docs/architecture.md`: Architektur, Datenmodell, APIs, CUPS-/Discovery-Design
- `docs/agent-workflow.md`: Agent-Ablauf, Eskalation, Commit-Disziplin
- `.opencode/agent/*.md`: Agent-Definitionen (Modell, Variante, Prompt)
- `backend/`, `frontend/`, `Dockerfile`, `docker-compose.yml`
