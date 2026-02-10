"""
Shared pytest fixtures for protocol tests.

All tests automatically use LLM recordings instead of real API calls.
"""

import os
import sys
import pytest
from pathlib import Path

# Automatically configure environment for all tests
# These settings ensure tests use recordings and don't make real API calls
os.environ.setdefault("USE_LLM_RECORDINGS", "true")
os.environ.setdefault("RECORD_LLM", "false")

# Add python directory to path for test_helpers import
python_dir = Path(__file__).parent.parent.parent
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))


@pytest.fixture
def test_data_dir():
    """Get shared test data directory."""
    return Path(__file__).parent.parent.parent.parent / "test-data"


@pytest.fixture
def input_data_dir(test_data_dir):
    """Get input test data directory."""
    return test_data_dir / "input"


@pytest.fixture
def output_data_dir(test_data_dir):
    """Get output test data directory."""
    return test_data_dir / "output"
