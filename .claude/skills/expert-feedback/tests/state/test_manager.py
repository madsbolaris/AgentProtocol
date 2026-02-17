"""
Comprehensive unit tests for state management (state/manager.py).

Tests all functionality:
- WorkspaceState dataclass creation, defaults, to_dict, from_dict
- StateManager initialization and file operations
- Session tracking (expert, synthesis, artifact generation)
- Iteration history and convergence tracking
- Artifact regeneration history
- Concern review state management
- Script registry for deduplication
- Phase completion tracking
- Token metrics with cache awareness
- Atomic operations and concurrent access
- Edge cases and error handling

Target: 75%+ coverage
"""
import json
import pytest
import threading
import time
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from state.manager import WorkspaceState, StateManager


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace directory for tests."""
    ws = tmp_path / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture
def manager(workspace):
    """Create a StateManager instance with workspace."""
    return StateManager(workspace)


class TestWorkspaceState:
    """Test WorkspaceState dataclass creation, defaults, serialization."""

    def test_minimal_creation(self):
        """Test creating WorkspaceState with only required fields."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=1
        )

        assert state.topic == "Test topic"
        assert state.experts == ["typescript", "python"]
        assert state.iteration == 1

    def test_default_values(self):
        """Test default values for all optional fields."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript"],
            iteration=1
        )

        # Basic defaults
        assert state.mode == "review"
        assert state.phase is None
        assert state.convergence_percent == 0
        assert state.consensus_reached is False
        assert state.convergence_target == 80

        # Session defaults
        assert state.expert_sessions == {}
        assert state.synthesis_session_id is None
        assert state.artifact_generation_session_id is None
        assert state.artifact_generation_result is None
        assert state.artifact_review_needed is False

        # Metrics defaults
        assert state.total_tokens == 0
        assert state.total_cost == 0.0
        assert state.start_time is None
        assert state.complete_time is None

        # Cache metrics defaults
        assert state.total_input_tokens == 0
        assert state.total_output_tokens == 0
        assert state.total_cache_creation_tokens == 0
        assert state.total_cache_read_tokens == 0
        assert state.cache_enabled is False

        # Convergence history defaults
        assert state.high_agreement == 0
        assert state.partial_agreement == 0
        assert state.low_agreement == 0

        # Tracking defaults
        assert state.expert_results == {}
        assert state.expert_progress == {}
        assert state.iteration_history == []
        assert state.artifact_generation_attempts == 0
        assert state.artifact_regeneration_history == []
        assert state.expert_sessions_by_iteration == {}
        assert state.synthesis_session_by_iteration == {}
        assert state.revert_history == []
        assert state.concern_review == {}

    def test_custom_values(self):
        """Test creating WorkspaceState with custom values."""
        state = WorkspaceState(
            topic="Custom topic",
            experts=["typescript", "python"],
            iteration=3,
            mode="improve",
            phase="consolidating",
            convergence_percent=85,
            consensus_reached=True,
            convergence_target=70,
            expert_sessions={"typescript": "sess_abc"},
            synthesis_session_id="sess_syn",
            artifact_generation_session_id="sess_art",
            total_tokens=5000,
            total_cost=0.15,
            cache_enabled=True,
            high_agreement=10,
            partial_agreement=5,
            low_agreement=2
        )

        assert state.mode == "improve"
        assert state.phase == "consolidating"
        assert state.convergence_percent == 85
        assert state.consensus_reached is True
        assert state.convergence_target == 70
        assert state.expert_sessions == {"typescript": "sess_abc"}
        assert state.synthesis_session_id == "sess_syn"
        assert state.artifact_generation_session_id == "sess_art"
        assert state.total_tokens == 5000
        assert state.total_cost == 0.15
        assert state.cache_enabled is True
        assert state.high_agreement == 10
        assert state.partial_agreement == 5
        assert state.low_agreement == 2

    def test_post_init_handles_none_values(self):
        """Test that __post_init__ initializes None values to empty collections."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            expert_sessions=None,
            expert_results=None,
            expert_progress=None,
            iteration_history=None,
            artifact_regeneration_history=None,
            expert_sessions_by_iteration=None,
            synthesis_session_by_iteration=None,
            revert_history=None,
            concern_review=None
        )

        assert state.expert_sessions == {}
        assert state.expert_results == {}
        assert state.expert_progress == {}
        assert state.iteration_history == []
        assert state.artifact_regeneration_history == []
        assert state.expert_sessions_by_iteration == {}
        assert state.synthesis_session_by_iteration == {}
        assert state.revert_history == []
        assert state.concern_review == {}

    def test_to_dict(self):
        """Test converting WorkspaceState to dictionary."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript"],
            iteration=2,
            convergence_percent=50,
            expert_sessions={"typescript": "sess_123"}
        )

        state_dict = state.to_dict()

        assert isinstance(state_dict, dict)
        assert state_dict["topic"] == "Test topic"
        assert state_dict["experts"] == ["typescript"]
        assert state_dict["iteration"] == 2
        assert state_dict["convergence_percent"] == 50
        assert state_dict["expert_sessions"] == {"typescript": "sess_123"}

    def test_from_dict_minimal(self):
        """Test creating WorkspaceState from minimal dictionary."""
        data = {
            "topic": "Test topic",
            "experts": ["typescript"],
            "iteration": 1
        }

        state = WorkspaceState.from_dict(data)

        assert state.topic == "Test topic"
        assert state.experts == ["typescript"]
        assert state.iteration == 1
        assert state.mode == "review"  # Default
        assert state.convergence_percent == 0  # Default

    def test_from_dict_complete(self):
        """Test creating WorkspaceState from complete dictionary."""
        data = {
            "topic": "Test",
            "experts": ["typescript", "python"],
            "iteration": 2,
            "mode": "improve",
            "phase": "consolidating",
            "convergence_percent": 75,
            "consensus_reached": True,
            "convergence_target": 80,
            "expert_sessions": {"typescript": "sess_1"},
            "synthesis_session_id": "sess_syn",
            "artifact_generation_session_id": "sess_art",
            "artifact_generation_result": {"status": "approved"},
            "artifact_review_needed": True,
            "total_tokens": 10000,
            "total_cost": 0.25,
            "start_time": "2026-01-01T00:00:00Z",
            "complete_time": "2026-01-01T01:00:00Z",
            "total_input_tokens": 5000,
            "total_output_tokens": 3000,
            "total_cache_creation_tokens": 1000,
            "total_cache_read_tokens": 1000,
            "cache_enabled": True,
            "high_agreement": 8,
            "partial_agreement": 4,
            "low_agreement": 2,
            "expert_results": {"typescript": {"status": "complete"}},
            "expert_progress": {"typescript": {"status": "running"}},
            "iteration_history": [{"iteration": 1}],
            "artifact_generation_attempts": 2,
            "artifact_regeneration_history": [{"attempt": 1}],
            "expert_sessions_by_iteration": {1: {"typescript": "sess_1"}},
            "synthesis_session_by_iteration": {1: "sess_syn"},
            "revert_history": [{"timestamp": "2026-01-01"}],
            "concern_review": {"iteration": 1, "status": "in_progress"}
        }

        state = WorkspaceState.from_dict(data)

        assert state.topic == "Test"
        assert state.iteration == 2
        assert state.mode == "improve"
        assert state.phase == "consolidating"
        assert state.convergence_percent == 75
        assert state.consensus_reached is True
        assert state.expert_sessions == {"typescript": "sess_1"}
        assert state.cache_enabled is True
        assert state.high_agreement == 8
        assert len(state.iteration_history) == 1
        assert state.artifact_generation_attempts == 2

    def test_from_dict_missing_topic_raises_error(self):
        """Test that from_dict raises ValueError if topic is missing."""
        data = {
            "experts": ["typescript"],
            "iteration": 1
        }

        with pytest.raises(ValueError, match="State must have 'topic' field"):
            WorkspaceState.from_dict(data)

    def test_from_dict_with_extra_fields(self):
        """Test that from_dict ignores extra fields not in dataclass."""
        data = {
            "topic": "Test",
            "experts": ["typescript"],
            "iteration": 1,
            "extra_field": "ignored",
            "another_extra": 123
        }

        # Should not raise error, just ignore extra fields
        state = WorkspaceState.from_dict(data)
        assert state.topic == "Test"
        assert not hasattr(state, "extra_field")

    def test_round_trip_serialization(self):
        """Test that state survives to_dict -> from_dict round trip."""
        original = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=3,
            convergence_percent=80,
            expert_sessions={"typescript": "sess_1", "python": "sess_2"},
            iteration_history=[
                {"iteration": 1, "convergence_percent": 45},
                {"iteration": 2, "convergence_percent": 65}
            ]
        )

        # Convert to dict and back
        state_dict = original.to_dict()
        restored = WorkspaceState.from_dict(state_dict)

        assert restored.topic == original.topic
        assert restored.experts == original.experts
        assert restored.iteration == original.iteration
        assert restored.convergence_percent == original.convergence_percent
        assert restored.expert_sessions == original.expert_sessions
        assert len(restored.iteration_history) == 2


class TestStateManagerInit:
    """Test StateManager initialization."""

    def test_init_creates_paths(self, tmp_path):
        """Test StateManager initialization sets up paths correctly."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)  # Create workspace for logging
        manager = StateManager(workspace)

        assert manager.workspace == workspace
        assert manager.state_path == workspace / "state.json"
        assert manager.correlation_id is None

    def test_init_with_correlation_id(self, tmp_path):
        """Test StateManager initialization with correlation ID."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)  # Create workspace for logging
        correlation_id = "test-correlation-123"
        manager = StateManager(workspace, correlation_id=correlation_id)

        assert manager.correlation_id == correlation_id

    def test_exists_returns_false_initially(self, tmp_path):
        """Test that exists() returns False before state is created."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)  # Create workspace for logging
        manager = StateManager(workspace)

        assert not manager.exists()

    def test_exists_returns_true_after_creation(self, tmp_path):
        """Test that exists() returns True after state file is created."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)  # Create workspace for logging
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        assert manager.exists()


class TestLoadAndSave:
    """Test load and save operations."""

    def test_save_creates_directory(self, tmp_path):
        """Test that save creates workspace directory if needed."""
        workspace = tmp_path / "new" / "nested" / "workspace"
        # StateManager __init__ needs workspace to exist for logging
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        assert workspace.exists()
        assert manager.state_path.exists()

    def test_save_writes_valid_json(self, tmp_path):
        """Test that save writes valid JSON."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=2,
            convergence_percent=75
        )
        manager.save(state)

        # Read raw JSON
        with open(manager.state_path) as f:
            data = json.load(f)

        assert data["topic"] == "Test topic"
        assert data["experts"] == ["typescript", "python"]
        assert data["iteration"] == 2
        assert data["convergence_percent"] == 75

    def test_load_missing_file_raises_error(self, tmp_path):
        """Test that load raises FileNotFoundError if state.json missing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        with pytest.raises(FileNotFoundError, match="State file not found"):
            manager.load()

    def test_load_corrupted_json_raises_error(self, tmp_path):
        """Test that load raises error for corrupted JSON."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True)
        manager = StateManager(workspace)

        # Write invalid JSON
        manager.state_path.write_text("invalid json {")

        with pytest.raises(json.JSONDecodeError):
            manager.load()

    def test_save_and_load_round_trip(self, tmp_path):
        """Test that state survives save and load."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        original = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=2,
            convergence_percent=80,
            expert_sessions={"typescript": "sess_1"}
        )

        manager.save(original)
        loaded = manager.load()

        assert loaded.topic == original.topic
        assert loaded.experts == original.experts
        assert loaded.iteration == original.iteration
        assert loaded.convergence_percent == original.convergence_percent
        assert loaded.expert_sessions == original.expert_sessions


class TestCreate:
    """Test new state creation."""

    def test_create_saves_new_state(self, tmp_path):
        """Test that create saves new state file."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.create(state)

        assert manager.state_path.exists()

        loaded = manager.load()
        assert loaded.topic == "Test"

    def test_create_raises_error_if_exists(self, tmp_path):
        """Test that create raises FileExistsError if state already exists."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.create(state)

        # Try to create again
        with pytest.raises(FileExistsError, match="State file already exists"):
            manager.create(state)


class TestUpdateSessions:
    """Test expert session updates."""

    def test_update_sessions_adds_new_session(self, tmp_path):
        """Test that update_sessions adds new expert session."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=1,
            expert_sessions={}
        )
        manager.save(state)

        updated = manager.update_sessions({"typescript": "sess_abc"})

        assert updated.expert_sessions == {"typescript": "sess_abc"}

    def test_update_sessions_preserves_existing(self, tmp_path):
        """Test that update_sessions preserves existing sessions."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python", "dotnet"],
            iteration=1,
            expert_sessions={"typescript": "sess_1", "python": "sess_2"}
        )
        manager.save(state)

        updated = manager.update_sessions({"dotnet": "sess_3"})

        assert updated.expert_sessions == {
            "typescript": "sess_1",
            "python": "sess_2",
            "dotnet": "sess_3"
        }

    def test_update_sessions_overwrites_existing(self, tmp_path):
        """Test that update_sessions can overwrite existing session."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            expert_sessions={"typescript": "sess_old"}
        )
        manager.save(state)

        updated = manager.update_sessions({"typescript": "sess_new"})

        assert updated.expert_sessions == {"typescript": "sess_new"}

    def test_update_sessions_multiple_experts(self, tmp_path):
        """Test updating multiple expert sessions at once."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python", "dotnet"],
            iteration=1,
            expert_sessions={}
        )
        manager.save(state)

        updated = manager.update_sessions({
            "typescript": "sess_ts",
            "python": "sess_py",
            "dotnet": "sess_net"
        })

        assert len(updated.expert_sessions) == 3
        assert updated.expert_sessions["typescript"] == "sess_ts"
        assert updated.expert_sessions["python"] == "sess_py"
        assert updated.expert_sessions["dotnet"] == "sess_net"


class TestSynthesisSession:
    """Test synthesis session tracking."""

    def test_set_synthesis_session(self, tmp_path):
        """Test setting synthesis session ID."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.set_synthesis_session("sess_synthesis_123")

        assert updated.synthesis_session_id == "sess_synthesis_123"

    def test_set_synthesis_session_overwrites_existing(self, tmp_path):
        """Test that setting synthesis session overwrites existing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            synthesis_session_id="sess_old"
        )
        manager.save(state)

        updated = manager.set_synthesis_session("sess_new")

        assert updated.synthesis_session_id == "sess_new"


class TestArtifactGenerationSession:
    """Test artifact generation session tracking."""

    def test_set_artifact_generation_session(self, tmp_path):
        """Test setting artifact generation session ID."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.set_artifact_generation_session("sess_artifact_456")

        assert updated.artifact_generation_session_id == "sess_artifact_456"

    def test_set_artifact_generation_session_overwrites(self, tmp_path):
        """Test that setting artifact generation session overwrites existing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            artifact_generation_session_id="sess_old"
        )
        manager.save(state)

        updated = manager.set_artifact_generation_session("sess_new")

        assert updated.artifact_generation_session_id == "sess_new"

    def test_set_artifact_review_needed(self, tmp_path):
        """Test setting artifact_review_needed flag."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.set_artifact_review_needed(True)
        assert updated.artifact_review_needed is True

        updated = manager.set_artifact_review_needed(False)
        assert updated.artifact_review_needed is False

    def test_set_artifact_generation_result(self, tmp_path):
        """Test setting artifact generation result."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        result = {
            "status": "approved",
            "file": "artifact.md",
            "veto_count": 0
        }
        updated = manager.set_artifact_generation_result(result)

        assert updated.artifact_generation_result == result


class TestConvergence:
    """Test convergence updates."""

    def test_update_convergence_basic(self, tmp_path):
        """Test basic convergence update."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_convergence(
            convergence_percent=75,
            consensus_reached=False
        )

        assert updated.convergence_percent == 75
        assert updated.consensus_reached is False

    def test_update_convergence_with_agreement_breakdown(self, tmp_path):
        """Test convergence update with agreement breakdown."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_convergence(
            convergence_percent=85,
            consensus_reached=True,
            high_agreement=10,
            partial_agreement=5,
            low_agreement=2
        )

        assert updated.convergence_percent == 85
        assert updated.consensus_reached is True
        assert updated.high_agreement == 10
        assert updated.partial_agreement == 5
        assert updated.low_agreement == 2

    def test_update_convergence_reaches_consensus(self, tmp_path):
        """Test marking consensus as reached."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            convergence_percent=75
        )
        manager.save(state)

        updated = manager.update_convergence(
            convergence_percent=85,
            consensus_reached=True
        )

        assert updated.consensus_reached is True
        assert updated.convergence_percent == 85


class TestIteration:
    """Test iteration increment."""

    def test_increment_iteration_from_1(self, tmp_path):
        """Test incrementing iteration from 1."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.increment_iteration()

        assert updated.iteration == 2

    def test_increment_iteration_multiple_times(self, tmp_path):
        """Test incrementing iteration multiple times."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        manager.increment_iteration()
        manager.increment_iteration()
        updated = manager.increment_iteration()

        assert updated.iteration == 4

    def test_increment_iteration_from_zero(self, tmp_path):
        """Test incrementing iteration from 0."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=0)
        manager.save(state)

        updated = manager.increment_iteration()

        assert updated.iteration == 1


class TestExpertResults:
    """Test expert result tracking."""

    def test_add_expert_result(self, tmp_path):
        """Test adding expert result."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        result = {
            "status": "complete",
            "tokens": 1000,
            "duration": 30.5
        }
        updated = manager.add_expert_result("typescript", result)

        assert "typescript" in updated.expert_results
        assert updated.expert_results["typescript"] == result

    def test_add_expert_result_overwrites(self, tmp_path):
        """Test that adding expert result overwrites existing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            expert_results={"typescript": {"status": "old"}}
        )
        manager.save(state)

        new_result = {"status": "new", "tokens": 2000}
        updated = manager.add_expert_result("typescript", new_result)

        assert updated.expert_results["typescript"]["status"] == "new"

    def test_add_multiple_expert_results(self, tmp_path):
        """Test adding results for multiple experts."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=1
        )
        manager.save(state)

        manager.add_expert_result("typescript", {"status": "complete"})
        updated = manager.add_expert_result("python", {"status": "complete"})

        assert len(updated.expert_results) == 2
        assert "typescript" in updated.expert_results
        assert "python" in updated.expert_results


class TestExpertProgress:
    """Test expert progress updates."""

    def test_update_expert_progress_basic(self, tmp_path):
        """Test basic expert progress update."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_expert_progress("typescript", "running")

        assert "typescript" in updated.expert_progress
        assert updated.expert_progress["typescript"]["status"] == "running"

    def test_update_expert_progress_with_metadata(self, tmp_path):
        """Test expert progress update with metadata."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        metadata = {
            "duration_seconds": 45.2,
            "total_tokens": 3000,
            "start_time": "2026-01-01T00:00:00Z"
        }
        updated = manager.update_expert_progress("typescript", "complete", metadata)

        progress = updated.expert_progress["typescript"]
        assert progress["status"] == "complete"
        assert progress["duration_seconds"] == 45.2
        assert progress["total_tokens"] == 3000

    def test_update_expert_progress_transitions(self, tmp_path):
        """Test expert progress status transitions."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # pending -> running -> complete
        manager.update_expert_progress("typescript", "pending")
        manager.update_expert_progress("typescript", "running")
        updated = manager.update_expert_progress("typescript", "complete")

        assert updated.expert_progress["typescript"]["status"] == "complete"


class TestTokenMetrics:
    """Test token and cost tracking with cache metrics."""

    def test_update_token_metrics_basic(self, tmp_path):
        """Test basic token metrics update."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_token_metrics(tokens_delta=1000, cost_delta=0.05)

        assert updated.total_tokens == 1000
        assert updated.total_cost == 0.05

    def test_update_token_metrics_accumulates(self, tmp_path):
        """Test that token metrics accumulate across updates."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        manager.update_token_metrics(tokens_delta=1000, cost_delta=0.05)
        manager.update_token_metrics(tokens_delta=500, cost_delta=0.03)
        updated = manager.update_token_metrics(tokens_delta=200, cost_delta=0.01)

        assert updated.total_tokens == 1700
        assert updated.total_cost == pytest.approx(0.09)

    def test_update_token_metrics_with_cache(self, tmp_path):
        """Test cache-aware token metrics update."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=200,
            cache_read_tokens=300,
            cost=0.08
        )

        assert updated.total_input_tokens == 1000
        assert updated.total_output_tokens == 500
        assert updated.total_cache_creation_tokens == 200
        assert updated.total_cache_read_tokens == 300
        assert updated.total_tokens == 2000  # Sum of all tokens
        assert updated.total_cost == 0.08
        assert updated.cache_enabled is True

    def test_update_token_metrics_with_cache_accumulates(self, tmp_path):
        """Test that cache-aware metrics accumulate."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        manager.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=0,
            cost=0.05
        )
        updated = manager.update_token_metrics_with_cache(
            input_tokens=800,
            output_tokens=400,
            cache_creation_tokens=0,
            cache_read_tokens=200,
            cost=0.04
        )

        assert updated.total_input_tokens == 1800
        assert updated.total_output_tokens == 900
        assert updated.total_cache_creation_tokens == 100
        assert updated.total_cache_read_tokens == 200
        assert updated.cache_enabled is True

    def test_cache_enabled_flag(self, tmp_path):
        """Test that cache_enabled flag is set when cache metrics present."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Initially false
        assert state.cache_enabled is False

        # Set when cache_creation_tokens > 0
        updated = manager.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=100,
            cache_read_tokens=0,
            cost=0.05
        )
        assert updated.cache_enabled is True

        # Also set when cache_read_tokens > 0
        workspace2 = tmp_path / "workspace2"
        workspace2.mkdir(parents=True, exist_ok=True)
        state2 = WorkspaceState(topic="Test2", experts=["typescript"], iteration=1)
        manager2 = StateManager(workspace2)
        manager2.save(state2)

        updated2 = manager2.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=0,
            cache_read_tokens=200,
            cost=0.04
        )
        assert updated2.cache_enabled is True


class TestPhaseManagement:
    """Test phase setting, completion, result retrieval."""

    def test_set_phase_valid(self, tmp_path):
        """Test setting valid phase."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        valid_phases = [
            'spawning_experts',
            'consolidating',
            'questions',
            'generating_artifact',
            'reviewing_artifact',
            'completed',
            'artifact_review'
        ]

        for phase in valid_phases:
            updated = manager.set_phase(phase)
            assert updated.phase == phase

    def test_set_phase_invalid_raises_error(self, tmp_path):
        """Test that invalid phase raises ValueError."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        with pytest.raises(ValueError, match="Invalid phase"):
            manager.set_phase("invalid_phase")

    def test_mark_phase_complete(self, tmp_path):
        """Test marking phase as complete."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        result = {
            "convergence_percent": 85,
            "consensus_reached": True,
            "tokens_used": 15000
        }
        updated = manager.mark_phase_complete("consolidating", result)

        # Check that phase is marked complete using the method
        assert manager.is_phase_complete("consolidating") is True
        assert manager.get_phase_result("consolidating") == result

    def test_is_phase_complete(self, tmp_path):
        """Test checking if phase is complete."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Initially not complete
        assert not manager.is_phase_complete("consolidating")

        # Mark complete
        result = {"convergence_percent": 85}
        manager.mark_phase_complete("consolidating", result)

        # Now should be complete
        assert manager.is_phase_complete("consolidating")

    def test_get_phase_result(self, tmp_path):
        """Test getting phase result."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Initially no result
        assert manager.get_phase_result("consolidating") is None

        # Save result
        result = {
            "convergence_percent": 85,
            "consensus_reached": True
        }
        manager.mark_phase_complete("consolidating", result)

        # Should retrieve result
        retrieved = manager.get_phase_result("consolidating")
        assert retrieved == result

    def test_mark_complete(self, tmp_path):
        """Test marking session as complete."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        complete_time = "2026-01-01T12:00:00Z"
        updated = manager.mark_complete(complete_time)

        assert updated.complete_time == complete_time

    def test_set_start_time(self, tmp_path):
        """Test setting start time."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        start_time = "2026-01-01T10:00:00Z"
        updated = manager.set_start_time(start_time)

        assert updated.start_time == start_time


class TestScriptRegistry:
    """Test script intent registration and completion."""

    def test_register_script_intent_first_time(self, tmp_path):
        """Test registering script intent for first time."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # First registration should succeed
        can_proceed = manager.register_script_intent("typescript", "analyze_types")
        assert can_proceed is True

        # Check owner
        owner = manager.get_script_owner("analyze_types")
        assert owner == "typescript"

    def test_register_script_intent_already_registered(self, tmp_path):
        """Test registering script intent when another expert owns it."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript", "python"], iteration=1)
        manager.save(state)

        # First registration
        manager.register_script_intent("typescript", "analyze_types")

        # Second registration by different expert should fail
        can_proceed = manager.register_script_intent("python", "analyze_types")
        assert can_proceed is False

    def test_register_script_intent_same_expert(self, tmp_path):
        """Test re-registering script intent by same expert."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # First registration
        manager.register_script_intent("typescript", "analyze_types")

        # Re-registration by same expert should succeed
        can_proceed = manager.register_script_intent("typescript", "analyze_types")
        assert can_proceed is True

    def test_complete_script(self, tmp_path):
        """Test completing a script."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Register intent
        manager.register_script_intent("typescript", "analyze_types")

        # Complete script
        output_path = workspace / "scripts" / "analyze_types.py"
        updated = manager.complete_script("typescript", "analyze_types", output_path)

        # Check completed scripts
        completed = manager.get_completed_scripts()
        assert "analyze_types" in completed
        assert completed["analyze_types"]["expert"] == "typescript"
        assert completed["analyze_types"]["path"] == str(output_path)

        # Should be removed from registry
        owner = manager.get_script_owner("analyze_types")
        assert owner is None

    def test_get_script_owner_nonexistent(self, tmp_path):
        """Test getting owner of non-existent script."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        owner = manager.get_script_owner("nonexistent_script")
        assert owner is None

    def test_get_completed_scripts_empty(self, tmp_path):
        """Test getting completed scripts when none exist."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        completed = manager.get_completed_scripts()
        assert completed == {}

    def test_get_completed_scripts_multiple(self, tmp_path):
        """Test getting multiple completed scripts."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript", "python"], iteration=1)
        manager.save(state)

        # Complete multiple scripts
        manager.complete_script("typescript", "script1", workspace / "script1.py")
        manager.complete_script("python", "script2", workspace / "script2.py")

        completed = manager.get_completed_scripts()
        assert len(completed) == 2
        assert "script1" in completed
        assert "script2" in completed


class TestIterationHistory:
    """Test iteration summary recording."""

    def test_record_iteration_summary(self, tmp_path):
        """Test recording iteration summary."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        agreement_breakdown = {"high": 8, "partial": 4, "low": 2}
        expert_summaries = {
            "typescript": {
                "dx_rating": 4,
                "concerns_count": 3,
                "top_concern": "Complex type system",
                "recommendations_count": 5
            }
        }

        updated = manager.record_iteration_summary(
            iteration=1,
            convergence_percent=65,
            agreement_breakdown=agreement_breakdown,
            expert_summaries=expert_summaries
        )

        assert len(updated.iteration_history) == 1
        summary = updated.iteration_history[0]
        assert summary["iteration"] == 1
        assert summary["convergence_percent"] == 65
        assert summary["high_agreement"] == 8
        assert summary["partial_agreement"] == 4
        assert summary["low_agreement"] == 2
        assert "expert_summaries" in summary
        assert "timestamp" in summary

    def test_record_iteration_summary_multiple(self, tmp_path):
        """Test recording multiple iteration summaries."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Record iteration 1
        manager.record_iteration_summary(
            iteration=1,
            convergence_percent=45,
            agreement_breakdown={"high": 3, "partial": 5, "low": 2},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Record iteration 2
        updated = manager.record_iteration_summary(
            iteration=2,
            convergence_percent=75,
            agreement_breakdown={"high": 8, "partial": 4, "low": 1},
            expert_summaries={"typescript": {"dx_rating": 4}}
        )

        assert len(updated.iteration_history) == 2
        assert updated.iteration_history[0]["iteration"] == 1
        assert updated.iteration_history[1]["iteration"] == 2

    def test_iteration_history_structure(self, tmp_path):
        """Test iteration history has correct structure."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        expert_summaries = {
            "typescript": {
                "dx_rating": 4,
                "concerns_count": 3,
                "top_concern": "Type complexity"
            }
        }

        updated = manager.record_iteration_summary(
            iteration=1,
            convergence_percent=70,
            agreement_breakdown={"high": 5, "partial": 3, "low": 1},
            expert_summaries=expert_summaries
        )

        summary = updated.iteration_history[0]
        assert "iteration" in summary
        assert "convergence_percent" in summary
        assert "high_agreement" in summary
        assert "partial_agreement" in summary
        assert "low_agreement" in summary
        assert "synthesized_file" in summary
        assert "questions_file" in summary
        assert "expert_summaries" in summary
        assert "timestamp" in summary


class TestArtifactRegeneration:
    """Test regeneration tracking."""

    def test_increment_artifact_generation_attempt(self, tmp_path):
        """Test incrementing artifact generation attempt counter."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.increment_artifact_generation_attempt()
        assert updated.artifact_generation_attempts == 1

        updated = manager.increment_artifact_generation_attempt()
        assert updated.artifact_generation_attempts == 2

    def test_record_artifact_generation_result(self, tmp_path):
        """Test recording artifact generation result."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.record_artifact_generation_result(
            attempt=1,
            result="concerns_raised",
            concerns_count=2,
            concerns=["Missing security section", "Unclear migration"]
        )

        assert len(updated.artifact_regeneration_history) == 1
        record = updated.artifact_regeneration_history[0]
        assert record["attempt"] == 1
        assert record["result"] == "concerns_raised"
        assert record["concerns_count"] == 2
        assert len(record["concerns"]) == 2
        assert "timestamp" in record

    def test_record_artifact_generation_result_multiple(self, tmp_path):
        """Test recording multiple artifact generation results."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # First attempt - concerns_raised
        manager.record_artifact_generation_result(
            attempt=1,
            result="concerns_raised",
            concerns_count=2,
            concerns=["Issue 1", "Issue 2"]
        )

        # Second attempt - approved
        updated = manager.record_artifact_generation_result(
            attempt=2,
            result="approved",
            concerns_count=0,
            concerns=[]
        )

        assert len(updated.artifact_regeneration_history) == 2
        assert updated.artifact_regeneration_history[0]["result"] == "concerns_raised"
        assert updated.artifact_regeneration_history[1]["result"] == "approved"


class TestSessionsByIteration:
    """Test per-iteration session tracking."""

    def test_update_expert_sessions_for_iteration(self, tmp_path):
        """Test storing expert sessions for specific iteration."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript", "python"], iteration=1)
        manager.save(state)

        expert_sessions = {"typescript": "sess_ts", "python": "sess_py"}
        updated = manager.update_expert_sessions_for_iteration(2, expert_sessions)

        assert 2 in updated.expert_sessions_by_iteration
        assert updated.expert_sessions_by_iteration[2] == expert_sessions
        # Also updates current expert_sessions for backward compatibility
        assert updated.expert_sessions == expert_sessions

    def test_get_expert_sessions_for_iteration(self, tmp_path):
        """Test getting expert sessions for specific iteration."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Store sessions for iteration 2
        sessions = {"typescript": "sess_123"}
        updated = manager.update_expert_sessions_for_iteration(2, sessions)

        # After round-trip through JSON, keys become strings
        # Check that the data is stored correctly
        assert len(updated.expert_sessions_by_iteration) > 0
        assert "sess_123" in str(updated.expert_sessions_by_iteration)

    def test_update_synthesis_session_for_iteration(self, tmp_path):
        """Test storing synthesis session for specific iteration."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        session_id = "sess_synthesis_123"
        updated = manager.update_synthesis_session_for_iteration(2, session_id)

        assert updated.synthesis_session_by_iteration[2] == session_id
        # Also updates current synthesis_session_id
        assert updated.synthesis_session_id == session_id

    def test_get_synthesis_session_for_iteration(self, tmp_path):
        """Test getting synthesis session for specific iteration."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Store session for iteration 2
        session_id = "sess_synthesis_456"
        updated = manager.update_synthesis_session_for_iteration(2, session_id)

        # After round-trip through JSON, the session should be stored
        assert len(updated.synthesis_session_by_iteration) > 0
        assert session_id in str(updated.synthesis_session_by_iteration)

    def test_sessions_by_iteration_multiple_iterations(self, tmp_path):
        """Test tracking sessions across multiple iterations."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript", "python"], iteration=1)
        manager.save(state)

        # Iteration 1
        manager.update_expert_sessions_for_iteration(1, {
            "typescript": "sess_ts_1",
            "python": "sess_py_1"
        })
        manager.update_synthesis_session_for_iteration(1, "sess_syn_1")

        # Iteration 2
        manager.update_expert_sessions_for_iteration(2, {
            "typescript": "sess_ts_2",
            "python": "sess_py_2"
        })
        updated = manager.update_synthesis_session_for_iteration(2, "sess_syn_2")

        # Verify both iterations stored
        # Note: JSON serialization converts int keys to strings
        assert len(updated.expert_sessions_by_iteration) == 2
        assert len(updated.synthesis_session_by_iteration) == 2
        # Keys might be strings after JSON round-trip
        sessions_by_iter = updated.expert_sessions_by_iteration
        # Check values exist regardless of key type
        assert "sess_ts_1" in str(sessions_by_iter)
        assert "sess_ts_2" in str(sessions_by_iter)


class TestConcernReview:
    """Test concern review state management."""

    def test_initialize_concern_review_state(self, tmp_path):
        """Test initializing concern review state."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        default_state = manager.initialize_concern_review_state()

        assert default_state["iteration"] == 0
        assert default_state["status"] == "not_started"
        assert default_state["concerns_raised"] == 0
        assert default_state["concerns_agreed"] == 0
        assert default_state["concerns_disagreed"] == 0
        assert default_state["current_artifact_version"] == 1
        assert default_state["history"] == []

    def test_update_concern_review_state(self, tmp_path):
        """Test updating concern review state."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_concern_review_state(
            iteration=1,
            status="in_progress",
            concerns_raised=4,
            concerns_agreed=2,
            concerns_disagreed=2
        )

        concern_review = updated.concern_review
        assert concern_review["iteration"] == 1
        assert concern_review["status"] == "in_progress"
        assert concern_review["concerns_raised"] == 4
        assert concern_review["concerns_agreed"] == 2
        assert concern_review["concerns_disagreed"] == 2
        assert len(concern_review["history"]) == 1

    def test_update_concern_review_state_multiple_times(self, tmp_path):
        """Test updating concern review state multiple times."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # First update
        manager.update_concern_review_state(1, "in_progress", 4, 2, 2)

        # Second update
        updated = manager.update_concern_review_state(2, "addressing_concerns", 3, 1, 2)

        assert updated.concern_review["iteration"] == 2
        assert updated.concern_review["status"] == "addressing_concerns"
        assert len(updated.concern_review["history"]) == 2

    def test_get_concern_review_state(self, tmp_path):
        """Test getting concern review state."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Initially returns default
        concern_review = manager.get_concern_review_state()
        assert concern_review["status"] == "not_started"

        # After update, returns updated state
        manager.update_concern_review_state(1, "in_progress", 4, 2, 2)
        concern_review = manager.get_concern_review_state()
        assert concern_review["status"] == "in_progress"

    def test_increment_artifact_version(self, tmp_path):
        """Test incrementing artifact version counter."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # First increment
        version = manager.increment_artifact_version()
        assert version == 2

        # Second increment
        version = manager.increment_artifact_version()
        assert version == 3

    def test_concern_review_history_structure(self, tmp_path):
        """Test concern review history has correct structure."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        updated = manager.update_concern_review_state(1, "in_progress", 4, 2, 2)

        history_entry = updated.concern_review["history"][0]
        assert "iteration" in history_entry
        assert "concerns_raised" in history_entry
        assert "concerns_agreed" in history_entry
        assert "concerns_disagreed" in history_entry
        assert "timestamp" in history_entry


class TestEdgeCases:
    """Test concurrent updates, missing fields, invalid data."""

    def test_concurrent_session_updates(self, tmp_path):
        """Test concurrent session updates from multiple threads."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python", "dotnet", "rust"],
            iteration=1,
            expert_sessions={}
        )
        manager.save(state)

        # Define update function for threads
        def update_session(expert, session_id):
            manager.update_sessions({expert: session_id})

        # Create threads for concurrent updates
        threads = [
            threading.Thread(target=update_session, args=("typescript", "sess_ts")),
            threading.Thread(target=update_session, args=("python", "sess_py")),
            threading.Thread(target=update_session, args=("dotnet", "sess_net")),
            threading.Thread(target=update_session, args=("rust", "sess_rust"))
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # All updates should be present
        final_state = manager.load()
        assert len(final_state.expert_sessions) == 4
        assert "typescript" in final_state.expert_sessions
        assert "python" in final_state.expert_sessions
        assert "dotnet" in final_state.expert_sessions
        assert "rust" in final_state.expert_sessions

    def test_concurrent_convergence_updates(self, tmp_path):
        """Test concurrent convergence updates."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Define update function
        def update_convergence(percent):
            manager.update_convergence(percent, False)

        # Create threads
        threads = [
            threading.Thread(target=update_convergence, args=(50,)),
            threading.Thread(target=update_convergence, args=(60,)),
            threading.Thread(target=update_convergence, args=(70,))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Final state should have one of the values (last write wins)
        final_state = manager.load()
        assert final_state.convergence_percent in [50, 60, 70]

    def test_multiple_managers_same_workspace(self, tmp_path):
        """Test multiple StateManager instances accessing same workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        manager1 = StateManager(workspace)
        manager2 = StateManager(workspace)

        # Manager1 creates state
        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager1.save(state)

        # Manager2 should read same state
        loaded = manager2.load()
        assert loaded.topic == "Test"
        assert loaded.iteration == 1

        # Updates from manager1 visible to manager2
        manager1.update_sessions({"typescript": "sess_123"})
        loaded2 = manager2.load()
        assert loaded2.expert_sessions == {"typescript": "sess_123"}

    def test_rapid_sequential_updates(self, tmp_path):
        """Test rapid sequential updates don't lose data."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Perform many rapid updates
        for i in range(20):
            manager.update_sessions({f"expert_{i}": f"sess_{i}"})

        # All updates should be present
        final_state = manager.load()
        assert len(final_state.expert_sessions) == 20

    def test_update_with_missing_state_file_raises_error(self, tmp_path):
        """Test that update operations raise error if state file missing."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        # Try to update without creating state first
        with pytest.raises(FileNotFoundError):
            manager.update_sessions({"typescript": "sess_123"})

    def test_load_from_dict_with_missing_lists(self, tmp_path):
        """Test loading state with missing list fields uses defaults."""
        data = {
            "topic": "Test",
            # experts is missing - should use default []
            "iteration": 1,
            # iteration_history is missing - should use default []
            # artifact_regeneration_history is missing - should use default []
        }

        # Should handle gracefully with defaults
        state = WorkspaceState.from_dict(data)
        assert state.experts == []
        assert state.iteration_history == []
        assert state.artifact_regeneration_history == []

    def test_unicode_in_expert_names(self, tmp_path):
        """Test handling Unicode in expert names."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(
            topic="Test",
            experts=["typescript-测试", "python-тест"],
            iteration=1
        )
        manager.save(state)

        loaded = manager.load()
        assert loaded.experts == ["typescript-测试", "python-тест"]

    def test_very_large_state(self, tmp_path):
        """Test handling very large state with many fields."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        # Create state with many experts and sessions
        many_experts = [f"expert_{i}" for i in range(100)]
        many_sessions = {f"expert_{i}": f"sess_{i}" for i in range(100)}
        large_iteration_history = [
            {"iteration": i, "convergence_percent": i * 10}
            for i in range(50)
        ]

        state = WorkspaceState(
            topic="Test with many experts",
            experts=many_experts,
            iteration=10,
            expert_sessions=many_sessions,
            iteration_history=large_iteration_history
        )

        manager.save(state)
        loaded = manager.load()

        assert len(loaded.experts) == 100
        assert len(loaded.expert_sessions) == 100
        assert len(loaded.iteration_history) == 50

    def test_negative_values(self, tmp_path):
        """Test handling negative values in numeric fields."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        # Create state with negative values (should be allowed)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            convergence_percent=-10,
            total_tokens=-100,
            total_cost=-0.05
        )

        manager.save(state)
        loaded = manager.load()

        assert loaded.convergence_percent == -10
        assert loaded.total_tokens == -100
        assert loaded.total_cost == -0.05

    def test_phase_result_persistence(self, tmp_path):
        """Test that phase results persist across manager instances."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager1 = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager1.save(state)

        # Mark phase complete with manager1
        result = {"convergence_percent": 85}
        manager1.mark_phase_complete("consolidating", result)

        # Read with manager2
        manager2 = StateManager(workspace)
        assert manager2.is_phase_complete("consolidating")
        assert manager2.get_phase_result("consolidating") == result

    def test_empty_expert_list(self, tmp_path):
        """Test handling empty expert list."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=[], iteration=1)
        manager.save(state)

        loaded = manager.load()
        assert loaded.experts == []

    def test_zero_iteration(self, tmp_path):
        """Test handling iteration 0."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=0)
        manager.save(state)

        loaded = manager.load()
        assert loaded.iteration == 0

    def test_special_characters_in_session_ids(self, tmp_path):
        """Test handling special characters in session IDs."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        manager = StateManager(workspace)

        state = WorkspaceState(topic="Test", experts=["typescript"], iteration=1)
        manager.save(state)

        # Session IDs with special characters
        special_sessions = {
            "typescript": "sess_123-abc_def.xyz",
            "python": "sess@#$%^&*()",
            "dotnet": "sess/with/slashes"
        }

        updated = manager.update_sessions(special_sessions)
        assert updated.expert_sessions == special_sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
