"""Output capture for test results in documentation."""

import json
import hashlib
import re
import os
import difflib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class OutputCapture:
    """
    Capture test outputs for documentation and cross-platform validation.

    This class captures test outputs in a structured JSON format that can be:
    1. Used in documentation as example outputs
    2. Compared across Python and .NET implementations
    3. Validated for consistency

    Modes:
    - Validation mode (default): Compares output against existing golden files
    - Update mode: Generates/updates golden files

    Example:
        def test_something(output_capture):
            result = do_something()
            output_capture.capture("test-id", result, metadata={"key": "value"})
    """

    def __init__(self, output_dir: Path, update_mode: bool = False):
        """
        Initialize output capture.

        Args:
            output_dir: Directory to store captured outputs
            update_mode: If True, update golden files. If False, validate against them.
        """
        self.output_dir = output_dir
        self.update_mode = update_mode
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(
        self,
        test_id: str,
        output: Any,
        metadata: Optional[Dict[str, Any]] = None,
        normalize: bool = True
    ) -> None:
        """
        Capture test output to JSON file or validate against existing golden file.

        Args:
            test_id: Unique test identifier (must match @doc_example test_id)
            output: The output to capture (will be serialized to string)
            metadata: Additional metadata to store with the output
            normalize: Whether to normalize whitespace for comparison

        Raises:
            AssertionError: If not in update mode and output doesn't match golden file
        """
        raw_output = self._serialize(output)
        output_file = self.output_dir / f"{test_id}.json"

        if self.update_mode:
            # Update mode: Write new golden file
            result = {
                "testId": test_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "output": {
                    "raw": raw_output,
                    "normalized": self._normalize(raw_output) if normalize else None,
                    "hash": self._hash(raw_output)
                },
                "metadata": metadata or {}
            }
            output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"  ✓ Updated golden file: {test_id}")
        else:
            # Validation mode: Compare against golden file
            if not output_file.exists():
                raise AssertionError(
                    f"\n\n❌ Golden file not found: {output_file}\n"
                    f"   Test ID: {test_id}\n"
                    f"   Run with --update-golden to create it:\n"
                    f"   pytest --update-golden tests/test_doc_examples.py::{test_id}\n"
                )

            # Load golden file
            golden = json.loads(output_file.read_text())
            golden_output = golden["output"]["raw"]
            golden_hash = golden["output"]["hash"]

            # Compare using normalized hash
            current_hash = self._hash(raw_output)

            if current_hash != golden_hash:
                # Generate diff for error message
                diff = self._generate_diff(golden_output, raw_output, test_id)
                raise AssertionError(
                    f"\n\n❌ Output mismatch for test: {test_id}\n"
                    f"   Golden file: {output_file}\n"
                    f"   Expected hash: {golden_hash}\n"
                    f"   Actual hash:   {current_hash}\n\n"
                    f"{diff}\n\n"
                    f"   If this change is intentional, update the golden file:\n"
                    f"   pytest --update-golden tests/test_doc_examples.py::{test_id}\n"
                )

    def _serialize(self, value: Any) -> str:
        """
        Serialize value to string.

        Args:
            value: Value to serialize

        Returns:
            String representation of the value
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, bytes):
            return value.decode('utf-8')
        elif isinstance(value, (dict, list)):
            return json.dumps(value, indent=2, ensure_ascii=False)
        else:
            return str(value)

    def _normalize(self, value: str) -> str:
        """
        Normalize whitespace for comparison.

        Removes extra whitespace and normalizes line endings to make
        cross-platform comparison more reliable.

        Args:
            value: String to normalize

        Returns:
            Normalized string
        """
        # Normalize line endings
        s = value.replace('\r\n', '\n').replace('\r', '\n')
        # Remove extra whitespace
        s = re.sub(r'[ \t]+', ' ', s)
        # Remove blank lines
        s = re.sub(r'\n\s*\n', '\n', s)
        # Trim
        return s.strip()

    def _hash(self, value: str) -> str:
        """
        Generate SHA-256 hash of normalized value.

        Args:
            value: String to hash

        Returns:
            Hexadecimal hash string
        """
        normalized = self._normalize(value)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _generate_diff(self, expected: str, actual: str, test_id: str) -> str:
        """
        Generate a unified diff between expected and actual output.

        Args:
            expected: Expected output (from golden file)
            actual: Actual output (from test)
            test_id: Test identifier for context

        Returns:
            Formatted diff string
        """
        expected_lines = expected.splitlines(keepends=True)
        actual_lines = actual.splitlines(keepends=True)

        diff = difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile=f"golden/{test_id}.json (expected)",
            tofile=f"actual output (from test)",
            lineterm=''
        )

        diff_lines = list(diff)
        if not diff_lines:
            return "   (No visible diff - whitespace differences only)"

        # Limit diff output to first 50 lines
        max_lines = 50
        if len(diff_lines) > max_lines:
            diff_lines = diff_lines[:max_lines]
            diff_lines.append(f"\n   ... (diff truncated, showing first {max_lines} lines)")

        return "   Diff:\n   " + "\n   ".join(line.rstrip() for line in diff_lines)


# Pytest fixture
def pytest_configure(config):
    """Configure pytest with output capture fixture."""
    pass  # Fixture registration happens via conftest.py


def create_output_capture_fixture(output_dir: Optional[Path] = None, sample_name: Optional[str] = None):
    """
    Create an output capture fixture for pytest.

    Args:
        output_dir: Optional custom output directory
        sample_name: Optional sample name (e.g., "echom365", "basic-m365")
                    If provided, uses test-data/results/{sample_name}/golden/

    Returns:
        OutputCapture instance

    Example in conftest.py:
        import pytest
        from test_helpers import create_output_capture_fixture

        @pytest.fixture
        def output_capture():
            return create_output_capture_fixture(sample_name="echom365")
    """
    if output_dir is None:
        repo_root = Path(__file__).parent.parent
        if sample_name:
            # Use sample-specific directory for golden files
            output_dir = repo_root / "test-data" / "results" / sample_name / "golden"
        else:
            # DEPRECATED: Default to shared directory (for backward compatibility)
            # This will be removed in a future version
            output_dir = repo_root / "test-data" / "results" / "shared"
            import warnings
            warnings.warn(
                "Using deprecated 'shared' results directory. "
                "Please specify sample_name parameter (e.g., sample_name='echom365')",
                DeprecationWarning,
                stacklevel=2
            )

    return OutputCapture(output_dir)
