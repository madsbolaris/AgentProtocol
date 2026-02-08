"""
Test format query parameter support in Agent Protocol server.

Verifies that endpoints properly handle ?format=json and ?format=xml query parameters.
"""

import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from microsoft.agents.protocol import add_agent_protocol_routes
from lxml import etree


class MockAgentApp:
    """Mock agent application for testing."""
    pass


@pytest_asyncio.fixture
async def test_client():
    """Create test client with Agent Protocol routes."""
    app = web.Application()
    mock_agent = MockAgentApp()
    add_agent_protocol_routes(app, mock_agent)

    server = TestServer(app)
    client = TestClient(server)

    await client.start_server()
    yield client
    await client.close()


class TestFormatParameter:
    """Test format query parameter support."""

    @pytest.mark.asyncio
    async def test_create_and_wait_returns_json_by_default(self, test_client):
        """Test that /runs/wait returns JSON by default (no format parameter)."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Hello"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs/wait", json=request_body)
        assert response.status == 200
        assert "application/json" in response.headers.get("Content-Type", "")

        data = await response.json()
        assert "runId" in data
        assert "output" in data
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_create_and_wait_returns_json_when_format_json(self, test_client):
        """Test that /runs/wait?format=json returns JSON."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Hello"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs/wait?format=json", json=request_body)
        assert response.status == 200
        assert "application/json" in response.headers.get("Content-Type", "")

        data = await response.json()
        assert "runId" in data
        assert "output" in data
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_create_and_wait_returns_xml_when_format_xml(self, test_client):
        """Test that /runs/wait?format=xml returns XML Thread."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Hello"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs/wait?format=xml", json=request_body)
        assert response.status == 200
        assert "application/xml" in response.headers.get("Content-Type", "")

        xml_text = await response.text()

        # Verify it's valid XML
        root = etree.fromstring(xml_text.encode('utf-8'))

        # Verify it's a Thread element
        assert root.tag == "thread"

        # Verify thread attributes
        assert "thread-id" in root.attrib
        assert "status" in root.attrib
        assert root.attrib["status"] == "active"
        assert "created-at" in root.attrib

        # Verify it contains output messages
        messages = list(root)
        assert len(messages) > 0, "Thread should contain at least one message"

    @pytest.mark.asyncio
    async def test_create_run_returns_json_by_default(self, test_client):
        """Test that /runs returns JSON by default."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Hello"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs", json=request_body)
        assert response.status == 201
        assert "application/json" in response.headers.get("Content-Type", "")

        data = await response.json()
        assert "runId" in data
        assert "output" in data

    @pytest.mark.asyncio
    async def test_create_run_returns_xml_when_format_xml(self, test_client):
        """Test that /runs?format=xml returns XML Thread."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Hello"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs?format=xml", json=request_body)
        assert response.status == 201
        assert "application/xml" in response.headers.get("Content-Type", "")

        xml_text = await response.text()

        # Verify it's valid XML
        root = etree.fromstring(xml_text.encode('utf-8'))
        assert root.tag == "thread"
        assert "thread-id" in root.attrib

    @pytest.mark.asyncio
    async def test_xml_thread_contains_assistant_messages(self, test_client):
        """Test that XML Thread contains properly formatted assistant messages."""
        request_body = {
            "agentId": "test-agent",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Test message"}
                    ]
                }
            ]
        }

        response = await test_client.post("/runs/wait?format=xml", json=request_body)
        xml_text = await response.text()
        root = etree.fromstring(xml_text.encode('utf-8'))

        # Find assistant messages
        assistant_messages = root.findall("assistant")
        assert len(assistant_messages) > 0, "Should have at least one assistant message"

        # Verify message structure
        first_msg = assistant_messages[0]
        text_elements = first_msg.findall("text")
        assert len(text_elements) > 0, "Assistant message should have text content"

    @pytest.mark.asyncio
    async def test_health_endpoint_still_works(self, test_client):
        """Test that health endpoint is not affected by format parameter changes."""
        response = await test_client.get("/health")
        assert response.status == 200

        data = await response.json()
        assert data["status"] == "healthy"
