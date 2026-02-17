# Expert-Feedback Skill Testing

Automated testing infrastructure for the expert-feedback skill that eliminates manual testing and waiting for LLM responses.

## Overview

This testing infrastructure provides:
- **Mock Claude Agent SDK** - Record/replay LLM interactions
- **Fast Tests** - Run in seconds instead of minutes
- **Comprehensive Coverage** - Workflow phases, state management, UI validation
- **Easy Recording** - Simple two-step process to generate test fixtures

## Quick Start

### Running Tests (Replay Mode)

```bash
# From the expert-feedback directory
cd .claude/skills/expert-feedback

# Run all tests with recorded data (fast, no API calls)
pytest tests/ -v

# Run specific test categories
pytest tests/integration/test_workflow_phases.py -v
pytest tests/integration/test_state_ui.py -v
pytest tests/unit/ -v
```

### Generating Recordings (Record Mode)

```bash
# Set environment to record mode
export EXPERT_FEEDBACK_TEST_MODE=record

# Run tests - will make real LLM calls and save responses
pytest tests/integration/test_workflow_phases.py::test_expert_spawning_basic -v

# Recordings saved to tests/recordings/
ls tests/recordings/
```

## Test Structure

```
tests/
├── mocks/
│   ├── mock_claude_sdk.py          # Mock Claude Agent SDK
│   └── sdk_recorder.py             # Recording/replay logic
├── fixtures/
│   ├── workspace_fixtures.py       # Workspace creation helpers
│   └── state_fixtures.py           # Pre-configured state objects
├── recordings/
│   ├── expert-spawning/            # Expert phase recordings
│   ├── synthesis/                  # Synthesis recordings
│   └── artifact-generation/        # Artifact recordings
├── integration/
│   ├── test_workflow_phases.py     # Phase-level tests
│   ├── test_full_workflow.py       # End-to-end tests
│   └── test_state_ui.py            # UI state validation
├── unit/
│   ├── test_state_manager.py       # State management tests
│   ├── test_config.py              # Configuration tests
│   ├── test_validation.py          # Validation tests
│   └── test_progress_tracker.py    # Progress tracking tests
├── conftest.py                     # Pytest configuration
└── README.md                       # This file
```

## Test Categories

### Integration Tests

**Workflow Phase Tests** ([test_workflow_phases.py](integration/test_workflow_phases.py))
- Expert spawning and timeout handling
- Synthesis and convergence calculation
- Artifact generation
- Phase transitions and tracking
- Resume/checkpoint functionality

**UI State Validation** ([test_state_ui.py](integration/test_state_ui.py))
- Required fields validation
- Expert progress structure
- Convergence metrics
- Token/cost tracking
- Session tracking

**Full Workflow Tests** ([test_full_workflow.py](integration/test_full_workflow.py))
- Single-iteration consensus
- Multi-iteration workflows
- Error conditions
- Minimum expert checks

### Unit Tests

- State manager operations
- Recording/hashing logic
- Request normalization
- Configuration management
- Schema validation
- Progress tracking

## Mock SDK Architecture

### Recording Format

Recordings are stored as JSON files with a hash-based naming:

```
recordings/
├── {hash}.request.json     # Request data
└── {hash}.response.json    # Stream events
```

**Request Hash:** Based on `prompt` + `system` + `messages` + `options` (excluding session IDs)

**Example Request:**
```json
{
  "prompt": "Review this API design...",
  "system": [...],
  "messages": [...],
  "options": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Example Response:**
```json
{
  "events": [
    {"type": "stream_start", "data": {...}},
    {"type": "content_block", "data": {"type": "text", "text": "..."}},
    {"type": "usage", "data": {"input_tokens": 1000, "output_tokens": 500}},
    {"type": "stream_end", "data": {...}}
  ]
}
```

### How Mocking Works

1. **Automatic Patching** - `conftest.py` automatically replaces `claude_agent_sdk` with the mock
2. **Request Hashing** - Each LLM call is hashed to find matching recording
3. **Event Replay** - Recorded stream events are replayed in order
4. **Zero API Calls** - Tests run completely offline

## Writing New Tests

### Example: Test a New Phase

```python
import pytest
from pathlib import Path
from state.manager import StateManager

@pytest.mark.integration
@pytest.mark.requires_recordings
class TestMyNewPhase:
    """Test my new workflow phase."""

    @pytest.mark.asyncio
    async def test_phase_basic(self, mock_claude_sdk, initialized_workspace):
        """Test basic phase functionality."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Your test logic here
        state_manager.set_phase("my_new_phase")

        # Assertions
        state = state_manager.load()
        assert state.to_dict().get("phase") == "my_new_phase"
```

### Example: Test UI State Contract

```python
def test_new_ui_field(self, initialized_workspace):
    """Test that new UI field is present."""
    state_manager = StateManager(initialized_workspace)
    state = state_manager.load()

    # UI requires this field
    assert hasattr(state, 'my_new_field')
    assert state.my_new_field == expected_value
```

## Environment Variables

- `EXPERT_FEEDBACK_TEST_MODE` - `replay` (default) or `record`
- `EXPERT_FEEDBACK_RECORDINGS_DIR` - Override recordings directory

## Fixtures Available

### Workspace Fixtures

```python
def test_example(test_workspace):
    """Use temporary test workspace."""
    # test_workspace is Path to clean workspace

def test_example(initialized_workspace):
    """Use workspace with initialized state."""
    # initialized_workspace has state.json already created
```

### State Fixtures

```python
from fixtures.state_fixtures import create_initial_state, create_state_with_sessions

def test_example():
    state = create_initial_state(
        topic="Test",
        experts=["typescript", "python"]
    )
```

### Mock SDK Fixture

```python
@pytest.mark.asyncio
async def test_example(mock_claude_sdk):
    """Mock SDK is automatically available."""
    # mock_claude_sdk is already patched into imports
    # Your code that uses claude_agent_sdk will use the mock
```

## Pytest Markers

- `@pytest.mark.integration` - Integration test
- `@pytest.mark.requires_recordings` - Test needs recorded data
- `@pytest.mark.slow` - Slow-running test

**Run specific markers:**
```bash
pytest -m integration  # Only integration tests
pytest -m "not slow"   # Skip slow tests
```

## Recording Workflow

### Step 1: Write Test

```python
@pytest.mark.asyncio
async def test_my_feature(mock_claude_sdk, initialized_workspace):
    """Test my new feature."""
    # Test code that calls LLM via claude_agent_sdk
    pass
```

### Step 2: Generate Recording

```bash
# Run in record mode
EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_my_feature.py -v
```

This will:
1. Make real LLM API calls
2. Save request/response to `recordings/`
3. Display hash for reference

### Step 3: Run with Recording

```bash
# Normal mode (replay)
pytest tests/integration/test_my_feature.py -v
```

Tests now run fast without API calls!

## Troubleshooting

### "No recording found for request hash: XXX"

**Cause:** Test parameters changed or recording doesn't exist yet

**Solution:**
1. Run in record mode to generate recording
2. Check if request parameters match exactly
3. Verify recordings directory exists

### Test imports failing

**Cause:** Scripts directory not in Python path

**Solution:** Add to top of test file:
```python
import sys
from pathlib import Path

_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))
```

### Mock SDK not working

**Cause:** `conftest.py` auto-patching might not be active

**Solution:** Check that:
1. `conftest.py` is in tests/ directory
2. Test is using pytest fixtures
3. `mock_claude_sdk` fixture is being used (even if not directly referenced)

## Maintenance

### Regenerating Recordings

When workflow changes, regenerate recordings:

```bash
# Clear old recordings
rm -rf tests/recordings/

# Generate new recordings
EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/ -v
```

### Adding New Experts

When adding new experts to workflow:

1. Update test fixtures with new expert names
2. Generate recordings for new expert combinations
3. Update UI state tests if new fields added

### Versioning Recordings

Recordings are tied to:
- Prompt structure
- Expert definitions
- Workflow logic

When these change significantly, regenerate recordings and consider versioning:

```
recordings/
├── v1/  # Old recordings
└── v2/  # New recordings
```

## Performance

**Test Suite Performance:**
- Unit tests: <5 seconds
- Integration tests (replay): <30 seconds
- Integration tests (record): 5-10 minutes (one-time)

**Coverage Goals:**
- State management: 95%+
- Workflow orchestration: 90%+
- UI state contract: 100%

## Best Practices

### DO

✅ Use fixtures for workspace and state setup
✅ Test state transitions explicitly
✅ Validate UI contract in dedicated tests
✅ Generate recordings when workflow changes
✅ Use descriptive test names
✅ Group related tests in classes

### DON'T

❌ Make real API calls in tests (use record mode explicitly)
❌ Modify `state.json` directly (use StateManager)
❌ Skip UI state validation tests
❌ Commit recordings with sensitive data
❌ Hard-code session IDs in tests

## CI Integration

```yaml
# .github/workflows/expert-feedback-tests.yml
name: Expert Feedback Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run tests
        run: |
          cd .claude/skills/expert-feedback
          pytest tests/ -v
        env:
          EXPERT_FEEDBACK_TEST_MODE: replay
```

## Running Existing Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Specific test files
pytest tests/test_config.py -v
pytest tests/test_state_manager.py -v
pytest tests/test_validation.py -v
pytest tests/test_progress_tracker.py -v
```

### Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Specific integration tests
pytest tests/integration/test_full_workflow.py -v
pytest tests/integration/test_workflow_phases.py -v
pytest tests/integration/test_state_ui.py -v
```

### With Coverage

```bash
# Run with coverage report
pytest tests/ --cov=scripts --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Workspace Snapshots

Tests can save/restore complete workspace state to avoid redundant work.

### How It Works

- **Snapshots saved**: `tests/recordings/{test_name}/workspace/`
- **Contains**: state.json, expert reviews, mock projects, logs, session files
- **Auto-cleanup**: Deleted when recordings regenerated (via existing cleanup in conftest.py)
- **Optional**: Tests have fallbacks for standalone execution

### Benefits

- **Faster recording generation**: Synthesis reuses expert reviews (~2m → ~45s)
- **Test chaining**: Build on previous test results
- **Maintains isolation**: Fallback ensures tests can run standalone
- **Zero new cleanup code**: Existing conftest.py cleanup handles snapshot directories

### Usage Pattern

**Producer test (saves snapshot):**

```python
# At end of test, in record mode
if mock_claude_sdk and mock_claude_sdk.mode == "record":
    from fixtures.workspace_snapshot import snapshot_workspace
    snapshot_workspace("test_name", workspace, recordings_dir)
    print("  📸 Workspace snapshot saved")
```

**Consumer test (restores snapshot):**

```python
# At beginning of test
from fixtures.workspace_snapshot import has_snapshot, restore_workspace

predecessor = "test_predecessor_name"
recordings_base = Path(__file__).parent.parent / "recordings"

if has_snapshot(predecessor, recordings_base):
    print("\n  ✅ Restoring workspace from snapshot")
    restore_workspace(predecessor, workspace, recordings_base)
else:
    # Fallback: generate ourselves
    print("\n  ⚠️  No snapshot found, running as fallback...")
    # ... run prerequisite work ...
```

### Example: Synthesis Test Chain

```bash
# Step 1: Generate iteration 1 expert reviews (saves snapshot)
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_iteration_1_with_questions -v

# Snapshot saved to: tests/recordings/test_generate_iteration_1_with_questions/workspace/

# Step 2: Generate synthesis (restores snapshot, skips re-running experts)
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_synthesis_iteration_1 -v

# Output: "✅ Restoring expert reviews from snapshot" (~45s instead of ~2m)
```

### Directory Structure

```text
tests/recordings/
├── test_generate_iteration_1_with_questions/
│   ├── *.request.json                    # LLM recordings
│   ├── *.response.json
│   └── workspace/                        # Workspace snapshot
│       ├── state.json
│       ├── simple-calculator/
│       ├── iteration-1/experts/
│       ├── logs/
│       └── session-*.json
└── test_generate_synthesis_iteration_1/
    ├── *.request.json
    ├── *.response.json
    └── workspace/                        # Includes synthesis results
        ├── state.json
        ├── iteration-1/
        │   ├── experts/
        │   ├── synthesized.md
        │   └── questions.json
        └── logs/
```

### Verification

**Test snapshot creation:**

```bash
cd .claude/skills/expert-feedback

# Generate with snapshot
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_iteration_1_with_questions -v

# Verify snapshot exists
ls tests/recordings/test_generate_iteration_1_with_questions/workspace/
# Should show: state.json, simple-calculator/, iteration-1/, logs/
```

**Test snapshot restoration:**

```bash
# Run synthesis test - should restore snapshot (fast)
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_synthesis_iteration_1 -v

# Check output for: "✅ Restoring expert reviews from snapshot"
# Should NOT see: "running experts" (unless no snapshot found)
```

**Test cleanup:**

```bash
# Regenerate recordings - should auto-delete snapshots
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_iteration_1_with_questions -v

# Old snapshot deleted before new one created
```

**Test standalone capability:**

```bash
# Delete snapshot manually
rm -rf tests/recordings/test_generate_iteration_1_with_questions/workspace

# Run synthesis - should use fallback
EXPERT_FEEDBACK_TEST_MODE=record \
  pytest tests/integration/test_generate_workflow_recordings.py::test_generate_synthesis_iteration_1 -v

# Check output for: "⚠️  No snapshot found, running experts as fallback..."
# Should complete successfully despite missing snapshot
```

### API Reference

**WorkspaceSnapshot class:**

```python
from fixtures.workspace_snapshot import WorkspaceSnapshot

snapshot = WorkspaceSnapshot("test_name", recordings_dir)
snapshot.save(workspace)           # Copy workspace to snapshot
snapshot.restore(workspace)        # Restore workspace from snapshot
snapshot.exists()                  # Check if snapshot exists
snapshot.get_state()              # Read state.json without full restore
snapshot.get_info()               # Get metadata (size, file count, state)
```

**Convenience functions:**

```python
from fixtures.workspace_snapshot import (
    snapshot_workspace,
    restore_workspace,
    has_snapshot,
    get_snapshot_info
)

# Simple API
snapshot_workspace("test_name", workspace, recordings_dir)
restore_workspace("test_name", workspace, recordings_dir)
has_snapshot("test_name", recordings_dir)  # Returns bool
info = get_snapshot_info("test_name", recordings_dir)  # Returns dict or None
```

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Generate recordings for new tests
3. Ensure UI state validation tests pass
4. Update this README if adding new patterns

## Support

For issues or questions:
- Check troubleshooting section above
- Review existing tests for patterns
- Check `conftest.py` for available fixtures

## Summary

This testing infrastructure enables:
- ✅ Fast iteration without LLM wait times
- ✅ Automated workflow validation
- ✅ UI state contract enforcement
- ✅ Easy test creation with fixtures
- ✅ Deterministic, repeatable tests

Happy testing! 🧪
