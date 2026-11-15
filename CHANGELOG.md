# Changelog

Alle nennenswerten Änderungen an PrintTool. Format orientiert sich an
Keep a Changelog, Versionierung nach Semantic Versioning.

## [Unreleased]

### Geändert

- Alle Compose-Volumes liegen gesammelt unter `./volumes/`
  (`data`, `uploads`, `cups-pdf`, `cups/{config,spool,log}`).
- Das CUPS-Config-Volume wird beim ersten Start aus den Image-Defaults befüllt.

## [0.8.1] – 2026-11-15

### Behoben

- SPA-Fallback: direkte Aufrufe von `/admin`, `/stats`, `/jobs` und anderen
  Frontend-Routen liefern wieder `index.html` statt 404.

## [0.8.0] – 2026-11-15

Erster Release-Kandidat. Der Funktionsumfang ist vollständig; der Docker-Build
konnte in der Entwicklungs-Sandbox nicht ausgeführt werden und muss auf dem
Zielhost verifiziert werden.

### Hinzugefügt

- FastAPI-Backend mit SQLite, JWT-Cookies, Admin-Bootstrap und Rollen `admin`/`user`
- Vue-3-WebUI (mobile-first, deutsch): Login, Drucken, Aufträge, Statistik, Admin
- CUPS-Anbindung: Queue anlegen/ändern/löschen, Job senden/abbrechen, Status
- Druckoptionen: Kopien, Seitenbereich, Doppelseitig, N-up, Farbe/SW, Papier
- Automatische Druckerkennung: mDNS/Bonjour, Subnetz-TCP-Scan, optionale SNMP-Anreicherung, IPP-Fähigkeiten
- Automatische Queue-/DB-Anlage, Hintergrund-Discovery und manueller Scan
- Job-Status-Sync mit CUPS sowie Farboptions-Fallback (`ColorModel`/`OutputMode`)
- Statistik pro Nutzer und Drucker mit Zeitraumfilter und CSV-Export
- Admin-CRUD für Drucker und Nutzer, Auftragsübersicht mit Nutzer-/Druckernamen
- Sicherheit: Argon2id, Rate-Limit, Security-Header/CSP, Upload-Validierung, Größenlimit
- Docker/Compose mit Host-Netzwerk, CUPS, Treibern und optionalem PDF-Drucker
- Tests: 47 pytest, 6 Vitest, 24 gemockte Playwright-Tests, 1 Integrationstest, visuelle Baselines
- Agent-First-Dokumentation (`AGENTS.md`, `.opencode/agent/*.md`, `docs/`)
- CI-Workflow für Backend-Tests, Frontend-Build/-Tests und Playwright

### Bewusste Einschränkungen

- Kein Nextcloud-Login; lokale Benutzerverwaltung.
- Kein AirPrint/Bonjour-Angebot der Drucker, damit alle Aufträge statistisch zugeordnet bleiben.
- Nur PDF, JPEG und PNG; keine Office-Konvertierung.
- Keine Benutzer-Selbstregistrierung.
- mDNS bleibt auf die Broadcast-Domain beschränkt; für VLANs Subnetz-Scan konfigurieren.
- Docker-Image und CUPS-PDF-E2E sind in der Sandbox unverifiziert.
