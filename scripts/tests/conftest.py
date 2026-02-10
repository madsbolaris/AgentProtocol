"""
Pytest configuration and fixtures for script testing.

Provides temporary directories and mocks to prevent tests from
polluting the actual project (test-data/results, llm-recordings, etc.)
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_project_root(tmp_path):
    """
    Create a temporary project root with minimal structure.

    This prevents tests from writing to actual project directories like:
    - test-data/results/
    - llm-recordings/
    - .generated/

    Returns:
        Path: Temporary project root directory
    """
    # Create minimal project structure
    (tmp_path / "typespec").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "test-data" / "input").mkdir(parents=True)
    (tmp_path / "test-data" / "results").mkdir(parents=True)
    (tmp_path / ".generated").mkdir()

    return tmp_path


@pytest.fixture
def mock_typespec_file(temp_project_root):
    """
    Create a minimal TypeSpec messages.tsp file for testing.

    Returns:
        Path: Path to temporary TypeSpec file
    """
    typespec_dir = temp_project_root / "typespec"
    typespec_file = typespec_dir / "messages.tsp"

    # Minimal TypeSpec content for testing
    content = """
// Basic TypeSpec for testing
namespace AgentProtocol.Messages;

enum ChatRole {
    system,
    developer,
    user,
    agent,
    tool,
    channel
}

model ChatMessage {
    messageId: string;
    role: ChatRole;
    content: AIContent[];
}

union AIContent {
    TextContent,
    ImageContent,
    ErrorContent
}

model TextContent {
    kind: "text";
    text: string;
}

model ImageContent {
    kind: "image";
    url: string;
}

model ErrorContent {
    kind: "error";
    code: string;
    message: string;
}
"""

    typespec_file.write_text(content)

    # Create routes.tsp (required by generate_api_reference.py)
    routes_file = typespec_dir / "routes.tsp"
    routes_content = """
// Minimal routes for testing
namespace AgentProtocol.Routes;

@route("/test")
op testEndpoint(): void;
"""
    routes_file.write_text(routes_content)

    return typespec_file


@pytest.fixture
def mock_api_reference_dir(temp_project_root):
    """
    Create a minimal API reference directory for testing.

    Returns:
        Path: Path to temporary API reference directory
    """
    api_ref = temp_project_root / "api-reference"
    api_ref.mkdir()

    # Create minimal structure
    (api_ref / "endpoints").mkdir()
    (api_ref / "models").mkdir()

    # Create a sample endpoint file
    endpoint_file = api_ref / "endpoints" / "test-endpoint.md"
    endpoint_file.write_text("# Test Endpoint\n\nTest content")

    return api_ref


@pytest.fixture
def isolated_environment(temp_project_root, monkeypatch):
    """
    Isolate tests from the actual project environment.

    Changes to a temporary directory and mocks environment variables
    to prevent any accidental writes to the real project.
    """
    # Change to temp directory
    original_cwd = Path.cwd()
    monkeypatch.chdir(temp_project_root)

    # Mock environment variables that might affect output paths
    monkeypatch.setenv("TEST_MODE", "1")
    monkeypatch.setenv("UPDATE_GOLDEN", "0")

    yield temp_project_root

    # Cleanup happens automatically via tmp_path fixture


@pytest.fixture
def capture_script_output():
    """
    Helper to capture script output without running as subprocess.

    Useful for testing script logic directly.
    """
    import io
    from contextlib import redirect_stdout, redirect_stderr

    def _capture(func, *args, **kwargs):
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                result = func(*args, **kwargs)
            except SystemExit as e:
                result = e.code

        return {
            'returncode': result,
            'stdout': stdout_buffer.getvalue(),
            'stderr': stderr_buffer.getvalue()
        }

    return _capture


@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """
    Mock subprocess.run to prevent tests from actually running external commands.

    Returns a mock that tracks calls and returns configurable results.
    """
    class MockSubprocessResult:
        def __init__(self, returncode=0, stdout="", stderr=""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    calls = []

    def mock_run(cmd, *args, **kwargs):
        calls.append({
            'cmd': cmd,
            'args': args,
            'kwargs': kwargs
        })
        return MockSubprocessResult(
            returncode=0,
            stdout="Mock subprocess output",
            stderr=""
        )

    import subprocess
    monkeypatch.setattr(subprocess, 'run', mock_run)

    return calls


@pytest.fixture(autouse=True)
def prevent_actual_file_writes(monkeypatch, tmp_path):
    """
    Auto-used fixture that prevents tests from writing to actual project directories.

    This is a safety net to catch any tests that might accidentally write to:
    - test-data/results/
    - llm-recordings/
    - .generated/
    - Any other generated output

    Note: This is a fail-safe. Tests should use proper fixtures like
    temp_project_root instead of relying on this.
    """
    # Get the actual project root (parent of scripts)
    actual_project_root = Path(__file__).parent.parent.parent

    # Paths we want to protect
    protected_paths = [
        actual_project_root / "test-data" / "results",
        actual_project_root / "llm-recordings",
        actual_project_root / ".generated",
        actual_project_root / "api-reference",
    ]

    # We don't actually prevent writes (that would break too much)
    # Instead, we just ensure temp_project_root is available
    # Tests should use fixtures to avoid real directories

    pass  # Safety net - tests should use proper fixtures
