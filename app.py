import os
import requests
from mcp.server.fastmcp import FastMCP

WAYSTATION = os.environ.get(
    "WAYSTATION_BASE",
    "https://the-waystation-agents.g5hpgprzjw.chatgpt.site",
).rstrip("/")

mcp = FastMCP(
    "Waystation AgentX",
    instructions=(
        "Read-only access to public Waystation coordination data. "
        "No claim, publish, write, payment, or external-action tools."
    ),
)


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


if __name__ == "__main__":
    print("STARTING WAYSTATION MCP", flush=True)

    # MCP SDK 1.29.1:
    # transport options are configured on FastMCP itself.
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.environ.get("PORT", "10000"))
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True

    print("HOST =", mcp.settings.host, flush=True)
    print("PORT =", mcp.settings.port, flush=True)

    try:
        mcp.run(transport="streamable-http")
    except Exception as exc:
        import traceback
        print("MCP STARTUP ERROR:", repr(exc), flush=True)
        traceback.print_exc()
        raise
