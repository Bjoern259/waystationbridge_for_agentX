from flask import Flask, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site"
).rstrip("/")

TEMPLATE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Waystation Bridge</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1000px;margin:32px auto;padding:0 18px}
h1{margin-bottom:4px}
.status{padding:10px;border-radius:8px;background:#f4f4f4}
section{margin-top:22px}
pre{white-space:pre-wrap;overflow:auto;background:#f4f4f4;padding:14px;border-radius:8px}
a{word-break:break-all}
.small{color:#666}
</style>
</head>
<body>
<h1>The Waystation Bridge</h1>
<p class="small">Read-only. Die Daten werden serverseitig von der Bridge abgerufen, damit ein Agent nur diese eine URL öffnen muss.</p>
<div class="status"><b>Waystation:</b> {{ base }}</div>

<section>
<h2>Aktueller Brief</h2>
<pre>{{ brief }}</pre>
</section>

<section>
<h2>Aktuelle Tasks</h2>
<pre>{{ tasks }}</pre>
</section>

<section>
<h2>Maschinenlesbarer Zugang</h2>
<p><a href="/agent-context">/agent-context</a> – kompakte, maschinenlesbare Zusammenfassung.</p>
</section>
</body>
</html>"""

def fetch(path):
    r = requests.get(
        WAYSTATION + path,
        timeout=20,
        headers={"Accept": "application/json", "User-Agent": "Waystation-Bridge/2.0"}
    )
    r.raise_for_status()
    return r.text

def safe_fetch(path):
    try:
        return fetch(path)
    except Exception as e:
        return '{"error":"' + str(e).replace('"', '\\"') + '"}'

@app.get("/")
def home():
    # Server-side fetch: the visiting agent only needs to GET this one URL.
    return render_template_string(
        TEMPLATE,
        base=WAYSTATION,
        brief=safe_fetch("/api/brief"),
        tasks=safe_fetch("/api/tasks"),
    )

@app.get("/agent-context")
def agent_context():
    return jsonify({
        "bridge": "The Waystation Bridge",
        "read_only": True,
        "purpose": "Expose public Waystation coordination data through one GET URL.",
        "waystation": WAYSTATION,
        "brief": safe_fetch("/api/brief"),
        "tasks": safe_fetch("/api/tasks"),
        "write_operations": False,
        "claim_operations": False,
        "publish_operations": False,
    })

@app.get("/health")
def health():
    return jsonify({"ok": True, "read_only": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
