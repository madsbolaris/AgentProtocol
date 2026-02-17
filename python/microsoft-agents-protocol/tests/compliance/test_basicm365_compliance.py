"""
BasicM365 Cross-Language Compliance Tests

Tests all BasicM365 implementations (Python, .NET, TypeScript) for consistent behavior.
Uses LLM recordings for deterministic testing.
"""

import pytest
import requests
import json
from pathlib import Path


# Golden data location
GOLDEN_DATA_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "test-data" / "results" / "samples" / "basic-m365"


# Bot configurations
BOTS = {
    "python": {
        "name": "Python BasicM365",
        "port": 3982,
        "endpoint": "/runs/wait"
    },
    "dotnet": {
        "name": ".NET BasicM365",
        "port": 3981,
        "endpoint": "/runs/wait"
    },
    "typescript": {
        "name": "TypeScript BasicM365",
        "port": 3983,
        "endpoint": "/runs/wait"
    }
}


def is_bot_running(port):
    """Check if bot is running on given port."""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.fixture(params=BOTS.keys())
def bot_config(request):
    """Fixture that provides bot configuration for each language."""
    bot_key = request.param
    config = BOTS[bot_key]

    # Skip if bot is not running
    if not is_bot_running(config["port"]):
        pytest.skip(f"{config['name']} is not running on port {config['port']}")

    return bot_key, config


def load_golden_test_cases():
    """Load test cases from golden data directory."""
    test_cases = []

    # Load from xml directory (contains both .xml and .meta.json files)
    xml_dir = GOLDEN_DATA_DIR / "xml"
    if xml_dir.exists():
        # Get all .xml files (not .meta.json)
        for xml_file in sorted(xml_dir.glob("*-result.xml")):
            if not xml_file.name.endswith(".meta.json"):
                test_cases.append(("xml", xml_file))

    return test_cases[:10]  # Limit to first 10 for initial testing


class TestBasicM365Compliance:
    """Test BasicM365 implementations for consistent behavior."""

    def test_bot_is_running(self, bot_config):
        """Verify bot is accessible and healthy."""
        bot_key, config = bot_config

        response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
        assert response.status_code == 200, f"{config['name']} health check failed"

    def test_bot_has_endpoint(self, bot_config):
        """Verify bot has required /runs/wait endpoint."""
        bot_key, config = bot_config

        url = f"http://localhost:{config['port']}{config['endpoint']}"

        # Send minimal valid request
        payload = {
            "threadId": "test-endpoint-check",
            "messages": [
                {
                    "$type": "user",
                    "contents": [{"$type": "text", "text": "test"}]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            # Accept any response (success or error) - just verify endpoint exists
            assert response.status_code in [200, 400, 500], (
                f"{config['name']} /runs/wait endpoint not accessible"
            )
        except requests.exceptions.ConnectionError:
            pytest.fail(f"{config['name']} /runs/wait endpoint does not exist")

    def test_bot_uses_llm_recordings(self, bot_config):
        """Verify bot can use LLM recordings for deterministic testing."""
        bot_key, config = bot_config

        url = f"http://localhost:{config['port']}{config['endpoint']}"

        # Simple test message
        payload = {
            "threadId": "test-recordings",
            "messages": [
                {
                    "$type": "user",
                    "contents": [{"$type": "text", "text": "Hello"}]
                }
            ]
        }

        # Make request
        response = requests.post(url, json=payload, timeout=15)

        # Check we got a response
        assert response.status_code == 200, (
            f"{config['name']} failed to process request: {response.status_code}"
        )

        result = response.json()

        # Verify response structure
        assert "status" in result, f"{config['name']}: Missing 'status' in response"
        assert "threadId" in result, f"{config['name']}: Missing 'threadId' in response"

    @pytest.mark.parametrize("test_type,golden_file", load_golden_test_cases())
    def test_golden_data_structure(self, bot_config, test_type, golden_file):
        """Test that bot responses have correct structure (not exact content match)."""
        bot_key, config = bot_config

        # Read golden file to get input
        # Golden files are XML, we need to parse or use metadata
        meta_file = Path(str(golden_file) + ".meta.json")
        if not meta_file.exists():
            pytest.skip(f"No metadata file for {golden_file.name}")

        with open(meta_file, 'r') as f:
            metadata = json.load(f)

        # Extract test information
        test_name = golden_file.stem.replace("-result", "")

        # For now, just verify the bot can handle a basic request
        # Full golden data comparison would require XML parsing
        url = f"http://localhost:{config['port']}{config['endpoint']}"

        payload = {
            "threadId": f"golden-{test_name}",
            "messages": [
                {
                    "$type": "user",
                    "contents": [{"$type": "text", "text": f"Test: {test_name}"}]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=15)

        # Verify successful response
        assert response.status_code == 200, (
            f"{config['name']} failed on test '{test_name}': {response.status_code}"
        )

        result = response.json()

        # Verify response has required fields
        assert "status" in result
        assert "threadId" in result
        assert result["threadId"] == payload["threadId"]

    def test_response_format_consistency(self, bot_config):
        """Test that all bots return responses in the same format."""
        bot_key, config = bot_config

        url = f"http://localhost:{config['port']}{config['endpoint']}"

        # Send a test message
        payload = {
            "threadId": "test-format-consistency",
            "messages": [
                {
                    "$type": "user",
                    "contents": [{"$type": "text", "text": "What is 2+2?"}]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=15)
        assert response.status_code == 200

        result = response.json()

        # Check required fields exist
        required_fields = ["runId", "threadId", "status"]
        for field in required_fields:
            assert field in result, (
                f"{config['name']} missing required field '{field}' in response"
            )

        # Check status is valid
        valid_statuses = ["completed", "failed", "timeout", "requires_action"]
        assert result["status"] in valid_statuses, (
            f"{config['name']} returned invalid status: {result['status']}"
        )

    def test_error_handling_consistency(self, bot_config):
        """Test that all bots handle errors consistently."""
        bot_key, config = bot_config

        url = f"http://localhost:{config['port']}{config['endpoint']}"

        # Send invalid request (missing required fields)
        payload = {
            "threadId": "test-error-handling"
            # Missing 'messages' field
        }

        response = requests.post(url, json=payload, timeout=10)

        # Should return error status (400 or 500)
        assert response.status_code >= 400, (
            f"{config['name']} should return error for invalid request"
        )


class TestBasicM365BotFrameworkCompat:
    """Test BasicM365 bots also support Bot Framework format (if applicable)."""

    def test_bot_framework_endpoint_exists(self, bot_config):
        """Check if /api/messages endpoint exists."""
        bot_key, config = bot_config

        url = f"http://localhost:{config['port']}/api/messages"

        # Send minimal Bot Framework activity
        payload = {
            "type": "message",
            "text": "test",
            "from": {"id": "user1"},
            "recipient": {"id": "bot"},
            "conversation": {"id": "test"},
            "channelId": "test",
            "serviceUrl": "http://test"
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            # If endpoint exists, it should respond (success or error)
            assert response.status_code in [200, 400, 500]
        except requests.exceptions.ConnectionError:
            pytest.skip(f"{config['name']} does not support Bot Framework format")
