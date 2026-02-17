"""
Comprehensive unit tests for analysis/iteration_diff.py

Tests iteration-to-iteration diff generation:
- Main function: generate_iteration_diff()
- Helper functions: _diff_own_review(), _diff_peer_reviews(), _diff_user_answers(), _diff_convergence()
- Edge cases: iteration 1 (no diff), missing files, empty data
- Different change types: added/removed/updated concerns, rating changes
- Convergence metric diffs
- Formatting: format_diff_summary()

Target: 85%+ coverage
"""
import json
import pytest
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from analysis.iteration_diff import (
    generate_iteration_diff,
    format_diff_summary,
    _diff_own_review,
    _diff_peer_reviews,
    _diff_user_answers,
    _diff_convergence
)
from state.manager import StateManager, WorkspaceState


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace directory for tests."""
    ws = tmp_path / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture
def create_expert_state():
    """Factory to create expert state JSON data."""
    def factory(
        dx_rating: int = 3,
        concerns: list = None,
        recommendations: list = None
    ):
        return {
            "dx_rating": {"stars": dx_rating},
            "concerns": concerns or [],
            "recommendations": recommendations or []
        }
    return factory


@pytest.fixture
def create_questions_data():
    """Factory to create questions.json data."""
    def factory(questions: list):
        return {"questions": questions}
    return factory


class TestGenerateIterationDiff:
    """Test main generate_iteration_diff function."""

    @pytest.mark.high
    def test_iteration_1_returns_empty(self, workspace):
        """Test that iteration 1 returns empty dict (no diff)."""
        result = generate_iteration_diff(workspace, "typescript", 1)

        assert result == {}

    @pytest.mark.high
    def test_iteration_2_structure(self, workspace, create_expert_state):
        """Test that iteration 2+ returns proper structure."""
        # Setup: Create iteration-1 expert state
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state_file = iter1_dir / "state-typescript.json"
        state_file.write_text(json.dumps(create_expert_state()))

        result = generate_iteration_diff(workspace, "typescript", 2)

        assert "own_review_changes" in result
        assert "peer_changes" in result
        assert "user_feedback" in result
        assert "convergence_change" in result

    @pytest.mark.high
    def test_all_components_integrated(self, workspace, create_expert_state, create_questions_data):
        """Test all diff components work together."""
        # Setup iteration 1
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        # Own expert state
        state_file = iter1_dir / "state-typescript.json"
        state_file.write_text(json.dumps(create_expert_state(
            dx_rating=3,
            concerns=[{"title": "Concern 1"}],
            recommendations=[{"title": "Rec 1"}]
        )))

        # Peer expert state
        peer_file = iter1_dir / "state-python.json"
        peer_file.write_text(json.dumps(create_expert_state(
            dx_rating=4,
            concerns=[{"title": "Python concern"}]
        )))

        # Questions
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.write_text(json.dumps(create_questions_data([
            {"question": "Q1?", "asked_by": ["typescript"], "answer": "A1"},
            {"question": "Q2?", "asked_by": ["python"], "answer": None}
        ])))

        # Setup iteration 2
        iter2_dir = workspace / "iteration-2" / "experts"
        iter2_dir.mkdir(parents=True, exist_ok=True)

        state_file2 = iter2_dir / "state-typescript.json"
        state_file2.write_text(json.dumps(create_expert_state(
            dx_rating=4,
            concerns=[],
            recommendations=[{"title": "Rec 1"}, {"title": "Rec 2"}]
        )))

        peer_file2 = iter2_dir / "state-python.json"
        peer_file2.write_text(json.dumps(create_expert_state(
            dx_rating=5,
            concerns=[]
        )))

        result = generate_iteration_diff(workspace, "typescript", 2)

        # Check own review
        assert result["own_review_changes"]["dx_rating_delta"] == 1
        assert result["own_review_changes"]["concerns_count_delta"] == -1
        assert result["own_review_changes"]["recommendations_count_delta"] == 1

        # Check peer changes
        assert "python" in result["peer_changes"]
        assert result["peer_changes"]["python"]["dx_rating"] == 5

        # Check user feedback
        assert result["user_feedback"]["questions_answered"] == 1
        assert result["user_feedback"]["your_questions_answered"] == 1

    @pytest.mark.medium
    def test_with_state_manager(self, workspace, create_expert_state):
        """Test with provided StateManager instance."""
        # Setup iteration 1
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state_file = iter1_dir / "state-typescript.json"
        state_file.write_text(json.dumps(create_expert_state()))

        # Create state manager with iteration history
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 60},
            {"iteration": 2, "convergence_percent": 75}
        ]
        state_manager.create(state)

        result = generate_iteration_diff(workspace, "typescript", 2, state_manager)

        assert "convergence_change" in result
        assert result["convergence_change"]["from"] == 60
        assert result["convergence_change"]["to"] == 75
        assert result["convergence_change"]["delta"] == 15

    @pytest.mark.medium
    def test_missing_previous_iteration(self, workspace):
        """Test when previous iteration files don't exist."""
        result = generate_iteration_diff(workspace, "typescript", 2)

        # Should still return structure but with empty/error values
        assert "own_review_changes" in result
        assert "peer_changes" in result
        assert "user_feedback" in result


class TestDiffOwnReview:
    """Test _diff_own_review helper function."""

    @pytest.mark.high
    def test_basic_diff(self, workspace, create_expert_state):
        """Test basic diff between two iterations."""
        # Setup iteration 1
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(
            dx_rating=3,
            concerns=[{"title": "C1"}, {"title": "C2"}],
            recommendations=[{"title": "R1"}]
        )))

        # Setup iteration 2
        iter2_dir = workspace / "iteration-2" / "experts"
        iter2_dir.mkdir(parents=True, exist_ok=True)

        state2 = iter2_dir / "state-typescript.json"
        state2.write_text(json.dumps(create_expert_state(
            dx_rating=4,
            concerns=[{"title": "C1"}],
            recommendations=[{"title": "R1"}, {"title": "R2"}, {"title": "R3"}]
        )))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_previous"] == 3
        assert result["dx_rating_current"] == 4
        assert result["dx_rating_delta"] == 1
        assert result["concerns_count_previous"] == 2
        assert result["concerns_count_current"] == 1
        assert result["concerns_count_delta"] == -1
        assert result["recommendations_count_previous"] == 1
        assert result["recommendations_count_current"] == 3
        assert result["recommendations_count_delta"] == 2

    @pytest.mark.high
    def test_top_concerns_extraction(self, workspace, create_expert_state):
        """Test extraction of top 3 concerns."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(
            concerns=[
                {"title": "First Concern"},
                {"title": "Second Concern"},
                {"title": "Third Concern"},
                {"title": "Fourth Concern"}
            ]
        )))

        result = _diff_own_review(workspace, "typescript", 1)

        assert len(result["top_concerns_previous"]) == 3
        assert result["top_concerns_previous"][0] == "First Concern"
        assert result["top_concerns_previous"][1] == "Second Concern"
        assert result["top_concerns_previous"][2] == "Third Concern"

    @pytest.mark.high
    def test_missing_previous_state(self, workspace):
        """Test when previous state file doesn't exist."""
        result = _diff_own_review(workspace, "typescript", 1)

        assert result == {}

    @pytest.mark.high
    def test_missing_current_state(self, workspace, create_expert_state):
        """Test when current iteration state doesn't exist yet."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(
            dx_rating=3,
            concerns=[{"title": "C1"}],
            recommendations=[{"title": "R1"}]
        )))

        # No iteration 2 created
        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_previous"] == 3
        assert result["dx_rating_current"] == 0
        assert result["dx_rating_delta"] == -3
        assert result["concerns_count_current"] == 0
        assert result["recommendations_count_current"] == 0

    @pytest.mark.medium
    def test_missing_dx_rating_field(self, workspace):
        """Test when dx_rating field is missing."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps({
            "concerns": [],
            "recommendations": []
        }))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_previous"] == 0
        assert result["dx_rating_current"] == 0

    @pytest.mark.medium
    def test_missing_stars_in_dx_rating(self, workspace):
        """Test when stars key is missing in dx_rating."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps({
            "dx_rating": {},
            "concerns": [],
            "recommendations": []
        }))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_previous"] == 0

    @pytest.mark.medium
    def test_concern_without_title(self, workspace):
        """Test concerns without title field use 'Unknown'."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "concerns": [
                {"description": "Missing title"},
                {"title": "Has Title"}
            ],
            "recommendations": []
        }))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["top_concerns_previous"][0] == "Unknown"
        assert result["top_concerns_previous"][1] == "Has Title"

    @pytest.mark.medium
    def test_invalid_json_returns_error(self, workspace):
        """Test invalid JSON file returns error dict."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text("{ invalid json }")

        result = _diff_own_review(workspace, "typescript", 1)

        assert "error" in result
        assert isinstance(result["error"], str)

    @pytest.mark.medium
    def test_no_concerns(self, workspace, create_expert_state):
        """Test when there are no concerns."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(
            dx_rating=5,
            concerns=[],
            recommendations=[]
        )))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["concerns_count_previous"] == 0
        assert result["top_concerns_previous"] == []

    @pytest.mark.medium
    def test_rating_decrease(self, workspace, create_expert_state):
        """Test when rating decreases between iterations."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(dx_rating=5)))

        iter2_dir = workspace / "iteration-2" / "experts"
        iter2_dir.mkdir(parents=True, exist_ok=True)
        state2 = iter2_dir / "state-typescript.json"
        state2.write_text(json.dumps(create_expert_state(dx_rating=2)))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_delta"] == -3

    @pytest.mark.medium
    def test_current_state_invalid_json(self, workspace, create_expert_state):
        """Test when current iteration state file has invalid JSON."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)
        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state(
            dx_rating=3,
            concerns=[{"title": "C1"}],
            recommendations=[{"title": "R1"}]
        )))

        # Create iteration 2 with invalid JSON
        iter2_dir = workspace / "iteration-2" / "experts"
        iter2_dir.mkdir(parents=True, exist_ok=True)
        state2 = iter2_dir / "state-typescript.json"
        state2.write_text("{ invalid json }")

        # Should handle gracefully - exception is caught and treated as no current data
        result = _diff_own_review(workspace, "typescript", 1)

        assert result["dx_rating_previous"] == 3
        assert result["dx_rating_current"] == 0  # Current treated as missing
        assert result["concerns_count_previous"] == 1
        assert result["concerns_count_current"] == 0


class TestDiffPeerReviews:
    """Test _diff_peer_reviews helper function."""

    @pytest.mark.high
    def test_single_peer(self, workspace, create_expert_state):
        """Test diff with single peer expert."""
        iter_dir = workspace / "iteration-2" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # Own expert (should be skipped)
        own_file = iter_dir / "state-typescript.json"
        own_file.write_text(json.dumps(create_expert_state(dx_rating=4)))

        # Peer expert
        peer_file = iter_dir / "state-python.json"
        peer_file.write_text(json.dumps(create_expert_state(
            dx_rating=3,
            concerns=[{"title": "Python concern"}],
            recommendations=[{"title": "Python rec"}]
        )))

        result = _diff_peer_reviews(workspace, "typescript", 2)

        assert "typescript" not in result  # Own review excluded
        assert "python" in result
        assert result["python"]["dx_rating"] == 3
        assert result["python"]["concerns_count"] == 1
        assert result["python"]["recommendations_count"] == 1
        assert result["python"]["top_concerns"] == ["Python concern"]

    @pytest.mark.high
    def test_multiple_peers(self, workspace, create_expert_state):
        """Test diff with multiple peer experts."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # Own expert
        own_file = iter_dir / "state-typescript.json"
        own_file.write_text(json.dumps(create_expert_state()))

        # Peer 1
        peer1 = iter_dir / "state-python.json"
        peer1.write_text(json.dumps(create_expert_state(
            dx_rating=4,
            concerns=[{"title": "C1"}]
        )))

        # Peer 2
        peer2 = iter_dir / "state-security.json"
        peer2.write_text(json.dumps(create_expert_state(
            dx_rating=2,
            concerns=[{"title": "S1"}, {"title": "S2"}]
        )))

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert len(result) == 2
        assert "python" in result
        assert "security" in result
        assert result["python"]["dx_rating"] == 4
        assert result["security"]["dx_rating"] == 2

    @pytest.mark.high
    def test_no_peers(self, workspace, create_expert_state):
        """Test when only own expert exists."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        own_file = iter_dir / "state-typescript.json"
        own_file.write_text(json.dumps(create_expert_state()))

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert result == {}

    @pytest.mark.high
    def test_missing_iteration_dir(self, workspace):
        """Test when iteration directory doesn't exist."""
        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert result == {}

    @pytest.mark.medium
    def test_peer_top_3_concerns(self, workspace, create_expert_state):
        """Test peer's top 3 concerns are extracted."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        peer_file = iter_dir / "state-python.json"
        peer_file.write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "concerns": [
                {"title": "C1"},
                {"title": "C2"},
                {"title": "C3"},
                {"title": "C4"},
                {"title": "C5"}
            ],
            "recommendations": []
        }))

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert len(result["python"]["top_concerns"]) == 3
        assert result["python"]["top_concerns"] == ["C1", "C2", "C3"]

    @pytest.mark.medium
    def test_peer_no_concerns(self, workspace, create_expert_state):
        """Test peer with no concerns."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        peer_file = iter_dir / "state-python.json"
        peer_file.write_text(json.dumps(create_expert_state(
            dx_rating=5,
            concerns=[]
        )))

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert result["python"]["top_concerns"] == []

    @pytest.mark.medium
    def test_peer_invalid_json_skipped(self, workspace, create_expert_state):
        """Test that peers with invalid JSON are skipped."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        # Valid peer
        peer1 = iter_dir / "state-python.json"
        peer1.write_text(json.dumps(create_expert_state(dx_rating=4)))

        # Invalid peer
        peer2 = iter_dir / "state-security.json"
        peer2.write_text("{ invalid }")

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert "python" in result
        assert "security" not in result

    @pytest.mark.medium
    def test_peer_missing_concerns_field(self, workspace):
        """Test peer state without concerns field."""
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        peer_file = iter_dir / "state-python.json"
        peer_file.write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "recommendations": []
        }))

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert result["python"]["concerns_count"] == 0
        assert result["python"]["top_concerns"] == []

    @pytest.mark.medium
    def test_general_exception_with_mock(self, workspace, create_expert_state, monkeypatch):
        """Test general exception handling returns error dict."""
        # Create a valid setup
        iter_dir = workspace / "iteration-1" / "experts"
        iter_dir.mkdir(parents=True, exist_ok=True)

        peer_file = iter_dir / "state-python.json"
        peer_file.write_text(json.dumps(create_expert_state()))

        # Mock Path.glob to raise an exception
        def mock_glob_error(self, pattern):
            raise PermissionError("Mock permission error")

        monkeypatch.setattr(Path, "glob", mock_glob_error)

        result = _diff_peer_reviews(workspace, "typescript", 1)

        assert "error" in result
        assert isinstance(result["error"], str)


class TestDiffUserAnswers:
    """Test _diff_user_answers helper function."""

    @pytest.mark.high
    def test_all_questions_answered(self, workspace, create_questions_data):
        """Test when all questions are answered."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps(create_questions_data([
            {"question": "Q1?", "asked_by": ["typescript"], "answer": "A1"},
            {"question": "Q2?", "asked_by": ["python"], "answer": "A2"},
            {"question": "Q3?", "asked_by": ["typescript", "python"], "answer": "A3"}
        ])))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 3
        assert result["questions_answered"] == 3
        assert result["your_questions_answered"] == 2  # Q1 and Q3

    @pytest.mark.high
    def test_some_questions_unanswered(self, workspace, create_questions_data):
        """Test when some questions are unanswered."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps(create_questions_data([
            {"question": "Q1?", "asked_by": ["typescript"], "answer": "A1"},
            {"question": "Q2?", "asked_by": ["python"], "answer": None},
            {"question": "Q3?", "asked_by": ["typescript"], "answer": None}
        ])))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 3
        assert result["questions_answered"] == 1
        assert result["your_questions_answered"] == 1  # Only Q1

    @pytest.mark.high
    def test_no_questions(self, workspace, create_questions_data):
        """Test when there are no questions."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps(create_questions_data([])))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 0
        assert result["questions_answered"] == 0
        assert result["your_questions_answered"] == 0

    @pytest.mark.high
    def test_missing_questions_file(self, workspace):
        """Test when questions.json doesn't exist."""
        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 0
        assert result["questions_answered"] == 0
        assert result["your_questions_answered"] == 0

    @pytest.mark.medium
    def test_expert_not_in_asked_by(self, workspace, create_questions_data):
        """Test when expert didn't ask any questions."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps(create_questions_data([
            {"question": "Q1?", "asked_by": ["python"], "answer": "A1"},
            {"question": "Q2?", "asked_by": ["security"], "answer": "A2"}
        ])))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 2
        assert result["questions_answered"] == 2
        assert result["your_questions_answered"] == 0

    @pytest.mark.medium
    def test_missing_asked_by_field(self, workspace, create_questions_data):
        """Test when asked_by field is missing."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps({
            "questions": [
                {"question": "Q1?", "answer": "A1"},
                {"question": "Q2?", "answer": None}
            ]
        }))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_total"] == 2
        assert result["questions_answered"] == 1
        assert result["your_questions_answered"] == 0

    @pytest.mark.medium
    def test_answer_field_missing_treated_as_unanswered(self, workspace, create_questions_data):
        """Test when answer field is missing (treated as None/unanswered)."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps({
            "questions": [
                {"question": "Q1?", "asked_by": ["typescript"], "answer": "A1"},
                {"question": "Q2?", "asked_by": ["typescript"]}  # No answer field
            ]
        }))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_answered"] == 1
        assert result["your_questions_answered"] == 1

    @pytest.mark.medium
    def test_invalid_json_returns_error(self, workspace):
        """Test invalid JSON returns error dict."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)
        questions_file.write_text("{ invalid json }")

        result = _diff_user_answers(workspace, "typescript", 1)

        assert "error" in result

    @pytest.mark.medium
    def test_empty_answer_string_counts_as_answered(self, workspace, create_questions_data):
        """Test that empty string answer counts as answered."""
        questions_file = workspace / "iteration-1" / "questions.json"
        questions_file.parent.mkdir(parents=True, exist_ok=True)

        questions_file.write_text(json.dumps(create_questions_data([
            {"question": "Q1?", "asked_by": ["typescript"], "answer": ""},
            {"question": "Q2?", "asked_by": ["typescript"], "answer": None}
        ])))

        result = _diff_user_answers(workspace, "typescript", 1)

        assert result["questions_answered"] == 1  # Empty string counts
        assert result["your_questions_answered"] == 1


class TestDiffConvergence:
    """Test _diff_convergence helper function."""

    @pytest.mark.high
    def test_convergence_increase(self, workspace):
        """Test when convergence increases between iterations."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 60},
            {"iteration": 2, "convergence_percent": 75}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result["from"] == 60
        assert result["to"] == 75
        assert result["delta"] == 15
        assert result["trending_up"] is True

    @pytest.mark.high
    def test_convergence_decrease(self, workspace):
        """Test when convergence decreases between iterations."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 80},
            {"iteration": 2, "convergence_percent": 65}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result["from"] == 80
        assert result["to"] == 65
        assert result["delta"] == -15
        assert result["trending_up"] is False

    @pytest.mark.high
    def test_no_change_in_convergence(self, workspace):
        """Test when convergence stays the same."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 70},
            {"iteration": 2, "convergence_percent": 70}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result["delta"] == 0
        assert result["trending_up"] is False

    @pytest.mark.high
    def test_no_state_manager_creates_one(self, workspace):
        """Test that function creates StateManager if not provided."""
        # Create state without providing manager
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 50},
            {"iteration": 2, "convergence_percent": 70}
        ]
        state_manager.create(state)

        # Call without state_manager parameter
        result = _diff_convergence(workspace, 1, 2, None)

        assert result["from"] == 50
        assert result["to"] == 70
        assert result["delta"] == 20

    @pytest.mark.medium
    def test_missing_iteration_history(self, workspace):
        """Test when iteration_history is empty."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result == {}

    @pytest.mark.medium
    def test_missing_previous_iteration_summary(self, workspace):
        """Test when previous iteration is not in history."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=3
        )
        state.iteration_history = [
            {"iteration": 2, "convergence_percent": 60},
            {"iteration": 3, "convergence_percent": 75}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result == {}

    @pytest.mark.medium
    def test_missing_current_iteration_summary(self, workspace):
        """Test when current iteration is not in history."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 60}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result == {}

    @pytest.mark.medium
    def test_convergence_percent_zero(self, workspace):
        """Test with zero convergence values."""
        state_manager = StateManager(workspace)
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        state.iteration_history = [
            {"iteration": 1, "convergence_percent": 0},
            {"iteration": 2, "convergence_percent": 0}
        ]
        state_manager.create(state)

        result = _diff_convergence(workspace, 1, 2, state_manager)

        assert result["from"] == 0
        assert result["to"] == 0
        assert result["delta"] == 0

    @pytest.mark.medium
    def test_exception_handling(self, workspace):
        """Test exception handling returns error dict."""
        # Don't create any state - should cause an error
        result = _diff_convergence(workspace, 1, 2, None)

        assert "error" in result


class TestFormatDiffSummary:
    """Test format_diff_summary formatting function."""

    @pytest.mark.high
    def test_empty_diff(self):
        """Test formatting empty diff (iteration 1)."""
        result = format_diff_summary({}, "typescript")

        assert "No iteration diff available" in result
        assert "iteration 1" in result

    @pytest.mark.high
    def test_own_review_changes(self):
        """Test formatting own review changes."""
        diff = {
            "own_review_changes": {
                "dx_rating_previous": 3,
                "concerns_count_previous": 5,
                "recommendations_count_previous": 2
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "typescript" in result
        assert "Your Previous Review" in result
        assert "3/5 stars" in result
        assert "5" in result  # Concerns count
        assert "2" in result  # Recommendations count

    @pytest.mark.high
    def test_convergence_trending_up(self):
        """Test formatting convergence trending upward."""
        diff = {
            "convergence_change": {
                "from": 60,
                "to": 75,
                "delta": 15,
                "trending_up": True
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "Convergence Progress" in result
        assert "60%" in result
        assert "75%" in result
        assert "+15%" in result
        assert "Trending upward" in result or "✅" in result

    @pytest.mark.high
    def test_convergence_not_improving(self):
        """Test formatting convergence not improving."""
        diff = {
            "convergence_change": {
                "from": 70,
                "to": 65,
                "delta": -5,
                "trending_up": False
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "65%" in result
        assert "Not improving" in result or "⚠️" in result

    @pytest.mark.high
    def test_user_feedback_with_answers(self):
        """Test formatting user feedback with answered questions."""
        diff = {
            "user_feedback": {
                "questions_total": 10,
                "questions_answered": 7,
                "your_questions_answered": 3
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "User Engagement" in result
        assert "7/10" in result
        assert "3" in result
        assert "YOUR questions" in result

    @pytest.mark.high
    def test_user_feedback_no_personal_answers(self):
        """Test formatting when no personal questions answered."""
        diff = {
            "user_feedback": {
                "questions_total": 5,
                "questions_answered": 2,
                "your_questions_answered": 0
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "2/5" in result
        # Should not show personal questions line when zero
        lines = result.split("\n")
        your_questions_lines = [l for l in lines if "YOUR questions" in l]
        assert len(your_questions_lines) == 0

    @pytest.mark.high
    def test_peer_changes(self):
        """Test formatting peer expert changes."""
        diff = {
            "peer_changes": {
                "python": {
                    "dx_rating": 4,
                    "concerns_count": 3
                },
                "security": {
                    "dx_rating": 2,
                    "concerns_count": 7
                }
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "Peer Expert Updates" in result
        assert "python" in result
        assert "4/5 stars" in result
        assert "3 concerns" in result
        assert "security" in result
        assert "2/5 stars" in result
        assert "7 concerns" in result

    @pytest.mark.high
    def test_complete_diff(self):
        """Test formatting complete diff with all sections."""
        diff = {
            "own_review_changes": {
                "dx_rating_previous": 3,
                "concerns_count_previous": 5,
                "recommendations_count_previous": 2
            },
            "convergence_change": {
                "from": 60,
                "to": 75,
                "delta": 15,
                "trending_up": True
            },
            "user_feedback": {
                "questions_total": 10,
                "questions_answered": 7,
                "your_questions_answered": 3
            },
            "peer_changes": {
                "python": {
                    "dx_rating": 4,
                    "concerns_count": 2
                }
            }
        }

        result = format_diff_summary(diff, "typescript")

        assert "typescript" in result
        assert "Your Previous Review" in result
        assert "Convergence Progress" in result
        assert "User Engagement" in result
        assert "Peer Expert Updates" in result
        assert "=" in result  # Header separator

    @pytest.mark.medium
    def test_negative_delta_formatting(self):
        """Test that negative deltas don't show + sign."""
        diff = {
            "convergence_change": {
                "from": 80,
                "to": 70,
                "delta": -10,
                "trending_up": False
            }
        }

        result = format_diff_summary(diff, "typescript")

        # Should show -10%, not +-10%
        assert "-10%" in result
        assert "+-10%" not in result

    @pytest.mark.medium
    def test_missing_optional_fields(self):
        """Test formatting with missing optional fields in dicts."""
        diff = {
            "own_review_changes": {},
            "convergence_change": {},
            "user_feedback": {},
            "peer_changes": {}
        }

        result = format_diff_summary(diff, "typescript")

        # Should handle missing fields gracefully with N/A or 0
        assert "typescript" in result

    @pytest.mark.medium
    def test_empty_peer_changes(self):
        """Test with empty peer changes dict."""
        diff = {
            "peer_changes": {}
        }

        result = format_diff_summary(diff, "typescript")

        # Should not include peer section if empty
        assert "Peer Expert Updates" not in result

    @pytest.mark.medium
    def test_zero_delta_no_plus_sign(self):
        """Test that zero delta doesn't show + sign."""
        diff = {
            "convergence_change": {
                "from": 70,
                "to": 70,
                "delta": 0,
                "trending_up": False
            }
        }

        result = format_diff_summary(diff, "typescript")

        # Should show (0%), not (+0%)
        lines = [l for l in result.split("\n") if "70%" in l]
        assert len(lines) > 0
        # Check that the delta is shown as 0, not +0
        assert "(0%)" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.medium
    def test_very_large_iteration_number(self, workspace, create_expert_state):
        """Test with very large iteration numbers."""
        # Setup iteration 99
        iter99_dir = workspace / "iteration-99" / "experts"
        iter99_dir.mkdir(parents=True, exist_ok=True)

        state99 = iter99_dir / "state-typescript.json"
        state99.write_text(json.dumps(create_expert_state()))

        result = generate_iteration_diff(workspace, "typescript", 100)

        assert "own_review_changes" in result

    @pytest.mark.medium
    def test_special_characters_in_expert_name(self, workspace, create_expert_state):
        """Test with special characters in expert name."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        expert_name = "rust-systems"
        state1 = iter1_dir / f"state-{expert_name}.json"
        state1.write_text(json.dumps(create_expert_state()))

        result = _diff_own_review(workspace, expert_name, 1)

        assert "dx_rating_previous" in result

    @pytest.mark.medium
    def test_unicode_in_concern_titles(self, workspace):
        """Test Unicode characters in concern titles."""
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "concerns": [
                {"title": "问题 (Problem)"},
                {"title": "مشكلة (Issue)"},
                {"title": "🔥 Critical Bug"}
            ],
            "recommendations": []
        }), encoding='utf-8')

        result = _diff_own_review(workspace, "typescript", 1)

        assert "问题" in result["top_concerns_previous"][0]
        assert "مشكلة" in result["top_concerns_previous"][1]
        assert "🔥" in result["top_concerns_previous"][2]

    @pytest.mark.medium
    def test_very_long_concern_titles(self, workspace, create_expert_state):
        """Test very long concern titles."""
        long_title = "A" * 1000
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps({
            "dx_rating": {"stars": 3},
            "concerns": [{"title": long_title}],
            "recommendations": []
        }))

        result = _diff_own_review(workspace, "typescript", 1)

        assert result["top_concerns_previous"][0] == long_title

    @pytest.mark.medium
    def test_empty_string_expert_name(self, workspace):
        """Test with empty string expert name."""
        result = generate_iteration_diff(workspace, "", 2)

        # Should handle gracefully
        assert isinstance(result, dict)

    @pytest.mark.low
    def test_readonly_filesystem(self, workspace, create_expert_state):
        """Test behavior when filesystem is readonly (can only read)."""
        # Setup valid data
        iter1_dir = workspace / "iteration-1" / "experts"
        iter1_dir.mkdir(parents=True, exist_ok=True)

        state1 = iter1_dir / "state-typescript.json"
        state1.write_text(json.dumps(create_expert_state()))

        # Reading should work fine
        result = _diff_own_review(workspace, "typescript", 1)

        assert "dx_rating_previous" in result
