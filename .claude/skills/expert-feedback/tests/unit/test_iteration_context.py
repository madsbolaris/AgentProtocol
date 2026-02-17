#!/usr/bin/env python3
"""
Unit tests for iteration context loading (Context Gap Fix 1.1).

Tests the _load_iteration_context() function in spawn_experts.py.
"""
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from core.spawn_experts import _load_iteration_context
from state.manager import StateManager, WorkspaceState


class TestIterationContextLoading:
    """Test suite for iteration context loading."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workspace = Path("/tmp/test-workspace-context")
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Create state.json
        self.state_path = self.workspace / "state.json"
        self.state_manager = StateManager(self.workspace)

        # Initialize state
        initial_state = WorkspaceState(
            topic="Test workflow",
            experts=["typescript", "python"],
            iteration=1,
            mode="review"
        )
        self.state_manager.create(initial_state)

    def teardown_method(self):
        """Clean up test files."""
        import shutil
        if self.workspace.exists():
            shutil.rmtree(self.workspace)

    def test_iteration_1_returns_empty_context(self):
        """Iteration 1 should return empty context (no previous iteration)."""
        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=1,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        assert context["consolidated_questions"] == []
        assert context["convergence_data"] is None
        assert context["other_experts"] == []
        assert context["previous_dx_rating"] is None

    def test_iteration_2_loads_previous_summary(self):
        """Iteration 2 should load summary from iteration 1."""
        # Set up iteration history
        state = self.state_manager.load()
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=45,
            agreement_breakdown={"high": 3, "partial": 2, "low": 1},
            expert_summaries={
                "typescript": {
                    "dx_rating": 4,
                    "concerns_count": 3,
                    "top_concern": "Type complexity",
                    "recommendations_count": 5
                },
                "python": {
                    "dx_rating": 3,
                    "concerns_count": 5,
                    "top_concern": "Missing docs",
                    "recommendations_count": 4
                }
            }
        )

        # Load context for typescript expert
        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        # Verify convergence data
        assert context["convergence_data"] is not None
        assert context["convergence_data"]["convergence_percent"] == 45
        assert context["convergence_data"]["high_agreement"] == 3
        assert context["convergence_data"]["partial_agreement"] == 2
        assert context["convergence_data"]["low_agreement"] == 1

        # Verify other experts (should not include typescript)
        assert len(context["other_experts"]) == 1
        assert context["other_experts"][0]["name"] == "python"
        assert context["other_experts"][0]["dx_rating"] == 3
        assert context["other_experts"][0]["concerns_count"] == 5

        # Verify previous DX rating
        assert context["previous_dx_rating"] == 4

    def test_loads_consolidated_questions(self):
        """Should load consolidated questions from previous iteration."""
        # Create iteration 1 questions file
        iter1_dir = self.workspace / "iteration-1"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        questions_file = iter1_dir / "questions.json"

        questions_data = {
            "questions": [
                {"id": "q-001", "question": "What is the authentication method?"},
                {"id": "q-002", "question": "How will errors be handled?"}
            ]
        }
        questions_file.write_text(json.dumps(questions_data, indent=2))

        # Set up minimal state
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=40,
            agreement_breakdown={"high": 1, "partial": 1, "low": 1},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Load context
        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        # Verify questions loaded
        assert len(context["consolidated_questions"]) == 2
        assert context["consolidated_questions"][0]["id"] == "q-001"
        assert context["consolidated_questions"][1]["question"] == "How will errors be handled?"

    def test_iteration_3_uses_iteration_2_summary(self):
        """Iteration 3 should load summary from iteration 2 (most recent)."""
        # Record iteration 1
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=35,
            agreement_breakdown={"high": 1, "partial": 2, "low": 2},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Record iteration 2 (should be used)
        self.state_manager.record_iteration_summary(
            iteration=2,
            convergence_percent=55,
            agreement_breakdown={"high": 4, "partial": 1, "low": 0},
            expert_summaries={"typescript": {"dx_rating": 4}}
        )

        # Load context for iteration 3
        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=3,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        # Should use iteration 2 data
        assert context["convergence_data"]["convergence_percent"] == 55
        assert context["previous_dx_rating"] == 4

    def test_handles_missing_questions_file(self):
        """Should handle missing questions.json gracefully."""
        # Set up state without questions file
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=40,
            agreement_breakdown={"high": 1, "partial": 1, "low": 1},
            expert_summaries={"typescript": {"dx_rating": 3}}
        )

        # Load context (no questions file exists)
        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        # Should return empty questions list
        assert context["consolidated_questions"] == []

    def test_excludes_self_from_other_experts(self):
        """Should not include the current expert in other_experts list."""
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=50,
            agreement_breakdown={"high": 2, "partial": 1, "low": 0},
            expert_summaries={
                "typescript": {"dx_rating": 4, "concerns_count": 2},
                "python": {"dx_rating": 3, "concerns_count": 4},
                "csharp": {"dx_rating": 5, "concerns_count": 1}
            }
        )

        context = _load_iteration_context(
            workspace=self.workspace,
            current_iteration=2,
            expert_name="typescript",
            state_manager=self.state_manager
        )

        # Should have python and csharp, but not typescript
        expert_names = [e["name"] for e in context["other_experts"]]
        assert "typescript" not in expert_names
        assert "python" in expert_names
        assert "csharp" in expert_names
        assert len(expert_names) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
