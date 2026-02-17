"""
Integration tests for individual workflow phases.

Tests each phase of the expert-feedback workflow independently:
- Expert spawning
- Synthesis/consolidation
- Artifact generation
- Artifact review

Uses mocked Claude SDK for fast, deterministic testing.
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path

# Add scripts directory to path
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from state.manager import StateManager, WorkspaceState
from file_io.json_ops import save_json


# Helper function to create test expert results
def create_expert_result_file(workspace: Path, iteration: int, expert: str):
    """Create a mock expert result file."""
    iteration_dir = workspace / f"iteration-{iteration}"
    iteration_dir.mkdir(exist_ok=True)

    result = {
        "expert": expert,
        "analysis": f"Mock analysis from {expert}",
        "recommendations": [
            {
                "title": f"Recommendation 1 from {expert}",
                "description": "Use consistent naming",
                "priority": "high"
            }
        ],
        "concerns": ["Backward compatibility"],
        "questions": ["What about versioning?"]
    }

    result_file = iteration_dir / f"state-{expert}-{iteration}.json"
    save_json(result, result_file)

    return result_file


@pytest.mark.integration
@pytest.mark.requires_recordings
class TestExpertSpawningPhase:
    """Test expert spawning phase of workflow."""

    @pytest.mark.asyncio
    async def test_expert_spawning_basic(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test basic expert spawning with 2 experts."""
        # This test will require recordings to be generated first
        # For now, we'll test the structure and state management

        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Create mock expert results (simulating successful spawn)
        create_expert_result_file(workspace, 1, "typescript")
        create_expert_result_file(workspace, 1, "python")

        # Update state as if experts spawned successfully
        state_manager.update_sessions({
            "typescript": "session-typescript-123",
            "python": "session-python-456"
        })

        # Update progress
        state_manager.update_expert_progress(
            "typescript", "complete",
            {"duration_seconds": 25.5, "total_tokens": 2000}
        )
        state_manager.update_expert_progress(
            "python", "complete",
            {"duration_seconds": 28.3, "total_tokens": 2100}
        )

        # Verify state
        state = state_manager.load()
        assert len(state.expert_sessions) == 2
        assert "typescript" in state.expert_sessions
        assert "python" in state.expert_sessions
        assert state.expert_progress["typescript"]["status"] == "complete"
        assert state.expert_progress["python"]["status"] == "complete"

    @pytest.mark.asyncio
    async def test_expert_timeout_handling(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test handling of expert timeout."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Simulate one expert completing, one timing out
        create_expert_result_file(workspace, 1, "typescript")

        state_manager.update_sessions({
            "typescript": "session-typescript-123"
        })

        state_manager.update_expert_progress(
            "typescript", "complete",
            {"duration_seconds": 25.5, "total_tokens": 2000}
        )

        state_manager.update_expert_progress(
            "python", "timeout",
            {"duration_seconds": 300.0}
        )

        # Verify state reflects timeout
        state = state_manager.load()
        assert state.expert_progress["typescript"]["status"] == "complete"
        assert state.expert_progress["python"]["status"] == "timeout"
        assert len(state.expert_sessions) == 1  # Only typescript completed


@pytest.mark.integration
@pytest.mark.requires_recordings
class TestSynthesisPhase:
    """Test synthesis/consolidation phase."""

    def test_synthesis_convergence_calculation(self, initialized_workspace):
        """Test convergence calculation logic."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Create mock expert results
        create_expert_result_file(workspace, 1, "typescript")
        create_expert_result_file(workspace, 1, "python")

        # Simulate synthesis results
        state_manager.update_convergence(
            convergence_percent=75,
            consensus_reached=False,
            high_agreement=2,
            partial_agreement=3,
            low_agreement=1
        )

        # Verify state
        state = state_manager.load()
        assert state.convergence_percent == 75
        assert state.consensus_reached is False
        assert state.high_agreement == 2
        assert state.partial_agreement == 3
        assert state.low_agreement == 1

    def test_synthesis_consensus_reached(self, initialized_workspace):
        """Test when synthesis reaches consensus."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Simulate high convergence
        state_manager.update_convergence(
            convergence_percent=85,
            consensus_reached=True,
            high_agreement=5,
            partial_agreement=0,
            low_agreement=0
        )

        # Verify state
        state = state_manager.load()
        assert state.convergence_percent == 85
        assert state.consensus_reached is True


@pytest.mark.integration
class TestIterationProgression:
    """Test workflow iteration progression."""

    def test_iteration_increment(self, initialized_workspace):
        """Test iteration counter increments correctly."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Initial state
        state = state_manager.load()
        assert state.iteration == 1

        # Increment
        state_manager.increment_iteration()
        state = state_manager.load()
        assert state.iteration == 2

        # Increment again
        state_manager.increment_iteration()
        state = state_manager.load()
        assert state.iteration == 3

    def test_session_persistence_across_iterations(self, initialized_workspace):
        """Test that sessions persist across iterations."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Set up iteration 1 sessions
        state_manager.update_sessions({
            "typescript": "session-typescript-123",
            "python": "session-python-456"
        })

        # Set synthesis session
        state_manager.set_synthesis_session("synthesis-session-789")

        # Move to iteration 2
        state_manager.increment_iteration()

        # Verify sessions persisted
        state = state_manager.load()
        assert state.iteration == 2
        assert state.expert_sessions["typescript"] == "session-typescript-123"
        assert state.synthesis_session_id == "synthesis-session-789"


@pytest.mark.integration
class TestArtifactGeneration:
    """Test artifact generation phase."""

    def test_artifact_generation_result_storage(self, initialized_workspace):
        """Test storing artifact generation results."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Simulate artifact generation
        artifact_result = {
            "status": "success",
            "temp_adr_file": "temp-adr.md",
            "final_adr_file": "final-adr.md",
            "recommendations": [
                {"id": 1, "title": "Use REST API"},
                {"id": 2, "title": "Add versioning"}
            ]
        }

        state_manager.set_artifact_generation_result(artifact_result)
        state_manager.set_artifact_generation_session("artifact-session-123")

        # Verify state
        state = state_manager.load()
        assert state.artifact_generation_result["status"] == "success"
        assert state.artifact_generation_session_id == "artifact-session-123"
        assert len(state.artifact_generation_result["recommendations"]) == 2


@pytest.mark.integration
class TestPhaseTracking:
    """Test workflow phase tracking for UI."""

    def test_phase_transitions(self, initialized_workspace):
        """Test that phase field updates correctly."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Initial phase
        state_manager.set_phase("spawning_experts")
        state = state_manager.load()
        assert state.to_dict().get("phase") == "spawning_experts"

        # Move to synthesis
        state_manager.set_phase("consolidating")
        state = state_manager.load()
        assert state.to_dict().get("phase") == "consolidating"

        # Move to questions
        state_manager.set_phase("questions")
        state = state_manager.load()
        assert state.to_dict().get("phase") == "questions"

        # Move to artifact generation
        state_manager.set_phase("generating_artifact")
        state = state_manager.load()
        assert state.to_dict().get("phase") == "generating_artifact"

        # Complete
        state_manager.set_phase("completed")
        state = state_manager.load()
        assert state.to_dict().get("phase") == "completed"

    def test_invalid_phase_rejected(self, initialized_workspace):
        """Test that invalid phase names are rejected."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        with pytest.raises(ValueError, match="Invalid phase"):
            state_manager.set_phase("invalid_phase_name")


@pytest.mark.integration
class TestResumeCapability:
    """Test workflow resume/checkpoint functionality."""

    def test_phase_completion_marking(self, initialized_workspace):
        """Test marking phases as complete."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Mark spawning phase complete
        state_manager.mark_phase_complete(
            "spawning_iteration_1",
            {"success_count": 2, "error_count": 0}
        )

        # Check if marked complete
        assert state_manager.is_phase_complete("spawning_iteration_1")
        assert not state_manager.is_phase_complete("synthesis_iteration_1")

        # Get phase result
        result = state_manager.get_phase_result("spawning_iteration_1")
        assert result["success_count"] == 2
        assert result["error_count"] == 0

    def test_resume_skips_completed_phases(self, initialized_workspace):
        """Test that resume functionality can detect completed phases."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Mark multiple phases complete
        state_manager.mark_phase_complete(
            "spawning_iteration_1",
            {"success_count": 2}
        )
        state_manager.mark_phase_complete(
            "synthesizing_iteration_1",
            {"convergence_percent": 75}
        )

        # Verify both marked complete
        assert state_manager.is_phase_complete("spawning_iteration_1")
        assert state_manager.is_phase_complete("synthesizing_iteration_1")

        # New phase should not be complete
        assert not state_manager.is_phase_complete("generating_artifact")


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in workflow phases."""

    def test_expert_error_tracking(self, initialized_workspace):
        """Test tracking expert errors."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Simulate expert error
        state_manager.update_expert_progress(
            "typescript",
            "error",
            {"error": "Connection timeout", "duration_seconds": 120.0}
        )

        state = state_manager.load()
        assert state.expert_progress["typescript"]["status"] == "error"
        assert "error" in state.expert_progress["typescript"]

    def test_partial_expert_completion(self, initialized_workspace):
        """Test when some experts complete and others fail."""
        workspace = initialized_workspace
        state_manager = StateManager(workspace)

        # Simulate mixed results
        state_manager.update_expert_progress(
            "typescript", "complete",
            {"duration_seconds": 25.5, "total_tokens": 2000}
        )
        state_manager.update_expert_progress(
            "python", "error",
            {"error": "API error", "duration_seconds": 10.0}
        )

        state = state_manager.load()
        assert state.expert_progress["typescript"]["status"] == "complete"
        assert state.expert_progress["python"]["status"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
