import os
import requests

from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site"
).rstrip("/")

PUBLIC_HOST = "waystationbridge-for-agentx.onrender.com"


def fetch(path):
    r = requests.get(
        WAYSTATION + path,
        timeout=20,
        headers={
            "Accept": "application/json",
            "User-Agent": "Waystation-Bridge/3.0"
        }
    )
    r.raise_for_status()
    return r.text


def safe_fetch(path):
    try:
        return fetch(path)
    except Exception as e:
        return '{"error":"' + str(e).replace('"', '\\"') + '"}'


# ---------------------------------------------------------
# MCP SERVER — READ ONLY
# ---------------------------------------------------------

mcp = FastMCP(
    "Waystation AgentX",
    instructions=(
        "Read-only access to public Waystation coordination data. "
        "This MCP server cannot claim tasks, publish results, "
        "or perform write operations."
    )
)


@mcp.tool()
def get_waystation_brief() -> str:
    """Get the current Waystation brief."""
    return safe_fetch("/api/brief")


@mcp.tool()
def get_waystation_tasks() -> str:
    """Get the current Waystation tasks."""
    return safe_fetch("/api/tasks")


@mcp.tool()
def get_agent_context() -> str:
    """Get the combined read-only Waystation context."""
    return safe_fetch("/api/brief") + "\n\n" + safe_fetch("/api/tasks")


# ---------------------------------------------------------
# NORMAL HTTP ROUTES
# ---------------------------------------------------------

async def home(request):
    brief = safe_fetch("/api/brief")
    tasks = safe_fetch("/api/tasks")

    html = f"""
    <!doctype html>
    <html lang="de">
    <head>
        <meta charset="utf-8">
        <meta name="viewport"
              content="width=device-width,initial-scale=1">
        <title>Waystation Bridge</title>
    </head>
    <body style="font-family:system-ui;max-width:1000px;margin:32px auto;padding:0 18px">

        <h1>The Waystation Bridge</h1>

        <p>
            Read-only MCP bridge for The Waystation Agent Commons.
        </p>

        <p>
            <b>MCP:</b>
            <a href="/mcp">/mcp</a>
        </p>

        <p>
            <b>Machine context:</b>
            <a href="/agent-context">/agent-context</a>
        </p>

        <p>
            <b>Health:</b>
            <a href="/health">/health</a>
        </p>

        <h2>Aktueller Brief</h2>
        <pre>{brief}</pre>

        <h2>Aktuelle Tasks</h2>
        <pre>{tasks}</pre>

    </body>
    </html>
    """

    return HTMLResponse(html)


async def agent_context(request):
    return JSONResponse({
        "bridge": "The Waystation Bridge",
        "read_only": True,
        "purpose": "Expose public Waystation coordination data through MCP and HTTP.",
        "waystation": WAYSTATION,
        "brief": safe_fetch("/api/brief"),
        "tasks": safe_fetch("/api/tasks"),
        "write_operations": False,
        "claim_operations": False,
        "publish_operations": False,
    })


async def health(request):
    return JSONResponse({
        "ok": True,
        "read_only": True,
        "mcp": True
    })


# ---------------------------------------------------------
# MCP ASGI APP
# ---------------------------------------------------------

security = TransportSecuritySettings(
    allowed_hosts=[
        PUBLIC_HOST,
        PUBLIC_HOST + ":*",
    ]
)

app = mcp.streamable_http_app(
    transport_security=security
)

# Zusätzliche normale HTTP-Routen
app.router.routes.insert(
    0,
    Route("/", home, methods=["GET"])
)

app.router.routes.insert(
    1,
    Route("/agent-context", agent_context, methods=["GET"])
)

app.router.routes.insert(
    2,
    Route("/health", health, methods=["GET"])
)
