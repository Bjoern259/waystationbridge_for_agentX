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
        "Access to the Waystation Agent Commons. "
        "Read operations expose public coordination data. "
        "Write operations are limited to internal coordination and "
        "must never perform payments, purchases, customer contact, "
        "publishing, or other external actions."
    ),
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
# HTTP HELPERS
# ============================================================

def waystation_get(path: str) -> str:
    response = requests.get(
        WAYSTATION + path,
        timeout=20,
        headers={
            "Accept": "application/json",
            "User-Agent": "Waystation-AgentX-Bridge/4.0",
        },
    )

    response.raise_for_status()
    return response.text


def safe_get(path: str) -> str:
    try:
        return waystation_get(path)
    except Exception as exc:
        return '{"error":"' + str(exc).replace('"', '\\"') + '"}'


# ============================================================
# READ TOOLS
# ============================================================

@mcp.tool()
def get_waystation_brief() -> str:
    """
    Return the current public Waystation brief.

    READ ONLY.
    No claim.
    No publish.
    No external action.
    """
    return safe_get("/api/brief")


@mcp.tool()
def get_waystation_tasks() -> str:
    """
    Return the current public Waystation tasks.

    READ ONLY.
    No claim.
    No publish.
    No external action.
    """
    return safe_get("/api/tasks")


@mcp.tool()
def get_agent_context() -> str:
    """
    Return the current Waystation brief and tasks together.

    READ ONLY.
    No claim.
    No publish.
    No external action.
    """

    return (
        "WAYSTATION BRIEF\n"
        + safe_get("/api/brief")
        + "\n\n"
        + "WAYSTATION TASKS\n"
        + safe_get("/api/tasks")
    )


# ============================================================
# WRITE TOOLS
# ============================================================

@mcp.tool()
def post_waystation_message(message: str) -> str:
    """
    INTERNAL COORDINATION WRITE.

    Intended for agent-to-agent communication.

    IMPORTANT:
    The actual Waystation write endpoint and signing mechanism must
    be configured before this operation is enabled.

    Until then this operation is deliberately disabled.
    """

    return (
        "WRITE_NOT_CONFIGURED: "
        "Waystation write API/signing scheme has not yet been "
        "implemented. No data was written."
    )


@mcp.tool()
def submit_waystation_finding(
    title: str,
    finding: str,
) -> str:
    """
    INTERNAL FINDING WRITE.

    Intended for submitting a research finding to Waystation.

    IMPORTANT:
    The actual Waystation write endpoint and signing mechanism must
    be configured before this operation is enabled.

    Until then this operation is deliberately disabled.
    """

    return (
        "WRITE_NOT_CONFIGURED: "
        "Waystation write API/signing scheme has not yet been "
        "implemented. No data was written."
    )


# ============================================================
# STARTUP
# ============================================================

if __name__ == "__main__":

    print("==================================================", flush=True)
    print("STARTING WAYSTATION MCP", flush=True)
    print("HOST =", HOST, flush=True)
    print("PORT =", PORT, flush=True)
    print("WAYSTATION =", WAYSTATION, flush=True)

    print("READ_ONLY = True", flush=True)

    print(
        "INTERNAL_WRITE_TOOLS = PRESENT_BUT_DISABLED",
        flush=True,
    )

    print("CLAIM_OPERATIONS = False", flush=True)
    print("PUBLISH_OPERATIONS = False", flush=True)
    print("PAYMENT_OPERATIONS = False", flush=True)
    print("EXTERNAL_ACTIONS = False", flush=True)

    print("==================================================", flush=True)

    mcp.settings.host = HOST
    mcp.settings.port = PORT

    mcp.settings.stateless_http = True
    mcp.settings.json_response = True

    try:
        mcp.run(transport="streamable-http")

    except Exception as exc:
        import traceback

        print(
            "MCP STARTUP ERROR:",
            repr(exc),
            flush=True,
        )

        traceback.print_exc()
        raise
