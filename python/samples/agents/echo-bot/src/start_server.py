import json
import sys
from os import environ
from pathlib import Path
from typing import Any

# Add protocol package to path for development
protocol_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "microsoft-agents-protocol"
if protocol_path.exists():
    sys.path.insert(0, str(protocol_path))

from microsoft_agents.hosting.core import AgentApplication, AgentAuthConfiguration, TurnContext
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft.agents.protocol import add_agent_protocol_routes
from aiohttp.web import Request, Response, Application, run_app, middleware, json_response


def get_port_from_config() -> int | None:
    """Read port from centralized agent-config.json."""
    try:
        config_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "agent-config.json"
        if not config_path.exists():
            return None
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("bots", {}).get("python", {}).get("port")
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
    async def anonymous_entry_point(req: Request) -> Response:
        """Handle messages in anonymous mode without authentication."""
        try:
            # Parse the incoming activity
            activity_data = await req.json()

            # Create a simple Activity object from the data
            from microsoft_agents.activity import Activity
            activity = Activity(**activity_data)

            # 🔧 FIX: Create a NEW adapter instance per request to avoid closure chain memory leak
            # DO NOT use the shared adapter from req.app["adapter"]
            from microsoft_agents.hosting.aiohttp import CloudAdapter
            adapter = CloudAdapter()
            turn_context = TurnContext(adapter, activity)

            # Create a mock connector client to avoid the "Unable to extract ConnectorClient" error
            class MockConnectorClient:
                def __init__(self):
                    self.conversations = self

                async def send_to_conversation(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}

                async def reply_to_activity(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}

            # Store responses sent by the agent
            responses = []

            # Override the adapter's send method BEFORE any use
            # This is safe because we're using a fresh adapter instance
            async def capture_send(context, activities):
                for activity in activities:
                    if hasattr(activity, 'text'):
                        responses.append(activity.text)
                # Return mock resource responses
                return [{"id": f"mock-{i}"} for i in range(len(activities))]

            adapter.send_activities = capture_send

            # Set mock connector client
            turn_context.turn_state["ConnectorClient"] = MockConnectorClient()

            # Process the activity through the agent
            agent: AgentApplication = req.app["agent_app"]
            await agent.on_turn(turn_context)

            # No need to restore - this adapter instance will be garbage collected
            
            # Return the bot's response
            response_text = responses[0] if responses else "OK"
            return json_response({
                "type": "message",
                "text": response_text,
                "from": {"id": "bot"},
                "recipient": activity_data.get("from", {}),
                "conversation": activity_data.get("conversation", {})
            })
                
        except Exception as e:
            import traceback
            print("\n=== Error processing message ===", file=sys.stderr)
            traceback.print_exc()
            print("================================\n", file=sys.stderr)
            return json_response(
                {"error": f"Error processing message: {str(e)}"}, 
                status=500
            )

    async def root_handler(req: Request) -> Response:
        """Root endpoint for connection checks."""
        return json_response({
            "status": "ok",
            "name": "Python Echo Bot",
            "description": "Echo bot running in anonymous mode"
        })

    APP = Application(middlewares=[cors_middleware])
    APP.router.add_get("/", root_handler)
    APP.router.add_post("/api/messages", anonymous_entry_point)
    if auth_configuration:
        APP["agent_configuration"] = auth_configuration
    APP["agent_app"] = agent_application
    APP["adapter"] = agent_application.adapter

    # Add Agent Protocol routes
    # Don't register /api/messages again since we already have it above
    add_agent_protocol_routes(APP, agent_application, messages_path=None)

    try:
        port_from_config = get_port_from_config()
        desired_port = port_from_config or int(environ.get("PORT", 3978))
        run_app(APP, host="localhost", port=desired_port)
    except Exception as error:
        raise error
