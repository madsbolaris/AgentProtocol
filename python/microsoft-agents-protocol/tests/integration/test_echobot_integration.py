"""
EchoBot Integration Tests - Validates against golden files.

This test suite:
1. Connects to running echo bot servers on ports 3978, 3979, 3980
2. Sends test-data/input/*.xml files to each bot
3. Validates responses against test-data/results/echobot/json/ golden files
4. Ensures all three language implementations (Python, C#, TypeScript) behave identically

Run with:
    # Start all echo bots first
    ./scripts/start-all-echo-bots.sh

    # Then run tests
    pytest tests/integration/test_echobot_integration.py -v

    # Or test specific language
    pytest tests/integration/test_echobot_integration.py -v -k python
    pytest tests/integration/test_echobot_integration.py -v -k dotnet
    pytest tests/integration/test_echobot_integration.py -v -k typescript
"""

import pytest
import httpx
import json
from pathlib import Path
from typing import Dict, Any
from lxml import etree

# Import test utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.test_helpers import (
    get_test_data_dir,
    load_golden_file,
    assert_response_structure,
)


# Echo bot server configurations
ECHO_BOT_SERVERS = {
    "python": "http://localhost:3978",
    "dotnet": "http://localhost:3979",
    "typescript": "http://localhost:3980",
}


def xml_to_agent_protocol_message(xml_content: str) -> Dict[str, Any]:
    """
    Convert XML message to Agent Protocol JSON format.

    This matches the conversion in scripts/generate_json_golden_files.py
    """
    root = etree.fromstring(xml_content.encode('utf-8'))

    # Extract role from root element tag
    role = root.tag

    # Build message
    message = {
        "role": role,
        "contents": []
    }

    # Add message-id if present
    if "message-id" in root.attrib:
        message["messageId"] = root.attrib["message-id"]

    # Extract text contents
    for text_elem in root.findall(".//text"):
        content = {
            "kind": "text",
            "text": text_elem.text or ""
        }
        if "audience" in text_elem.attrib:
            content["audience"] = text_elem.attrib["audience"]
        message["contents"].append(content)

    # If no text contents, add empty one
    if not message["contents"]:
        message["contents"].append({"kind": "text", "text": ""})

    return message


def get_input_files():
    """Get all XML input files for testing."""
    test_data_dir = get_test_data_dir()
    input_dir = test_data_dir / "input"

    # Get all XML files except error cases
    xml_files = sorted([
        f for f in input_dir.glob("*.xml")
        if not f.name.startswith("error-") and "errors" not in str(f)
    ])

    return xml_files


@pytest.fixture(scope="session")
def check_servers():
    """Check that all echo bot servers are running before tests."""
    missing_servers = []

    for lang, url in ECHO_BOT_SERVERS.items():
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{url}/health")
                response.raise_for_status()
                print(f"  ✓ {lang} echo bot running at {url}")
        except Exception as e:
            missing_servers.append((lang, url, str(e)))

    if missing_servers:
        error_msg = "\n❌ Echo bot servers not running:\n"
        for lang, url, error in missing_servers:
            error_msg += f"  - {lang} ({url}): {error}\n"
        error_msg += "\nPlease start all echo bots first:\n"
        error_msg += "  ./scripts/start-all-echo-bots.sh\n"
        pytest.skip(error_msg)


# Get test cases from input files
input_files = get_input_files()
test_cases = [(f.stem, f) for f in input_files]


@pytest.mark.integration
@pytest.mark.parametrize("language,base_url", ECHO_BOT_SERVERS.items())
@pytest.mark.parametrize("test_name,input_file", test_cases, ids=lambda x: x[0] if isinstance(x, tuple) else str(x))
def test_echobot_against_golden_files(
    check_servers,
    language: str,
    base_url: str,
    test_name: str,
    input_file: Path
):
    """
    Test echo bot implementation against golden files.

    This test validates that the echo bot:
    1. Accepts the input message
    2. Returns a response matching the golden file structure
    3. Does NOT include the input field (per @visibility("create") in TypeSpec)
    4. Returns appropriate output for user messages
    5. Returns empty output for non-user messages (system, agent, etc.)
    """
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {language} - {test_name}")
    print(f"   Server: {base_url}")
    print(f"   Input: {input_file.name}")
    print(f"{'='*70}")

    # Load input XML
    xml_content = input_file.read_text()
    print(f"📄 Loaded input: {len(xml_content)} bytes")

    # Convert to Agent Protocol message
    message = xml_to_agent_protocol_message(xml_content)
    print(f"📨 Message role: {message['role']}")

    # Create run request
    run_request = {
        "agentId": "echo-agent",
        "input": [message]
    }

    # Send to echo bot
    print(f"🤖 Calling {base_url}/runs/wait")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{base_url}/runs/wait",
                params={"format": "json"},
                json=run_request
            )
            response.raise_for_status()
            actual = response.json()
    except Exception as e:
        pytest.fail(
            f"Failed to connect to {language} echo bot at {base_url}:\n{e}\n\n"
            f"Make sure the echo bot is running:\n"
            f"  ./scripts/start-all-echo-bots.sh"
        )

    print(f"✅ {language} echo bot responded")

    # Load golden file
    try:
        expected = load_golden_file(test_name, pattern="json", agent="echobot")
        print(f"📋 Loaded golden file: {test_name}-result.json")
    except FileNotFoundError:
        pytest.skip(
            f"Golden file not found: {test_name}-result.json\n"
            f"Generate golden files first:\n"
            f"  python scripts/generate_json_golden_files.py"
        )

    # Validate response structure
    print("🔍 Validating response structure...")
    print(f"   Checking: input field is NOT in response (TypeSpec @visibility compliance)")
    print(f"   Checking: status matches expected")
    print(f"   Checking: output structure matches")

    try:
        assert_response_structure(actual, expected)
        print("   ✓ Structure validation passed")
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED for {language}:")
        print(f"   Error: {e}")
        print(f"\n   Actual response:")
        print(f"   {json.dumps(actual, indent=2)}")
        print(f"\n   Expected (golden file):")
        print(f"   {json.dumps(expected, indent=2)}")
        raise

    # Additional validation: Check echo behavior
    if message["role"] == "user":
        # User messages should get echoed
        assert "output" in actual, "User message should produce output"
        assert len(actual["output"]) > 0, "User message should produce non-empty output"

        # Check that output contains expected text
        if actual["output"]:
            output_text = actual["output"][0].get("contents", [{}])[0].get("text", "")
            print(f"   ✓ Output text: {output_text[:50]}...")
    else:
        # Non-user messages should return empty output
        assert "output" in actual, "Response should have output field"
        output = actual.get("output", [])
        assert len(output) == 0, f"Non-user message ({message['role']}) should produce empty output, got: {output}"
        print(f"   ✓ Non-user message correctly returned empty output")

    print(f"{'='*70}")
    print(f"✅ TEST PASSED: {language} - {test_name}")
    print(f"{'='*70}\n")


@pytest.mark.integration
def test_all_servers_respond_to_health_check():
    """Verify all echo bot servers are running and healthy."""
    for lang, url in ECHO_BOT_SERVERS.items():
        print(f"Checking {lang} at {url}...")
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{url}/health")
            assert response.status_code == 200, f"{lang} health check failed"
            data = response.json()
            assert data.get("status") in ["healthy", "ok"], f"{lang} not healthy: {data}"
            print(f"  ✓ {lang} is healthy")


@pytest.mark.integration
def test_input_field_not_in_responses():
    """
    CRITICAL TEST: Verify that input field is NOT in responses.

    Per TypeSpec, input has @visibility("create") which means it should
    ONLY appear in request bodies, NOT in response bodies.

    This test explicitly checks this requirement across all implementations.
    """
    test_message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "test"}]
    }

    run_request = {
        "agentId": "echo-agent",
        "input": [test_message]
    }

    for lang, url in ECHO_BOT_SERVERS.items():
        print(f"\nChecking {lang} for input field visibility compliance...")

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{url}/runs/wait",
                    params={"format": "json"},
                    json=run_request
                )
                response.raise_for_status()
                result = response.json()
        except Exception as e:
            pytest.skip(f"{lang} echo bot not running: {e}")

        # CRITICAL: Response must NOT contain input field
        assert "input" not in result, (
            f"{lang} echo bot VIOLATES TypeSpec @visibility('create') rule!\n"
            f"The 'input' field appears in response but should only be in requests.\n"
            f"Response: {json.dumps(result, indent=2)}"
        )

        print(f"  ✓ {lang} correctly omits input field from response")
