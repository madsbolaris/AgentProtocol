"""
Shared pytest fixtures for protocol tests.
"""

import pytest
from pathlib import Path


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
