import json
import sys
from os import environ
from pathlib import Path

# Add protocol package to path for development
protocol_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol"
if protocol_path.exists():
    sys.path.insert(0, str(protocol_path))

from aiohttp.web import Application, run_app, middleware, Response, json_response, Request
from microsoft.agents.protocol import add_agent_protocol_routes

# Import the emoji chat bot agent
try:
    from .emoji_chat_bot import create_agent_host
except ImportError:
    from emoji_chat_bot import create_agent_host


def get_port_from_config() -> int | None:
    """Read port from centralized agent-config.json."""
    try:
        config_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "agent-config.json"
        if not config_path.exists():
            return None
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("bots", {}).get("python-emoji-chat", {}).get("port")
    except Exception:
        return None


@middleware
async def cors_middleware(request, handler):
    """Add CORS headers for development."""
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response

    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response


async def root_handler(req: Request) -> Response:
    """Root endpoint for connection checks."""
    return json_response({
        "status": "ok",
        "name": "Python Emoji Chat Bot",
        "description": "Emoji bot with function calling and reaction handling"
    })


def main():
    """Start the emoji chat bot HTTP server with Agent Protocol routes."""
    print("=" * 60)
    print("Emoji Chat Bot - Agent Protocol Server")
    print("=" * 60)
    print("\nFeatures:")
    print("  🎨 Add emoji reactions to messages")
    print("  💡 Suggest emojis based on sentiment")
    print("  📊 Track conversation statistics")
    print("  🎉 Handle system events (user joined/left)")
    print("\nPress Ctrl+C to stop.\n")

    # Create the agent host
    agent_host = create_agent_host()

    # Get the underlying agent application for protocol routes
    # The AgentHost wraps an AgentApplication
    agent_application = agent_host._agent_application

    # Create aiohttp application
    app = Application(middlewares=[cors_middleware])
    app.router.add_get("/", root_handler)

    # Add Agent Protocol routes (/health, /runs/wait, /runs/stream, etc.)
    add_agent_protocol_routes(app, agent_application)

    # Determine port
    port_from_config = get_port_from_config()
    desired_port = port_from_config or int(environ.get("PORT", 3985))

    print(f"Starting server on http://localhost:{desired_port}")
    print(f"Agent Protocol endpoints:")
    print(f"  - GET  http://localhost:{desired_port}/health")
    print(f"  - GET  http://localhost:{desired_port}/agent-card")
    print(f"  - POST http://localhost:{desired_port}/runs/wait")
    print(f"  - POST http://localhost:{desired_port}/runs/stream")
    print()

    try:
        run_app(app, host="localhost", port=desired_port)
    except KeyboardInterrupt:
        print("\n\nEmoji Chat Bot stopped.")
    except Exception as error:
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
