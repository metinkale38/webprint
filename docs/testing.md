# Testing PrintTool

Stand: 2026-11-15 (M7)

## Test-Pyramide

| Ebene | Werkzeug | Umfang |
|---|---|---|
| Backend-Unit/Integration | pytest + TestClient | Auth, Rollen, CRUD, Jobs, Statistik, Discovery, CUPS-Wrapper |
| Frontend-Komponenten | Vitest + Vue Test Utils | Status-Badge, Druckerkarte, Options-Sheet |
| UI/E2E (gemockt) | Playwright | Login, Druck-Flow, Aufträge, Admin, Statistik |
| Visuell | Playwright Screenshots | Login, Drucken, Admin, Statistik in Mobile/Desktop |
| Integration | Playwright + echtes FastAPI | Admin legt Drucker an, druckt, sieht Auftrag und Statistik |
| CUPS-PDF (Docker) | CUPS + `cups-pdf` | echter Spool/PDF-Ausgabe, manuell/CI mit Docker |

## Kommandos

Backend:

```bash
cd backend
.venv/bin/pytest -q
```

Frontend:

```bash
cd frontend
npm run build
npm run test
npx playwright test          # gemockte UI- und visuelle Tests
npx playwright test -c playwright.integration.config.ts  # echtes Backend
```

Visuelle Baselines aktualisieren (nach bewussten UI-Änderungen):

```bash
cd frontend
npm run e2e:update
# Screenshots unter e2e/tests/__screenshots__/ prüfen und committen
```

## Gemockte UI-Tests

`frontend/e2e/tests/` mockt alle API-Aufrufe mit `page.route`. Vorteile:

- schnell, kein Backend/CUPS nötig
- prüft Formulare, Validierung, Routing, deutsche Texte und Zustände
- nutzt echte Browser-Viewports (iPhone/Pixel/Desktop)

Wichtige Dateien:

- `helpers.ts`: Testdaten und Auth-Mocks
- `flow.spec.ts`: Upload, Druckerwahl, Optionen, Auftragserstellung
- `admin.spec.ts`: Tabs, Formulare, Auftragsübersicht
- `stats.spec.ts`: Kennzahlen, Nutzer-/Druckeransicht, Zeitraumfilter
- `visual.spec.ts`: Screenshot-Baselines

## Integrationstest mit echtem Backend

`playwright.integration.config.ts` startet:

1. Uvicorn mit temporärer SQLite-DB (Admin `admin` / `e2e-password`,
   Discovery und Job-Sync deaktiviert)
2. Vite Dev-Server mit Proxy auf `127.0.0.1:8000`

Ablauf in `e2e/integration/workflow.spec.ts`:

1. Admin-Login
2. Drucker über die Admin-UI anlegen
3. PDF über die Druck-UI hochladen und Optionen setzen
4. Auftrag in „Meine Aufträge“ prüfen
5. Statistik prüfen
6. Nutzer über die Admin-UI anlegen

Da in dieser Sandbox kein CUPS installiert ist, bleibt der Auftrag im Status
„Wartet“; die API- und UI-Integration wird trotzdem vollständig geprüft.

## CUPS-PDF-Drucker (Docker)

Für echte Spool-Tests den Container mit virtuellem PDF-Drucker starten:

```bash
CUPS_PDF_QUEUE=printtool-pdf docker compose up -d --build
```

Die Ausgaben landen im Volume `./volumes/cups-pdf` (`/var/spool/cups-pdf`). Damit lassen
sich PDF-Inhalt und Seitenzahl nach einem UI-Druck prüfen. In der aktuellen
Sandbox ist `docker run/build` gesperrt; der Docker-CUPS-E2E-Lauf ist daher noch
nicht verifiziert.

## Hinweise

- `mobile-iphone` nutzt Chromium mit iPhone-13-Viewport (WebKit-Systemlibs fehlen
  in der Sandbox).
- Screenshots werden pro Projekt unter
  `frontend/e2e/tests/__screenshots__/<projekt>/` abgelegt.
- Keine echten Drucker, Produktionsdaten oder Zugangsdaten in Tests verwenden.
- Bei bewussten UI-Änderungen: `npm run e2e:update`, Screenshots visuell prüfen,
  dann committen.
