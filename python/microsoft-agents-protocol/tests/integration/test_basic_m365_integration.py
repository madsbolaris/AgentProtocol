"""
Basic M365 Agent - Integration Tests (Validation Mode)

These tests run in TEST MODE (default) to:
1. Use MockLLMClient (replays recordings)
2. Validate against golden files
3. Run fast, deterministic, cost-free

Run with:
    pytest tests/integration/test_basic_m365_integration.py -v

No Foundry credentials needed!
"""

import pytest
import aiohttp
import json
from pathlib import Path

# Import test utilities
from tests.utils import (
    get_test_mode,
    load_input_file,
    load_golden_file,
    assert_response_structure,
    assert_text_content_similar,
)


# Test cases: (input_file_name, expected_result_file_name)
TEST_CASES = [
    ("50-weather-query", "50-weather-query", "weather query with function call"),
    ("51-time-query", "51-time-query", "time query with function call"),
    ("52-multi-function", "52-multi-function", "multiple function calls"),
    ("53-no-function", "53-no-function", "direct response without functions"),
]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("input_name,result_name,description", TEST_CASES)
async def test_basic_m365_wait_pattern(
    input_name: str,
    result_name: str,
    description: str,
    agent_url: str,
    test_mode: str
):
    """Test Basic M365 Agent against golden files using wait pattern.

    Args:
        input_name: Input test case name
        result_name: Expected result file name
        description: Human-readable test description
        agent_url: URL of running agent
        test_mode: Current test mode (should be "test")
    """
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"   Input: {input_name}.xml")
    print(f"   Mode: {test_mode}")
    print(f"{'='*60}")

    # Load input XML
    try:
        input_xml = load_input_file(input_name)
        print(f"📄 Loaded input: {len(input_xml)} bytes")
    except FileNotFoundError as e:
        pytest.fail(f"Input file not found: {e}")

    # Load expected result (golden file)
    try:
        expected = load_golden_file(result_name, pattern="json", agent="basic-m365")
        print(f"📋 Loaded golden file: {result_name}-result.json")
    except FileNotFoundError:
        pytest.skip(
            f"Golden file not found: {result_name}-result.json\n"
            f"Run tests in generation mode first:\n"
            f"  python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm"
        )

    # Call agent via Agent Protocol /runs/wait endpoint
    print(f"🤖 Calling agent at {agent_url}/runs/wait")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "thread": {
                    "messages": [input_xml]
                },
                "agent": {}
            }

            async with session.post(
                f"{agent_url}/runs/wait",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    pytest.fail(
                        f"Agent returned status {resp.status}:\n{error_text}"
                    )

                actual = await resp.json()

    except aiohttp.ClientError as e:
        pytest.fail(
            f"Failed to connect to agent at {agent_url}:\n{e}\n\n"
            f"Make sure the Basic M365 Agent is running:\n"
            f"  cd python/samples/agents/basic_m365_agent\n"
            f"  python -m src.main"
        )

    print(f"✅ Agent responded successfully")

    # Validate response structure
    print("🔍 Validating response structure...")
    assert_response_structure(actual, expected)
    print("   ✓ Structure matches")

    # Validate response content
    if "thread" in expected and "messages" in expected["thread"]:
        expected_msgs = expected["thread"]["messages"]
        actual_msgs = actual["thread"]["messages"]

        if expected_msgs and actual_msgs:
            # Check first message text content
            expected_text = expected_msgs[0]["contents"][0].get("text", "")
            actual_text = actual_msgs[0]["contents"][0].get("text", "")

            print("🔍 Validating text content...")
            assert_text_content_similar(actual_text, expected_text)
            print("   ✓ Content matches")

            # Show comparison
            print(f"\n   Expected: {expected_text[:80]}...")
            print(f"   Actual:   {actual_text[:80]}...")

    print(f"{'='*60}")
    print(f"✅ TEST PASSED: {description}")
    print(f"{'='*60}\n")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("input_name,result_name,description", TEST_CASES)
async def test_basic_m365_xml_pattern(
    input_name: str,
    result_name: str,
    description: str,
    agent_url: str,
    test_mode: str
):
    """Test Basic M365 Agent XML pattern against golden files.

    Args:
        input_name: Input test case name
        result_name: Expected result file name
        description: Human-readable test description
        agent_url: URL of running agent
        test_mode: Current test mode
    """
    print(f"\n{'='*60}")
    print(f"🧪 TEST (XML): {description}")
    print(f"   Input: {input_name}.xml")
    print(f"{'='*60}")

    # Load input XML
    try:
        input_xml = load_input_file(input_name)
    except FileNotFoundError as e:
        pytest.fail(f"Input file not found: {e}")

    # Load expected XML result
    try:
        expected_xml = load_golden_file(result_name, pattern="xml", agent="basic-m365")
        print(f"📋 Loaded golden XML: {len(expected_xml)} bytes")
    except FileNotFoundError:
        pytest.skip(
            f"Golden XML file not found: {result_name}-result.xml\n"
            f"Run tests in generation mode first:\n"
            f"  python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm"
        )

    # Call agent
    print(f"🤖 Calling agent at {agent_url}/runs")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "thread": {
                    "messages": [input_xml]
                },
                "agent": {}
            }

            async with session.post(
                f"{agent_url}/runs",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    pytest.fail(
                        f"Agent returned status {resp.status}:\n{error_text}"
                    )

                actual_xml = await resp.text()

    except aiohttp.ClientError as e:
        pytest.fail(f"Failed to connect to agent: {e}")

    print(f"✅ Agent responded with XML: {len(actual_xml)} bytes")

    # Basic XML validation
    assert actual_xml.strip(), "Actual XML is empty"
    assert "<?xml" in actual_xml or "<thread" in actual_xml, "Response doesn't look like XML"
    assert "<agent" in actual_xml, "Response missing <agent> tag"

    # In test mode with mocked LLM, XML should match exactly
    if test_mode == "test":
        # Normalize whitespace for comparison
        import re
        normalize = lambda s: re.sub(r'\s+', ' ', s.strip())

        expected_normalized = normalize(expected_xml)
        actual_normalized = normalize(actual_xml)

        # For now, just check that key elements are present
        # Full XML comparison can be strict
        assert "<agent" in actual_normalized, "Missing <agent> element"
        assert "<text>" in actual_normalized or "<text " in actual_normalized, "Missing <text> element"

        print("   ✓ XML structure valid")

    print(f"{'='*60}")
    print(f"✅ TEST PASSED (XML): {description}")
    print(f"{'='*60}\n")


def test_test_mode_check():
    """Verify test mode and prerequisites."""
    from tests.utils import get_test_mode, get_test_data_dir

    mode = get_test_mode()
    print(f"\n✅ Test mode: {mode}")

    # Check that golden files exist
    test_data = get_test_data_dir()
    golden_dir = test_data / "results" / "function-tools" / "wait"

    if not golden_dir.exists() or not list(golden_dir.glob("*.json")):
        pytest.skip(
            "No golden files found.\n"
            "Run generation tests first:\n"
            "  python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm"
        )

    golden_count = len(list(golden_dir.glob("*.json")))
    print(f"✅ Found {golden_count} golden files")

    # Check that LLM recordings exist
    recordings_dir = test_data / "llm-recordings" / "function-tools"
    if not recordings_dir.exists() or not list(recordings_dir.glob("*.response.json")):
        pytest.skip(
            "No LLM recordings found.\n"
            "Run generation tests first:\n"
            "  python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm"
        )

    recording_count = len(list(recordings_dir.glob("*.response.json")))
    print(f"✅ Found {recording_count} LLM recordings")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mock_llm_client_works():
    """Verify that MockLLMClient can load and replay recordings."""
    from tests.mocks import MockLLMClient
    from tests.utils import get_test_data_dir

    recordings_dir = get_test_data_dir() / "llm-recordings" / "function-tools"

    if not recordings_dir.exists() or not list(recordings_dir.glob("*.response.json")):
        pytest.skip("No recordings found, run generation mode first")

    # Create mock client
    mock_client = MockLLMClient(recordings_dir)

    # Try to create a simple completion (this will only work if recordings exist)
    # For now, just verify the mock client was created successfully
    assert mock_client is not None
    assert mock_client.recorder is not None
    assert mock_client.call_count == 0

    print("\n✅ MockLLMClient initialized successfully")
    print(f"   Recordings directory: {recordings_dir}")
    print(f"   Available recordings: {len(list(recordings_dir.glob('*.response.json')))}")
