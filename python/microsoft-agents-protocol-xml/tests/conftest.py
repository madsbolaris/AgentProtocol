"""
Pytest configuration and fixtures for agent-xml tests.

All tests automatically use LLM recordings instead of real API calls.
"""

import pytest
import os
from pathlib import Path
import sys

# Automatically configure environment for all tests
# These settings ensure tests use recordings and don't make real API calls
os.environ.setdefault("USE_LLM_RECORDINGS", "true")
os.environ.setdefault("RECORD_LLM", "false")

# Add python directory to path so we can import test_helpers
repo_root = Path(__file__).parent.parent.parent.parent
python_dir = repo_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from test_helpers import OutputCapture


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Update golden files instead of validating against them"
    )


@pytest.fixture
def output_capture(request):
    """
    Fixture for capturing test outputs for documentation.

    Modes:
    - Normal: pytest (validates against golden files)
    - Update: pytest --update-golden (updates golden files)

    Environment variable alternative:
    - UPDATE_GOLDEN=1 pytest (updates golden files)

    Usage:
        def test_something(output_capture):
            result = do_something()
            output_capture.capture("test-id", result)
    """
    # Determine repository root (go up 4 levels from this file)
    repo_root = Path(__file__).parent.parent.parent.parent

    # Use docs results directory for documentation examples
    output_dir = repo_root / "test-data" / "results" / "docs"

    # Check if we're in update mode (via flag or environment variable)
    update_mode = request.config.getoption("--update-golden") or os.getenv("UPDATE_GOLDEN") == "1"

    if update_mode:
        print("\n🔄 Running in UPDATE mode - golden files will be updated")
    else:
        print("\n✅ Validating against golden files")

    return OutputCapture(output_dir, update_mode=update_mode)
