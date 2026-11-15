# Architektur PrintTool

Stand: 2026-11-15 (M8 / v0.8.0)

## Übersicht

Ein Docker-Container mit zwei Prozessen:

- `cupsd` – CUPS-Daemon, Queues, Treiber, Spool
- `uvicorn` – FastAPI-Anwendung, ausliefert die Vue-3-SPA und die JSON-API

`network_mode: host` ist Pflicht, damit mDNS und Subnetz-Scans funktionieren.

```
Browser ──HTTP──> FastAPI ──> SQLite (data/app.db)
                    │
                    ├──> CUPS HTTP/IPP (localhost:631) + CLI (lp, lpadmin, lpstat, ipptool)
                    └──> Discovery (zeroconf mDNS + asyncio TCP-Scan + optional SNMP)
```

## Tech-Stack

- **Backend:** Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2, Alembic, Pydantic v2, PyJWT, passlib/argon2-cffi, python-multipart, zeroconf, pypdf, Pillow, httpx
- **Frontend:** Vue 3, TypeScript, Vite, Tailwind CSS, Pinia, Vue Router, Chart.js (Stats), Playwright (E2E/visuell)
- **Druck:** CUPS 2.4+, cups-filters, IPP Everywhere, `printer-driver-all`, HPLIP, Gutenprint
- **Daten:** SQLite (Datei, Volume), Uploads als Dateien unter `uploads/` (ignoriert)

## Datenmodell (Entwurf)

- `users`: id, username (unique), password_hash, display_name, role (`admin`/`user`), active, created_at, last_login
- `printers`: id, name, slug (unique), device_uri, protocol (`ipp`/`ipps`/`lpd`/`socket`), model, location, driver_mode, auto_discovered, enabled, status, capabilities (JSON), last_seen
- `print_jobs`: id, user_id, printer_id, filename, options (JSON), pages, copies, color_mode, duplex, status, cups_job_id, error, created_at, started_at, finished_at
- `settings`: key (PK), value
- optional `audit_log`: id, user_id, action, entity, entity_id, created_at, meta (JSON)

## API (Entwurf)

- Auth: `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET /api/auth/me`
- Drucker: `GET/POST /api/printers`, `GET/PATCH/DELETE /api/printers/{id}`, `POST /api/printers/scan`, `POST /api/printers/refresh`, `GET /api/printers/{id}/capabilities`
- Jobs: `POST /api/jobs` (multipart), `GET /api/jobs?all_jobs=true` (Admin), `GET /api/jobs/{id}`, `POST /api/jobs/{id}/cancel`; Antworten enthalten `user_name`/`printer_name`
- Nutzer (Admin): `GET/POST /api/users`, `GET/PATCH/DELETE /api/users/{id}`
- Statistik: `GET /api/stats/overview|users|printers|export` mit optionalem `start=YYYY-MM-DD`/`end=YYYY-MM-DD`
- System: `GET /healthz`, `GET /api/settings`

## Druckerkennung

1. **mDNS/Bonjour** mit `zeroconf`: `_ipp._tcp`, `_ipps._tcp`, `_printer._tcp`, `_pdl-datastream._tcp`; TXT-Felder `ty`, `pdl`, `rp`, `note` werden zu Geräte-URI und Modell gemappt.
2. **Aktiver Scan** (konfigurierbare Subnetze, max. 1024 Hosts pro Lauf): TCP 631/515/9100; optional SNMP via `snmpget` für sysName/sysDescr.
3. **IPP-Anreicherung** via `ipptool` (Get-Printer-Attributes): Farbe, Duplex, Formate, Auflösung, Papier.
4. **Queue:** `lpadmin -p <slug> -v <uri> -m everywhere -E`; LPD `lpd://`, JetDirect `socket://` mit passendem Treiber.
5. **Deduplizierung** pro Host, IPP/IPPS bevorzugt vor LPD/Socket; Treffer werden in SQLite gespeichert.
6. **Hintergrund-Loop** (`DISCOVERY_ENABLED`, `DISCOVERY_INTERVAL`) und manueller Scan (`POST /api/printers/scan`) legen neue Drucker automatisch an und aktualisieren `last_seen`, Fähigkeiten und CUPS-Status. Fehlgeschlagene Queue-Anlagen werden beim nächsten Lauf erneut versucht.

## Druckoptionen-Mapping

| UI-Option | CUPS |
|---|---|
| Kopien | `-n N` |
| Seiten | `-P "1-5,8"` |
| Doppelseitig | `-o sides=two-sided-long-edge` / `two-sided-short-edge` / `one-sided` |
| N-up | `-o number-up=2|4|6|9|16` |
| Farbe/SW | `-o print-color-mode=color|monochrome`; Fallback PPD `ColorModel`/`OutputMode` |
| Papier | `-o media=A4|Letter|...` |
| Qualität | `-o print-quality=3|4|5` (optional) |

Bei PPD-basierten Queues wird die Farboption automatisch auf `ColorModel` oder
`OutputMode` abgebildet (Erkennung via `lpoptions -p <queue> -l`). Die Job-ID aus
`lp` (`request id is <queue>-<id>`) wird gespeichert; ein Hintergrund-Loop
(`JOB_SYNC_INTERVAL`) gleicht `lpstat -W not-completed/completed` ab, zusätzlich
aktualisiert `GET /api/jobs/{id}` den Status direkt.

## CUPS-Queues und virtueller PDF-Drucker

- Jeder Drucker wird als CUPS-Queue mit sicherem Slug angelegt:
  `lpadmin -p <slug> -v <uri> -m everywhere -E`, danach `cupsenable`/`cupsaccept`.
- Status wird über `lpstat -p` gelesen (`idle`, `printing`, `disabled`, `offline`).
- Fähigkeiten werden mit `ipptool -tv <uri> /usr/share/cups/ipptool/get-printer-attributes.test`
  gelesen und geparst (Farbe, Duplex, Formate, Auflösung, Papier).
- Optionaler virtueller PDF-Drucker für Entwicklung/E2E:
  `CUPS_PDF_QUEUE=printtool-pdf` legt beim Start eine Queue mit `cups-pdf:/` an;
  Ausgaben landen im Volume `./volumes/cups-pdf` (`/var/spool/cups-pdf`).

## Sicherheit

- Argon2id/bcrypt, JWT Access + Refresh (HttpOnly, Secure, SameSite=Strict); SameSite=Strict plus CORS-Beschränkung als CSRF-Schutz
- Login-Rate-Limit: max. 5 Fehlversuche pro Minute je IP+Benutzername; erfolgreicher Login setzt den Zähler zurück
- Rollen-Guards, Upload-Typ/-Größe (Magic Bytes), UUID-Dateinamen, Bereinigung alter Uploads
- Validierung: Geräte-URI-Schemata (`ipp`/`ipps`/`lpd`/`socket`/`dnssd`/`cups-pdf`), Drucker-Slugs, Seitenbereiche, Kopien 1–99
- Request-Größenlimit per `Content-Length`, Security-Header inkl. CSP, ORM-only (keine String-SQL), CORS nur Same-Origin
- HTTPS optional hinter Reverse Proxy; Container nur im LAN

## Testing

- Backend: pytest (Unit/Integration, Testclient, temp DB); CUPS-CLI in Tests durch Fake-Binaries ersetzt
- Frontend: Vitest + Vue Test Utils, TypeScript-Check
- E2E/visuell: Playwright (Mobile/Desktop, API-Mocks), Screenshot-Baselines und echter Integrationslauf mit FastAPI + Vite
- CUPS-PDF: virtueller Drucker (`CUPS_PDF_QUEUE=printtool-pdf`) für Spool-/PDF-Prüfungen im Docker-Container
- Details: `docs/testing.md`

## Deployment

- `Dockerfile` (Multi-Stage: Node-Build → Ubuntu + CUPS + Python)
- `docker-compose.yml`: `network_mode: host`, alle Volumes unter `./volumes/` (`data`, `uploads`, `cups-pdf`, `cups/config`, `cups/spool`, `cups/log`)
- Env: `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `JWT_SECRET`, `DISCOVERY_SUBNETS`, `DISCOVERY_INTERVAL`, `UPLOAD_MAX_MB`, `TIMEZONE`, `CUPS_PDF_QUEUE`
