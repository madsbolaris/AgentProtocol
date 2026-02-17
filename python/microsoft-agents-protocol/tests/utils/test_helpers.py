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
        recordings_dir: Directory for recordings (default: test-data/llm-recordings/sample/basic-m365)
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
            "2. Record LLM interactions to test-data/llm-recordings/sample/basic-m365/\n"
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
    agent: str = "basic-m365",
    subdir: Optional[str] = None
) -> Union[Dict[str, Any], str]:
    """Load golden file for comparison.

    Args:
        test_name: Test case name (e.g., "50-weather-query" or "01-simple-text-expect")
        pattern: Test pattern ("json" or "xml")
        agent: Agent name (default: "basic-m365")
        subdir: Optional subdirectory under results/ (e.g., "evals")

    Returns:
        Parsed golden file content (dict for JSON, str for XML)

    Raises:
        FileNotFoundError: If golden file doesn't exist
    """
    test_data_dir = get_test_data_dir()
    filename = f"{test_name}-result.{pattern}"

    if pattern == "json":
        if subdir:
            # For hierarchical structure: search recursively in results/subdir/
            search_dir = test_data_dir / "results" / subdir

            # Try old flat structure first (backwards compatibility)
            old_path = search_dir / "json" / filename
            if old_path.exists():
                with open(old_path, 'r') as f:
                    return json.load(f)

            # Search recursively in new hierarchical structure
            if search_dir.exists():
                for found_path in search_dir.rglob(filename):
                    with open(found_path, 'r') as f:
                        return json.load(f)

            raise FileNotFoundError(
                f"Golden file not found: {filename}\n"
                f"Searched in: {search_dir}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )
        else:
            # Agent-specific results: keep old structure
            golden_path = test_data_dir / "results" / agent / "json" / filename
            if golden_path.exists():
                with open(golden_path, 'r') as f:
                    return json.load(f)

            raise FileNotFoundError(
                f"Golden file not found: {golden_path}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )

    elif pattern == "xml":
        if subdir:
            # For hierarchical structure: search recursively in results/subdir/
            search_dir = test_data_dir / "results" / subdir

            # Try old flat structure first (backwards compatibility)
            old_path = search_dir / "xml" / filename
            if old_path.exists():
                with open(old_path, 'r') as f:
                    return f.read()

            # Search recursively in new hierarchical structure
            if search_dir.exists():
                for found_path in search_dir.rglob(filename):
                    with open(found_path, 'r') as f:
                        return f.read()

            raise FileNotFoundError(
                f"Golden file not found: {filename}\n"
                f"Searched in: {search_dir}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )
        else:
            # Agent-specific results: keep old structure
            golden_path = test_data_dir / "results" / agent / "xml" / filename
            if golden_path.exists():
                with open(golden_path, 'r') as f:
                    return f.read()

            raise FileNotFoundError(
                f"Golden file not found: {golden_path}\n"
                f"Run tests with TEST_MODE=generate to create golden files."
            )

    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def save_golden_file(
    content: Union[Dict[str, Any], str],
    test_name: str,
    pattern: Literal["json", "xml"] = "json",
    agent: str = "basic-m365",
    subdir: Optional[str] = None
):
    """Save golden file, preserving input directory structure.

    Args:
        content: Content to save (dict for JSON, str for XML)
        test_name: Test case name (e.g., "50-weather-query" or "01-simple-text-expect")
        pattern: Test pattern ("json" or "xml")
        agent: Agent name (default: "basic-m365")
        subdir: Optional subdirectory under results/ (e.g., "evals")
    """
    test_data_dir = get_test_data_dir()
    filename = f"{test_name}-result.{pattern}"

    if subdir:
        # Find the input file to determine the subdirectory structure
        input_dir = test_data_dir / "input" / subdir
        input_filename = f"{test_name}.xml"

        relative_dir = None
        if input_dir.exists():
            # Search for the input file
            for input_path in input_dir.rglob(input_filename):
                # Get relative path from input category directory
                try:
                    rel_path = input_path.parent.relative_to(input_dir)
                    if rel_path != Path("."):
                        relative_dir = rel_path
                    break
                except ValueError:
                    continue

        # Build the golden file path
        results_dir = test_data_dir / "results" / subdir
        if relative_dir:
            results_dir = results_dir / relative_dir
        golden_path = results_dir / filename
    else:
        # Agent-specific results: use old flat structure
        golden_path = test_data_dir / "results" / agent / pattern / filename

    golden_path.parent.mkdir(parents=True, exist_ok=True)

    if pattern == "json":
        with open(golden_path, 'w') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    elif pattern == "xml":
        with open(golden_path, 'w') as f:
            f.write(content)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")

    print(f"  ✅ Generated golden file: {golden_path}")


def load_input_file(test_name: str, subdir: Optional[str] = None) -> str:
    """Load input XML file.

    Args:
        test_name: Test case name (e.g., "50-weather-query" or "01-simple-text-expect")
        subdir: Optional subdirectory under input/ (e.g., "evals")

    Returns:
        Input XML content

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    test_data_dir = get_test_data_dir()

    if subdir:
        input_path = test_data_dir / "input" / subdir / f"{test_name}.xml"
    else:
        input_path = test_data_dir / "input" / f"{test_name}.xml"

    # If direct path exists, use it
    if input_path.exists():
        with open(input_path, 'r') as f:
            return f.read()

    # Search recursively in specified subdir or entire input directory
    if subdir:
        search_dir = test_data_dir / "input" / subdir
    else:
        search_dir = test_data_dir / "input"

    for found_path in search_dir.rglob(f"{test_name}.xml"):
        with open(found_path, 'r') as f:
            return f.read()

    raise FileNotFoundError(f"Input file not found: {input_path}")


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


def load_eval_input_file(test_name: str) -> str:
    """Load eval input XML file from test-data/input/evals/.

    Args:
        test_name: Test case name (e.g., "01-simple-text-expect")

    Returns:
        Input XML content

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    return load_input_file(test_name, subdir="evals")


def load_eval_golden_file(test_name: str) -> Dict[str, Any]:
    """Load eval golden result file from test-data/results/evals/json/.

    Args:
        test_name: Test case name (e.g., "01-simple-text-expect")

    Returns:
        Parsed golden result content

    Raises:
        FileNotFoundError: If golden file doesn't exist
    """
    return load_golden_file(test_name, pattern="json", subdir="evals")


def save_eval_golden_file(content: Dict[str, Any], test_name: str):
    """Save eval golden result file to test-data/results/evals/json/.

    Args:
        content: Result content to save
        test_name: Test case name (e.g., "01-simple-text-expect")
    """
    save_golden_file(content, test_name, pattern="json", subdir="evals")


def assert_eval_result_structure(actual: Dict[str, Any], expected_thread_id: str):
    """Assert eval result has correct structure.

    Args:
        actual: Actual eval result
        expected_thread_id: Expected thread ID
    """
    # Check if we have the wrapped format with timestamp, content, hash, metadata
    if "content" in actual and "timestamp" in actual:
        result = actual["content"]
    else:
        result = actual

    # Validate required fields
    assert "threadId" in result, "Missing 'threadId' in result"
    assert result["threadId"] == expected_thread_id, \
        f"Thread ID mismatch: {result['threadId']} != {expected_thread_id}"

    assert "passed" in result, "Missing 'passed' in result"
    assert isinstance(result["passed"], bool), "'passed' should be boolean"

    assert "runs" in result, "Missing 'runs' in result"
    assert isinstance(result["runs"], list), "'runs' should be a list"

    # Check stats
    assert "totalRuns" in result, "Missing 'totalRuns' in result"
    assert "passedRuns" in result, "Missing 'passedRuns' in result"
    assert "failedRuns" in result, "Missing 'failedRuns' in result"
    assert "totalAsserts" in result, "Missing 'totalAsserts' in result"
    assert "passedAsserts" in result, "Missing 'passedAsserts' in result"
    assert "failedAsserts" in result, "Missing 'failedAsserts' in result"

    # Validate each run
    for run in result["runs"]:
        assert "runNumber" in run, "Missing 'runNumber' in run"
        assert "passed" in run, "Missing 'passed' in run"
        assert isinstance(run["passed"], bool), "'passed' should be boolean in run"

        if "expects" in run:
            for expect in run["expects"]:
                assert "name" in expect, "Missing 'name' in expect"
                assert "passed" in expect, "Missing 'passed' in expect"


def assert_eval_results_match(actual: Dict[str, Any], expected: Dict[str, Any]):
    """Assert eval results match (structure and key values).

    Args:
        actual: Actual eval result
        expected: Expected eval result from golden file
    """
    # Extract content if wrapped
    if "content" in actual and "timestamp" in actual:
        actual_result = actual["content"]
    else:
        actual_result = actual

    if "content" in expected and "timestamp" in expected:
        expected_result = expected["content"]
    else:
        expected_result = expected

    # Compare key fields
    assert actual_result["threadId"] == expected_result["threadId"], \
        f"Thread ID mismatch: {actual_result['threadId']} != {expected_result['threadId']}"

    assert actual_result["passed"] == expected_result["passed"], \
        f"Passed status mismatch: {actual_result['passed']} != {expected_result['passed']}"

    assert actual_result["totalRuns"] == expected_result["totalRuns"], \
        f"Total runs mismatch: {actual_result['totalRuns']} != {expected_result['totalRuns']}"

    assert actual_result["passedRuns"] == expected_result["passedRuns"], \
        f"Passed runs mismatch: {actual_result['passedRuns']} != {expected_result['passedRuns']}"

    assert actual_result["totalAsserts"] == expected_result["totalAsserts"], \
        f"Total asserts mismatch: {actual_result['totalAsserts']} != {expected_result['totalAsserts']}"

    assert actual_result["passedAsserts"] == expected_result["passedAsserts"], \
        f"Passed asserts mismatch: {actual_result['passedAsserts']} != {expected_result['passedAsserts']}"

    # Compare run count
    assert len(actual_result["runs"]) == len(expected_result["runs"]), \
        f"Run count mismatch: {len(actual_result['runs'])} != {len(expected_result['runs'])}"
