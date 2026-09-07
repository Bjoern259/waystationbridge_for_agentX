# Waystation Bridge

Kleine read-only Python-Web-App als Brücke zu The Waystation.

## Lokal starten

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Dann: http://localhost:8080

## Deployment

Die App ist für einen einfachen Python-Webhost vorbereitet. Startkommando:

```bash
gunicorn app:app
```

Optional kann die Waystation-Basis-URL über `WAYSTATION_BASE` gesetzt werden.

## Sicherheit

Diese Version ist absichtlich read-only. Sie führt keine POST-/JSON-RPC-Requests an Waystation aus,
claimt keine Tasks und veröffentlicht keine Ergebnisse.
