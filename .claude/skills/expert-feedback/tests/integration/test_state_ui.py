"""
UI State Validation Tests.

Tests that state.json contains all fields required by the UI
and that the state structure matches the UI's expectations.

The UI (React app) relies on specific fields in state.json to display:
- Expert progress and status
- Convergence metrics
- Phase information
- Token/cost tracking
- Iteration progress
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from state.manager import StateManager, WorkspaceState


@pytest.mark.integration
class TestUIStateContract:
    """Test that state.json adheres to UI contract."""

    def test_required_top_level_fields(self, initialized_workspace):
        """Verify all required top-level fields are present."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # Required fields for UI
        assert hasattr(state, 'topic'), "Missing 'topic' field"
        assert hasattr(state, 'experts'), "Missing 'experts' field"
        assert hasattr(state, 'iteration'), "Missing 'iteration' field"
        assert hasattr(state, 'mode'), "Missing 'mode' field"
        assert hasattr(state, 'convergence_percent'), "Missing 'convergence_percent' field"
        assert hasattr(state, 'consensus_reached'), "Missing 'consensus_reached' field"
        assert hasattr(state, 'convergence_target'), "Missing 'convergence_target' field"

        # Metadata fields
        assert hasattr(state, 'expert_sessions'), "Missing 'expert_sessions' field"
        assert hasattr(state, 'expert_progress'), "Missing 'expert_progress' field"
        assert hasattr(state, 'total_tokens'), "Missing 'total_tokens' field"
        assert hasattr(state, 'total_cost'), "Missing 'total_cost' field"

    def test_state_serialization(self, initialized_workspace):
        """Test that state can be serialized to dict for JSON."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # Convert to dict (what UI reads from JSON)
        state_dict = state.to_dict()

        # Verify dict structure
        assert isinstance(state_dict, dict)
        assert 'topic' in state_dict
        assert 'experts' in state_dict
        assert 'iteration' in state_dict
        assert 'convergence_percent' in state_dict

    def test_expert_list_structure(self, initialized_workspace):
        """Test that experts field is a list of strings."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        assert isinstance(state.experts, list)
        assert len(state.experts) > 0
        assert all(isinstance(e, str) for e in state.experts)


@pytest.mark.integration
class TestExpertProgressStructure:
    """Test expert_progress field structure for UI consumption."""

    def test_expert_progress_dict_structure(self, initialized_workspace):
        """Test that expert_progress has correct structure."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Add progress for experts
        state_manager.update_expert_progress(
            "typescript", "running",
            {"start_time": "2026-02-15T10:00:00"}
        )
        state_manager.update_expert_progress(
            "python", "complete",
            {
                "duration_seconds": 25.5,
                "total_tokens": 2000,
                "end_time": "2026-02-15T10:00:30"
            }
        )

        state = state_manager.load()

        # Verify structure
        assert isinstance(state.expert_progress, dict)
        assert "typescript" in state.expert_progress
        assert "python" in state.expert_progress

        # Check typescript (running)
        ts_progress = state.expert_progress["typescript"]
        assert ts_progress["status"] == "running"
        assert "start_time" in ts_progress

        # Check python (complete)
        py_progress = state.expert_progress["python"]
        assert py_progress["status"] == "complete"
        assert "duration_seconds" in py_progress
        assert "total_tokens" in py_progress

    def test_valid_expert_status_values(self, initialized_workspace):
        """Test that expert status values are valid."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        valid_statuses = ["pending", "running", "complete", "error", "timeout"]

        # Test each valid status
        for status in valid_statuses:
            state_manager.update_expert_progress("typescript", status)
            state = state_manager.load()
            assert state.expert_progress["typescript"]["status"] == status

    def test_expert_progress_with_metadata(self, initialized_workspace):
        """Test expert progress with full metadata."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.update_expert_progress(
            "typescript",
            "complete",
            {
                "duration_seconds": 28.5,
                "total_tokens": 3500,
                "input_tokens": 2000,
                "output_tokens": 1500,
                "start_time": "2026-02-15T10:00:00",
                "end_time": "2026-02-15T10:00:28"
            }
        )

        state = state_manager.load()
        progress = state.expert_progress["typescript"]

        # UI needs these fields
        assert progress["status"] == "complete"
        assert progress["duration_seconds"] == 28.5
        assert progress["total_tokens"] == 3500


@pytest.mark.integration
class TestConvergenceMetrics:
    """Test convergence metrics structure for UI charts."""

    def test_convergence_metrics_present(self, initialized_workspace):
        """Test that convergence metrics are available."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.update_convergence(
            convergence_percent=75,
            consensus_reached=False,
            high_agreement=3,
            partial_agreement=2,
            low_agreement=1
        )

        state = state_manager.load()

        # UI displays these metrics
        assert hasattr(state, 'convergence_percent')
        assert hasattr(state, 'consensus_reached')
        assert hasattr(state, 'high_agreement')
        assert hasattr(state, 'partial_agreement')
        assert hasattr(state, 'low_agreement')

        # Verify values
        assert state.convergence_percent == 75
        assert state.consensus_reached is False
        assert state.high_agreement == 3
        assert state.partial_agreement == 2
        assert state.low_agreement == 1

    def test_convergence_target_configurable(self, initialized_workspace):
        """Test that convergence target is stored for UI display."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # UI shows progress toward target (e.g., "75% of 80% target")
        assert hasattr(state, 'convergence_target')
        assert state.convergence_target == 80  # Default


@pytest.mark.integration
class TestPhaseTracking:
    """Test phase field for UI phase indicator."""

    def test_phase_field_in_state_dict(self, initialized_workspace):
        """Test that phase field is in serialized state."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.set_phase("spawning_experts")

        # UI reads from JSON
        state_dict = state_manager.load().to_dict()
        assert "phase" in state_dict
        assert state_dict["phase"] == "spawning_experts"

    def test_all_valid_phases(self, initialized_workspace):
        """Test that all expected phases can be set."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        phases = [
            "spawning_experts",
            "consolidating",
            "questions",
            "generating_artifact",
            "artifact_review",
            "completed"
        ]

        for phase in phases:
            state_manager.set_phase(phase)
            state_dict = state_manager.load().to_dict()
            assert state_dict.get("phase") == phase


@pytest.mark.integration
class TestTokenAndCostTracking:
    """Test token and cost metrics for UI display."""

    def test_token_metrics_present(self, initialized_workspace):
        """Test that token metrics are tracked."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # UI displays token usage
        assert hasattr(state, 'total_tokens')
        assert hasattr(state, 'total_cost')
        assert hasattr(state, 'total_input_tokens')
        assert hasattr(state, 'total_output_tokens')

        # Initial values
        assert state.total_tokens == 0
        assert state.total_cost == 0.0

    def test_token_metrics_update(self, initialized_workspace):
        """Test updating token metrics."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=200,
            cache_read_tokens=300,
            cost=0.75
        )

        state = state_manager.load()

        # Verify updates
        assert state.total_input_tokens == 1000
        assert state.total_output_tokens == 500
        assert state.total_cache_creation_tokens == 200
        assert state.total_cache_read_tokens == 300
        assert state.total_cost == 0.75

    def test_cache_metrics_for_ui_performance_display(self, initialized_workspace):
        """Test cache metrics for UI performance display."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Update with cache metrics
        state_manager.update_token_metrics_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=500,  # First expert creates cache
            cache_read_tokens=0,
            cost=0.50
        )

        # Second expert reads from cache
        state_manager.update_token_metrics_with_cache(
            input_tokens=100,
            output_tokens=500,
            cache_creation_tokens=0,
            cache_read_tokens=500,  # Cache hit!
            cost=0.20
        )

        state = state_manager.load()

        # UI can calculate cache hit rate
        assert state.cache_enabled is True
        assert state.total_cache_creation_tokens == 500
        assert state.total_cache_read_tokens == 500
        assert state.total_cost == 0.70  # Cumulative


@pytest.mark.integration
class TestSessionTracking:
    """Test session tracking for UI debug/info display."""

    def test_expert_sessions_tracked(self, initialized_workspace):
        """Test that expert sessions are tracked."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.update_sessions({
            "typescript": "session-ts-123",
            "python": "session-py-456"
        })

        state = state_manager.load()

        assert isinstance(state.expert_sessions, dict)
        assert "typescript" in state.expert_sessions
        assert "python" in state.expert_sessions

    def test_synthesis_session_tracked(self, initialized_workspace):
        """Test that synthesis session is tracked."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.set_synthesis_session("synthesis-session-789")

        state = state_manager.load()

        assert state.synthesis_session_id == "synthesis-session-789"

    def test_artifact_generation_session_tracked(self, initialized_workspace):
        """Test that artifact generation session is tracked."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        state_manager.set_artifact_generation_session("artifact-session-abc")

        state = state_manager.load()

        assert state.artifact_generation_session_id == "artifact-session-abc"


@pytest.mark.integration
class TestIterationTracking:
    """Test iteration tracking for UI progress display."""

    def test_iteration_number_accessible(self, initialized_workspace):
        """Test that iteration number is accessible."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # UI shows "Iteration 1 of 3"
        assert state.iteration == 1

    def test_iteration_progression(self, initialized_workspace):
        """Test that iteration increments."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Initial
        state = state_manager.load()
        assert state.iteration == 1

        # Progress
        state_manager.increment_iteration()
        state = state_manager.load()
        assert state.iteration == 2


@pytest.mark.integration
class TestModeField:
    """Test mode field for UI display."""

    def test_mode_field_present(self, initialized_workspace):
        """Test that mode field is present."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # UI shows mode (review/improve/create)
        assert hasattr(state, 'mode')
        assert state.mode in ["review", "improve", "create"]

    def test_different_modes(self, tmp_path):
        """Test different workflow modes."""
        from fixtures.workspace_fixtures import setup_workspace_with_state

        modes = ["review", "improve", "create"]

        for mode in modes:
            workspace = tmp_path / f"workspace-{mode}"
            workspace.mkdir()

            state_manager = setup_workspace_with_state(
                workspace,
                topic=f"Test {mode} mode",
                mode=mode
            )

            state = state_manager.load()
            assert state.mode == mode


@pytest.mark.integration
class TestCompletionTimestamps:
    """Test timestamp tracking for UI display."""

    def test_start_and_complete_times(self, initialized_workspace):
        """Test that timestamps can be set."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Set start time
        state_manager.set_start_time("2026-02-15T10:00:00")

        state = state_manager.load()
        assert state.start_time == "2026-02-15T10:00:00"

        # Set complete time
        state_manager.mark_complete("2026-02-15T10:30:00")

        state = state_manager.load()
        assert state.complete_time == "2026-02-15T10:30:00"


@pytest.mark.integration
class TestUIStateDefaults:
    """Test that state has sensible defaults."""

    def test_default_values_present(self, test_workspace):
        """Test that new state has default values."""
        from state.manager import StateManager, WorkspaceState

        state_manager = StateManager(test_workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )

        # Defaults should be set
        assert state.mode == "review"  # Default mode
        assert state.convergence_percent == 0
        assert state.consensus_reached is False
        assert state.convergence_target == 80
        assert state.total_tokens == 0
        assert state.total_cost == 0.0
        assert state.expert_sessions == {}
        assert state.expert_progress == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
