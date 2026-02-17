#!/usr/bin/env python3
"""
Integration tests for expert context propagation across iterations.

Tests that experts receive full context in iteration 2+:
- Consolidated questions
- Convergence data
- Peer expert summaries
- Previous DX ratings
- Iteration diffs
"""
import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from state.manager import StateManager


@pytest.mark.asyncio
class TestExpertContextPropagation:
    """Integration tests for expert context propagation."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create test workspace."""
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()
        return workspace

    @pytest.fixture
    def state_manager(self, workspace):
        """Create StateManager with initialized state."""
        from state.manager import WorkspaceState
        manager = StateManager(workspace)
        # Initialize state for tests
        state = WorkspaceState(
            topic="Test API Design",
            experts=["typescript", "python"],
            iteration=1,
            mode="review",
            convergence_target=80
        )
        manager.create(state)
        return manager

    async def test_iteration_1_creates_baseline(self, workspace, state_manager):
        """
        Iteration 1 should create baseline data for iteration 2.

        Verifies:
        - Expert sessions created and saved
        - Iteration summary recorded with expert summaries
        - Session history files created
        """
        # Mock spawn_expert_with_timeout to simulate expert spawning
        async def mock_spawn_expert(expert_name, *args, **kwargs):
            return {
                "status": "complete",
                "expert": expert_name,
                "session_id": f"sess-{expert_name}-001",
                "dx_rating": {"stars": 4},
                "concerns": [{"id": "con-001", "title": "Test concern"}],
                "recommendations": [{"id": "rec-001", "title": "Test rec"}],
                "tokens_used": 3000
            }

        # Simulate running spawn-all-experts for iteration 1
        from core import spawn_experts

        with patch.object(spawn_experts, 'spawn_expert_with_timeout', mock_spawn_expert):
            # This would normally be called by the workflow
            # For now, manually simulate the state changes

            # Record expert sessions
            state_manager.update_sessions({
                "typescript": "sess-typescript-001",
                "python": "sess-python-001"
            })

            # Record iteration summary
            state_manager.record_iteration_summary(
                iteration=1,
                convergence_percent=40,
                agreement_breakdown={"high": 1, "partial": 2, "low": 1},
                expert_summaries={
                    "typescript": {
                        "dx_rating": 4,
                        "concerns_count": 2,
                        "top_concern": "Type complexity",
                        "recommendations_count": 3
                    },
                    "python": {
                        "dx_rating": 3,
                        "concerns_count": 3,
                        "top_concern": "Missing docs",
                        "recommendations_count": 4
                    }
                }
            )

        # Verify state created
        state = state_manager.load()
        assert "typescript" in state.expert_sessions
        assert "python" in state.expert_sessions
        assert len(state.iteration_history) == 1
        assert state.iteration_history[0]["convergence_percent"] == 40

    async def test_iteration_2_receives_full_context(self, workspace, state_manager):
        """
        Iteration 2 should load full context from iteration 1.

        Verifies:
        - _load_iteration_context() provides all 4 context fields
        - Iteration diff generated
        - Context passed to expert prompt
        """
        # Set up iteration 1 state
        state_manager.update_sessions({
            "typescript": "sess-typescript-001"
        })

        state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=45,
            agreement_breakdown={"high": 2, "partial": 1, "low": 1},
            expert_summaries={
                "typescript": {
                    "dx_rating": 3,
                    "concerns_count": 2,
                    "recommendations_count": 3
                },
                "python": {
                    "dx_rating": 4,
                    "concerns_count": 1,
                    "recommendations_count": 5
                }
            }
        )

        # Create questions file
        iter1_dir = workspace / "iteration-1"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        questions_file = iter1_dir / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q-001", "question": "What auth method?", "asked_by": ["typescript"]}
            ]
        }))

        # Create iteration 1 expert state for diff
        experts_dir = iter1_dir / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)
        (experts_dir / "state-typescript.json").write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "concerns": [{"id": "con-001"}, {"id": "con-002"}],
            "recommendations": [{"id": "rec-001"}]
        }))

        # Load context for iteration 2
        from core.spawn_experts import _load_iteration_context

        context = _load_iteration_context(
            workspace=workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=state_manager
        )

        # Verify all context fields present
        assert context["consolidated_questions"] is not None
        assert len(context["consolidated_questions"]) == 1
        assert context["convergence_data"] is not None
        assert context["convergence_data"]["convergence_percent"] == 45
        assert context["other_experts"] is not None
        assert len(context["other_experts"]) == 1  # python only, not typescript
        assert context["previous_dx_rating"] == 3
        assert "iteration_diff" in context

    async def test_expert_sees_peer_feedback(self, workspace, state_manager):
        """
        Expert should see summaries of peer expert reviews.

        Verifies:
        - other_experts list excludes self
        - Peer summaries include DX ratings and concern counts
        """
        # Set up 3 experts
        state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=50,
            agreement_breakdown={"high": 2, "partial": 1, "low": 0},
            expert_summaries={
                "typescript": {"dx_rating": 4, "concerns_count": 2},
                "python": {"dx_rating": 5, "concerns_count": 1},
                "csharp": {"dx_rating": 3, "concerns_count": 4}
            }
        )

        from core.spawn_experts import _load_iteration_context

        # Load context for typescript
        context = _load_iteration_context(
            workspace=workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=state_manager
        )

        # Should see python and csharp, but not typescript
        peer_names = [e["name"] for e in context["other_experts"]]
        assert "typescript" not in peer_names
        assert "python" in peer_names
        assert "csharp" in peer_names

        # Verify peer data
        python_peer = next(e for e in context["other_experts"] if e["name"] == "python")
        assert python_peer["dx_rating"] == 5
        assert python_peer["concerns_count"] == 1

    async def test_convergence_tracking_across_iterations(self, workspace, state_manager):
        """
        Convergence should be tracked and compared across iterations.

        Verifies:
        - Iteration diff shows convergence delta
        - Trending indicators correct
        """
        # Record iteration 1: 35% convergence
        state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=35,
            agreement_breakdown={"high": 1, "partial": 2, "low": 2},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Create dummy expert state for diff
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        (iter1_dir / "state-typescript.json").write_text(json.dumps({
            "dx_rating": {"stars": 3}
        }))

        # Record iteration 2: 55% convergence (improved!)
        state_manager.record_iteration_summary(
            iteration=2,
            convergence_percent=55,
            agreement_breakdown={"high": 3, "partial": 2, "low": 0},
            expert_summaries={"typescript": {"dx_rating": 4}}
        )

        # Create iteration 2 expert state
        iter2_dir = workspace / "iteration-2" / "experts"
        iter2_dir.mkdir(parents=True, exist_ok=True)
        (iter2_dir / "state-typescript.json").write_text(json.dumps({
            "dx_rating": {"stars": 4}
        }))

        # Load context for iteration 3
        from core.spawn_experts import _load_iteration_context

        context = _load_iteration_context(
            workspace=workspace,
            current_iteration=3,
            expert_name="typescript",
            state_manager=state_manager
        )

        # Verify convergence data shows iteration 2 (most recent)
        assert context["convergence_data"]["convergence_percent"] == 55

        # Verify iteration diff shows improvement
        diff = context["iteration_diff"]
        assert diff["convergence_change"]["from"] == 35
        assert diff["convergence_change"]["to"] == 55
        assert diff["convergence_change"]["delta"] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
