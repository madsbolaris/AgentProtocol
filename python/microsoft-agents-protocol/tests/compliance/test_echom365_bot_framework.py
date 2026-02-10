"""
EchoM365 Bot Framework Compliance Tests

Tests all EchoM365 implementations using Bot Framework format
to verify consistent output across languages.
"""

import pytest
import requests


# Bot configurations
BOTS = {
    "python": {
        "name": "Python EchoM365",
        "port": 3978
    },
    "dotnet": {
        "name": ".NET EchoM365",
        "port": 3979
    },
    "typescript": {
        "name": "TypeScript EchoM365",
        "port": 3980
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


class TestEchoM365Consistency:
    """Test EchoM365 implementations for consistent behavior."""

    def test_simple_echo_format(self, bot_config):
        """Test that all bots use consistent 'you said:' format."""
        bot_key, config = bot_config

        # Send Bot Framework Activity
        url = f"http://localhost:{config['port']}/api/messages"
        payload = {
            "type": "message",
            "text": "Test message",
            "from": {"id": "user-test", "name": "User"},
            "recipient": {"id": "bot", "name": "Bot"},
            "conversation": {"id": "test-conv"},
            "channelId": "test",
            "serviceUrl": "http://test"
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        actual_text = result.get("text", "")

        # Golden standard: "you said: {text}" (lowercase, no counter, no brackets)
        expected_prefix = "you said:"
        expected_text = "you said: Test message"

        # Check exact format
        errors = []

        # Check 1: Should start with lowercase "you said:"
        if not actual_text.startswith(expected_prefix):
            if actual_text.startswith("You said:"):
                errors.append(
                    f"❌ Uses 'You said:' (capital Y) instead of 'you said:' (lowercase)"
                )
            elif actual_text.strip().startswith("["):
                errors.append(
                    f"❌ Includes message counter like '[1]' which should be removed"
                )
            else:
                errors.append(
                    f"❌ Does not start with 'you said:'"
                )

        # Check 2: Should NOT have brackets/counters
        if "[" in actual_text and "]" in actual_text:
            errors.append(
                f"❌ Contains brackets/counter which should be removed"
            )

        # Check 3: Full text comparison (if no other errors)
        if not errors and actual_text.strip() != expected_text:
            errors.append(
                f"❌ Text mismatch:\n"
                f"   Expected: {expected_text!r}\n"
                f"   Actual:   {actual_text.strip()!r}"
            )

        # Report all errors
        if errors:
            error_msg = f"\n\n{config['name']} (port {config['port']}) FAILED:\n"
            error_msg += "\n".join(f"  {err}" for err in errors)
            error_msg += f"\n\n  Actual output: {actual_text!r}\n"
            error_msg += f"  Expected:      {expected_text!r}\n"
            pytest.fail(error_msg)

    def test_multiline_echo_format(self, bot_config):
        """Test echo format with multiline input."""
        bot_key, config = bot_config

        test_input = "Hello\nWorld"
        expected_output = f"you said: {test_input}"

        url = f"http://localhost:{config['port']}/api/messages"
        payload = {
            "type": "message",
            "text": test_input,
            "from": {"id": "user-test", "name": "User"},
            "recipient": {"id": "bot", "name": "Bot"},
            "conversation": {"id": "test-conv"},
            "channelId": "test",
            "serviceUrl": "http://test"
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        result = response.json()
        actual_text = result.get("text", "")

        # Remove any counter prefix like "[1] "
        if actual_text.strip().startswith("["):
            # Extract text after the counter
            parts = actual_text.split("]", 1)
            if len(parts) > 1:
                actual_text = parts[1].strip()

        # Normalize case for "You" vs "you"
        if actual_text.startswith("You said:"):
            actual_text = "y" + actual_text[1:]

        assert actual_text.strip() == expected_output.strip(), (
            f"\n{config['name']} multiline output mismatch:\n"
            f"Expected: {expected_output!r}\n"
            f"Actual:   {actual_text.strip()!r}"
        )
