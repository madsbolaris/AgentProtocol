"""
Integration test for session reuse functionality.

Tests that expert sessions, synthesizion sessions, and finalization sessions
can be persisted and resumed across iterations.
"""
import json
import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from state.manager import StateManager, WorkspaceState


class TestSessionReuse:
    """Test session reuse across iterations."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.state_manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_expert_session_persistence(self):
        """Test that expert sessions persist across iterations."""
        # Iteration 1 - create sessions
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript", "python"],
            iteration=1
        )
        self.state_manager.save(state)

        # Simulate expert sessions
        self.state_manager.update_sessions({
            "typescript": "session-ts-123",
            "python": "session-py-456"
        })

        # Load and verify
        loaded_state = self.state_manager.load()
        assert loaded_state.expert_sessions["typescript"] == "session-ts-123"
        assert loaded_state.expert_sessions["python"] == "session-py-456"

        # Iteration 2 - sessions should still be available
        state.iteration = 2
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.expert_sessions["typescript"] == "session-ts-123"
        assert loaded_state.expert_sessions["python"] == "session-py-456"
        assert loaded_state.iteration == 2

    def test_synthesizion_session_reuse(self):
        """Test that synthesizion session can be reused across iterations."""
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1
        )
        self.state_manager.save(state)

        # Set synthesizion session in iteration 1
        self.state_manager.set_synthesizion_session("synthesizion-abc")

        loaded_state = self.state_manager.load()
        assert loaded_state.synthesizion_session_id == "synthesizion-abc"

        # Move to iteration 2
        state.iteration = 2
        self.state_manager.save(state)

        # Synthesizion session should persist
        loaded_state = self.state_manager.load()
        assert loaded_state.synthesizion_session_id == "synthesizion-abc"
        assert loaded_state.iteration == 2

    def test_finalization_session_tracking(self):
        """Test that finalization session is tracked."""
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1,
            finalization_session_id=None
        )
        self.state_manager.save(state)

        # Set finalization session
        loaded_state = self.state_manager.load()
        loaded_state.finalization_session_id = "finalize-xyz"
        self.state_manager.save(loaded_state)

        # Verify persistence
        reloaded_state = self.state_manager.load()
        assert reloaded_state.finalization_session_id == "finalize-xyz"

    def test_session_addition_preserves_existing(self):
        """Test that adding new expert sessions preserves existing ones."""
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript", "python", "dotnet"],
            iteration=1
        )
        self.state_manager.save(state)

        # Add first expert session
        self.state_manager.update_sessions({"typescript": "session-ts-1"})

        # Add second expert session
        self.state_manager.update_sessions({"python": "session-py-1"})

        # Add third expert session
        self.state_manager.update_sessions({"dotnet": "session-dn-1"})

        # All should be present
        loaded_state = self.state_manager.load()
        assert len(loaded_state.expert_sessions) == 3
        assert loaded_state.expert_sessions["typescript"] == "session-ts-1"
        assert loaded_state.expert_sessions["python"] == "session-py-1"
        assert loaded_state.expert_sessions["dotnet"] == "session-dn-1"

    def test_session_reuse_across_workspace_reload(self):
        """Test that sessions persist even after workspace is reloaded."""
        # Create initial state with sessions
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1
        )
        self.state_manager.save(state)
        self.state_manager.update_sessions({"typescript": "session-123"})
        self.state_manager.set_synthesizion_session("consol-456")

        # Create new StateManager instance (simulating restart)
        new_manager = StateManager(self.workspace)
        loaded_state = new_manager.load()

        # Sessions should still be available
        assert loaded_state.expert_sessions["typescript"] == "session-123"
        assert loaded_state.synthesizion_session_id == "consol-456"

    def test_multiple_iteration_session_tracking(self):
        """Test session tracking through multiple iterations."""
        # Iteration 1
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript", "python"],
            iteration=1,
            convergence_percent=0
        )
        self.state_manager.save(state)
        self.state_manager.update_sessions({
            "typescript": "session-ts-iter1",
            "python": "session-py-iter1"
        })
        self.state_manager.set_synthesizion_session("consol-iter1")

        # Iteration 2 - low convergence, continue
        state.iteration = 2
        state.convergence_percent = 60
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.expert_sessions["typescript"] == "session-ts-iter1"
        assert loaded_state.expert_sessions["python"] == "session-py-iter1"
        assert loaded_state.synthesizion_session_id == "consol-iter1"
        assert loaded_state.iteration == 2

        # Iteration 3 - consensus reached
        state.iteration = 3
        state.convergence_percent = 85
        state.consensus_reached = True
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.expert_sessions["typescript"] == "session-ts-iter1"
        assert loaded_state.expert_sessions["python"] == "session-py-iter1"
        assert loaded_state.synthesizion_session_id == "consol-iter1"
        assert loaded_state.consensus_reached is True


class TestSessionReuseBenefits:
    """Test the benefits of session reuse."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.state_manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_context_preservation_simulation(self):
        """
        Simulate that session reuse preserves conversation context.

        Note: Full test would require mocking Claude Agent SDK.
        This demonstrates the state tracking that enables context preservation.
        """
        # Iteration 1 - initial review
        state = WorkspaceState(
            topic="API design review",
            experts=["typescript"],
            iteration=1
        )
        self.state_manager.save(state)
        self.state_manager.update_sessions({"typescript": "session-with-context"})

        # Iteration 2 - refine with user answers
        # Session ID allows resuming with full context
        state.iteration = 2
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()

        # Session ID is preserved, enabling context continuation
        assert loaded_state.expert_sessions["typescript"] == "session-with-context"
        assert loaded_state.iteration == 2

    def test_cost_savings_through_session_reuse(self):
        """
        Document cost savings from session reuse.

        Session reuse avoids re-explaining context, saving tokens.
        This test documents the expected behavior.
        """
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1
        )
        self.state_manager.save(state)
        self.state_manager.update_sessions({"typescript": "session-123"})

        # Iteration 2 with session reuse
        state.iteration = 2
        self.state_manager.save(state)

        # Session reuse means:
        # - No need to re-read entire codebase
        # - No need to re-explain context
        # - Expert continues from previous state
        # Expected token savings: 30-50% per iteration

        loaded_state = self.state_manager.load()
        assert loaded_state.expert_sessions["typescript"] == "session-123"


# Note: Full session reuse tests would require:
# 1. Mocking Claude Agent SDK
# 2. Verifying that resume() is called with correct session IDs
# 3. Testing actual context preservation through API
#
# These tests verify the state management that enables session reuse.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
