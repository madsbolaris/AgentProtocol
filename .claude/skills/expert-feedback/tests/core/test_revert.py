"""
Tests for workflow revert functionality.

This module tests the ability to revert to previous phases and iterations
for testing and debugging purposes.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

import pytest

from validation.revert_validation import (
    parse_revert_target,
    validate_revert_target,
    get_phases_after,
    should_clear_synthesis_session,
    should_clear_artifact_session,
    normalize_phase,
    get_phase_index
)
from core.revert import (
    archive_for_revert,
    cleanup_reverted_data,
    filter_valid_sessions,
    restore_state_to_target,
    execute_revert,
    preview_revert,
    handle_revert
)
from state.manager import StateManager, WorkspaceState
from file_io.json_ops import load_json, save_json


class TestRevertValidation:
    """Test revert target validation."""

    def test_parse_iteration_only(self):
        """Parse iteration-only target."""
        result = parse_revert_target("iteration=2")
        assert result == {"iteration": 2}

    def test_parse_phase_only(self):
        """Parse phase-only target."""
        result = parse_revert_target("phase=synthesizing")
        assert result == {"phase": "synthesizing"}

    def test_parse_iteration_and_phase(self):
        """Parse combined iteration and phase."""
        result = parse_revert_target("iteration=2,phase=spawning_experts")
        assert result == {"iteration": 2, "phase": "spawning_experts"}

    def test_parse_init_shorthand(self):
        """Parse 'init' shorthand."""
        result = parse_revert_target("init")
        assert result == {"iteration": 1, "phase": "spawning_experts"}

    def test_parse_invalid_format(self):
        """Reject invalid format."""
        with pytest.raises(ValueError, match="Invalid target format"):
            parse_revert_target("invalid")

    def test_parse_invalid_iteration(self):
        """Reject invalid iteration number."""
        with pytest.raises(ValueError, match="Invalid iteration number"):
            parse_revert_target("iteration=abc")

    def test_parse_invalid_phase(self):
        """Reject invalid phase name."""
        with pytest.raises(ValueError, match="Invalid phase"):
            parse_revert_target("phase=invalid_phase")

    def test_parse_iteration_zero(self):
        """Reject iteration < 1."""
        with pytest.raises(ValueError, match="Must be >= 1"):
            parse_revert_target("iteration=0")

    def test_parse_invalid_key(self):
        """Reject invalid target key."""
        with pytest.raises(ValueError, match="Invalid target key"):
            parse_revert_target("invalid_key=value")

    def test_parse_empty_target(self):
        """Reject empty target specification."""
        with pytest.raises(ValueError, match="Invalid target format"):
            parse_revert_target("")

    def test_reject_forward_revert(self, tmp_path):
        """Reject reverting to future iteration."""
        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=2
        )

        result = validate_revert_target(
            current_state=state,
            target_iteration=3,
            target_phase=None,
            workspace=tmp_path
        )

        assert not result["valid"]
        assert "Cannot revert forward" in result["error"]

    def test_reject_missing_iteration_dir(self, tmp_path):
        """Reject reverting to non-existent iteration."""
        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        )

        # Don't create iteration-2 directory
        result = validate_revert_target(
            current_state=state,
            target_iteration=2,
            target_phase=None,
            workspace=tmp_path
        )

        assert not result["valid"]
        assert "directory not found" in result["error"]

    def test_reject_invalid_phase_name(self, tmp_path):
        """Reject invalid phase name."""
        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=2
        )

        result = validate_revert_target(
            current_state=state,
            target_iteration=None,
            target_phase="invalid_phase",
            workspace=tmp_path
        )

        assert not result["valid"]
        assert "Invalid phase" in result["error"]

    def test_reject_no_op_revert(self, tmp_path):
        """Reject reverting to current state."""
        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=2
        )
        # Set phase attribute
        state_dict = state.to_dict()
        state_dict["phase"] = "synthesizing"
        state = WorkspaceState.from_dict(state_dict)

        result = validate_revert_target(
            current_state=state,
            target_iteration=2,
            target_phase="synthesizing",
            workspace=tmp_path
        )

        assert not result["valid"]
        assert "Already at target state" in result["error"]

    def test_accept_valid_revert(self, tmp_path):
        """Accept valid revert target."""
        # Create iteration directories
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()

        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        )

        result = validate_revert_target(
            current_state=state,
            target_iteration=2,
            target_phase="synthesizing",
            workspace=tmp_path
        )

        assert result["valid"]
        assert result["error"] is None


class TestPhaseHelpers:
    """Test phase helper functions."""

    def test_normalize_phase(self):
        """Test phase normalization."""
        assert normalize_phase("synthesizing") == "consolidating"
        assert normalize_phase("artifact_review") == "reviewing_artifact"
        assert normalize_phase("spawning_experts") == "spawning_experts"

    def test_get_phase_index(self):
        """Test getting phase index."""
        assert get_phase_index("spawning_experts") == 0
        assert get_phase_index("consolidating") >= 0
        assert get_phase_index("completed") >= 0

    def test_get_phase_index_invalid(self):
        """Test getting phase index for invalid phase returns -1."""
        assert get_phase_index("invalid_phase_name") == -1
        assert get_phase_index("") == -1

    def test_get_phases_after(self):
        """Test getting phases after target."""
        phases = get_phases_after("synthesizing")
        assert "questions" in phases
        assert "generating_artifact" in phases
        assert "spawning_experts" not in phases

    def test_get_phases_after_invalid_phase(self):
        """Test get_phases_after returns empty list for invalid phase."""
        assert get_phases_after("invalid_phase") == []
        assert get_phases_after("") == []

    def test_should_clear_synthesis_session(self):
        """Test synthesis session clearing logic."""
        assert should_clear_synthesis_session("spawning_experts") is True
        assert should_clear_synthesis_session("synthesizing") is False
        assert should_clear_synthesis_session("questions") is False

    def test_should_clear_artifact_session(self):
        """Test artifact session clearing logic."""
        assert should_clear_artifact_session("spawning_experts") is True
        assert should_clear_artifact_session("synthesizing") is True
        assert should_clear_artifact_session("generating_artifact") is False
        assert should_clear_artifact_session("reviewing_artifact") is False


class TestRevertExecution:
    """Test revert execution."""

    def test_archive_creates_directory(self, tmp_path):
        """Verify archive directory is created."""
        # Setup workspace
        (tmp_path / "state.json").write_text('{"topic": "test", "iteration": 3}')
        (tmp_path / "iteration-3").mkdir()

        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        )

        result = archive_for_revert(
            workspace=tmp_path,
            current_state=state,
            target_iteration=2,
            target_phase="synthesizing"
        )

        archive_dir = Path(result["archive_dir"])
        assert archive_dir.exists()
        assert (archive_dir / "state.json").exists()
        assert (archive_dir / "revert-manifest.json").exists()
        assert "state.json" in result["archived_items"]

    def test_archive_includes_later_iterations(self, tmp_path):
        """Verify later iterations are archived."""
        # Setup workspace with iterations 1, 2, 3
        (tmp_path / "state.json").write_text('{"topic": "test", "iteration": 3}')
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()
        (tmp_path / "iteration-3").mkdir()

        state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        )

        result = archive_for_revert(
            workspace=tmp_path,
            current_state=state,
            target_iteration=1,
            target_phase="synthesizing"
        )

        archive_dir = Path(result["archive_dir"])
        assert (archive_dir / "iteration-2").exists()
        assert (archive_dir / "iteration-3").exists()
        assert not (archive_dir / "iteration-1").exists()

    def test_cleanup_removes_iterations(self, tmp_path):
        """Verify cleanup removes iteration directories."""
        # Setup workspace
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()
        (tmp_path / "iteration-3").mkdir()

        removed = cleanup_reverted_data(
            workspace=tmp_path,
            current_iteration=3,
            target_iteration=1
        )

        assert not (tmp_path / "iteration-2").exists()
        assert not (tmp_path / "iteration-3").exists()
        assert (tmp_path / "iteration-1").exists()
        assert "iteration-2/" in removed
        assert "iteration-3/" in removed

    def test_filter_valid_sessions_spawning(self):
        """Verify session filtering for spawning phase."""
        expert_sessions = {"typescript": "sess_1", "python": "sess_2"}
        expert_sessions_by_iteration = {1: {"typescript": "sess_1"}}

        result = filter_valid_sessions(
            expert_sessions=expert_sessions,
            expert_sessions_by_iteration=expert_sessions_by_iteration,
            target_iteration=1,
            target_phase="spawning_experts"
        )

        assert result == {}  # Should clear all sessions

    def test_filter_valid_sessions_synthesis(self):
        """Verify session filtering for synthesis phase."""
        expert_sessions = {"typescript": "sess_1", "python": "sess_2"}
        expert_sessions_by_iteration = {
            1: {"typescript": "sess_1"},
            2: {"typescript": "sess_2", "python": "sess_3"}
        }

        result = filter_valid_sessions(
            expert_sessions=expert_sessions,
            expert_sessions_by_iteration=expert_sessions_by_iteration,
            target_iteration=2,
            target_phase="synthesizing"
        )

        # Should preserve iteration 2 sessions
        assert result == {"typescript": "sess_2", "python": "sess_3"}

    def test_restore_state_updates_iteration(self, tmp_path):
        """Verify state restoration updates iteration."""
        state_dict = {
            "topic": "test",
            "experts": ["typescript"],
            "iteration": 3,
            "phase": "artifact_review",
            "expert_sessions": {"typescript": "sess_1"}
        }

        restored = restore_state_to_target(
            state_dict=state_dict,
            current_iteration=3,
            target_iteration=2,
            target_phase="synthesizing"
        )

        assert restored["iteration"] == 2
        assert restored["phase"] == "synthesizing"
        assert "revert_history" in restored
        assert len(restored["revert_history"]) == 1

    def test_restore_state_clears_future_phases(self):
        """Verify completion flags for future phases are cleared."""
        state_dict = {
            "topic": "test",
            "experts": ["typescript"],
            "iteration": 2,
            "phase": "artifact_review",
            "generating_artifact_complete": True,
            "generating_artifact_result": {"some": "data"},
            "reviewing_artifact_complete": True
        }

        restored = restore_state_to_target(
            state_dict=state_dict,
            current_iteration=2,
            target_iteration=2,
            target_phase="synthesizing"
        )

        assert "generating_artifact_complete" not in restored
        assert "generating_artifact_result" not in restored
        assert "reviewing_artifact_complete" not in restored

    def test_restore_state_clears_artifact_session(self):
        """Verify artifact session is cleared when appropriate."""
        state_dict = {
            "topic": "test",
            "experts": ["typescript"],
            "iteration": 2,
            "phase": "artifact_review",
            "artifact_generation_session_id": "sess_artifact",
            "artifact_generation_result": {"some": "data"}
        }

        restored = restore_state_to_target(
            state_dict=state_dict,
            current_iteration=2,
            target_iteration=2,
            target_phase="synthesizing"
        )

        assert restored["artifact_generation_session_id"] is None
        assert restored["artifact_generation_result"] is None


class TestRevertIntegration:
    """Integration tests for revert functionality."""

    def test_execute_revert_success(self, tmp_path):
        """Test successful revert execution."""
        # Setup workspace
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()
        (tmp_path / "iteration-3").mkdir()

        state_manager = StateManager(tmp_path)
        initial_state = WorkspaceState(
            topic="test",
            experts=["typescript", "python"],
            iteration=3
        )
        state_manager.save(initial_state)

        # Set phase for more realistic state
        state_manager.set_phase("completed")

        # Load state for revert
        current_state = state_manager.load()

        # Execute revert
        result = execute_revert(
            workspace=tmp_path,
            current_state=current_state,
            target={"iteration": 2, "phase": "synthesizing"}
        )

        assert result["status"] == "success"
        assert result["reverted_from"]["iteration"] == 3
        assert result["reverted_to"]["iteration"] == 2
        assert result["reverted_to"]["phase"] == "synthesizing"
        assert len(result["archived"]["archived_items"]) > 0
        assert "iteration-3/" in result["removed"]

        # Verify state was updated
        new_state = state_manager.load()
        assert new_state.iteration == 2

    def test_preview_revert_no_changes(self, tmp_path):
        """Verify preview doesn't modify workspace."""
        # Setup workspace
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()
        (tmp_path / "iteration-3").mkdir()

        state_manager = StateManager(tmp_path)
        initial_state = WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        )
        state_manager.save(initial_state)

        # Get original state
        original_state_dict = state_manager.load().to_dict()

        # Preview revert
        result = preview_revert(
            workspace=tmp_path,
            current_state=initial_state,
            target={"iteration": 2}
        )

        assert result["status"] == "success"
        assert "would_archive" in result
        assert "would_remove" in result

        # Verify no changes
        new_state_dict = state_manager.load().to_dict()
        assert new_state_dict == original_state_dict
        assert (tmp_path / "iteration-3").exists()  # Not removed

    def test_handle_revert_with_dry_run(self, tmp_path):
        """Test handle_revert with dry-run flag."""
        # Setup workspace
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()

        state_manager = StateManager(tmp_path)
        state_manager.save(WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=2
        ))

        # Dry run
        result = handle_revert(
            workspace=tmp_path,
            revert_target="iteration=1",
            dry_run=True
        )

        assert result["status"] == "success"
        assert "would_archive" in result
        assert (tmp_path / "iteration-2").exists()  # Not removed

    def test_handle_revert_invalid_target(self, tmp_path):
        """Test handle_revert with invalid target."""
        result = handle_revert(
            workspace=tmp_path,
            revert_target="invalid",
            dry_run=False
        )

        assert result["status"] == "error"
        assert "Invalid revert target" in result["error"]

    def test_handle_revert_no_state_file(self, tmp_path):
        """Test handle_revert with missing state file."""
        result = handle_revert(
            workspace=tmp_path,
            revert_target="iteration=1",
            dry_run=False
        )

        assert result["status"] == "error"
        assert "No state file found" in result["error"]

    def test_multiple_reverts_maintain_consistency(self, tmp_path):
        """Test multiple sequential reverts."""
        import time

        # Setup workspace with iterations 1, 2, 3
        (tmp_path / "iteration-1").mkdir()
        (tmp_path / "iteration-2").mkdir()
        (tmp_path / "iteration-3").mkdir()

        state_manager = StateManager(tmp_path)
        state_manager.save(WorkspaceState(
            topic="test",
            experts=["typescript"],
            iteration=3
        ))

        # First revert: 3 -> 2
        result1 = handle_revert(
            workspace=tmp_path,
            revert_target="iteration=2",
            dry_run=False
        )
        assert result1["status"] == "success"

        # Check archives
        archives = list(tmp_path.glob(".archive/revert-*"))
        assert len(archives) == 1

        # Wait a bit to ensure different timestamp for second archive
        time.sleep(1.1)

        # Second revert: 2 -> 1
        result2 = handle_revert(
            workspace=tmp_path,
            revert_target="iteration=1",
            dry_run=False
        )
        assert result2["status"] == "success"

        # Check archives increased
        archives = list(tmp_path.glob(".archive/revert-*"))
        assert len(archives) == 2

        # State should be at iteration 1
        final_state = state_manager.load()
        assert final_state.iteration == 1

        # Check revert history
        assert len(final_state.revert_history) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
