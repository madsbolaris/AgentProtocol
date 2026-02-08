import json
import sys
from os import environ
from pathlib import Path

# Add protocol package to path for development
protocol_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol"
if protocol_path.exists():
    sys.path.insert(0, str(protocol_path))

from microsoft_agents.hosting.core import AgentApplication, AgentAuthConfiguration
from microsoft_agents.hosting.aiohttp import (
    start_agent_process,
    CloudAdapter,
)
from microsoft.agents.protocol import add_agent_protocol_routes
from aiohttp.web import Request, Response, Application, run_app, middleware


def get_port_from_config() -> int | None:
    """Read port from centralized agent-config.json."""
    try:
        config_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "agent-config.json"
        if not config_path.exists():
            return None
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("bots", {}).get("python-basic-m365", {}).get("port")
    except Exception:
        return None


@middleware
async def cors_middleware(request, handler):
    """Add CORS headers to all responses for development."""
    if request.method == "OPTIONS":
        # Handle preflight requests
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def start_server(
    agent_application: AgentApplication, auth_configuration: AgentAuthConfiguration = None
):
    async def entry_point(req: Request) -> Response:
        agent: AgentApplication = req.app["agent_app"]
        adapter: CloudAdapter = req.app["adapter"]
        return await start_agent_process(
            req,
            agent,
            adapter,
        )

    APP = Application(middlewares=[cors_middleware])
    APP.router.add_post("/api/messages", entry_point)
    if auth_configuration:
        APP["agent_configuration"] = auth_configuration
    APP["agent_app"] = agent_application
    APP["adapter"] = agent_application.adapter

    # Add Agent Protocol routes
    # Don't register /api/messages again since we already have it above
    # Use None to skip the messages_path registration
    add_agent_protocol_routes(APP, agent_application, messages_path=None)

    try:
        port_from_config = get_port_from_config()
        desired_port = port_from_config or int(environ.get("PORT", 3982))
        print(f"🚀 Basic M365 Agent starting on http://localhost:{desired_port}")
        print(f"📡 Agent Protocol routes available at:")
        print(f"   - GET  /health")
        print(f"   - POST /runs")
        print(f"   - POST /runs/wait")
        print(f"   - POST /runs/stream")
        run_app(APP, host="localhost", port=desired_port)
    except Exception as error:
        raise error
