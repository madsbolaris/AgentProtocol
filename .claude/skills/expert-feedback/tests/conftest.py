"""
Pytest configuration for expert-feedback skill tests.

This module provides fixtures and configuration for automated testing,
including automatic mocking of the Claude Agent SDK.
"""

import os
import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Add scripts directory to path for imports
_scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

# Add .claude directory to path for sdk_auth imports
_claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_dir))


# Test mode configuration

@pytest.fixture(scope="session")
def test_mode() -> str:
    """
    Get test mode from environment.

    Returns:
        "replay" (default) or "record"
    """
    return os.getenv("EXPERT_FEEDBACK_TEST_MODE", "replay")


@pytest.fixture(scope="function")
def recordings_dir(request, test_mode: str) -> Path:
    """
    Get test-specific recordings directory.

    Each test gets its own subdirectory to avoid mixing recordings.
    In record mode, clears old recordings to ensure fresh capture.
    Can be overridden via EXPERT_FEEDBACK_RECORDINGS_DIR environment variable.

    Returns:
        Path to test-specific recordings directory
    """
    env_dir = os.getenv("EXPERT_FEEDBACK_RECORDINGS_DIR")
    base_dir = Path(env_dir) if env_dir else Path(__file__).parent / "recordings"

    # Get test name and create subdirectory
    test_name = request.node.name
    test_dir = base_dir / test_name
    test_dir.mkdir(parents=True, exist_ok=True)

    # Clear old recordings in record mode
    if test_mode == "record":
        import shutil
        for item in test_dir.glob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"  🗑️  Cleared old recordings from {test_dir}")

    return test_dir


# Mock SDK configuration

@pytest.fixture(scope="function")
def mock_claude_sdk(test_mode: str, recordings_dir: Path):
    """
    Automatically mock Claude Agent SDK for tests.

    This fixture is applied to all tests by default. It replaces the real
    claude_agent_sdk with a mock that can record or replay interactions.

    Args:
        test_mode: "replay" or "record"
        recordings_dir: Where recordings are stored

    Yields:
        MockClaudeAgentSDK instance (in replay mode) or None (in record mode)
    """
    import sys  # Need sys for both replay and record modes

    if test_mode == "replay":
        # Replay mode: use mock SDK
        from tests.mocks.mock_claude_sdk import MockClaudeAgentSDK

        # Create mock instance
        mock_sdk = MockClaudeAgentSDK(recordings_dir, mode="replay")

        # Save original module if it exists
        original_module = sys.modules.get('claude_agent_sdk')

        # Install mock SDK directly as the module (no wrapper - fixes async deadlock!)
        sys.modules['claude_agent_sdk'] = mock_sdk
        # Also register types submodule for "from claude_agent_sdk.types import X"
        sys.modules['claude_agent_sdk.types'] = mock_sdk.types

        yield mock_sdk

        # Restore original module
        if original_module:
            sys.modules['claude_agent_sdk'] = original_module
        else:
            del sys.modules['claude_agent_sdk']
        # Also clean up types submodule
        if 'claude_agent_sdk.types' in sys.modules:
            del sys.modules['claude_agent_sdk.types']

    else:
        # Record mode: use mock SDK in record mode (makes real calls + saves recordings)

        # Setup authentication BEFORE importing real SDK
        print("  🔑 Setting up Claude authentication for record mode...")
        try:
            # Import sdk_auth from parent directory
            from pathlib import Path
            sdk_auth_path = Path(__file__).parent.parent.parent.parent  # Go up to repo root/.claude
            sys.path.insert(0, str(sdk_auth_path))
            from sdk_auth import setup_claude_auth

            if not setup_claude_auth(verbose=True):
                raise RuntimeError("Failed to setup Claude authentication")
        except Exception as e:
            raise ImportError(
                "Cannot setup authentication for record mode.\n"
                "\n"
                f"Error: {e}\n"
                "\n"
                "Make sure Claude Code is authenticated with an API key.\n"
                "Or run tests in replay mode (default):\n"
                "  pytest tests/ -v\n"
            ) from e

        # CRITICAL: Import real SDK AFTER authentication is setup
        try:
            import claude_agent_sdk as real_sdk_module
            print("  ✅ Real claude_agent_sdk imported for record mode")
        except ImportError as e:
            raise ImportError(
                "Cannot import real claude_agent_sdk for record mode.\n"
                "\n"
                "To install:\n"
                "  pip install claude-agent-sdk\n"
                "\n"
                "Or run tests in replay mode (default):\n"
                "  pytest tests/ -v\n"
            ) from e

        from tests.mocks.mock_claude_sdk import MockClaudeAgentSDK

        # Create mock instance with real SDK reference
        mock_sdk = MockClaudeAgentSDK(
            recordings_dir,
            mode="record",
            real_sdk_module=real_sdk_module  # Pass the real SDK!
        )

        # Save original module if it exists
        original_module = sys.modules.get('claude_agent_sdk')

        # Install mock SDK directly as the module (no wrapper - fixes async deadlock!)
        sys.modules['claude_agent_sdk'] = mock_sdk
        # Also register types submodule for "from claude_agent_sdk.types import X"
        sys.modules['claude_agent_sdk.types'] = mock_sdk.types

        yield mock_sdk

        # Restore original module
        if original_module:
            sys.modules['claude_agent_sdk'] = original_module
        else:
            del sys.modules['claude_agent_sdk']
        # Also clean up types submodule
        if 'claude_agent_sdk.types' in sys.modules:
            del sys.modules['claude_agent_sdk.types']


class _MockClaudeAgentOptions:
    """Mock ClaudeAgentOptions class for testing."""

    def __init__(self, **kwargs):
        """Initialize with any kwargs."""
        # Set default mock callables for common callback attributes
        self.stderr = lambda msg: None  # Mock stderr callback
        self.debug_stderr = None
        self.hooks = None

        # Override with any provided kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        # If can_use_tool not provided, set default async mock
        if not hasattr(self, 'can_use_tool') or self.can_use_tool is None:
            async def default_can_use_tool(tool_name: str, params: dict, context: Any) -> Any:
                """Default mock - always allow."""
                return {"type": "allow"}
            self.can_use_tool = default_can_use_tool

    def model_dump(self) -> dict:
        """Mock model_dump method for Pydantic-style serialization."""
        # Return a simple dict of our attributes (excluding callables and private attrs)
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

    def __getattr__(self, name: str):
        """Return appropriate mock for any unset attributes."""
        # For callback-like attributes, return a no-op function
        if name.endswith('_callback') or name.startswith('on_'):
            return lambda *args, **kwargs: None
        # For other attributes, return None
        return None


class _MockTypesModule:
    """Mock types module for claude_agent_sdk.types imports."""

    def __getattr__(self, name: str):
        """
        Return mock for any type requested.

        This allows imports like:
            from claude_agent_sdk.types import AssistantMessage, UserMessage

        To work without errors during mocking.
        """
        # Return a simple mock class
        return type(name, (), {
            "model_dump": lambda self: {},
            "to_dict": lambda self: {}
        })


# Output capture fixtures

@pytest.fixture
def stderr_capture():
    """
    Capture stderr output for testing progress/logging output.

    Automatically restores original stderr after test completes.

    Yields:
        io.StringIO: Captured stderr stream

    Example:
        def test_output(stderr_capture):
            print("Error!", file=sys.stderr)
            assert "Error!" in stderr_capture.getvalue()
    """
    import io

    original_stderr = sys.stderr
    capture = io.StringIO()
    sys.stderr = capture

    yield capture

    sys.stderr = original_stderr


# Workspace fixtures

@pytest.fixture
def test_workspace(tmp_path: Path) -> Path:
    """
    Create a temporary test workspace.

    Creates a clean workspace directory with standard structure
    for each test. Automatically cleaned up after test.

    Args:
        tmp_path: pytest's temporary directory

    Returns:
        Path to test workspace
    """
    workspace = tmp_path / "test-workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    # Create standard subdirectories
    (workspace / "logs").mkdir(exist_ok=True)
    (workspace / "iteration-1").mkdir(exist_ok=True)

    return workspace


@pytest.fixture
def initialized_workspace(test_workspace: Path) -> Path:
    """
    Create workspace with initialized state.

    Args:
        test_workspace: Base test workspace

    Returns:
        Path to initialized workspace
    """
    # Ensure scripts directory is in sys.path before importing (absolute path)
    import sys
    from pathlib import Path
    _scripts_path = str((Path(__file__).parent.parent / "scripts").resolve())

    # Remove and re-add to ensure it's at position 0 (same pattern as Q tests)
    if _scripts_path in sys.path:
        sys.path.remove(_scripts_path)
    sys.path.insert(0, _scripts_path)

    from state.manager import StateManager, WorkspaceState

    # Initialize state
    state_manager = StateManager(test_workspace)
    state = WorkspaceState(
        topic="Test API Design",
        experts=["typescript", "python"],
        iteration=1,
        mode="review",
        convergence_target=80
    )
    state_manager.create(state)

    return test_workspace


# Import helpers for tests

@pytest.fixture
def file_io():
    """Provide file I/O utilities for tests."""
    from file_io import json_ops
    return json_ops


@pytest.fixture
def state_manager_factory(test_workspace: Path):
    """
    Factory for creating StateManager instances.

    Returns:
        Function that creates StateManager for a workspace
    """
    from state.manager import StateManager

    def create_manager(workspace: Optional[Path] = None) -> StateManager:
        return StateManager(workspace or test_workspace)

    return create_manager


@pytest.fixture
def workspace_snapshot(request, recordings_dir):
    """
    Workspace snapshot manager for current test.

    Provides a WorkspaceSnapshot instance configured for the current test,
    enabling tests to save/restore complete workspace state alongside
    LLM recordings for test chaining.

    Args:
        request: pytest request with test node name
        recordings_dir: Base recordings directory fixture

    Returns:
        WorkspaceSnapshot instance for current test
    """
    from fixtures.workspace_snapshot import WorkspaceSnapshot
    return WorkspaceSnapshot(request.node.name, recordings_dir)


# Mock data fixtures

@pytest.fixture
def mock_experts_json():
    """
    Mock experts.json data for testing.

    Returns:
        Dict with mock expert configurations
    """
    return {
        "typescript": {
            "name": "TypeScript Expert",
            "background": "Senior TypeScript architect with 10+ years experience",
            "perspective": "Focus on type safety and maintainability",
            "focus_areas": ["Type system", "Testing", "API design"],
            "anti_patterns": ["Any types", "Type assertions"]
        },
        "python": {
            "name": "Python Expert",
            "background": "Python core contributor",
            "perspective": "Pythonic patterns and performance",
            "focus_areas": ["Async patterns", "Type hints", "Testing"],
            "anti_patterns": ["Mutable defaults", "Overly complex"]
        },
        "security": {
            "name": "Security Expert",
            "background": "Application security specialist",
            "perspective": "Security-first architecture",
            "focus_areas": ["Input validation", "Auth/authz", "Data protection"],
            "anti_patterns": ["Hardcoded secrets", "SQL injection risks"]
        }
    }


@pytest.fixture
def mock_state_json():
    """
    Mock state.json data for testing.

    Returns:
        Dict with mock workspace state
    """
    return {
        "iteration": 1,
        "experts": ["typescript", "python"],
        "status": "initialized",
        "workspace": "/tmp/test-workspace",
        "topic": "Test API Design",
        "mode": "review",
        "convergence_target": 80,
        "started_at": "2024-01-01T00:00:00Z"
    }


# Test utilities

@pytest.fixture
def create_mock_expert_response():
    """
    Factory for creating mock expert responses.

    Returns:
        Function that creates expert response dict
    """

    def factory(
        expert_name: str,
        recommendations: list,
        concerns: Optional[list] = None,
        questions: Optional[list] = None
    ) -> dict:
        return {
            "expert": expert_name,
            "analysis": f"Mock analysis from {expert_name}",
            "recommendations": recommendations,
            "concerns": concerns or [],
            "questions": questions or []
        }

    return factory


@pytest.fixture
def create_mock_synthesis_response():
    """
    Factory for creating mock synthesis responses.

    Returns:
        Function that creates synthesis response dict
    """

    def factory(
        convergence_percent: int,
        consensus_reached: bool,
        high_agreement: Optional[list] = None,
        partial_agreement: Optional[list] = None,
        low_agreement: Optional[list] = None
    ) -> dict:
        return {
            "convergence_percent": convergence_percent,
            "consensus_reached": consensus_reached,
            "high_agreement": high_agreement or [],
            "partial_agreement": partial_agreement or [],
            "low_agreement": low_agreement or []
        }

    return factory


# Pytest configuration

@pytest.fixture(autouse=True)
def cleanup_loggers():
    """
    Cleanup logger handlers between tests to ensure test isolation.

    This prevents logger handlers from persisting across tests, which can cause
    tests to fail when they expect files to be created in their own temp directories.
    """
    import logging

    yield  # Run the test

    # Clean up all expert-feedback loggers after test
    loggers_to_clean = [
        name for name in logging.Logger.manager.loggerDict
        if name.startswith('expert-feedback')
    ]

    for logger_name in loggers_to_clean:
        logger = logging.getLogger(logger_name)
        # Remove all handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        # Clear logger from manager
        if logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[logger_name]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_recordings: mark test as requiring recorded data"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers automatically based on test location and requirements."""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests that require recordings
        if "test_workflow" in item.name or "test_phase" in item.name:
            item.add_marker(pytest.mark.requires_recordings)
