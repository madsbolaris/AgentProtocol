"""
Integration test for full expert-feedback workflow.

Tests the complete workflow from expert spawning through synthesizion
to finalization, simulating a real review session.
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
from config import get_config


class TestFullWorkflow:
    """
    Integration test for complete expert-feedback workflow.

    Note: These tests are placeholders that demonstrate the workflow structure.
    Full implementation would require mocking the Claude Agent SDK or using
    recorded responses.
    """

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.state_manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_workflow_initialization(self):
        """Test that workflow can be initialized properly."""
        # Create initial state
        state = WorkspaceState(
            topic="Test API design review",
            experts=["typescript", "python"],
            iteration=1,
            mode="review",
            convergence_target=80
        )

        self.state_manager.save(state)

        # Verify state saved correctly
        loaded_state = self.state_manager.load()
        assert loaded_state.topic == "Test API design review"
        assert loaded_state.experts == ["typescript", "python"]
        assert loaded_state.iteration == 1
        assert loaded_state.mode == "review"

    def test_workflow_expert_session_tracking(self):
        """Test tracking expert sessions through workflow."""
        # Initialize
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript", "python"],
            iteration=1
        )
        self.state_manager.save(state)

        # Simulate expert spawning
        self.state_manager.update_sessions({
            "typescript": "session-typescript-123",
            "python": "session-python-456"
        })

        # Verify sessions tracked
        loaded_state = self.state_manager.load()
        assert "typescript" in loaded_state.expert_sessions
        assert "python" in loaded_state.expert_sessions
        assert loaded_state.expert_sessions["typescript"] == "session-typescript-123"
        assert loaded_state.expert_sessions["python"] == "session-python-456"

    def test_workflow_iteration_progression(self):
        """Test that workflow can progress through iterations."""
        # Iteration 1
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1,
            convergence_percent=0
        )
        self.state_manager.save(state)

        # Simulate convergence below threshold
        state.convergence_percent = 65
        state.iteration = 2
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.iteration == 2
        assert loaded_state.convergence_percent == 65
        assert loaded_state.consensus_reached is False

        # Simulate reaching consensus
        state.convergence_percent = 85
        state.consensus_reached = True
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.convergence_percent == 85
        assert loaded_state.consensus_reached is True

    def test_workflow_synthesizion_session_reuse(self):
        """Test that synthesizion session can be tracked for reuse."""
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1
        )
        self.state_manager.save(state)

        # Set synthesizion session
        self.state_manager.set_synthesizion_session("synthesizion-session-789")

        # Verify it persists
        loaded_state = self.state_manager.load()
        assert loaded_state.synthesizion_session_id == "synthesizion-session-789"

        # Verify it persists across iterations
        state.iteration = 2
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.synthesizion_session_id == "synthesizion-session-789"

    def test_workflow_artifact_review_flag(self):
        """Test that artifact review flag can be set and tracked."""
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1,
            artifact_review_needed=False
        )
        self.state_manager.save(state)

        # After generating artifact, set flag
        state.artifact_review_needed = True
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.artifact_review_needed is True

    def test_workflow_configuration_override(self):
        """Test that workflow can use custom configuration."""
        from config import get_config_with_overrides

        # Custom config for this session
        config = get_config_with_overrides(
            convergence_target=70,
            expert_timeout_seconds=600
        )

        assert config.convergence_target == 70
        assert config.expert_timeout_seconds == 600

        # Create state with custom convergence
        state = WorkspaceState(
            topic="Test review",
            experts=["typescript"],
            iteration=1,
            convergence_target=70
        )
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.convergence_target == 70

    def test_workflow_handles_multiple_experts(self):
        """Test workflow with multiple experts."""
        experts = ["typescript", "python", "dotnet", "dx", "openai-sdk"]

        state = WorkspaceState(
            topic="Multi-expert review",
            experts=experts,
            iteration=1
        )
        self.state_manager.save(state)

        # Simulate all experts completing
        sessions = {expert: f"session-{expert}-{i}" for i, expert in enumerate(experts)}
        self.state_manager.update_sessions(sessions)

        loaded_state = self.state_manager.load()
        assert len(loaded_state.expert_sessions) == 5
        for expert in experts:
            assert expert in loaded_state.expert_sessions


class TestWorkflowModes:
    """Test different workflow operation modes."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.state_manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_review_mode_workflow(self):
        """Test workflow in review mode (ADR generation)."""
        state = WorkspaceState(
            topic="Architecture decision review",
            experts=["typescript", "dotnet"],
            iteration=1,
            mode="review"
        )
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.mode == "review"

    def test_improve_mode_workflow(self):
        """Test workflow in improve mode (Implementation Plan)."""
        state = WorkspaceState(
            topic="Improve error handling",
            experts=["typescript", "python"],
            iteration=1,
            mode="improve"
        )
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.mode == "improve"

    def test_create_mode_workflow(self):
        """Test workflow in create mode (Architecture Plan)."""
        state = WorkspaceState(
            topic="Design new streaming system",
            experts=["typescript", "dotnet", "python"],
            iteration=1,
            mode="create"
        )
        self.state_manager.save(state)

        loaded_state = self.state_manager.load()
        assert loaded_state.mode == "create"


# Note: Full integration tests would require:
# 1. Mock Claude Agent SDK responses
# 2. Recorded expert conversations
# 3. Test fixtures with complete workspace states
# 4. Validation of actual agent outputs
#
# These placeholder tests demonstrate the workflow structure
# and state management integration.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
