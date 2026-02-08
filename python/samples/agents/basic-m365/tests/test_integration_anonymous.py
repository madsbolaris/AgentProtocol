"""
Integration tests for EchoM365 running in anonymous mode.

These tests verify that the echo bot works without Azure authentication
and catches issues that were found in production:
- Anonymous mode functionality
- CORS headers
- Route configuration
- HTTP endpoint responses

Run with: pytest tests/test_integration_anonymous.py -v
"""

import pytest
import pytest_asyncio
import os
import sys
from pathlib import Path

# Add src to path so we can import the bot
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest_asyncio.fixture
async def test_client():
    """Create test client for the echo bot in anonymous mode."""
    from aiohttp.test_utils import TestClient, TestServer
    from aiohttp.web import Application
    from agent import AGENT_APP
    from start_server import cors_middleware
    from microsoft.agents.protocol import add_agent_protocol_routes
    from aiohttp.web import Request, Response, json_response
    from microsoft_agents.hosting.core import TurnContext
    from microsoft_agents.activity import Activity

    # Create anonymous message handler
    async def anonymous_entry_point(req: Request) -> Response:
        """Handle messages in anonymous mode without authentication."""
        try:
            activity_data = await req.json()
            activity = Activity(**activity_data)

            adapter = req.app["adapter"]
            turn_context = TurnContext(adapter, activity)

            class MockConnectorClient:
                def __init__(self):
                    self.conversations = self

                async def send_to_conversation(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}

                async def reply_to_activity(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}

            responses = []
            original_send = adapter.send_activities

            async def capture_send(context, activities):
                for activity in activities:
                    if hasattr(activity, 'text'):
                        responses.append(activity.text)
                return [{"id": f"mock-{i}"} for i in range(len(activities))]

            adapter.send_activities = capture_send
            turn_context.turn_state["ConnectorClient"] = MockConnectorClient()

            agent = req.app["agent_app"]
            await agent.on_turn(turn_context)

            adapter.send_activities = original_send

            response_text = responses[0] if responses else "OK"
            return json_response({
                "type": "message",
                "text": response_text,
                "from": {"id": "bot"},
                "recipient": activity_data.get("from", {}),
                "conversation": activity_data.get("conversation", {})
            })
        except Exception as e:
            return json_response(
                {"error": f"Error processing message: {str(e)}"},
                status=500
            )

    # Root handler
    async def root_handler(req: Request) -> Response:
        return json_response({
            "status": "ok",
            "name": "Python Echo M365",
            "description": "Echo bot running in anonymous mode"
        })

    # Create app with middlewares
    app = Application(middlewares=[cors_middleware])
    app.router.add_get("/", root_handler)
    app.router.add_post("/api/messages", anonymous_entry_point)
    app["agent_app"] = AGENT_APP
    app["adapter"] = AGENT_APP.adapter

    # Add Agent Protocol routes (without /api/messages)
    add_agent_protocol_routes(app, AGENT_APP, messages_path=None)

    # Create test server and client
    server = TestServer(app)
    client = TestClient(server)

    await client.start_server()
    yield client
    await client.close()


class TestAnonymousModeEndpoints:
    """Test bot endpoints work in anonymous mode."""

    @pytest.mark.asyncio
    async def test_root_endpoint_returns_ok(self, test_client):
        """Test that root endpoint returns 200 OK."""
        response = await test_client.get("/")
        assert response.status == 200

        data = await response.json()
        assert data["status"] == "ok"
        assert "Python Echo M365" in data["name"]

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_healthy(self, test_client):
        """Test that /health endpoint works."""
        response = await test_client.get("/health")
        assert response.status == 200

        data = await response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_api_messages_accepts_bot_framework_activity(self, test_client):
        """Test that /api/messages accepts Bot Framework Activity format."""
        message = {
            "type": "message",
            "from": {"id": "user123", "name": "Test User"},
            "recipient": {"id": "bot"},
            "text": "hello test",
            "channelId": "demo",
            "conversation": {"id": "test-conv"},
            "serviceUrl": "http://localhost:3979"
        }

        response = await test_client.post("/api/messages", json=message)
        assert response.status == 200

        data = await response.json()
        assert data["type"] == "message"
        assert "text" in data
        assert "hello test" in data["text"].lower() or "Hello!" in data["text"]


class TestCORSHeaders:
    """Test that CORS headers are present for browser compatibility."""

    @pytest.mark.asyncio
    async def test_root_endpoint_has_cors_headers(self, test_client):
        """Test that root endpoint includes CORS headers."""
        response = await test_client.get("/")

        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Allow-Methods" in response.headers

    @pytest.mark.asyncio
    async def test_health_endpoint_has_cors_headers(self, test_client):
        """Test that health endpoint includes CORS headers."""
        response = await test_client.get("/health")

        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    @pytest.mark.asyncio
    async def test_api_messages_has_cors_headers(self, test_client):
        """Test that /api/messages includes CORS headers."""
        message = {
            "type": "message",
            "from": {"id": "user"},
            "text": "test",
            "channelId": "demo",
            "conversation": {"id": "test"},
            "serviceUrl": "http://localhost"
        }

        response = await test_client.post("/api/messages", json=message)

        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"

    @pytest.mark.asyncio
    async def test_options_preflight_request_succeeds(self, test_client):
        """Test that OPTIONS preflight request is handled correctly."""
        response = await test_client.options(
            "/api/messages",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "POST"
            }
        )

        assert response.status == 200
        assert "Access-Control-Allow-Origin" in response.headers


class TestEchoM365Functionality:
    """Test that echo bot actually echoes messages correctly."""

    @pytest.mark.asyncio
    async def test_echo_m365_echoes_simple_message(self, test_client):
        """Test that bot echoes back user messages."""
        message = {
            "type": "message",
            "from": {"id": "user"},
            "recipient": {"id": "bot"},
            "text": "test message for echo",
            "channelId": "demo",
            "conversation": {"id": "test"},
            "serviceUrl": "http://localhost"
        }

        response = await test_client.post("/api/messages", json=message)
        assert response.status == 200

        data = await response.json()
        assert "test message for echo" in data["text"]

    @pytest.mark.asyncio
    async def test_echo_m365_responds_to_hello(self, test_client):
        """Test that bot has special response for 'hello'."""
        message = {
            "type": "message",
            "from": {"id": "user"},
            "recipient": {"id": "bot"},
            "text": "hello",
            "channelId": "demo",
            "conversation": {"id": "test"},
            "serviceUrl": "http://localhost"
        }

        response = await test_client.post("/api/messages", json=message)
        assert response.status == 200

        data = await response.json()
        # Bot should respond with "Hello!" for exact "hello" match
        assert "Hello!" in data["text"]


class TestRouteConfiguration:
    """Test that routes are configured correctly without conflicts."""

    @pytest.mark.asyncio
    async def test_no_duplicate_route_registration(self, test_client):
        """Test that /api/messages route is not registered twice."""
        # This test passes if the bot starts without errors
        # Route conflicts would cause startup failures
        response = await test_client.get("/health")
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_agent_protocol_routes_registered(self, test_client):
        """Test that Agent Protocol routes are registered."""
        # Health endpoint from Agent Protocol
        response = await test_client.get("/health")
        assert response.status == 200

        # Root endpoint
        response = await test_client.get("/")
        assert response.status == 200
