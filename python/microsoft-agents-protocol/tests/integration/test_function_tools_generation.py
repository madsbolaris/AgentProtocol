"""
Function Tools Agent - Generation Mode Tests

These tests run in GENERATION MODE to:
1. Call real Foundry LLM
2. Record LLM interactions
3. Create golden files (expected outputs)

Run with:
    export TEST_MODE=generate
    export FOUNDRY_ENDPOINT=https://...
    export FOUNDRY_API_KEY=...
    export FOUNDRY_MODEL_DEPLOYMENT=gpt-5-nano
    pytest tests/integration/test_function_tools_generation.py -v

This creates:
- test-data/llm-recordings/basic-m365/*.json (LLM recordings)
- test-data/results/basic-m365/json/*.json (golden files)
"""

import pytest
import aiohttp
import json
import sys
from pathlib import Path

# Import test utilities
from tests.utils import (
    get_test_mode,
    load_input_file,
    save_golden_file,
    get_test_data_dir,
)


# Test cases: (input_file_name, expected_result_file_name)
TEST_CASES = [
    ("50-weather-query", "50-weather-query"),
    ("51-time-query", "51-time-query"),
    ("52-multi-function", "52-multi-function"),
    ("53-no-function", "53-no-function"),
]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.generation
@pytest.mark.parametrize("input_name,result_name", TEST_CASES)
async def test_function_tools_generation_wait(
    input_name: str,
    result_name: str,
    agent_url: str,
    test_mode: str
):
    """Generate golden files for Function Tools Agent using wait pattern.

    Args:
        input_name: Input test case name (e.g., "50-weather-query")
        result_name: Result file name (usually same as input)
        agent_url: URL of running agent
        test_mode: Current test mode (should be "generate")
    """
    # Verify we're in generation mode
    if test_mode != "generate":
        pytest.skip("This test only runs in generation mode (TEST_MODE=generate)")

    print(f"\n{'='*60}")
    print(f"🏗️  GENERATION MODE: {input_name}")
    print(f"{'='*60}")

    # Load input XML
    try:
        input_xml = load_input_file(input_name)
        print(f"📄 Input: {input_name}.xml")
    except FileNotFoundError as e:
        pytest.fail(f"Input file not found: {e}")

    # Call agent via Agent Protocol /runs/wait endpoint
    print(f"🤖 Calling Function Tools Agent at {agent_url}/runs/wait")

    try:
        async with aiohttp.ClientSession() as session:
            # Build request payload
            payload = {
                "thread": {
                    "messages": [input_xml]
                },
                "agent": {}
            }

            # Call agent
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

                result = await resp.json()

    except aiohttp.ClientError as e:
        pytest.fail(
            f"Failed to connect to agent at {agent_url}:\n{e}\n\n"
            f"Make sure the Function Tools Agent is running:\n"
            f"  cd python/samples/agents/function_tools_agent\n"
            f"  python -m src.main"
        )

    # Validate result structure (run format)
    assert "status" in result, "Result missing 'status' field"
    assert "runId" in result, "Result missing 'runId' field"
    assert "output" in result, "Result missing 'output' field"

    print(f"✅ Agent responded with status: {result['status']}")
    print(f"📋 Run ID: {result['runId']}")

    # Check for output messages
    output_msgs = result.get("output", [])
    msg_count = len(output_msgs)
    print(f"📨 Received {msg_count} output message(s)")

    if msg_count > 0:
        first_msg = output_msgs[0]
        if "contents" in first_msg and len(first_msg["contents"]) > 0:
            text = first_msg["contents"][0].get("text", "")
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"💬 Response preview: {preview}")

    # Save golden file
    save_golden_file(result, result_name, pattern="json", agent="basic-m365")
    print(f"💾 Saved golden file: test-data/results/basic-m365/json/{result_name}-result.json")

    # Check that LLM recordings were created
    recordings_dir = get_test_data_dir() / "llm-recordings" / "basic-m365"
    recording_count = len(list(recordings_dir.glob("*.response.json")))
    print(f"📹 Total LLM recordings: {recording_count}")

    print(f"{'='*60}")
    print(f"✅ GENERATION COMPLETE: {input_name}")
    print(f"{'='*60}\n")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.generation
@pytest.mark.parametrize("input_name,result_name", TEST_CASES)
async def test_function_tools_generation_xml(
    input_name: str,
    result_name: str,
    agent_url: str,
    test_mode: str
):
    """Generate golden XML files for Function Tools Agent.

    Args:
        input_name: Input test case name
        result_name: Result file name
        agent_url: URL of running agent
        test_mode: Current test mode (should be "generate")
    """
    # Verify we're in generation mode
    if test_mode != "generate":
        pytest.skip("This test only runs in generation mode (TEST_MODE=generate)")

    print(f"\n{'='*60}")
    print(f"🏗️  GENERATION MODE (XML): {input_name}")
    print(f"{'='*60}")

    # Load input XML
    try:
        input_xml = load_input_file(input_name)
        print(f"📄 Input: {input_name}.xml")
    except FileNotFoundError as e:
        pytest.fail(f"Input file not found: {e}")

    # Call agent via Agent Protocol /runs endpoint (returns XML)
    print(f"🤖 Calling Function Tools Agent at {agent_url}/runs")

    try:
        async with aiohttp.ClientSession() as session:
            # Build request payload
            payload = {
                "thread": {
                    "messages": [input_xml]
                },
                "agent": {}
            }

            # Call agent with format=xml query parameter
            async with session.post(
                f"{agent_url}/runs?format=xml",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    pytest.fail(
                        f"Agent returned status {resp.status}:\n{error_text}"
                    )

                # Response should be XML
                result_xml = await resp.text()

    except aiohttp.ClientError as e:
        pytest.fail(
            f"Failed to connect to agent at {agent_url}:\n{e}\n\n"
            f"Make sure the Function Tools Agent is running:\n"
            f"  cd python/samples/agents/function_tools_agent\n"
            f"  python -m src.main"
        )

    # Validate XML
    assert result_xml.strip(), "Result XML is empty"
    assert "<?xml" in result_xml or "<thread" in result_xml, "Result doesn't look like XML"

    print(f"✅ Agent responded with XML ({len(result_xml)} chars)")

    # Save golden file
    save_golden_file(result_xml, result_name, pattern="xml", agent="basic-m365")
    print(f"💾 Saved golden file: test-data/results/basic-m365/xml/{result_name}-result.xml")

    print(f"{'='*60}")
    print(f"✅ GENERATION COMPLETE (XML): {input_name}")
    print(f"{'='*60}\n")


def test_generation_mode_check():
    """Verify we're actually in generation mode."""
    mode = get_test_mode()
    if mode != "generate":
        pytest.skip(
            "These tests only run in generation mode.\n"
            "Set TEST_MODE=generate to run:\n"
            "  export TEST_MODE=generate\n"
            "  export FOUNDRY_ENDPOINT=https://...\n"
            "  export FOUNDRY_API_KEY=...\n"
            "  pytest tests/integration/test_function_tools_generation.py -v"
        )

    # Verify Foundry credentials are set
    import os
    if not os.getenv("FOUNDRY_ENDPOINT") or not os.getenv("FOUNDRY_API_KEY"):
        pytest.fail(
            "FOUNDRY_ENDPOINT and FOUNDRY_API_KEY must be set in generation mode.\n"
            "Set them before running:\n"
            "  export FOUNDRY_ENDPOINT=https://...\n"
            "  export FOUNDRY_API_KEY=..."
        )

    print("\n✅ Generation mode check passed")
    print(f"   Mode: {mode}")
    print(f"   Endpoint: {os.getenv('FOUNDRY_ENDPOINT')}")
    print(f"   Model: {os.getenv('FOUNDRY_MODEL_DEPLOYMENT', 'gpt-5-nano')}")
