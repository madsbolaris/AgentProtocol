"""
EchoM365 Golden Data Compliance Tests

Tests all EchoM365 implementations (Python, .NET, TypeScript) against golden data sets
to ensure consistent behavior across languages.
"""

import pytest
import json
import requests
from pathlib import Path


# Golden data location
GOLDEN_DATA_DIR = Path(__file__).parent.parent.parent.parent.parent.parent / "test-data" / "results" / "samples" / "echo-m365"


# Bot configurations
BOTS = {
    "python": {
        "name": "Python EchoM365",
        "port": 3978,
        "endpoint": "/runs/wait"
    },
    "dotnet": {
        "name": ".NET EchoM365",
        "port": 3979,
        "endpoint": "/runs/wait"
    },
    "typescript": {
        "name": "TypeScript EchoM365",
        "port": 3980,
        "endpoint": "/runs/wait"
    }
}


def load_golden_data_files():
    """Load all golden data test cases."""
    test_files = []

    # Load from xml results directory
    xml_dir = GOLDEN_DATA_DIR / "xml"
    if xml_dir.exists():
        for file_path in xml_dir.glob("*-result.json"):
            test_files.append(("xml", file_path))

    return test_files


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


class TestEchoM365GoldenData:
    """Test EchoM365 implementations against golden data."""

    @pytest.mark.parametrize("test_type,golden_file", load_golden_data_files())
    def test_golden_data_output(self, bot_config, test_type, golden_file):
        """Test that bot output matches golden data."""
        bot_key, config = bot_config

        # Load golden data
        with open(golden_file, 'r') as f:
            golden = json.load(f)

        # Extract input message
        if not golden.get("input") or len(golden["input"]) == 0:
            pytest.skip(f"No input in golden file {golden_file.name}")

        input_message = golden["input"][0]
        expected_output = golden.get("output", [])

        if len(expected_output) == 0:
            pytest.skip(f"No expected output in golden file {golden_file.name}")

        # Send request to bot
        url = f"http://localhost:{config['port']}{config['endpoint']}"
        payload = {
            "threadId": f"test-golden-{golden_file.stem}",
            "messages": [
                {
                    "$type": "user",
                    "contents": input_message["contents"]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            pytest.fail(f"Request failed for {config['name']}: {e}")

        result = response.json()

        # Extract actual output
        actual_messages = result.get("messages", [])
        if len(actual_messages) == 0:
            pytest.fail(f"{config['name']}: No messages in response")

        actual_output = actual_messages[-1]  # Get last message (agent response)

        # Compare output text
        expected_text = expected_output[0]["contents"][0]["text"]
        actual_contents = actual_output.get("contents", [])

        if len(actual_contents) == 0:
            pytest.fail(f"{config['name']}: No contents in output message")

        actual_text = actual_contents[0].get("text", "")

        # Normalize for comparison (remove leading/trailing whitespace, normalize newlines)
        expected_normalized = expected_text.strip()
        actual_normalized = actual_text.strip()

        # Check if output matches
        assert actual_normalized == expected_normalized, (
            f"\n{config['name']} output mismatch for {golden_file.name}:\n"
            f"Expected: {expected_normalized!r}\n"
            f"Actual:   {actual_normalized!r}\n"
            f"Bot:      {bot_key}"
        )

    def test_output_format_consistency(self, bot_config):
        """Test that all bots use the same output format."""
        bot_key, config = bot_config

        # Send a simple test message
        url = f"http://localhost:{config['port']}{config['endpoint']}"
        payload = {
            "threadId": "test-consistency",
            "messages": [
                {
                    "$type": "user",
                    "contents": [{"$type": "text", "text": "Test message"}]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            pytest.fail(f"Request failed for {config['name']}: {e}")

        result = response.json()
        actual_messages = result.get("messages", [])

        if len(actual_messages) == 0:
            pytest.fail(f"{config['name']}: No messages in response")

        actual_text = actual_messages[-1]["contents"][0]["text"]

        # Check format: should start with "you said:" (lowercase, no brackets)
        assert actual_text.startswith("you said:"), (
            f"{config['name']} output format incorrect:\n"
            f"Expected to start with 'you said:' (lowercase)\n"
            f"Actual: {actual_text!r}"
        )

        # Should NOT have brackets/counters like "[1]"
        assert not actual_text.strip().startswith("["), (
            f"{config['name']} should not include message counter:\n"
            f"Actual: {actual_text!r}"
        )

        # Should NOT have capital Y
        assert not actual_text.startswith("You said:"), (
            f"{config['name']} should use lowercase 'you said:', not 'You said:':\n"
            f"Actual: {actual_text!r}"
        )
