# Agent-Workflow PrintTool

Stand: 2026-11-15 (M0)

## Prinzip

Agent-first: Der `architect` plant und koordiniert, Spezial-Agenten setzen um, `qa` und `ux-e2e` prüfen. Jeder Agent hat eine klar definierte Rolle, ein festes Modell (`deepseek/deepseek-flash`) und eine Reasoning-Variante.

## Rollen

- **architect** (primary): Zusammenstellung der Aufgabe, Recherche, Architektur-Entscheidungen, Aufgaben-Splitting, Integration, finaler Review. Kein DeepSeek Pro.
- **backend**: FastAPI, SQLite, Auth, CUPS-Anbindung, Discovery, Druckjobs, Statistik-API.
- **frontend**: Vue-3-Mobile-First-UI, Design-System, Barrierefreiheit, API-Client.
- **devops**: Dockerfile, Compose, Volumes, Entrypoint, CI, Release-Artefakte.
- **qa**: Unit-/Integration-/API-Tests, Security-Checks, Code-Review.
- **ux-e2e**: Playwright-Workflows, visuelle Tests/Screenshots, Mobile-Viewports, komplette User-Journeys mit gemockten/PDF-Druckern.
- **docs**: README, Architektur-, Agent-Doku, Changelog, Release Notes.

## Ablauf pro Meilenstein

1. `architect` legt Ziele, Dateien und Akzeptanzkriterien fest (kurze Planungsnachricht).
2. Agenten parallel/sequenziell implementieren (disjunkte Dateimengen, sonst sequenziell).
3. `qa` prüft Backend/Security; `ux-e2e` prüft UI/Workflow/E2E.
4. `architect` integriert,Review, Merge nach `main`, Tag.
5. `docs` aktualisiert Doku/Changelog.

## Eskalation

-_schema-Fehler/Blocker: Agent gibt kontextuelle Fehlerursache + Optionen an `architect` zurück statt wild zu experimentieren.
- Modell-Varianterhöhung nur bei Komplexität: `low` → `medium` → `high`; `max` nur für Architektur/harte Bugs.
- Nicht im Plan Mode editieren; vor größeren Änderungen Ziel klarstellen.

## Commit-Disziplin

- Conventional Commits, Deutsch.
- Ein Commit = eine logische Änderung; keine gemischten Features.
- Vor Commit: Tests/lint grün, keine Secrets, `.gitignore` geprüft.
- Meilenstein-Branch `milestone/n-*`, Merge nach `main`, Tag `v0.x.0`.

## Token-Sparsamkeit

- Reasoning-Variante der Aufgabenkomplexität anpassen.
- Bestehenden Code zuerst lesen, nicht neu erfinden.
- Agenten nur mit den nötigen Dateien/Kontext füttern; große Auszüge vermeiden.
- `docs` und kleine Fixes mit `low`, Implementierung mit `high`.
