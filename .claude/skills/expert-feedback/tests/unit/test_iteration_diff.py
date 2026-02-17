#!/usr/bin/env python3
"""
Unit tests for iteration diff generation (Context Gap Fix 1.2).

Tests the generate_iteration_diff() function.
"""
import json
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from analysis.iteration_diff import (
    generate_iteration_diff,
    _diff_own_review,
    _diff_peer_reviews,
    _diff_user_answers,
    _diff_convergence
)
from state.manager import StateManager


class TestIterationDiff:
    """Test suite for iteration diff generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.workspace = Path("/tmp/test-workspace-diff")
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state_manager = StateManager(self.workspace)

        # Initialize state
        from state.manager import WorkspaceState
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

    def test_iteration_1_returns_empty_diff(self):
        """Iteration 1 has no previous iteration, should return empty."""
        diff = generate_iteration_diff(
            workspace=self.workspace,
            expert_name="typescript",
            current_iteration=1,
            state_manager=self.state_manager
        )

        assert diff == {}

    def test_diff_own_review_detects_changes(self):
        """Should detect changes in expert's own review."""
        # Create iteration 1 review (new structure: experts/{expert}/state.json)
        iter1_expert_dir = self.workspace / "iteration-1" / "experts" / "typescript"
        iter1_expert_dir.mkdir(parents=True, exist_ok=True)

        iter1_state = {
            "dx_rating": {"stars": 3},
            "concerns": [
                {"id": "con-001", "title": "Type complexity"},
                {"id": "con-002", "title": "Missing tests"}
            ],
            "recommendations": [
                {"id": "rec-001", "title": "Add types"},
                {"id": "rec-002", "title": "Write tests"}
            ]
        }
        (iter1_expert_dir / "state.json").write_text(json.dumps(iter1_state))

        # Create iteration 2 review (new structure: experts/{expert}/state.json)
        iter2_expert_dir = self.workspace / "iteration-2" / "experts" / "typescript"
        iter2_expert_dir.mkdir(parents=True, exist_ok=True)

        iter2_state = {
            "dx_rating": {"stars": 4},
            "concerns": [
                {"id": "con-001", "title": "Type complexity"}
                # con-002 resolved
            ],
            "recommendations": [
                {"id": "rec-001", "title": "Add types"},
                {"id": "rec-002", "title": "Write tests"},
                {"id": "rec-003", "title": "Add docs"}  # New
            ]
        }
        (iter2_expert_dir / "state.json").write_text(json.dumps(iter2_state))

        # Generate diff
        diff = _diff_own_review(self.workspace, "typescript", 1)

        # Verify changes detected
        assert diff["dx_rating_previous"] == 3
        assert diff["dx_rating_current"] == 4
        assert diff["concerns_count_previous"] == 2
        assert diff["concerns_count_current"] == 1
        assert diff["recommendations_count_previous"] == 2
        assert diff["recommendations_count_current"] == 3

    def test_diff_convergence_calculates_delta(self):
        """Should calculate convergence delta between iterations."""
        # Record iteration 1
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=35,
            agreement_breakdown={"high": 1, "partial": 2, "low": 2},
            expert_summaries={}
        )

        # Record iteration 2
        self.state_manager.record_iteration_summary(
            iteration=2,
            convergence_percent=55,
            agreement_breakdown={"high": 3, "partial": 2, "low": 0},
            expert_summaries={}
        )

        # Calculate diff
        diff = _diff_convergence(self.workspace, 1, 2, self.state_manager)

        # Verify delta
        assert diff["from"] == 35
        assert diff["to"] == 55
        assert diff["delta"] == 20
        assert diff["trending_up"] is True

    def test_diff_user_answers_counts_questions(self):
        """Should count how many questions were answered."""
        # Create questions file with answers
        iter1_dir = self.workspace / "iteration-1"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        questions_data = {
            "questions": [
                {
                    "id": "q-001",
                    "question": "What auth method?",
                    "asked_by": ["typescript", "python"],
                    "answer": "OAuth2"
                },
                {
                    "id": "q-002",
                    "question": "How to handle errors?",
                    "asked_by": ["typescript"],
                    "answer": "Return error codes"
                },
                {
                    "id": "q-003",
                    "question": "Deployment strategy?",
                    "asked_by": ["python"],
                    "answer": None  # Not answered
                }
            ]
        }
        (iter1_dir / "questions.json").write_text(json.dumps(questions_data))

        # Generate diff
        diff = _diff_user_answers(self.workspace, "typescript", 1)

        # Verify counts
        assert diff["questions_answered"] == 2
        assert diff["your_questions_answered"] == 2  # Both q-001 and q-002

    def test_full_diff_integration(self):
        """Test full diff generation with all components."""
        # Set up iteration 1 (new structure: experts/{expert}/state.json)
        iter1_ts_dir = self.workspace / "iteration-1" / "experts" / "typescript"
        iter1_ts_dir.mkdir(parents=True, exist_ok=True)

        iter1_state_ts = {
            "dx_rating": {"stars": 3},
            "concerns": [{"id": "con-001"}],
            "recommendations": [{"id": "rec-001"}]
        }
        (iter1_ts_dir / "state.json").write_text(json.dumps(iter1_state_ts))

        iter1_py_dir = self.workspace / "iteration-1" / "experts" / "python"
        iter1_py_dir.mkdir(parents=True, exist_ok=True)

        iter1_state_py = {
            "dx_rating": {"stars": 4},
            "concerns": [{"id": "con-002"}],
            "recommendations": [{"id": "rec-002"}]
        }
        (iter1_py_dir / "state.json").write_text(json.dumps(iter1_state_py))

        # Set up iteration 2 (new structure: experts/{expert}/state.json)
        iter2_ts_dir = self.workspace / "iteration-2" / "experts" / "typescript"
        iter2_ts_dir.mkdir(parents=True, exist_ok=True)

        iter2_state_ts = {
            "dx_rating": {"stars": 4},
            "concerns": [],
            "recommendations": [{"id": "rec-001"}, {"id": "rec-003"}]
        }
        (iter2_ts_dir / "state.json").write_text(json.dumps(iter2_state_ts))

        iter2_py_dir = self.workspace / "iteration-2" / "experts" / "python"
        iter2_py_dir.mkdir(parents=True, exist_ok=True)

        iter2_state_py = {
            "dx_rating": {"stars": 5},
            "concerns": [],
            "recommendations": [{"id": "rec-002"}]
        }
        (iter2_py_dir / "state.json").write_text(json.dumps(iter2_state_py))

        # Record convergence
        self.state_manager.record_iteration_summary(
            iteration=1,
            convergence_percent=40,
            agreement_breakdown={"high": 1, "partial": 1, "low": 1},
            expert_summaries={}
        )

        self.state_manager.record_iteration_summary(
            iteration=2,
            convergence_percent=65,
            agreement_breakdown={"high": 2, "partial": 1, "low": 0},
            expert_summaries={}
        )

        # Generate full diff
        diff = generate_iteration_diff(
            workspace=self.workspace,
            expert_name="typescript",
            current_iteration=2,
            state_manager=self.state_manager
        )

        # Verify all sections present
        assert "own_review_changes" in diff
        assert "peer_changes" in diff
        assert "user_feedback" in diff
        assert "convergence_change" in diff

        # Verify own review changes
        assert diff["own_review_changes"]["dx_rating_previous"] == 3
        assert diff["own_review_changes"]["dx_rating_current"] == 4

        # Verify peer changes (python)
        assert "python" in diff["peer_changes"]
        assert diff["peer_changes"]["python"]["dx_rating"] == 5

        # Verify convergence
        assert diff["convergence_change"]["from"] == 40
        assert diff["convergence_change"]["to"] == 65
        assert diff["convergence_change"]["delta"] == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
