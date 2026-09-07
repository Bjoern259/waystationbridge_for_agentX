import os
import requests

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse


WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site",
).rstrip("/")

PUBLIC_HOST = "waystationbridge-for-agentx.onrender.com"


def fetch(path):
    response = requests.get(
        WAYSTATION + path,
        timeout=20,
        headers={
            "Accept": "application/json",
            "User-Agent": "Waystation-Bridge/3.0",
        },
    )
    response.raise_for_status()
    return response.text


def safe_fetch(path):
    try:
        return fetch(path)
    except Exception as exc:
        return '{"error":"' + str(exc).replace('"', '\\"') + '"}'


mcp = FastMCP(
    "Waystation AgentX",
    instructions=(
        "Read-only access to public Waystation coordination data. "
        "No claim, publish, write, payment, or external-action tools."
    ),
)


@mcp.tool()
def get_waystation_brief() -> str:
    """Return the current public Waystation brief."""
    return safe_fetch("/api/brief")


@mcp.tool()
def get_waystation_tasks() -> str:
    """Return the current public Waystation tasks."""
    return safe_fetch("/api/tasks")


@mcp.tool()
def get_agent_context() -> str:
    """Return the current Waystation brief and tasks."""
    return (
        "WAYSTATION BRIEF\n"
        + safe_fetch("/api/brief")
        + "\n\nWAYSTATION TASKS\n"
        + safe_fetch("/api/tasks")
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    return JSONResponse({
        "ok": True,
        "read_only": True,
        "mcp": True,
    })


security = TransportSecuritySettings(
    allowed_hosts=[
        PUBLIC_HOST,
        PUBLIC_HOST + ":*",
    ]
)

app = mcp.streamable_http_app(
    transport_security=security
)
