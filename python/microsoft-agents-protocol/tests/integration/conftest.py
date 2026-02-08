"""
Pytest configuration and fixtures for integration tests.
"""

import os
import pytest
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent / "samples" / "agents" / "basic_m365_agent"))


@pytest.fixture
def test_mode():
    """Get current test mode from environment."""
    from tests.utils import get_test_mode
    return get_test_mode()


@pytest.fixture
def llm_client(test_mode):
    """Create LLM client based on test mode (recording or mock)."""
    from tests.utils import create_llm_client
    return create_llm_client(test_mode=test_mode)


@pytest.fixture
def agent_url():
    """URL of the running Basic M365 Agent."""
    # Read from config or use default
    port = os.getenv("AGENT_PORT", "3982")
    return f"http://localhost:{port}"


@pytest.fixture(autouse=True)
def inject_llm_client(llm_client):
    """Automatically inject LLM client into agent for all tests."""
    try:
        # Import and inject
        from src.agent import set_openai_client
        set_openai_client(llm_client)
        yield
        # Cleanup after test
        set_openai_client(None)
    except ImportError:
        # Agent not available, skip injection
        yield
