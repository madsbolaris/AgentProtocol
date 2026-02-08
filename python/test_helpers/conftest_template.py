"""
Template conftest.py for pytest integration.

Copy this content to your test directory's conftest.py file, or add the
fixture to your existing conftest.py.
"""

import pytest
from pathlib import Path
import sys

# Add test_helpers to path if needed
test_helpers_path = Path(__file__).parent.parent / "test_helpers"
if test_helpers_path.exists() and str(test_helpers_path) not in sys.path:
    sys.path.insert(0, str(test_helpers_path))

from test_helpers import OutputCapture


@pytest.fixture
def output_capture():
    """
    Fixture for capturing test outputs.

    Usage:
        def test_something(output_capture):
            result = do_something()
            output_capture.capture("test-id", result)
    """
    # Determine repository root
    repo_root = Path(__file__).parent.parent.parent

    # Create output directory (shared across all language implementations)
    output_dir = repo_root / "test-data" / "results" / "shared"

    return OutputCapture(output_dir)
