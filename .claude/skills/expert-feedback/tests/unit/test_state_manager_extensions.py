#!/usr/bin/env python3
"""
Unit tests for StateManager extensions (Context Gap Fixes 1.1 and 2.1).

Tests new methods:
- record_iteration_summary()
- increment_artifact_generation_attempt()
- record_artifact_generation_result()
"""
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from state.manager import StateManager, WorkspaceState


class TestStateManagerExtensions:
    """Test suite for StateManager extensions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workspace = Path("/tmp/test-workspace-state")
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state_manager = StateManager(self.workspace)

        # Initialize state with minimal data
        initial_state = WorkspaceState(
            topic="Test workflow",
            experts=["typescript"],
            iteration=1,
            mode="review"
        )
        self.state_manager.create(initial_state)

    def teardown_method(self):
        """Clean up test files."""
        import shutil
        if self.workspace.exists():
            shutil.rmtree(self.workspace)

    def test_record_iteration_summary_creates_history(self):
        """Should create iteration_history entry."""
        # Record summary
        updated_state = self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=45,
            agreement_breakdown={"high": 3, "partial": 2, "low": 1},
            expert_summaries={
                "typescript": {
                    "dx_rating": 4,
                    "concerns_count": 3,
                    "top_concern": "Type complexity"
                }
            }
        )

        # Verify iteration_history created
        assert len(updated_state.iteration_history) == 1

        history_entry = updated_state.iteration_history[0]
        assert history_entry["iteration"] == 1
        assert history_entry["convergence_percent"] == 45
        assert history_entry["high_agreement"] == 3
        assert history_entry["partial_agreement"] == 2
        assert history_entry["low_agreement"] == 1
        assert "typescript" in history_entry["expert_summaries"]
        assert history_entry["expert_summaries"]["typescript"]["dx_rating"] == 4

    def test_record_multiple_iterations(self):
        """Should append to iteration_history for each iteration."""
        # Record iteration 1
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=35,
            agreement_breakdown={"high": 1, "partial": 2, "low": 2},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Record iteration 2
        self.state_manager.record_iteration_summary(
            iteration=2,
            convergence_percent=55,
            agreement_breakdown={"high": 3, "partial": 2, "low": 0},
            expert_summaries={"typescript": {"dx_rating": 4}}
        )

        # Verify both in history
        state = self.state_manager.load()
        assert len(state.iteration_history) == 2
        assert state.iteration_history[0]["iteration"] == 1
        assert state.iteration_history[1]["iteration"] == 2

    def test_increment_artifact_generation_attempt(self):
        """Should increment attempt counter."""
        # Initial state has 0 attempts
        state = self.state_manager.load()
        assert state.artifact_generation_attempts == 0

        # Increment
        updated = self.state_manager.increment_artifact_generation_attempt()
        assert updated.artifact_generation_attempts == 1

        # Increment again
        updated = self.state_manager.increment_artifact_generation_attempt()
        assert updated.artifact_generation_attempts == 2

    def test_record_artifact_generation_result_concerns_raised(self):
        """Should record concerns_raised result with concerns."""
        # Record concerns
        updated = self.state_manager.record_artifact_generation_result(
            attempt=1,
            result="concerns_raised",
            veto_count=2,
            concerns=["Missing security", "Unclear migration"]
        )

        # Verify history
        assert len(updated.artifact_regeneration_history) == 1

        entry = updated.artifact_regeneration_history[0]
        assert entry["attempt"] == 1
        assert entry["result"] == "concerns_raised"
        assert entry["veto_count"] == 2
        assert len(entry["concerns"]) == 2
        assert "timestamp" in entry

    def test_record_artifact_generation_result_approved(self):
        """Should record approved result."""
        updated = self.state_manager.record_artifact_generation_result(
            attempt=2,
            result="approved",
            veto_count=0,
            concerns=[]
        )

        # Verify history
        entry = updated.artifact_regeneration_history[0]
        assert entry["attempt"] == 2
        assert entry["result"] == "approved"
        assert entry["veto_count"] == 0
        assert entry["concerns"] == []

    def test_multiple_regeneration_attempts_tracked(self):
        """Should track complete regeneration history."""
        # Attempt 1: concerns_raised
        self.state_manager.record_artifact_generation_result(
            attempt=1,
            result="concerns_raised",
            veto_count=3,
            concerns=["Security", "Performance", "Testing"]
        )

        # Attempt 2: still concerns_raised
        self.state_manager.record_artifact_generation_result(
            attempt=2,
            result="concerns_raised",
            veto_count=1,
            concerns=["Security"]
        )

        # Attempt 3: approved
        self.state_manager.record_artifact_generation_result(
            attempt=3,
            result="approved",
            veto_count=0,
            concerns=[]
        )

        # Verify all tracked
        state = self.state_manager.load()
        assert len(state.artifact_regeneration_history) == 3
        assert state.artifact_regeneration_history[0]["result"] == "concerns_raised"
        assert state.artifact_regeneration_history[1]["veto_count"] == 1
        assert state.artifact_regeneration_history[2]["result"] == "approved"

    def test_state_persistence_across_loads(self):
        """State should persist across StateManager instances."""
        # Record data
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=50,
            agreement_breakdown={"high": 2, "partial": 1, "low": 0},
            expert_summaries={"typescript": {"dx_rating": 5}}
        )

        self.state_manager.increment_artifact_generation_attempt()

        # Create new StateManager instance
        new_state_manager = StateManager(self.workspace)
        state = new_state_manager.load()

        # Verify data persisted
        assert len(state.iteration_history) == 1
        assert state.artifact_generation_attempts == 1

    def test_backward_compatibility_with_missing_fields(self):
        """Should handle old state.json without new fields."""
        # Create old-style state.json without new fields
        old_state = {
            "topic": "Test topic",
            "mode": "review",
            "iteration": 1,
            "experts": ["typescript"]
            # No iteration_history, artifact_generation_attempts, or artifact_regeneration_history
        }

        state_path = self.workspace / "state.json"
        import json
        state_path.write_text(json.dumps(old_state, indent=2))

        # Load with StateManager (should not crash)
        state = self.state_manager.load()

        # Verify defaults applied
        assert state.iteration_history == []
        assert state.artifact_generation_attempts == 0
        assert state.artifact_regeneration_history == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
