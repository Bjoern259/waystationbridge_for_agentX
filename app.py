import os
import requests

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


# ============================================================
# CONFIG
# ============================================================

WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site",
).rstrip("/")

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))

PUBLIC_HOST = "waystationbridge-for-agentx.onrender.com"


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP(
    "Waystation AgentX",

    instructions=(
        "Read-only access to public Waystation coordination data. "
        "This server does not claim tasks, publish content, write data, "
        "make payments, or perform external actions."
    ),

    # Fix for public deployment behind Render.
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            PUBLIC_HOST,
            PUBLIC_HOST + ":*",
        ],
        allowed_origins=[
            "https://" + PUBLIC_HOST,
        ],
    ),
)


# ============================================================
# WAYSTATION FETCH
# ============================================================

def fetch(path: str) -> str:
    response = requests.get(
        WAYSTATION + path,
        timeout=20,
        headers={
            "Accept": "application/json",
            "User-Agent": "Waystation-AgentX-Bridge/3.0",
        },
    )

    response.raise_for_status()

    return response.text


def safe_fetch(path: str) -> str:
    try:
        return fetch(path)

    except Exception as exc:
        error = str(exc).replace('"', '\\"')

        return '{"error":"' + error + '"}'


# ============================================================
# MCP TOOLS
# ============================================================

@mcp.tool()
def get_waystation_brief() -> str:
    """
    Return the current public Waystation brief.

    Read-only.
    No actions are performed.
    """

    return safe_fetch("/api/brief")


@mcp.tool()
def get_waystation_tasks() -> str:
    """
    Return the current public Waystation tasks.

    Read-only.
    No actions are performed.
    """

    return safe_fetch("/api/tasks")


@mcp.tool()
def get_agent_context() -> str:
    """
    Return the current Waystation brief and tasks together.

    Read-only.
    No actions are performed.
    """

    return (
        "WAYSTATION BRIEF\n"
        + safe_fetch("/api/brief")
        + "\n\n"
        + "WAYSTATION TASKS\n"
        + safe_fetch("/api/tasks")
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "==================================================",
        flush=True,
    )

    print(
        "STARTING WAYSTATION MCP",
        flush=True,
    )

    print(
        "HOST =",
        HOST,
        flush=True,
    )

    print(
        "PORT =",
        PORT,
        flush=True,
    )

    print(
        "WAYSTATION =",
        WAYSTATION,
        flush=True,
    )

    print(
        "READ_ONLY = True",
        flush=True,
    )

    print(
        "CLAIM_OPERATIONS = False",
        flush=True,
    )

    print(
        "PUBLISH_OPERATIONS = False",
        flush=True,
    )

    print(
        "WRITE_OPERATIONS = False",
        flush=True,
    )

    print(
        "==================================================",
        flush=True,
    )

    # MCP SDK 1.29.1 takes host/port from mcp.settings.
    mcp.settings.host = HOST
    mcp.settings.port = PORT

    # Claude does not need session state for our three read-only tools.
    mcp.settings.stateless_http = True

    # Return JSON responses for Streamable HTTP.
    mcp.settings.json_response = True

    try:

        mcp.run(
            transport="streamable-http",
        )

    except Exception as exc:

        import traceback

        print(
            "MCP STARTUP ERROR:",
            repr(exc),
            flush=True,
        )

        traceback.print_exc()

        raise
