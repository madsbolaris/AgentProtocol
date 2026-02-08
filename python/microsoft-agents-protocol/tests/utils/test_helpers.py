"""
Test helper utilities for LLM testing.

Provides utilities for:
- Mode detection (generate vs test)
- LLM client creation
- Golden file management
- Test data access
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

from openai import AsyncOpenAI


TestMode = Literal["generate", "test"]


def get_test_mode() -> TestMode:
    """Get current test mode from environment.

    Returns:
        "generate" if TEST_MODE=generate, otherwise "test"

    Example:
        if get_test_mode() == "generate":
            save_golden_file(result)
        else:
            assert result == load_golden_file()
    """
    mode = os.getenv("TEST_MODE", "test").lower()
    if mode not in ("generate", "test"):
        raise ValueError(
            f"Invalid TEST_MODE: {mode}. Must be 'generate' or 'test'."
        )
    return mode  # type: ignore


def create_llm_client(
    recordings_dir: Optional[Path] = None,
    test_mode: Optional[TestMode] = None
) -> "MockLLMClient":
    """Create LLM client for test mode.

    In test mode, creates MockLLMClient that replays recordings.

    Note: LLM recording (generation mode) is now done by the .NET BasicM365Agent bot.
    Use: python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm

    Args:
        recordings_dir: Directory for recordings (default: test-data/llm-recordings/basic-m365)
        test_mode: Force specific mode (default: from environment)

    Returns:
        MockLLMClient that replays recorded LLM interactions

    Raises:
        ValueError: If called in generation mode (use .NET bot instead)
    """
    if test_mode is None:
        test_mode = get_test_mode()

    if recordings_dir is None:
        recordings_dir = get_test_data_dir() / "llm-recordings" / "basic-m365"

    if test_mode == "generate":
        # Generation mode: use .NET bot with recording
        raise ValueError(
            "LLM recording (generation mode) is now done by the .NET BasicM365Agent bot.\n"
            "Use: python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm\n"
            "\n"
            "The .NET bot will:\n"
            "1. Generate golden files from .NET (canonical source)\n"
            "2. Record LLM interactions to test-data/llm-recordings/basic-m365/\n"
            "\n"
            "Then run Python tests in test mode to validate against those recordings."
        )

    else:
        # Test mode: use mock LLM
        from ..mocks import MockLLMClient
        return MockLLMClient(recordings_dir)


def get_test_data_dir() -> Path:
    """Get path to test-data directory.

    Returns:
        Absolute path to test-data directory
    """
    # Assumes test-data is at repository root
    # Walk up from tests/ directory
    current = Path(__file__).resolve()

    # Go up to find repository root (has test-data/ dir)
    for parent in current.parents:
        test_data = parent / "test-data"
        if test_data.exists() and test_data.is_dir():
            return test_data

    # Fallback: assume standard structure
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    return repo_root / "test-data"


def load_golden_file(
    test_name: str,
    pattern: Literal["json", "xml"] = "json",
    agent: str = "function-tools"
) -> Dict[str, Any]:
    """Load golden file for comparison.

    Args:
        test_name: Test case name (e.g., "50-weather-query")
        pattern: Test pattern ("json" or "xml")
        agent: Agent name (default: "function-tools")

    Returns:
        Parsed golden file content

    Raises:
        FileNotFoundError: If golden file doesn't exist
    """
    test_data_dir = get_test_data_dir()

    if pattern == "json":
        golden_path = test_data_dir / "results" / agent / "json" / f"{test_name}-result.json"

        if not golden_path.exists():
            raise FileNotFoundError(
                f"Golden file not found: {golden_path}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )

        with open(golden_path, 'r') as f:
            return json.load(f)

    elif pattern == "xml":
        golden_path = test_data_dir / "results" / agent / "xml" / f"{test_name}-result.xml"

        if not golden_path.exists():
            raise FileNotFoundError(
                f"Golden file not found: {golden_path}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )

        with open(golden_path, 'r') as f:
            return f.read()

    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def save_golden_file(
    content: Union[Dict[str, Any], str],
    test_name: str,
    pattern: Literal["json", "xml"] = "json",
    agent: str = "function-tools"
):
    """Save golden file.

    Args:
        content: Content to save (dict for JSON, str for XML)
        test_name: Test case name (e.g., "50-weather-query")
        pattern: Test pattern ("json" or "xml")
        agent: Agent name (default: "function-tools")
    """
    test_data_dir = get_test_data_dir()

    if pattern == "json":
        golden_path = test_data_dir / "results" / agent / "json" / f"{test_name}-result.json"
        golden_path.parent.mkdir(parents=True, exist_ok=True)

        with open(golden_path, 'w') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        print(f"  ✅ Generated golden file: {golden_path}")

    elif pattern == "xml":
        golden_path = test_data_dir / "results" / agent / "xml" / f"{test_name}-result.xml"
        golden_path.parent.mkdir(parents=True, exist_ok=True)

        with open(golden_path, 'w') as f:
            f.write(content)

        print(f"  ✅ Generated golden file: {golden_path}")

    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def load_input_file(test_name: str) -> str:
    """Load input XML file.

    Args:
        test_name: Test case name (e.g., "50-weather-query")

    Returns:
        Input XML content

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    test_data_dir = get_test_data_dir()
    input_path = test_data_dir / "input" / f"{test_name}.xml"

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, 'r') as f:
        return f.read()


def assert_response_structure(actual: Dict[str, Any], expected: Dict[str, Any]):
    """Assert response structure matches.

    Validates structure while allowing some flexibility for LLM variability.

    Args:
        actual: Actual response from agent
        expected: Expected response from golden file
    """
    # CRITICAL: Per TypeSpec, input field has @visibility("create") which means
    # it should ONLY appear in request bodies, NOT in response bodies.
    # Verify that responses do NOT contain the input field.
    assert "input" not in actual, \
        "input field has @visibility('create') and must not appear in responses (TypeSpec violation)"

    # Status must match exactly
    assert actual.get("status") == expected.get("status"), \
        f"Status mismatch: {actual.get('status')} != {expected.get('status')}"

    # Thread status must match
    if "thread" in expected:
        assert "thread" in actual, "Missing 'thread' in actual response"
        assert actual["thread"].get("status") == expected["thread"].get("status"), \
            f"Thread status mismatch: {actual['thread'].get('status')} != {expected['thread'].get('status')}"

        # Message count should match
        actual_msgs = actual["thread"].get("messages", [])
        expected_msgs = expected["thread"].get("messages", [])
        assert len(actual_msgs) == len(expected_msgs), \
            f"Message count mismatch: {len(actual_msgs)} != {len(expected_msgs)}"

        # First message should be agent response
        if expected_msgs:
            assert actual_msgs[0].get("type") == expected_msgs[0].get("type"), \
                f"Message type mismatch: {actual_msgs[0].get('type')} != {expected_msgs[0].get('type')}"

            # Content count should match
            actual_contents = actual_msgs[0].get("contents", [])
            expected_contents = expected_msgs[0].get("contents", [])
            assert len(actual_contents) == len(expected_contents), \
                f"Content count mismatch: {len(actual_contents)} != {len(expected_contents)}"


def assert_text_content_similar(actual_text: str, expected_text: str, min_similarity: float = 0.8):
    """Assert text content is similar (for LLM variability).

    Args:
        actual_text: Actual text content
        expected_text: Expected text content
        min_similarity: Minimum similarity ratio (0.0 to 1.0)
    """
    # For now, just check that actual text is not empty and not an error
    assert actual_text, "Actual text is empty"
    assert len(actual_text) > 0, "Actual text has no content"
    assert "apologize" not in actual_text.lower() or "error" not in actual_text.lower(), \
        f"Response appears to be an error: {actual_text}"

    # In test mode with mocked LLM, responses should be identical
    if get_test_mode() == "test":
        assert actual_text == expected_text, \
            f"Text must match exactly in test mode.\nActual: {actual_text}\nExpected: {expected_text}"
