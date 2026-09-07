from flask import Flask, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site"
).rstrip("/")

HTML = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Waystation Bridge</title>
<style>
body{font-family:system-ui,sans-serif;max-width:800px;margin:40px auto;padding:0 20px}
button{padding:12px 18px;border:0;border-radius:8px;cursor:pointer}
pre{white-space:pre-wrap;background:#f4f4f4;padding:16px;border-radius:8px}
.small{color:#666}
</style>
</head>
<body>
<h1>The Waystation Bridge</h1>
<p>Read-only Bridge für <code>/api/brief</code> und <code>/api/tasks</code>.</p>
<button onclick="loadData()">Aktuelle Waystation-Daten laden</button>
<p class="small">Diese Version kann nichts claimen und nichts veröffentlichen.</p>
<pre id="out">Noch keine Daten geladen.</pre>
<script>
async function loadData(){
  const out=document.getElementById('out');
  out.textContent='Lade...';
  try{
    const r=await fetch('/api/waystation');
    const data=await r.json();
    out.textContent=JSON.stringify(data,null,2);
  }catch(e){out.textContent='Fehler: '+e}
}
</script>
</body>
</html>"""

def fetch_json(path):
    r = requests.get(WAYSTATION + path, timeout=15,
                     headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()

@app.get("/")
def home():
    return render_template_string(HTML)

@app.get("/api/waystation")
def waystation():
    result = {"source": WAYSTATION, "read_only": True}
    for name, path in [("brief", "/api/brief"), ("tasks", "/api/tasks")]:
        try:
            result[name] = fetch_json(path)
        except Exception as e:
            result[name] = {"error": str(e)}
    return jsonify(result)

@app.get("/health")
def health():
    return jsonify({"ok": True, "read_only": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
