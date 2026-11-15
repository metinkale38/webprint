# E2E-Testdaten

Die UI-Tests erzeugen ihre PDF-/Bild-Uploads direkt im Test (Buffer), damit keine
Binärdateien im Repo liegen. Für echte CUPS-E2E-Tests (M7) wird zusätzlich eine
kleine PDF benötigt.

Vorschlag für eine lokale Testdatei (nicht committen):

```bash
python3 - <<'PY'
from pathlib import Path
content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]>>endobj
trailer<</Root 1 0 R>>
%%EOF
"""
Path("e2e/fixtures/sample.pdf").write_bytes(content)
PY
```

Echte Drucker oder Produktionsdaten dürfen nicht verwendet werden. Der virtuelle
CUPS-PDF-Drucker (`printer-driver-cups-pdf`) ist für E2E vorgesehen.
