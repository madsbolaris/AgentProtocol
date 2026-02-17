"""
Unit tests for parsers/synthesized.py

Tests synthesized markdown parsing including:
- parse_convergence_from_summary() - Extract convergence metrics
- parse_questions_section() - Parse Open Questions
- parse_conflicts_section() - Parse conflicts
- parse_synthesized_markdown() - Main parser
- update_state_from_synthesized() - State file updates
- merge_all_questions() - Multi-iteration question merging
- generate_questions_json() - Questions file generation

Target coverage: 85%+
"""
import pytest
from pathlib import Path
import json
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from parsers import synthesized


class TestParseConvergenceFromSummary:
    """Test parse_convergence_from_summary function."""

    @pytest.mark.high
    def test_parse_basic_convergence(self):
        """Test parsing basic convergence percentage."""
        section = "**Convergence:** 75%"

        result = synthesized.parse_convergence_from_summary(section)

        assert result["convergence_percent"] == 75

    @pytest.mark.high
    def test_parse_consensus_yes(self):
        """Test parsing consensus reached as yes."""
        section = "**Consensus Reached:** yes"

        result = synthesized.parse_convergence_from_summary(section)

        assert result["consensus_reached"] is True

    @pytest.mark.high
    def test_parse_consensus_no(self):
        """Test parsing consensus reached as no."""
        section = "**Consensus Reached:** no"

        result = synthesized.parse_convergence_from_summary(section)

        assert result["consensus_reached"] is False

    @pytest.mark.medium
    def test_parse_convergence_trend(self):
        """Test parsing convergence trend."""
        section = "**Convergence Trend:** improving"

        result = synthesized.parse_convergence_from_summary(section)

        assert result["convergence_trend"] == "improving"

    @pytest.mark.medium
    def test_parse_all_metrics(self):
        """Test parsing all convergence metrics."""
        section = """
**Convergence:** 85%
**Consensus Reached:** yes
**Convergence Trend:** stable
**Metrics:**
- **High Agreement:** 10 recommendations
- **Partial Agreement:** 5 recommendations
- **Individual:** 2 recommendations
        """

        result = synthesized.parse_convergence_from_summary(section)

        assert result["convergence_percent"] == 85
        assert result["consensus_reached"] is True
        assert result["convergence_trend"] == "stable"
        assert result["high_agreement"] == 10
        assert result["partial_agreement"] == 5
        assert result["individual"] == 2

    @pytest.mark.medium
    def test_parse_empty_section(self):
        """Test parsing empty section returns defaults."""
        section = ""

        result = synthesized.parse_convergence_from_summary(section)

        assert result["convergence_percent"] == 0
        assert result["consensus_reached"] is False
        assert result["convergence_trend"] is None


class TestParseQuestionsSection:
    """Test parse_questions_section function."""

    @pytest.mark.high
    def test_parse_single_question(self):
        """Test parsing a single question with metadata."""
        section = """
### What is the recommended error handling approach?

**Asked by:** [Expert1, Expert2]
**Importance:** high
**Requires User Decision:** yes
**Context:** Experts disagree on whether to use exceptions or error codes.
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 1
        question = result[0]
        assert question["question"] == "What is the recommended error handling approach?"
        assert question["asked_by"] == ["Expert1", "Expert2"]
        assert question["importance"] == "high"
        assert question["requires_user_decision"] is True
        assert "Experts disagree" in question["context"]

    @pytest.mark.high
    def test_parse_multiple_questions(self):
        """Test parsing multiple questions."""
        section = """
### Question 1?

**Asked by:** [Expert1]
**Importance:** high
**Requires User Decision:** yes

### Question 2?

**Asked by:** [Expert2]
**Importance:** medium
**Requires User Decision:** no
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 2
        assert result[0]["question"] == "Question 1?"
        assert result[1]["question"] == "Question 2?"

    @pytest.mark.medium
    def test_parse_question_with_references(self):
        """Test parsing question with references."""
        section = """
### How should we handle caching?

**Asked by:** [Expert1]
**Importance:** medium
**Requires User Decision:** no
**Context:** Performance concerns.
**References:**
- **Expert1:** `cache.py` - suggested LRU cache
- **Expert2:** `storage.py` - mentioned Redis option
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 1
        question = result[0]
        assert len(question["references"]) == 2
        assert question["references"][0]["expert"] == "Expert1"
        assert question["references"][0]["file"] == "cache.py"
        assert question["references"][0]["excerpt"] == "suggested LRU cache"

    @pytest.mark.medium
    def test_parse_question_defaults(self):
        """Test parsing question with minimal metadata uses defaults."""
        section = """
### Should we add logging?

**Asked by:** [Expert1]
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 1
        question = result[0]
        assert question["importance"] == "medium"  # default
        # Note: requires_user_decision is None when not specified, not False
        assert question["requires_user_decision"] in (False, None)  # default when not specified
        assert question["context"] == ""  # empty if not provided
        assert question["references"] == []

    @pytest.mark.medium
    def test_question_id_generation(self):
        """Test question ID generation from question text."""
        section = """
### What is the best approach for error handling?

**Asked by:** [Expert1]
**Importance:** high
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 1
        question = result[0]
        # Should be slugified and truncated to 50 chars
        assert question["id"] == "what-is-the-best-approach-for-error-handling"

    @pytest.mark.medium
    def test_parse_empty_section(self):
        """Test parsing empty section returns empty list."""
        section = ""

        result = synthesized.parse_questions_section(section)

        assert result == []

    @pytest.mark.medium
    def test_parse_question_case_insensitive(self):
        """Test parsing is case insensitive for metadata."""
        section = """
### Test Question?

**Asked by:** [Expert1]
**Importance:** HIGH
**Requires User Decision:** YES
**Convergence Trend:** {IMPROVING}
"""

        result = synthesized.parse_questions_section(section)

        assert len(result) == 1
        question = result[0]
        assert question["importance"] == "high"
        assert question["requires_user_decision"] is True


class TestParseConflictsSection:
    """Test parse_conflicts_section function."""

    @pytest.mark.high
    def test_parse_single_conflict(self):
        """Test parsing a single conflict."""
        section = """
### ⚠️ CONFLICT: Synchronous vs Async API

**The Disagreement:**
Experts disagree on whether the API should be sync or async.

**Position A** (Expert1, Expert2):
Use synchronous API for simplicity.

**Position B** (Expert3):
Use async API for better performance.
"""

        result = synthesized.parse_conflicts_section(section)

        assert len(result) == 1
        conflict = result[0]
        assert "Synchronous vs Async API" in conflict["question"]
        assert conflict["importance"] == "high"
        assert conflict["requires_user_decision"] is True
        assert conflict["asked_by"] == ["Expert1", "Expert2", "Expert3"]
        assert conflict["conflict_details"]["experts_position_a"] == ["Expert1", "Expert2"]
        assert conflict["conflict_details"]["experts_position_b"] == ["Expert3"]

    @pytest.mark.high
    def test_parse_multiple_conflicts(self):
        """Test parsing multiple conflicts."""
        section = """
### ⚠️ CONFLICT: Database Choice

**Position A** (Expert1):
Use PostgreSQL.

**Position B** (Expert2):
Use MongoDB.

### ⚠️ CONFLICT: Testing Framework

**Position A** (Expert3):
Use pytest.

**Position B** (Expert4):
Use unittest.
"""

        result = synthesized.parse_conflicts_section(section)

        assert len(result) == 2
        assert "Database Choice" in result[0]["question"]
        assert "Testing Framework" in result[1]["question"]

    @pytest.mark.medium
    def test_conflict_id_generation(self):
        """Test conflict ID generation."""
        section = """
### ⚠️ CONFLICT: Very Long Conflict Title That Should Be Truncated Properly

**Position A** (Expert1):
Position A details.

**Position B** (Expert2):
Position B details.
"""

        result = synthesized.parse_conflicts_section(section)

        assert len(result) == 1
        conflict = result[0]
        # Should start with "conflict-" and be truncated
        assert conflict["id"].startswith("conflict-")
        assert len(conflict["id"]) <= 50

    @pytest.mark.medium
    def test_conflict_context_extraction(self):
        """Test extracting context from disagreement section."""
        section = """
### ⚠️ CONFLICT: API Design

**The Disagreement:**
This is a critical disagreement about API design.
Multiple lines of context here.

**Position A** (Expert1):
Position A.

**Position B** (Expert2):
Position B.
"""

        result = synthesized.parse_conflicts_section(section)

        assert len(result) == 1
        conflict = result[0]
        assert "critical disagreement" in conflict["context"]
        assert "Multiple lines" in conflict["context"]

    @pytest.mark.medium
    def test_parse_empty_conflicts_section(self):
        """Test parsing empty conflicts section."""
        section = ""

        result = synthesized.parse_conflicts_section(section)

        assert result == []


class TestParseSynthesizedMarkdown:
    """Test parse_synthesized_markdown function."""

    @pytest.mark.high
    def test_parse_complete_markdown(self, tmp_path):
        """Test parsing complete synthesized markdown."""
        markdown_path = tmp_path / "synthesized.md"
        markdown_path.write_text("""
## Executive Summary

**Convergence:** 80%
**Consensus Reached:** yes
**Convergence Trend:** improving
**Metrics:**
- **High Agreement:** 5 recommendations
- **Partial Agreement:** 3 recommendations
- **Individual:** 1 recommendations

## Open Questions

### What testing framework should we use?

**Asked by:** [Expert1, Expert2]
**Importance:** high
**Requires User Decision:** yes
**Context:** Need to decide on testing approach.

## Conflicts to Resolve

### ⚠️ CONFLICT: Database Selection

**Position A** (Expert1):
Use PostgreSQL.

**Position B** (Expert2):
Use MongoDB.
""")

        result = synthesized.parse_synthesized_markdown(markdown_path)

        assert "convergence_data" in result
        assert "questions" in result
        assert result["convergence_data"]["convergence_percent"] == 80
        assert result["convergence_data"]["consensus_reached"] is True
        assert len(result["questions"]) == 2  # 1 question + 1 conflict

    @pytest.mark.medium
    def test_parse_markdown_sections_split(self, tmp_path):
        """Test that sections are correctly split."""
        markdown_path = tmp_path / "synthesized.md"
        markdown_path.write_text("""
## Executive Summary
Summary content here.

## Open Questions
Questions content here.

## Conflicts to Resolve
Conflicts content here.
""")

        result = synthesized.parse_synthesized_markdown(markdown_path)

        # Should parse all sections
        assert "convergence_data" in result
        assert "questions" in result

    @pytest.mark.medium
    def test_parse_markdown_minimal(self, tmp_path):
        """Test parsing markdown with minimal content."""
        markdown_path = tmp_path / "synthesized.md"
        markdown_path.write_text("""
## Executive Summary

No metrics here.
""")

        result = synthesized.parse_synthesized_markdown(markdown_path)

        # Should return defaults when sections are missing
        assert result["convergence_data"]["convergence_percent"] == 0
        assert result["questions"] == []


class TestUpdateStateFromSynthesized:
    """Test update_state_from_synthesized function."""

    @pytest.mark.high
    def test_update_state_new_file(self, tmp_path):
        """Test updating state when file doesn't exist."""
        state_path = tmp_path / "state.json"
        convergence_data = {
            "convergence_percent": 75,
            "consensus_reached": True,
            "convergence_trend": "improving",
            "high_agreement": 10,
            "partial_agreement": 5,
            "individual": 2
        }

        synthesized.update_state_from_synthesized(state_path, convergence_data, iteration=1)

        assert state_path.exists()
        with open(state_path) as f:
            state = json.load(f)
        assert state["iteration"] == 1
        assert state["convergence_percent"] == 75
        assert state["consensus_reached"] is True
        assert state["convergence_trend"] == "improving"

    @pytest.mark.high
    def test_update_state_existing_file(self, tmp_path):
        """Test updating state when file already exists."""
        state_path = tmp_path / "state.json"
        # Create existing state
        state_path.write_text(json.dumps({"iteration": 1, "some_field": "value"}))

        convergence_data = {
            "convergence_percent": 85,
            "consensus_reached": True,
            "convergence_trend": "stable",
            "high_agreement": 12,
            "partial_agreement": 3,
            "individual": 1
        }

        synthesized.update_state_from_synthesized(state_path, convergence_data, iteration=2)

        with open(state_path) as f:
            state = json.load(f)
        # Should update iteration and convergence data
        assert state["iteration"] == 2
        assert state["convergence_percent"] == 85
        # Should preserve existing fields
        assert state["some_field"] == "value"

    @pytest.mark.medium
    def test_update_state_no_trend(self, tmp_path):
        """Test updating state when convergence_trend is None."""
        state_path = tmp_path / "state.json"
        convergence_data = {
            "convergence_percent": 75,
            "consensus_reached": False,
            "convergence_trend": None,
            "high_agreement": 10,
            "partial_agreement": 5,
            "individual": 2
        }

        synthesized.update_state_from_synthesized(state_path, convergence_data, iteration=1)

        with open(state_path) as f:
            state = json.load(f)
        # Should not set convergence_trend if None
        assert "convergence_trend" not in state


class TestMergeAllQuestions:
    """Test merge_all_questions function."""

    @pytest.mark.high
    def test_merge_questions_single_iteration(self, tmp_path):
        """Test merging questions from a single iteration."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)

        # Create questions file
        questions_file = iter1 / "questions.json"
        questions_file.write_text(json.dumps({
            "iteration": 1,
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"},
                {"id": "q2", "question": "Question 2?", "importance": "medium"}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        assert len(result) == 2
        assert result[0]["id"] == "q1"
        assert result[0]["first_asked_iteration"] == 1

    @pytest.mark.high
    def test_merge_questions_multiple_iterations(self, tmp_path):
        """Test merging questions from multiple iterations."""
        workspace = tmp_path / "workspace"

        # Iteration 1
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)
        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"}
            ]
        }))

        # Iteration 2
        iter2 = workspace / "iteration-2"
        iter2.mkdir(parents=True)
        (iter2 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"},
                {"id": "q2", "question": "Question 2?", "importance": "medium"}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=2)

        assert len(result) == 2
        # q1 should be merged from both iterations
        q1 = next(q for q in result if q["id"] == "q1")
        assert q1["first_asked_iteration"] == 1
        assert set(q1["asked_in_iterations"]) == {1, 2}

    @pytest.mark.high
    def test_merge_skips_answered_questions(self, tmp_path):
        """Test that merge skips questions that were answered."""
        workspace = tmp_path / "workspace"

        # Iteration 1 with questions
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)
        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"},
                {"id": "q2", "question": "Question 2?", "importance": "medium"}
            ]
        }))

        # Iteration 1 with answers (q1 was answered)
        (iter1 / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "Question 1?", "answer": "Answer 1"}
            ]
        }))

        # Iteration 2 with questions
        iter2 = workspace / "iteration-2"
        iter2.mkdir(parents=True)
        (iter2 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"},
                {"id": "q2", "question": "Question 2?", "importance": "medium"}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=2)

        # Only q2 should be in results (q1 was answered)
        assert len(result) == 1
        assert result[0]["id"] == "q2"

    @pytest.mark.medium
    def test_merge_from_expert_questions(self, tmp_path):
        """Test merging questions from expert review files."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1" / "experts"
        iter1.mkdir(parents=True)

        # Create expert questions file
        (iter1 / "questions-expert1.json").write_text(json.dumps([
            {"id": "q1", "question": "Expert question?", "importance": "high"}
        ]))

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        assert len(result) == 1
        assert result[0]["id"] == "q1"

    @pytest.mark.medium
    def test_merge_sorts_by_importance(self, tmp_path):
        """Test that questions are sorted by importance."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)

        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Low priority", "importance": "low"},
                {"id": "q2", "question": "High priority", "importance": "high"},
                {"id": "q3", "question": "Medium priority", "importance": "medium"}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        # Should be sorted: high, medium, low
        assert result[0]["importance"] == "high"
        assert result[1]["importance"] == "medium"
        assert result[2]["importance"] == "low"


class TestGenerateQuestionsJson:
    """Test generate_questions_json function."""

    @pytest.mark.high
    def test_generate_questions_basic(self, tmp_path):
        """Test generating questions.json without merging."""
        output_path = tmp_path / "questions.json"
        questions = [
            {"id": "q1", "question": "Question 1?", "importance": "high"},
            {"id": "q2", "question": "Question 2?", "importance": "medium"}
        ]

        synthesized.generate_questions_json(questions, output_path, iteration=1)

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["iteration"] == 1
        assert len(data["questions"]) == 2
        assert "merged_from_iterations" not in data

    @pytest.mark.high
    def test_generate_questions_with_merge(self, tmp_path):
        """Test generating questions.json with merge_all=True."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)

        # Create previous iteration questions
        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Old question?", "importance": "high"}
            ]
        }))

        # Generate new questions with merge
        output_path = workspace / "iteration-2" / "questions.json"
        new_questions = [
            {"id": "q2", "question": "New question?", "importance": "medium"}
        ]

        synthesized.generate_questions_json(
            new_questions, output_path, iteration=2, workspace=workspace, merge_all=True
        )

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["iteration"] == 2
        assert len(data["questions"]) == 2  # q1 + q2
        assert data["merged_from_iterations"] == [1, 2]

    @pytest.mark.medium
    def test_generate_creates_parent_directories(self, tmp_path):
        """Test that generate creates parent directories."""
        output_path = tmp_path / "deep" / "nested" / "path" / "questions.json"
        questions = [{"id": "q1", "question": "Question?"}]

        synthesized.generate_questions_json(questions, output_path, iteration=1)

        assert output_path.exists()


class TestParseAndUpdate:
    """Test parse_and_update function."""

    @pytest.mark.high
    def test_parse_and_update_iteration_1(self, tmp_path):
        """Test parse_and_update for iteration 1."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)

        markdown_path = iter1 / "synthesized.md"
        markdown_path.write_text("""
## Executive Summary

**Convergence:** 75%
**Consensus Reached:** yes

## Open Questions

### What should we do?

**Asked by:** [Expert1]
**Importance:** high
**Requires User Decision:** yes
""")

        synthesized.parse_and_update(markdown_path, workspace, iteration=1, merge_all=True)

        # Check state.json
        state_path = workspace / "state.json"
        assert state_path.exists()
        with open(state_path) as f:
            state = json.load(f)
        assert state["iteration"] == 1
        assert state["convergence_percent"] == 75

        # Check questions.json
        questions_path = iter1 / "questions.json"
        assert questions_path.exists()
        with open(questions_path) as f:
            data = json.load(f)
        assert data["iteration"] == 1
        assert len(data["questions"]) == 1

    @pytest.mark.high
    def test_parse_and_update_iteration_2_merges(self, tmp_path):
        """Test parse_and_update for iteration 2 with merging."""
        workspace = tmp_path / "workspace"

        # Setup iteration 1
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)
        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Old question?", "importance": "high"}
            ]
        }))

        # Setup iteration 2
        iter2 = workspace / "iteration-2"
        iter2.mkdir(parents=True)
        markdown_path = iter2 / "synthesized.md"
        markdown_path.write_text("""
## Executive Summary

**Convergence:** 85%
**Consensus Reached:** yes

## Open Questions

### New question?

**Asked by:** [Expert1]
**Importance:** medium
**Requires User Decision:** no
""")

        synthesized.parse_and_update(markdown_path, workspace, iteration=2, merge_all=True)

        # Check questions.json includes both old and new
        questions_path = iter2 / "questions.json"
        assert questions_path.exists()
        with open(questions_path) as f:
            data = json.load(f)
        assert data["iteration"] == 2
        assert len(data["questions"]) == 2  # merged


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.medium
    def test_parse_malformed_convergence(self):
        """Test parsing malformed convergence metrics."""
        section = "**Convergence:** Not a number"

        result = synthesized.parse_convergence_from_summary(section)

        # Should return defaults on parse error
        assert result["convergence_percent"] == 0

    @pytest.mark.medium
    def test_parse_question_without_id(self):
        """Test parsing question without proper heading."""
        section = "This is not a proper question section"

        result = synthesized.parse_questions_section(section)

        # Should handle gracefully
        assert isinstance(result, list)

    @pytest.mark.medium
    def test_merge_questions_nonexistent_workspace(self, tmp_path):
        """Test merging from non-existent workspace."""
        workspace = tmp_path / "nonexistent"

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        # Should return empty list for non-existent workspace
        assert result == []

    @pytest.mark.medium
    def test_merge_expert_questions_without_id(self, tmp_path):
        """Test merging expert questions that don't have IDs."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        experts_dir = iter1 / "experts"
        experts_dir.mkdir(parents=True)

        # Create expert questions file with questions missing IDs
        questions_typescript = experts_dir / "questions-typescript.json"
        questions_typescript.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Valid question?", "importance": "high"},
                {"question": "No ID question?", "importance": "medium"},  # Missing ID
                {"id": "", "question": "Empty ID question?", "importance": "low"}  # Empty ID
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        # Only q1 should be included (questions without IDs are skipped)
        assert len(result) == 1
        assert result[0]["id"] == "q1"

    @pytest.mark.medium
    def test_merge_expert_questions_already_answered(self, tmp_path):
        """Test that expert questions that were answered are skipped."""
        workspace = tmp_path / "workspace"
        iter1 = workspace / "iteration-1"
        experts_dir = iter1 / "experts"
        experts_dir.mkdir(parents=True)

        # Create qa-answers showing q1 was answered
        qa_answers = iter1 / "qa-answers.json"
        qa_answers.write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "Question 1?", "answer": "Answer 1"}
            ]
        }))

        # Create expert questions file
        questions_typescript = experts_dir / "questions-typescript.json"
        questions_typescript.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high"},
                {"id": "q2", "question": "Question 2?", "importance": "medium"}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=1)

        # Only q2 should be included (q1 was already answered)
        assert len(result) == 1
        assert result[0]["id"] == "q2"

    @pytest.mark.medium
    def test_merge_synthesized_questions_merges_asked_by(self, tmp_path):
        """Test that asked_by lists are merged when same question appears in multiple iterations."""
        workspace = tmp_path / "workspace"

        # Iteration 1
        iter1 = workspace / "iteration-1"
        iter1.mkdir(parents=True)
        (iter1 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high", "asked_by": ["typescript", "python"]}
            ]
        }))

        # Iteration 2 - same question asked by different experts
        iter2 = workspace / "iteration-2"
        iter2.mkdir(parents=True)
        (iter2 / "questions.json").write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "Question 1?", "importance": "high", "asked_by": ["python", "rust"]}
            ]
        }))

        result = synthesized.merge_all_questions(workspace, current_iteration=2)

        # Should merge asked_by lists: typescript, python, rust (sorted, unique)
        assert len(result) == 1
        assert result[0]["id"] == "q1"
        assert set(result[0]["asked_by"]) == {"typescript", "python", "rust"}
        assert result[0]["asked_by"] == sorted(result[0]["asked_by"])  # Should be sorted

    @pytest.mark.medium
    def test_update_state_invalid_json(self, tmp_path):
        """Test updating state with corrupted JSON file."""
        state_path = tmp_path / "state.json"
        state_path.write_text("{ invalid json }")

        convergence_data = {
            "convergence_percent": 75,
            "consensus_reached": True,
            "convergence_trend": "improving",
            "high_agreement": 10,
            "partial_agreement": 5,
            "individual": 2
        }

        # Should raise JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            synthesized.update_state_from_synthesized(state_path, convergence_data, iteration=1)
