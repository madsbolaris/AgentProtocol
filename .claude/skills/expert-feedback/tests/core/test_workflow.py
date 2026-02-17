"""
Tests for workflow orchestration (core/workflow.py).

Tests the main workflow functions without requiring real LLM calls.
Uses mocked subprocess calls and file operations.

Target coverage: 70%+

Test classes:
1. TestSpawnExpertsIteration - Test subprocess spawning for experts
2. TestSynthesizeFeedback - Test subprocess synthesis execution
3. TestGenerateArtifact - Test artifact generation subprocess
4. TestRegenerateArtifactWithVeto - Test veto-based regeneration
5. TestWaitForUserAnswers - Test Q&A waiting and polling
6. TestWaitForUserApproval - Test approval waiting
7. TestRunConcernReviewLoop - Test concern review iteration
8. TestRunWorkflow - Test full workflow with resume logic
9. TestCircuitBreaker - Test stall detection
10. TestMain - Test CLI with --revert-to, --resume flags
11. TestEdgeCases - Subprocess failures, missing files, max iterations
"""
import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
import sys
import argparse

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from core.workflow import (
    spawn_experts_iteration,
    synthesize_feedback,
    generate_artifact,
    wait_for_user_answers,
    wait_for_user_approval,
    run_concern_review_loop,
    run_workflow,
    main
)
from state.manager import StateManager, WorkspaceState
from errors import MinimumExpertsError, CircuitBreakerError


@pytest.mark.asyncio
class TestSpawnExpertsIteration:
    """Test expert spawning orchestration."""

    async def test_spawn_experts_basic(self, test_workspace, tmp_path):
        """Test basic expert spawning."""
        workspace = test_workspace

        # Mock subprocess to return success
        mock_result = {
            "success_count": 2,
            "error_count": 0,
            "results": {
                "typescript": {"status": "success"},
                "python": {"status": "success"}
            },
            "expert_sessions": {
                "typescript": "session-123",
                "python": "session-456"
            }
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript", "python"],
                review_context="Test review"
            )

            assert result["success_count"] == 2
            assert result["error_count"] == 0
            assert "typescript" in result["results"]
            assert "python" in result["results"]
            assert "expert_sessions" in result

    async def test_spawn_experts_with_failures(self, test_workspace):
        """Test expert spawning with some failures."""
        workspace = test_workspace

        mock_result = {
            "success_count": 1,
            "error_count": 1,
            "failed_experts": ["python"],
            "results": {
                "typescript": {"status": "success"},
                "python": {"status": "error", "error": "Timeout"}
            }
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript", "python"],
                review_context="Test review"
            )

            assert result["success_count"] == 1
            assert result["error_count"] == 1
            assert "failed_experts" in result

    async def test_spawn_experts_with_correlation_id(self, test_workspace):
        """Test spawning experts with correlation ID."""
        workspace = test_workspace

        mock_result = {
            "success_count": 1,
            "error_count": 0,
            "results": {"typescript": {"status": "success"}}
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript"],
                review_context="Test review",
                correlation_id="corr-123"
            )

            # Verify correlation-id was passed to subprocess
            call_args = mock_exec.call_args[0]
            assert "--correlation-id" in call_args
            assert "corr-123" in call_args

    async def test_spawn_experts_with_qa_answers(self, test_workspace):
        """Test spawning experts with QA answers path."""
        workspace = test_workspace
        qa_file = workspace / "qa-answers.json"
        qa_file.write_text(json.dumps({"answer_1": "Use REST"}))

        mock_result = {
            "success_count": 1,
            "error_count": 0,
            "results": {"typescript": {"status": "success"}}
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=2,
                experts=["typescript"],
                review_context="Test review",
                qa_answers_path=qa_file
            )

            # Verify qa-answers was passed
            call_args = mock_exec.call_args[0]
            assert "--qa-answers" in call_args

    async def test_spawn_experts_with_focus_files(self, test_workspace):
        """Test spawning experts with focus files."""
        workspace = test_workspace

        mock_result = {
            "success_count": 1,
            "error_count": 0,
            "results": {"typescript": {"status": "success"}}
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript"],
                review_context="Test review",
                focus_files=["src/api.ts", "src/types.ts"]
            )

            # Verify focus files were passed
            call_args = mock_exec.call_args[0]
            assert "--focus-files" in call_args
            assert "src/api.ts" in call_args

    async def test_spawn_experts_with_focus_folders(self, test_workspace):
        """Test spawning experts with focus folders."""
        workspace = test_workspace

        mock_result = {
            "success_count": 1,
            "error_count": 0,
            "results": {"typescript": {"status": "success"}}
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript"],
                review_context="Test review",
                focus_folders=["src/", "tests/"]
            )

            # Verify focus folders were passed
            call_args = mock_exec.call_args[0]
            assert "--focus-folders" in call_args

    async def test_spawn_experts_with_focus_context(self, test_workspace):
        """Test spawning experts with focus context."""
        workspace = test_workspace

        mock_result = {
            "success_count": 1,
            "error_count": 0,
            "results": {"typescript": {"status": "success"}}
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript"],
                review_context="Test review",
                focus_context="Review OAuth2 implementation"
            )

            # Verify focus context was passed
            call_args = mock_exec.call_args[0]
            assert "--focus-context" in call_args
            assert "Review OAuth2 implementation" in call_args

    async def test_spawn_experts_json_parse_error(self, test_workspace):
        """Test handling of JSON parse errors from spawn-all-experts."""
        workspace = test_workspace

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(b"Invalid JSON output", b"Some error")
            )
            mock_exec.return_value = mock_process

            result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=1,
                experts=["typescript", "python"],
                review_context="Test review"
            )

            # Should return error result
            assert result["status"] == "error"
            assert result["error"] == "Failed to spawn experts"
            assert result["success_count"] == 0
            assert result["error_count"] == 2  # All experts counted as failed


@pytest.mark.asyncio
class TestSynthesizeFeedback:
    """Test feedback synthesis orchestration."""

    async def test_synthesize_basic(self, test_workspace):
        """Test basic feedback synthesis."""
        workspace = test_workspace

        mock_result = {
            "convergence_percent": 75,
            "consensus_reached": False,
            "high_agreement": 3,
            "partial_agreement": 2,
            "low_agreement": 1
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_process.returncode = 0
            mock_exec.return_value = mock_process

            result = await synthesize_feedback(
                workspace=workspace,
                iteration=1
            )

            assert result["convergence_percent"] == 75
            assert result["consensus_reached"] is False
            assert result["high_agreement"] == 3

    async def test_synthesize_with_consensus(self, test_workspace):
        """Test synthesis with consensus reached."""
        workspace = test_workspace

        mock_result = {
            "convergence_percent": 95,
            "consensus_reached": True,
            "high_agreement": 10,
            "partial_agreement": 0,
            "low_agreement": 0
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await synthesize_feedback(
                workspace=workspace,
                iteration=2
            )

            assert result["convergence_percent"] == 95
            assert result["consensus_reached"] is True

    async def test_synthesize_with_correlation_id(self, test_workspace):
        """Test synthesis with correlation ID."""
        workspace = test_workspace

        mock_result = {
            "convergence_percent": 50,
            "consensus_reached": False
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await synthesize_feedback(
                workspace=workspace,
                iteration=1,
                correlation_id="corr-456"
            )

            # Verify correlation-id was passed
            call_args = mock_exec.call_args[0]
            assert "--correlation-id" in call_args
            assert "corr-456" in call_args

    async def test_synthesize_json_parse_error(self, test_workspace):
        """Test handling of JSON parse errors from synthesis."""
        workspace = test_workspace

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(b"Not valid JSON", b"Error details")
            )
            mock_exec.return_value = mock_process

            result = await synthesize_feedback(
                workspace=workspace,
                iteration=1
            )

            # Should return error result
            assert result["status"] == "error"
            assert result["error"] == "Failed to synthesize feedback"
            assert result["convergence_percent"] == 0
            assert result["consensus_reached"] is False


@pytest.mark.asyncio
class TestGenerateArtifact:
    """Test artifact generation subprocess."""

    async def test_generate_artifact_review_mode(self, test_workspace):
        """Test generating artifact in review mode (ADR)."""
        workspace = test_workspace

        mock_result = {
            "status": "success",
            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
            "final_adr_file": str(workspace / "adrs" / "adr-001.md"),
            "recommendations": []
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await generate_artifact(
                workspace=workspace,
                review_context="Test API review",
                mode="review"
            )

            assert result["status"] == "success"
            assert "temp_adr_file" in result
            assert "final_adr_file" in result

    async def test_generate_artifact_improve_mode(self, test_workspace):
        """Test generating artifact in improve mode."""
        workspace = test_workspace

        mock_result = {
            "status": "success",
            "temp_plan_file": str(workspace / "artifact" / "improvement-plan-v1.md"),
            "final_plan_file": str(workspace / "improvement-plan.md"),
            "recommendations": [
                {"id": "1", "priority": "high", "title": "Improve error handling"}
            ]
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await generate_artifact(
                workspace=workspace,
                review_context="Improvement suggestions",
                mode="improve"
            )

            assert result["status"] == "success"
            assert "temp_plan_file" in result
            assert len(result["recommendations"]) == 1

    async def test_generate_artifact_with_correlation_id(self, test_workspace):
        """Test artifact generation with correlation ID."""
        workspace = test_workspace

        mock_result = {
            "status": "success",
            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md")
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await generate_artifact(
                workspace=workspace,
                review_context="Test",
                mode="review",
                correlation_id="corr-789"
            )

            # Verify correlation-id was passed
            call_args = mock_exec.call_args[0]
            assert "--correlation-id" in call_args
            assert "corr-789" in call_args

    async def test_generate_artifact_json_parse_error(self, test_workspace):
        """Test handling of JSON parse errors from artifact generation."""
        workspace = test_workspace

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(b"Invalid JSON", b"Error")
            )
            mock_exec.return_value = mock_process

            result = await generate_artifact(
                workspace=workspace,
                review_context="Test",
                mode="review"
            )

            assert result["status"] == "error"
            assert result["error"] == "Failed to generate artifact"


@pytest.mark.asyncio
class TestRegenerateArtifactWithVeto:
    """Test veto-based regeneration subprocess."""

    async def test_regenerate_with_veto_basic(self, test_workspace):
        """Test basic artifact regeneration with veto feedback."""
        workspace = test_workspace

        vetoes = {
            "total_vetoes": 1,
            "critical_issues": [
                {"title": "Missing security considerations", "summary": "No security section"}
            ],
            "questions_for_user": ["What auth method to use?"]
        }

        mock_result = {
            "status": "success",
            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v2.md"),
            "regeneration_attempt": 1
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await regenerate_artifact_with_veto(
                workspace=workspace,
                review_context="Test review",
                mode="review",
                vetoes=vetoes,
                attempt=1
            )

            assert result["status"] == "success"
            assert "temp_adr_file" in result

    async def test_regenerate_with_veto_second_attempt(self, test_workspace):
        """Test second regeneration attempt."""
        workspace = test_workspace

        vetoes = {
            "total_vetoes": 1,
            "critical_issues": [{"title": "Still missing details"}]
        }

        mock_result = {
            "status": "success",
            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v3.md"),
            "regeneration_attempt": 2
        }

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_result).encode(), b"")
            )
            mock_exec.return_value = mock_process

            result = await regenerate_artifact_with_veto(
                workspace=workspace,
                review_context="Test review",
                mode="review",
                vetoes=vetoes,
                correlation_id="corr-123",
                attempt=2
            )

            # Verify regeneration-attempt was passed correctly
            call_args = mock_exec.call_args[0]
            assert "--regeneration-attempt" in call_args
            assert "2" in call_args
            assert "--regenerate" in call_args

    async def test_regenerate_json_parse_error(self, test_workspace):
        """Test handling of JSON parse errors during regeneration."""
        workspace = test_workspace

        vetoes = {"total_vetoes": 1}

        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(b"Bad JSON", b"Error")
            )
            mock_exec.return_value = mock_process

            result = await regenerate_artifact_with_veto(
                workspace=workspace,
                review_context="Test",
                mode="review",
                vetoes=vetoes,
                attempt=1
            )

            assert result["status"] == "error"
            assert result["error"] == "Failed to regenerate artifact"


@pytest.mark.asyncio
class TestWaitForUserAnswers:
    """Test waiting for user QA answers."""

    async def test_wait_finds_existing_answers(self, test_workspace):
        """Test finding existing QA answers file."""
        workspace = test_workspace
        iteration_dir = workspace / f"iteration-1"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        qa_file = iteration_dir / "qa-answers.json"
        answers = {"answer_1": "Use REST API", "answer_2": "Version 1.0"}
        qa_file.write_text(json.dumps(answers))

        # Should find answers immediately
        result = await wait_for_user_answers(workspace, 1)

        assert result is not None
        assert result["answer_1"] == "Use REST API"
        assert result["answer_2"] == "Version 1.0"

    async def test_wait_for_answers_polling(self, test_workspace):
        """Test polling for answers that appear later."""
        workspace = test_workspace
        iteration_dir = workspace / "iteration-1"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        qa_file = iteration_dir / "qa-answers.json"
        answers = {"answer_1": "GraphQL"}

        # Mock asyncio.sleep to simulate waiting
        sleep_count = 0

        async def mock_sleep(seconds):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count >= 2:
                # Create file after 2 polling attempts
                qa_file.write_text(json.dumps(answers))

        with patch('asyncio.sleep', side_effect=mock_sleep):
            result = await wait_for_user_answers(workspace, 1)

        assert result is not None
        assert result["answer_1"] == "GraphQL"
        assert sleep_count >= 2

    async def test_wait_user_skips_iteration(self, test_workspace):
        """Test handling skip_iteration flag in answers."""
        workspace = test_workspace
        iteration_dir = workspace / "iteration-1"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        qa_file = iteration_dir / "qa-answers.json"
        answers = {"skip_iteration": True}
        qa_file.write_text(json.dumps(answers))

        result = await wait_for_user_answers(workspace, 1)

        # Should return None when user skips
        assert result is None


@pytest.mark.asyncio
class TestWaitForUserApproval:
    """Test waiting for user approval."""

    async def test_wait_finds_existing_approvals(self, test_workspace):
        """Test finding existing approvals file."""
        workspace = test_workspace

        approvals_file = workspace / "approvals.json"
        approvals = [
            {"id": "1", "status": "approved"},
            {"id": "2", "status": "rejected"}
        ]
        approvals_file.write_text(json.dumps(approvals))

        result = await wait_for_user_approval(workspace, 2)

        assert len(result) == 2
        assert result[0]["status"] == "approved"
        assert result[1]["status"] == "rejected"

    async def test_wait_for_approvals_polling(self, test_workspace):
        """Test polling for approvals that appear later."""
        workspace = test_workspace
        approvals_file = workspace / "approvals.json"

        # Mock asyncio.sleep to simulate waiting
        sleep_count = 0

        async def mock_sleep(seconds):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count == 1:
                # First check: file doesn't exist yet
                pass
            elif sleep_count == 2:
                # Second check: file exists but incomplete
                approvals_file.write_text(json.dumps([{"id": "1", "status": "approved"}]))
            elif sleep_count >= 3:
                # Third check: all approvals present
                approvals = [
                    {"id": "1", "status": "approved"},
                    {"id": "2", "status": "approved"}
                ]
                approvals_file.write_text(json.dumps(approvals))

        with patch('asyncio.sleep', side_effect=mock_sleep):
            result = await wait_for_user_approval(workspace, 2)

        assert len(result) == 2
        assert sleep_count >= 3


@pytest.mark.asyncio
class TestRunConcernReviewLoop:
    """Test concern review iteration loop."""

    async def test_no_concerns_exits_immediately(self, test_workspace):
        """Test loop exits when no concerns are raised."""
        workspace = test_workspace

        # Mock artifact_concern_review to return no concerns
        concern_result = {
            "status": "success",
            "concern_review_dir": str(workspace / "concern-reviews" / "iteration-1")
        }

        synthesized = {
            "total_concerns": 0,
            "experts_with_concerns": [],
            "concerns": []
        }

        with patch('core.workflow.artifact_concern_review', new_callable=AsyncMock) as mock_concern:
            with patch('core.workflow.synthesize_concerns', new_callable=AsyncMock) as mock_synth:
                mock_concern.return_value = concern_result
                mock_synth.return_value = synthesized

                had_concerns = await run_concern_review_loop(
                    workspace=workspace,
                    experts=["typescript", "python"],
                    review_context="Test review",
                    mode="review",
                    artifact_path=workspace / "artifact" / "draft-adr-v1.md"
                )

        assert had_concerns is False

    async def test_user_disagrees_with_all_concerns(self, test_workspace):
        """Test loop exits when user disagrees with all concerns."""
        workspace = test_workspace

        concern_result = {
            "status": "success",
            "concern_review_dir": str(workspace / "concern-reviews" / "iteration-1")
        }

        synthesized = {
            "total_concerns": 2,
            "experts_with_concerns": ["typescript"],
            "concerns": [
                {"id": "1", "title": "Concern 1"},
                {"id": "2", "title": "Concern 2"}
            ]
        }

        user_decisions = {
            "should_iterate": False,
            "concerns_agreed": []
        }

        with patch('core.workflow.artifact_concern_review', new_callable=AsyncMock) as mock_concern:
            with patch('core.workflow.synthesize_concerns', new_callable=AsyncMock) as mock_synth:
                with patch('core.workflow.user_concern_review_interactive') as mock_user_review:
                    mock_concern.return_value = concern_result
                    mock_synth.return_value = synthesized
                    mock_user_review.return_value = user_decisions

                    had_concerns = await run_concern_review_loop(
                        workspace=workspace,
                        experts=["typescript", "python"],
                        review_context="Test review",
                        mode="review",
                        artifact_path=workspace / "artifact" / "draft-adr-v1.md"
                    )

        assert had_concerns is False

    async def test_concern_review_error_breaks_loop(self, test_workspace):
        """Test loop breaks on concern review error."""
        workspace = test_workspace

        concern_result = {
            "status": "error",
            "error": "Failed to review artifact"
        }

        with patch('core.workflow.artifact_concern_review', new_callable=AsyncMock) as mock_concern:
            mock_concern.return_value = concern_result

            had_concerns = await run_concern_review_loop(
                workspace=workspace,
                experts=["typescript"],
                review_context="Test review",
                mode="review",
                artifact_path=workspace / "artifact" / "draft-adr-v1.md"
            )

        # Should handle error gracefully
        assert had_concerns is False

    async def test_max_concern_iterations_reached(self, test_workspace):
        """Test loop exits after max iterations."""
        workspace = test_workspace

        concern_result = {
            "status": "success",
            "concern_review_dir": str(workspace / "concern-reviews" / "iteration-1")
        }

        synthesized = {
            "total_concerns": 1,
            "experts_with_concerns": ["typescript"],
            "concerns": [{"id": "1", "title": "Persistent concern"}]
        }

        user_decisions = {
            "should_iterate": True,
            "concerns_agreed": [{"id": "1", "title": "Persistent concern"}]
        }

        address_result = {
            "status": "success",
            "concern_iteration_dir": str(workspace / "concern-iterations" / "iteration-1")
        }

        synthesis_result = {
            "status": "success",
            "consolidated_recommendations": []
        }

        regeneration_result = {
            "status": "success",
            "artifact_path": str(workspace / "artifact" / "draft-adr-v2.md"),
            "artifact_version": 2
        }

        with patch('core.workflow.artifact_concern_review', new_callable=AsyncMock) as mock_concern:
            with patch('core.workflow.synthesize_concerns', new_callable=AsyncMock) as mock_synth:
                with patch('core.workflow.user_concern_review_interactive') as mock_user:
                    with patch('core.workflow.address_concerns_iteration', new_callable=AsyncMock) as mock_address:
                        with patch('core.workflow.synthesize_concern_updates', new_callable=AsyncMock) as mock_synth_updates:
                            with patch('core.workflow.regenerate_artifact_with_concerns', new_callable=AsyncMock) as mock_regen:
                                mock_concern.return_value = concern_result
                                mock_synth.return_value = synthesized
                                mock_user.return_value = user_decisions
                                mock_address.return_value = address_result
                                mock_synth_updates.return_value = synthesis_result
                                mock_regen.return_value = regeneration_result

                                had_concerns = await run_concern_review_loop(
                                    workspace=workspace,
                                    experts=["typescript"],
                                    review_context="Test review",
                                    mode="review",
                                    artifact_path=workspace / "artifact" / "draft-adr-v1.md"
                                )

        # Should complete max iterations (5)
        assert had_concerns is True
        assert mock_concern.call_count == 5  # Called max_concern_iterations times


@pytest.mark.asyncio
class TestRunWorkflow:
    """Test full workflow orchestration with resume logic."""

    async def test_workflow_basic_single_iteration(self, initialized_workspace):
        """Test basic workflow with single iteration reaching consensus."""
        workspace = initialized_workspace

        # Mock config - use Mock object with attributes
        mock_config = Mock()
        mock_config.max_iterations = 3
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        # Create mock state manager that tracks calls but doesn't do real I/O
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript", "python"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {}
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()
        mock_state_manager.increment_artifact_generation_attempt = Mock()
        mock_state_manager.record_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                    with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                        # Setup mocks
                                        mock_spawn.return_value = {
                                            "success_count": 2,
                                            "error_count": 0,
                                            "expert_sessions": {}
                                        }

                                        mock_synth.return_value = {
                                            "convergence_percent": 85,
                                            "consensus_reached": True,
                                            "status": "success"
                                        }

                                        mock_qa.return_value = None  # User skips

                                        mock_gen.return_value = {
                                            "status": "success",
                                            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                            "final_adr_file": str(workspace / "adrs" / "adr-001.md"),
                                            "recommendations": []
                                        }

                                        mock_concern.return_value = False

                                        # Mock artifact review subprocess
                                        review_result = {
                                            "status": "approved",
                                            "total_approvals": 2
                                        }
                                        mock_process = AsyncMock()
                                        mock_process.communicate = AsyncMock(
                                            return_value=(json.dumps(review_result).encode(), b"")
                                        )
                                        mock_exec.return_value = mock_process

                                        # Run workflow
                                        await run_workflow(
                                            workspace=workspace,
                                            review_context="Test API review",
                                            mode="review"
                                        )

        # Verify key steps were called
        assert mock_spawn.call_count == 1
        assert mock_synth.call_count == 1
        assert mock_gen.call_count == 1

    async def test_workflow_minimum_experts_error(self, initialized_workspace):
        """Test workflow fails when too few experts succeed."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 3
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python", "security"] if key == "experts" else None

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                # Only 1 expert succeeds, need at least 2 (50% of 3)
                mock_spawn.return_value = {
                    "success_count": 1,
                    "error_count": 2,
                    "failed_experts": ["python", "security"],
                    "expert_sessions": {}
                }

                with pytest.raises(MinimumExpertsError):
                    await run_workflow(
                        workspace=workspace,
                        review_context="Test review",
                        mode="review"
                    )

    async def test_workflow_with_resume_skips_completed_phases(self, initialized_workspace):
        """Test workflow resume skips already completed phases."""
        workspace = initialized_workspace

        # Setup state with completed phases
        state_manager = StateManager(workspace)
        state_manager.mark_phase_complete("spawning_iteration_1", {"success_count": 2})
        state_manager.mark_phase_complete("synthesizing_iteration_1", {"convergence_percent": 75})

        mock_config = Mock()
        mock_config.max_iterations = 3
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                    with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                        with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                            with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                    mock_qa.return_value = None  # Skip iteration
                                    mock_gen.return_value = {
                                        "status": "success",
                                        "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                        "recommendations": []
                                    }
                                    mock_concern.return_value = False

                                    # Mock artifact review
                                    review_result = {"status": "approved"}
                                    mock_process = AsyncMock()
                                    mock_process.communicate = AsyncMock(
                                        return_value=(json.dumps(review_result).encode(), b"")
                                    )
                                    mock_exec.return_value = mock_process

                                    await run_workflow(
                                        workspace=workspace,
                                        review_context="Test review",
                                        mode="review",
                                        resume=True  # Enable resume
                                    )

        # Spawning and synthesis should NOT be called (already completed)
        assert mock_spawn.call_count == 0
        assert mock_synth.call_count == 0


@pytest.mark.asyncio
class TestCircuitBreaker:
    """Test circuit breaker stall detection."""

    async def test_circuit_breaker_triggers_on_stalled_convergence(self, initialized_workspace):
        """Test circuit breaker triggers when convergence stalls."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 5
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        # Mock convergence staying at same level
        convergence_values = [30, 30, 30]  # Stuck at 30%

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript", "python"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.get_phase_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        mock_spawn.return_value = {
                            "success_count": 2,
                            "error_count": 0,
                            "expert_sessions": {}
                        }

                        call_count = 0

                        async def mock_synth_side_effect(*args, **kwargs):
                            nonlocal call_count
                            result = {
                                "convergence_percent": convergence_values[call_count],
                                "consensus_reached": False,
                                "status": "success"
                            }
                            call_count += 1
                            return result

                        mock_synth.side_effect = mock_synth_side_effect

                        with pytest.raises(CircuitBreakerError) as exc_info:
                            await run_workflow(
                                workspace=workspace,
                                review_context="Test review",
                                mode="review"
                            )

                        # Verify circuit breaker was triggered
                        assert "stuck" in str(exc_info.value).lower() or "stall" in str(exc_info.value).lower()

    async def test_circuit_breaker_triggers_on_consecutive_failures(self, initialized_workspace):
        """Test circuit breaker triggers on consecutive synthesis failures."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 5
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript", "python"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.get_phase_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        mock_spawn.return_value = {
                            "success_count": 2,
                            "error_count": 0,
                            "expert_sessions": {}
                        }

                        # Mock consecutive failures
                        mock_synth.return_value = {
                            "status": "error",
                            "error": "Synthesis failed",
                            "convergence_percent": 0,
                            "consensus_reached": False
                        }

                        with pytest.raises(CircuitBreakerError) as exc_info:
                            await run_workflow(
                                workspace=workspace,
                                review_context="Test review",
                                mode="review"
                            )

                        # Verify failure-based circuit breaker
                        assert "fail" in str(exc_info.value).lower()


@pytest.mark.asyncio
class TestVetoRegenerationLoop:
    """Test artifact veto regeneration logic."""

    async def test_veto_regeneration_success_after_one_attempt(self, initialized_workspace):
        """Test successful regeneration resolves veto after one attempt."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 1
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript", "python"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()
        mock_state_manager.increment_artifact_generation_attempt = Mock()
        mock_state_manager.record_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                with patch('core.workflow.regenerate_artifact_with_veto', new_callable=AsyncMock) as mock_regen:
                                    with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                            mock_spawn.return_value = {
                                                "success_count": 2,
                                                "error_count": 0,
                                                "expert_sessions": {}
                                            }

                                            mock_synth.return_value = {
                                                "convergence_percent": 85,
                                                "consensus_reached": True,
                                                "status": "success"
                                            }

                                            mock_qa.return_value = None

                                            mock_gen.return_value = {
                                                "status": "success",
                                                "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                                "recommendations": []
                                            }

                                            mock_concern.return_value = False

                                            mock_regen.return_value = {
                                                "status": "success",
                                                "temp_adr_file": str(workspace / "artifact" / "draft-adr-v2.md")
                                            }

                                            # First review: vetoed
                                            # Second review: approved
                                            review_results = [
                                                {
                                                    "status": "vetoed",
                                                    "vetoes": {
                                                        "total_vetoes": 1,
                                                        "critical_issues": [{"title": "Missing security"}],
                                                        "questions_for_user": []
                                                    }
                                                },
                                                {
                                                    "status": "approved"
                                                }
                                            ]

                                            call_count = 0

                                            async def mock_exec_side_effect(*args, **kwargs):
                                                nonlocal call_count
                                                result = review_results[call_count]
                                                call_count += 1
                                                mock_process = AsyncMock()
                                                mock_process.communicate = AsyncMock(
                                                    return_value=(json.dumps(result).encode(), b"")
                                                )
                                                return mock_process

                                            mock_exec.side_effect = mock_exec_side_effect

                                            await run_workflow(
                                                workspace=workspace,
                                                review_context="Test review",
                                                mode="review"
                                            )

        # Verify regeneration was called once
        assert mock_regen.call_count == 1

    async def test_veto_max_regeneration_attempts_exits(self, initialized_workspace):
        """Test workflow exits after max regeneration attempts."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 1
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript", "python"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript", "python"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()
        mock_state_manager.increment_artifact_generation_attempt = Mock()
        mock_state_manager.record_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                with patch('core.workflow.regenerate_artifact_with_veto', new_callable=AsyncMock) as mock_regen:
                                    with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                            mock_spawn.return_value = {
                                                "success_count": 2,
                                                "error_count": 0,
                                                "expert_sessions": {}
                                            }

                                            mock_synth.return_value = {
                                                "convergence_percent": 85,
                                                "consensus_reached": True,
                                                "status": "success"
                                            }

                                            mock_qa.return_value = None

                                            mock_gen.return_value = {
                                                "status": "success",
                                                "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                                "recommendations": []
                                            }

                                            mock_concern.return_value = False

                                            mock_regen.return_value = {
                                                "status": "success",
                                                "temp_adr_file": str(workspace / "artifact" / "draft-adr-v2.md")
                                            }

                                            # Always return vetoed
                                            review_result = {
                                                "status": "vetoed",
                                                "vetoes": {
                                                    "total_vetoes": 1,
                                                    "critical_issues": [{"title": "Still wrong"}]
                                                }
                                            }

                                            mock_process = AsyncMock()
                                            mock_process.communicate = AsyncMock(
                                                return_value=(json.dumps(review_result).encode(), b"")
                                            )
                                            mock_exec.return_value = mock_process

                                            # Should exit with error
                                            with pytest.raises(SystemExit) as exc_info:
                                                await run_workflow(
                                                    workspace=workspace,
                                                    review_context="Test review",
                                                    mode="review"
                                                )

                                            assert exc_info.value.code == 1

        # Verify max regeneration attempts (2)
        assert mock_regen.call_count == 2


@pytest.mark.asyncio
class TestMain:
    """Test CLI entrypoint with argument parsing."""

    def test_main_missing_workspace(self):
        """Test main exits when workspace doesn't exist."""
        with patch('sys.argv', ['workflow.py', '--workspace', '/nonexistent', '--review-context', 'Test']):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_revert_flag(self):
        """Test main handles --revert-to flag."""
        with patch('sys.argv', ['workflow.py', '--workspace', '/tmp', '--revert-to', 'iteration=2']):
            with patch('core.workflow.handle_revert') as mock_revert:
                with patch('pathlib.Path.exists', return_value=True):
                    mock_revert.return_value = {"status": "success"}

                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 0
                    assert mock_revert.called

    def test_main_missing_review_context(self):
        """Test main requires review-context for normal workflow."""
        with patch('sys.argv', ['workflow.py', '--workspace', '/tmp']):
            with patch('pathlib.Path.exists', return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1

    def test_main_keyboard_interrupt(self):
        """Test main handles keyboard interrupt gracefully."""
        with patch('sys.argv', ['workflow.py', '--workspace', '/tmp', '--review-context', 'Test']):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('asyncio.run', side_effect=KeyboardInterrupt()):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 130  # Standard SIGINT exit code


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and error handling."""

    async def test_artifact_generation_failure_exits(self, initialized_workspace):
        """Test workflow exits when artifact generation fails."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 1
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                mock_spawn.return_value = {
                                    "success_count": 1,
                                    "error_count": 0,
                                    "expert_sessions": {}
                                }

                                mock_synth.return_value = {
                                    "convergence_percent": 85,
                                    "consensus_reached": True,
                                    "status": "success"
                                }

                                mock_qa.return_value = None

                                # Artifact generation fails
                                mock_gen.return_value = {
                                    "status": "error",
                                    "error": "Failed to generate artifact"
                                }

                                with pytest.raises(SystemExit) as exc_info:
                                    await run_workflow(
                                        workspace=workspace,
                                        review_context="Test review",
                                        mode="review"
                                    )

                                assert exc_info.value.code == 1

    async def test_max_iterations_reached(self, initialized_workspace):
        """Test workflow completes after max iterations."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 2
        mock_config.convergence_target = 90  # High target
        mock_config.__getitem__ = lambda self, key: ["typescript"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript"],
                "convergence_target": 90,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()
        mock_state_manager.increment_artifact_generation_attempt = Mock()
        mock_state_manager.record_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                    with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                        mock_spawn.return_value = {
                                            "success_count": 1,
                                            "error_count": 0,
                                            "expert_sessions": {}
                                        }

                                        # Never reach consensus
                                        mock_synth.return_value = {
                                            "convergence_percent": 50,
                                            "consensus_reached": False,
                                            "status": "success"
                                        }

                                        # User answers to continue iterations
                                        mock_qa.return_value = {"answer": "value"}

                                        mock_gen.return_value = {
                                            "status": "success",
                                            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                            "recommendations": []
                                        }

                                        mock_concern.return_value = False

                                        # Mock artifact review
                                        review_result = {"status": "approved"}
                                        mock_process = AsyncMock()
                                        mock_process.communicate = AsyncMock(
                                            return_value=(json.dumps(review_result).encode(), b"")
                                        )
                                        mock_exec.return_value = mock_process

                                        await run_workflow(
                                            workspace=workspace,
                                            review_context="Test review",
                                            mode="review"
                                        )

        # Should spawn experts max_iterations times
        assert mock_spawn.call_count == 2

    async def test_artifact_review_subprocess_json_error(self, initialized_workspace):
        """Test handling of artifact review subprocess JSON errors."""
        workspace = initialized_workspace

        mock_config = Mock()
        mock_config.max_iterations = 1
        mock_config.convergence_target = 80
        mock_config.__getitem__ = lambda self, key: ["typescript"] if key == "experts" else None

        # Create mock state manager
        mock_state_manager = Mock()
        mock_state_manager.load = Mock(return_value=Mock(
            to_dict=Mock(return_value={
                "experts": ["typescript"],
                "convergence_target": 80,
                "convergence_percent": 0,
                "expert_results": {},
                "topic": "Test API Design"
            })
        ))
        mock_state_manager.is_phase_complete = Mock(return_value=False)
        mock_state_manager.mark_phase_complete = Mock()
        mock_state_manager.set_phase = Mock()
        mock_state_manager.update_sessions = Mock()
        mock_state_manager.update_convergence = Mock()
        mock_state_manager.set_artifact_generation_result = Mock()
        mock_state_manager.increment_artifact_generation_attempt = Mock()
        mock_state_manager.record_artifact_generation_result = Mock()

        with patch('core.workflow.get_config', return_value=mock_config):
            with patch('core.workflow.WorkspaceStateManager', return_value=mock_state_manager):
                with patch('core.workflow.spawn_experts_iteration', new_callable=AsyncMock) as mock_spawn:
                    with patch('core.workflow.synthesize_feedback', new_callable=AsyncMock) as mock_synth:
                        with patch('core.workflow.wait_for_user_answers', new_callable=AsyncMock) as mock_qa:
                            with patch('core.workflow.generate_artifact', new_callable=AsyncMock) as mock_gen:
                                with patch('core.workflow.run_concern_review_loop', new_callable=AsyncMock) as mock_concern:
                                    with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_exec:
                                        mock_spawn.return_value = {
                                            "success_count": 1,
                                            "error_count": 0,
                                            "expert_sessions": {}
                                        }

                                        mock_synth.return_value = {
                                            "convergence_percent": 85,
                                            "consensus_reached": True,
                                            "status": "success"
                                        }

                                        mock_qa.return_value = None

                                        mock_gen.return_value = {
                                            "status": "success",
                                            "temp_adr_file": str(workspace / "artifact" / "draft-adr-v1.md"),
                                            "recommendations": []
                                        }

                                        mock_concern.return_value = False

                                        # Artifact review returns invalid JSON
                                        mock_process = AsyncMock()
                                        mock_process.communicate = AsyncMock(
                                            return_value=(b"Not valid JSON", b"Error details")
                                        )
                                        mock_exec.return_value = mock_process

                                        # Should handle gracefully - currently just logs and continues
                                        await run_workflow(
                                            workspace=workspace,
                                            review_context="Test review",
                                            mode="review"
                                        )

        # Workflow should complete despite JSON parse error
        assert mock_gen.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
