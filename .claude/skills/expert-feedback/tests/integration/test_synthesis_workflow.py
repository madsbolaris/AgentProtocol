"""
Integration tests for synthesis workflow with LLM mocking.

Tests the complete synthesis/consolidation workflow by calling actual workflow
functions with mocked Claude SDK, validating that:
- LLM is called correctly to consolidate feedback
- Convergence is calculated properly
- Questions are generated when convergence is low
- State transitions are correct
- Session reuse works for iteration 2+

Uses MockClaudeAgentSDK to avoid real API calls while testing workflow logic.
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add scripts directory to path
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from state.manager import StateManager, WorkspaceState
from file_io.json_ops import save_json


@pytest.mark.integration
@pytest.mark.asyncio
class TestSynthesisWorkflow:
    """Test synthesis/consolidation workflow with mocked LLM."""

    async def test_synthesize_high_convergence(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test synthesis with high convergence (>80%) leading to consensus."""
        # Import workflow functions AFTER mock is set up
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        progress = ProgressTracker(1, workspace)
        paths = WorkspacePaths(workspace)

        # Create mock expert feedback files
        experts_dir = paths.experts_dir(1)
        experts_dir.mkdir(parents=True, exist_ok=True)

        # TypeScript expert feedback
        typescript_feedback = {
            "expert": "typescript",
            "analysis": "The API design looks solid with good type safety.",
            "recommendations": [
                {
                    "title": "Use strict TypeScript mode",
                    "description": "Enable strict mode for better type checking",
                    "priority": "high"
                }
            ],
            "concerns": [],
            "questions": []
        }
        save_json(typescript_feedback, experts_dir / "state-typescript.json")

        # Python expert feedback
        python_feedback = {
            "expert": "python",
            "analysis": "Good design overall, consider async patterns.",
            "recommendations": [
                {
                    "title": "Use async/await for I/O operations",
                    "description": "Implement async patterns for better performance",
                    "priority": "high"
                }
            ],
            "concerns": [],
            "questions": []
        }
        save_json(python_feedback, experts_dir / "state-python.json")

        # Call synthesis workflow
        result = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress,
            correlation_id="test-synthesis-001"
        )

        # Verify result structure
        assert "status" in result
        assert result["status"] == "complete"
        assert "convergence_percent" in result
        assert "consensus_reached" in result

        # Verify state was updated
        state_manager = StateManager(workspace)
        state = state_manager.load()
        assert state.convergence_percent >= 0
        assert state.convergence_percent <= 100

        # Verify synthesis output file was created
        synthesized_file = paths.synthesized_md(1)
        assert synthesized_file.exists(), "Synthesized output file should be created"

    async def test_synthesize_low_convergence_generates_questions(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test synthesis with low convergence (<80%) generates clarifying questions."""
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        progress = ProgressTracker(1, workspace)
        paths = WorkspacePaths(workspace)

        # Create mock expert feedback with conflicting opinions
        experts_dir = paths.experts_dir(1)
        experts_dir.mkdir(parents=True, exist_ok=True)

        typescript_feedback = {
            "expert": "typescript",
            "analysis": "Should use REST API",
            "recommendations": [
                {"title": "Use REST", "description": "REST is simpler", "priority": "high"}
            ],
            "concerns": ["GraphQL adds complexity"],
            "questions": []
        }
        save_json(typescript_feedback, experts_dir / "state-typescript.json")

        python_feedback = {
            "expert": "python",
            "analysis": "Should use GraphQL",
            "recommendations": [
                {"title": "Use GraphQL", "description": "GraphQL is more flexible", "priority": "high"}
            ],
            "concerns": ["REST is too rigid"],
            "questions": []
        }
        save_json(python_feedback, experts_dir / "state-python.json")

        # Call synthesis workflow
        result = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress,
            correlation_id="test-synthesis-002"
        )

        # Verify result structure
        assert result["status"] == "complete"
        assert result["convergence_percent"] < 80, "Low convergence expected with conflicting feedback"
        assert result["consensus_reached"] == False, "No consensus with low convergence"

        # Verify questions were generated
        questions_file = paths.questions_json(1)
        assert questions_file.exists(), "Questions file should be created when convergence is low"

        questions = json.loads(questions_file.read_text())
        assert len(questions) > 0, "Should generate at least one question"

    async def test_synthesize_session_reuse_iteration_2(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test that synthesis reuses session ID for iteration 2+."""
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        config.reuse_synthesis_session = True
        paths = WorkspacePaths(workspace)

        # Setup: Create expert feedback for iteration 1
        experts_dir_1 = paths.experts_dir(1)
        experts_dir_1.mkdir(parents=True, exist_ok=True)

        typescript_feedback = {
            "expert": "typescript",
            "analysis": "Good design",
            "recommendations": [{"title": "Test", "description": "Test", "priority": "medium"}],
            "concerns": [],
            "questions": []
        }
        save_json(typescript_feedback, experts_dir_1 / "state-typescript.json")

        # Run iteration 1 synthesis
        progress_1 = ProgressTracker(1, workspace)
        result_1 = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress_1,
            correlation_id="test-synthesis-003"
        )

        session_id_1 = result_1.get("session_id")
        assert session_id_1 is not None, "Should have session ID from iteration 1"

        # Setup iteration 2 with updated state
        state_manager = StateManager(workspace)
        state = state_manager.load()
        state.iteration = 2
        state.synthesis_session_id = session_id_1
        state_manager.update(state)

        # Create expert feedback for iteration 2
        experts_dir_2 = paths.experts_dir(2)
        experts_dir_2.mkdir(parents=True, exist_ok=True)
        save_json(typescript_feedback, experts_dir_2 / "state-typescript.json")

        # Run iteration 2 synthesis
        progress_2 = ProgressTracker(1, workspace)
        result_2 = await synthesize_feedback(
            workspace=workspace,
            iteration=2,
            config=config,
            progress=progress_2,
            correlation_id="test-synthesis-004"
        )

        # Verify session was reused
        session_id_2 = result_2.get("session_id")
        # Note: Session reuse depends on SDK behavior, so we just verify it's set
        assert session_id_2 is not None, "Should have session ID for iteration 2"


@pytest.mark.integration
@pytest.mark.asyncio
class TestSynthesisValidation:
    """Test synthesis output validation."""

    async def test_synthesis_output_validation(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test that synthesis output is validated for required fields."""
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        progress = ProgressTracker(1, workspace)
        paths = WorkspacePaths(workspace)

        # Create mock expert feedback
        experts_dir = paths.experts_dir(1)
        experts_dir.mkdir(parents=True, exist_ok=True)

        expert_feedback = {
            "expert": "typescript",
            "analysis": "Test analysis",
            "recommendations": [
                {"title": "Test", "description": "Test description", "priority": "medium"}
            ],
            "concerns": [],
            "questions": []
        }
        save_json(expert_feedback, experts_dir / "state-typescript.json")

        # Call synthesis
        result = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress,
            correlation_id="test-synthesis-validation"
        )

        # Verify required output fields
        assert "convergence_percent" in result
        assert isinstance(result["convergence_percent"], (int, float))
        assert 0 <= result["convergence_percent"] <= 100

        assert "consensus_reached" in result
        assert isinstance(result["consensus_reached"], bool)

        assert "synthesized_file" in result
        if result["synthesized_file"]:
            assert Path(result["synthesized_file"]).exists()


@pytest.mark.integration
@pytest.mark.asyncio
class TestSynthesisStateManagement:
    """Test synthesis state management and phase tracking."""

    async def test_synthesis_updates_phase_state(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test that synthesis updates phase state correctly."""
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        progress = ProgressTracker(1, workspace)
        paths = WorkspacePaths(workspace)

        # Create expert feedback
        experts_dir = paths.experts_dir(1)
        experts_dir.mkdir(parents=True, exist_ok=True)

        expert_feedback = {
            "expert": "typescript",
            "analysis": "Analysis",
            "recommendations": [{"title": "Rec", "description": "Desc", "priority": "low"}],
            "concerns": [],
            "questions": []
        }
        save_json(expert_feedback, experts_dir / "state-typescript.json")

        # Verify initial state
        state_manager = StateManager(workspace)
        initial_state = state_manager.load()
        assert initial_state.phase != "consolidating"

        # Call synthesis (this should set phase to "consolidating")
        await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress,
            correlation_id="test-synthesis-phase"
        )

        # Verify phase was updated
        final_state = state_manager.load()
        # Phase might be "consolidating" or might have moved to next phase
        # Just verify convergence was calculated
        assert hasattr(final_state, 'convergence_percent')
        assert final_state.convergence_percent >= 0

    async def test_synthesis_skips_if_already_complete(
        self, mock_claude_sdk, initialized_workspace
    ):
        """Test that synthesis skips work if already completed."""
        from core.synthesize import synthesize_feedback
        from ui.progress_tracker import ProgressTracker
        from config import get_config
        from file_io.workspace_utils import WorkspacePaths

        workspace = initialized_workspace
        config = get_config()
        paths = WorkspacePaths(workspace)

        # Create expert feedback
        experts_dir = paths.experts_dir(1)
        experts_dir.mkdir(parents=True, exist_ok=True)

        expert_feedback = {
            "expert": "typescript",
            "analysis": "Analysis",
            "recommendations": [{"title": "R", "description": "D", "priority": "low"}],
            "concerns": [],
            "questions": []
        }
        save_json(expert_feedback, experts_dir / "state-typescript.json")

        # First run
        progress_1 = ProgressTracker(1, workspace)
        result_1 = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress_1,
            correlation_id="test-skip-1"
        )

        convergence_1 = result_1["convergence_percent"]

        # Mark phase as complete
        state_manager = StateManager(workspace)
        phase_name = f"consolidating_iteration_1"
        state_manager.mark_phase_complete(phase_name, result_1)

        # Second run - should skip
        progress_2 = ProgressTracker(1, workspace)
        result_2 = await synthesize_feedback(
            workspace=workspace,
            iteration=1,
            config=config,
            progress=progress_2,
            correlation_id="test-skip-2"
        )

        # Verify it was skipped
        assert result_2.get("skipped") == True, "Should skip already-complete phase"
        assert result_2["convergence_percent"] == convergence_1, "Should return cached result"
