"""
Comprehensive tests for ui/deduplicate_questions.py

Tests question deduplication including:
- load_json() / save_json() - file I/O operations
- find_answered_questions() - finding previously answered questions
- fuzzy_similarity() - text similarity calculation
- is_duplicate_question() - duplicate detection with various thresholds
- deduplicate_questions() - complete deduplication workflow
- CLI main() function
- Edge cases and error handling

Target coverage: 90%+
"""
import pytest
import json
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from ui import deduplicate_questions


class TestLoadJson:
    """Test load_json function."""

    @pytest.mark.high
    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))

        result = deduplicate_questions.load_json(test_file)

        assert result == test_data

    @pytest.mark.medium
    def test_load_json_with_nested_structure(self, tmp_path):
        """Test loading JSON with nested structure."""
        test_file = tmp_path / "nested.json"
        test_data = {
            "answers": [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"}
            ]
        }
        test_file.write_text(json.dumps(test_data))

        result = deduplicate_questions.load_json(test_file)

        assert len(result["answers"]) == 2


class TestSaveJson:
    """Test save_json function."""

    @pytest.mark.high
    def test_save_json_basic(self, tmp_path):
        """Test saving JSON to file."""
        test_file = tmp_path / "output.json"
        test_data = {"key": "value"}

        deduplicate_questions.save_json(test_file, test_data)

        # Verify file was created
        assert test_file.exists()

        # Verify content
        loaded = json.loads(test_file.read_text())
        assert loaded == test_data

    @pytest.mark.medium
    def test_save_json_with_indent(self, tmp_path):
        """Test that JSON is saved with proper indentation."""
        test_file = tmp_path / "indented.json"
        test_data = {"key": "value", "nested": {"a": 1}}

        deduplicate_questions.save_json(test_file, test_data)

        # Check that file has indentation
        content = test_file.read_text()
        assert "  " in content  # Should have indentation


class TestFindAnsweredQuestions:
    """Test find_answered_questions function."""

    @pytest.mark.high
    def test_find_no_previous_iterations(self, tmp_path):
        """Test when no previous iterations exist."""
        result = deduplicate_questions.find_answered_questions(tmp_path, current_iteration=1)

        assert len(result) == 0

    @pytest.mark.high
    def test_find_answered_questions_single_iteration(self, tmp_path):
        """Test finding questions from single previous iteration."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)

        qa_data = {
            "answers": [
                {
                    "question_id": "q1",
                    "question": "What pattern to use?",
                    "answer": "Repository pattern"
                }
            ]
        }
        qa_file = iter1_dir / "qa-answers.json"
        qa_file.write_text(json.dumps(qa_data))

        result = deduplicate_questions.find_answered_questions(tmp_path, current_iteration=2)

        assert len(result) == 1
        assert "q1" in result
        assert result["q1"]["answer"] == "Repository pattern"
        assert result["q1"]["iteration"] == 1

    @pytest.mark.high
    def test_find_answered_questions_multiple_iterations(self, tmp_path):
        """Test finding questions from multiple iterations."""
        # Create iteration 1
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [{"question_id": "q1", "question": "Q1", "answer": "A1"}]
        }))

        # Create iteration 2
        iter2_dir = tmp_path / "iteration-2"
        iter2_dir.mkdir(parents=True)
        (iter2_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [{"question_id": "q2", "question": "Q2", "answer": "A2"}]
        }))

        result = deduplicate_questions.find_answered_questions(tmp_path, current_iteration=3)

        assert len(result) == 2
        assert "q1" in result
        assert "q2" in result
        assert result["q1"]["iteration"] == 1
        assert result["q2"]["iteration"] == 2

    @pytest.mark.medium
    def test_find_skips_missing_qa_files(self, tmp_path):
        """Test that missing QA files are skipped gracefully."""
        (tmp_path / "iteration-1").mkdir(parents=True)

        result = deduplicate_questions.find_answered_questions(tmp_path, current_iteration=2)

        assert len(result) == 0

    @pytest.mark.medium
    def test_find_handles_empty_answers(self, tmp_path):
        """Test handling of QA file with no answers."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({"answers": []}))

        result = deduplicate_questions.find_answered_questions(tmp_path, current_iteration=2)

        assert len(result) == 0


class TestFuzzySimilarity:
    """Test fuzzy_similarity function."""

    @pytest.mark.high
    def test_identical_strings(self):
        """Test similarity of identical strings."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What pattern should we use?",
            "What pattern should we use?"
        )

        assert similarity == 1.0

    @pytest.mark.high
    def test_case_insensitive(self):
        """Test that comparison is case-insensitive."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What Pattern Should We Use?",
            "what pattern should we use?"
        )

        assert similarity == 1.0

    @pytest.mark.high
    def test_similar_strings(self):
        """Test similarity of similar strings."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What pattern should we use?",
            "What pattern should be used?"
        )

        assert similarity > 0.8

    @pytest.mark.high
    def test_dissimilar_strings(self):
        """Test similarity of dissimilar strings."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What pattern should we use?",
            "How to implement error handling?"
        )

        assert similarity < 0.5

    @pytest.mark.medium
    def test_empty_strings(self):
        """Test similarity with empty strings."""
        similarity = deduplicate_questions.fuzzy_similarity("", "")

        assert similarity == 1.0

    @pytest.mark.medium
    def test_whitespace_differences(self):
        """Test similarity with whitespace differences."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What    pattern?",
            "What pattern?"
        )

        # Should be very similar despite whitespace
        assert similarity > 0.85

    @pytest.mark.low
    def test_punctuation_differences(self):
        """Test similarity with punctuation differences."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What pattern?",
            "What pattern"
        )

        assert similarity > 0.9


class TestIsDuplicateQuestion:
    """Test is_duplicate_question function."""

    @pytest.mark.high
    def test_exact_id_match(self):
        """Test exact question ID match."""
        new_question = {"id": "q1", "question": "Test question"}
        answered = {
            "q1": {"question": "Different text", "answer": "Answer"}
        }

        is_dup, dup_id = deduplicate_questions.is_duplicate_question(new_question, answered)

        assert is_dup is True
        assert dup_id == "q1"

    @pytest.mark.high
    def test_exact_text_match(self):
        """Test exact question text match."""
        new_question = {"id": "q2", "question": "What pattern to use?"}
        answered = {
            "q1": {"question": "What pattern to use?", "answer": "Repository"}
        }

        is_dup, dup_id = deduplicate_questions.is_duplicate_question(new_question, answered)

        assert is_dup is True
        assert dup_id == "q1"

    @pytest.mark.high
    def test_case_insensitive_text_match(self):
        """Test case-insensitive text matching."""
        new_question = {"id": "q2", "question": "WHAT PATTERN TO USE?"}
        answered = {
            "q1": {"question": "what pattern to use?", "answer": "Repository"}
        }

        is_dup, dup_id = deduplicate_questions.is_duplicate_question(new_question, answered)

        assert is_dup is True

    @pytest.mark.high
    def test_fuzzy_match_above_threshold(self):
        """Test fuzzy similarity match above threshold."""
        new_question = {"id": "q2", "question": "What pattern should we use?"}
        answered = {
            "q1": {"question": "What pattern should be used?", "answer": "Repository"}
        }

        is_dup, dup_id = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=0.85
        )

        assert is_dup is True

    @pytest.mark.high
    def test_no_match_below_threshold(self):
        """Test no match when below similarity threshold."""
        new_question = {"id": "q2", "question": "How to handle errors?"}
        answered = {
            "q1": {"question": "What pattern to use?", "answer": "Repository"}
        }

        is_dup, dup_id = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=0.85
        )

        assert is_dup is False
        assert dup_id is None

    @pytest.mark.high
    def test_custom_similarity_threshold(self):
        """Test custom similarity threshold."""
        new_question = {"id": "q2", "question": "What pattern?"}
        answered = {
            "q1": {"question": "Which pattern?", "answer": "Repository"}
        }

        # With high threshold, shouldn't match
        is_dup, _ = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=0.95
        )
        assert is_dup is False

        # With low threshold, should match
        is_dup, _ = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=0.60
        )
        assert is_dup is True

    @pytest.mark.medium
    def test_threshold_boundary_cases(self):
        """Test behavior at exact threshold boundary."""
        new_question = {"id": "q2", "question": "What design pattern?"}
        answered = {
            "q1": {"question": "Which design pattern?", "answer": "Singleton"}
        }

        # Calculate actual similarity
        similarity = deduplicate_questions.fuzzy_similarity(
            new_question["question"],
            answered["q1"]["question"]
        )

        # Test at exact threshold
        is_dup_at, _ = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=similarity
        )
        is_dup_above, _ = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=similarity - 0.01
        )
        is_dup_below, _ = deduplicate_questions.is_duplicate_question(
            new_question, answered, similarity_threshold=similarity + 0.01
        )

        assert is_dup_at is True  # Should match at exact threshold
        assert is_dup_above is True  # Should match below threshold
        assert is_dup_below is False  # Should not match above threshold


class TestDeduplicateQuestions:
    """Test main deduplicate_questions function."""

    @pytest.mark.high
    def test_deduplicate_with_no_previous_answers(self, tmp_path, capsys):
        """Test deduplication when no previous answers exist."""
        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "What pattern?"},
                {"id": "q2", "question": "How to test?"}
            ]
        }))

        stats = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=1
        )

        assert stats["total_questions"] == 2
        assert stats["duplicates_removed"] == 0
        assert stats["unique_questions"] == 2

        captured = capsys.readouterr()
        assert "No previously answered questions found" in captured.out

    @pytest.mark.high
    def test_deduplicate_removes_exact_duplicate(self, tmp_path, capsys):
        """Test that exact duplicates are removed."""
        # Create previous iteration with answered question
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "What pattern?", "answer": "Repository"}
            ]
        }))

        # Current iteration questions
        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "What pattern?"},  # Duplicate
                {"id": "q2", "question": "How to test?"}     # New
            ]
        }))

        stats = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2
        )

        assert stats["total_questions"] == 2
        assert stats["duplicates_removed"] == 1
        assert stats["unique_questions"] == 1

        # Verify file was updated
        updated = json.loads(questions_file.read_text())
        assert len(updated["questions"]) == 1
        assert updated["questions"][0]["id"] == "q2"

        # Verify report was saved
        report_file = questions_file.parent / "deduplication-report.json"
        assert report_file.exists()

    @pytest.mark.high
    def test_deduplicate_with_dry_run(self, tmp_path, capsys):
        """Test dry run mode doesn't modify files."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "What pattern?", "answer": "Repository"}
            ]
        }))

        questions_file = tmp_path / "questions.json"
        original_content = json.dumps({
            "questions": [
                {"id": "q1", "question": "What pattern?"},
                {"id": "q2", "question": "How to test?"}
            ]
        })
        questions_file.write_text(original_content)

        stats = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2,
            dry_run=True
        )

        # Stats should be computed
        assert stats["duplicates_removed"] == 1

        # But file should not be modified
        assert questions_file.read_text() == original_content

        # And no report should be saved
        report_file = questions_file.parent / "deduplication-report.json"
        assert not report_file.exists()

    @pytest.mark.high
    def test_deduplicate_with_custom_threshold(self, tmp_path):
        """Test deduplication with custom similarity threshold."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "What pattern should we use?", "answer": "Repository"}
            ]
        }))

        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q2", "question": "Which pattern should be used?"}  # Similar but not identical
            ]
        }))

        # With high threshold, should not match
        stats_high = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2,
            similarity_threshold=0.99,
            dry_run=True
        )

        # Reset file
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q2", "question": "Which pattern should be used?"}
            ]
        }))

        # With low threshold, should match
        stats_low = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2,
            similarity_threshold=0.7,
            dry_run=True
        )

        assert stats_high["duplicates_removed"] == 0
        assert stats_low["duplicates_removed"] == 1

    @pytest.mark.medium
    def test_deduplicate_report_structure(self, tmp_path):
        """Test the structure of deduplication report."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "What pattern?", "answer": "Repository"}
            ]
        }))

        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "What pattern?"},
                {"id": "q2", "question": "How to test?"}
            ]
        }))

        deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2
        )

        report_file = questions_file.parent / "deduplication-report.json"
        report = json.loads(report_file.read_text())

        # Verify report structure
        assert "total_questions" in report
        assert "duplicates_removed" in report
        assert "unique_questions" in report
        assert "duplicates" in report

        # Verify duplicate info
        assert len(report["duplicates"]) == 1
        dup = report["duplicates"][0]
        assert "question" in dup
        assert "duplicate_of" in dup
        assert "answered_iteration" in dup
        assert "answer" in dup

    @pytest.mark.medium
    def test_deduplicate_multiple_duplicates(self, tmp_path):
        """Test deduplication with multiple duplicates."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": [
                {"question_id": "q1", "question": "What is the best pattern?", "answer": "Repository pattern"},
                {"question_id": "q2", "question": "How to handle errors?", "answer": "Use try-catch"}
            ]
        }))

        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [
                {"id": "q1", "question": "What is the best pattern?"},  # Duplicate
                {"id": "q2", "question": "How to handle errors?"},  # Duplicate
                {"id": "q3", "question": "What about testing strategies?"}   # New (sufficiently different)
            ]
        }))

        stats = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=2
        )

        assert stats["duplicates_removed"] == 2
        assert stats["unique_questions"] == 1


class TestMain:
    """Test CLI main function."""

    @pytest.mark.high
    def test_main_success(self, tmp_path, monkeypatch, capsys):
        """Test successful main execution."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({
            "answers": []
        }))

        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({
            "questions": [{"id": "q1", "question": "Test?"}]
        }))

        monkeypatch.setattr("sys.argv", [
            "deduplicate_questions.py",
            "--questions-file", str(questions_file),
            "--workspace", str(tmp_path),
            "--iteration", "2"
        ])

        deduplicate_questions.main()

        captured = capsys.readouterr()
        assert "Summary:" in captured.out

    @pytest.mark.high
    def test_main_with_dry_run(self, tmp_path, monkeypatch, capsys):
        """Test main with dry run flag."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({"answers": []}))

        questions_file = tmp_path / "questions.json"
        original_content = json.dumps({"questions": [{"id": "q1", "question": "Test?"}]})
        questions_file.write_text(original_content)

        monkeypatch.setattr("sys.argv", [
            "deduplicate_questions.py",
            "--questions-file", str(questions_file),
            "--workspace", str(tmp_path),
            "--iteration", "2",
            "--dry-run"
        ])

        deduplicate_questions.main()

        # File should not be modified
        assert questions_file.read_text() == original_content

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out

    @pytest.mark.high
    def test_main_missing_questions_file(self, tmp_path, monkeypatch):
        """Test main with missing questions file."""
        nonexistent = tmp_path / "nonexistent.json"

        monkeypatch.setattr("sys.argv", [
            "deduplicate_questions.py",
            "--questions-file", str(nonexistent),
            "--workspace", str(tmp_path),
            "--iteration", "2"
        ])

        with pytest.raises(SystemExit) as exc_info:
            deduplicate_questions.main()

        assert exc_info.value.code == 1

    @pytest.mark.high
    def test_main_missing_workspace(self, tmp_path, monkeypatch):
        """Test main with missing workspace."""
        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({"questions": []}))
        nonexistent_workspace = tmp_path / "nonexistent"

        monkeypatch.setattr("sys.argv", [
            "deduplicate_questions.py",
            "--questions-file", str(questions_file),
            "--workspace", str(nonexistent_workspace),
            "--iteration", "2"
        ])

        with pytest.raises(SystemExit) as exc_info:
            deduplicate_questions.main()

        assert exc_info.value.code == 1

    @pytest.mark.medium
    def test_main_custom_similarity_threshold(self, tmp_path, monkeypatch, capsys):
        """Test main with custom similarity threshold."""
        iter1_dir = tmp_path / "iteration-1"
        iter1_dir.mkdir(parents=True)
        (iter1_dir / "qa-answers.json").write_text(json.dumps({"answers": []}))

        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({"questions": [{"id": "q1", "question": "Test?"}]}))

        monkeypatch.setattr("sys.argv", [
            "deduplicate_questions.py",
            "--questions-file", str(questions_file),
            "--workspace", str(tmp_path),
            "--iteration", "2",
            "--similarity-threshold", "0.9"
        ])

        deduplicate_questions.main()

        captured = capsys.readouterr()
        assert "Similarity threshold: 0.9" in captured.out


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.medium
    def test_empty_question_list(self, tmp_path):
        """Test with empty question list."""
        questions_file = tmp_path / "questions.json"
        questions_file.write_text(json.dumps({"questions": []}))

        stats = deduplicate_questions.deduplicate_questions(
            questions_file=questions_file,
            workspace=tmp_path,
            current_iteration=1
        )

        assert stats["total_questions"] == 0
        assert stats["duplicates_removed"] == 0

    @pytest.mark.medium
    def test_question_with_special_characters(self):
        """Test similarity with special characters."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "What's the best <pattern>?",
            "What's the best <pattern>?"
        )

        assert similarity == 1.0

    @pytest.mark.medium
    def test_question_with_unicode(self):
        """Test similarity with Unicode characters."""
        similarity = deduplicate_questions.fuzzy_similarity(
            "Qué patrón usar? 🚀",
            "Qué patrón usar? 🚀"
        )

        assert similarity == 1.0

    @pytest.mark.low
    def test_very_long_questions(self):
        """Test similarity with very long questions."""
        long_q1 = "What pattern should we use for " * 50
        long_q2 = "What pattern should we use for " * 50

        similarity = deduplicate_questions.fuzzy_similarity(long_q1, long_q2)

        assert similarity == 1.0

    @pytest.mark.medium
    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        new_question = {"id": "q2", "question": "  What pattern?  "}
        answered = {
            "q1": {"question": "What pattern?", "answer": "Repository"}
        }

        is_dup, _ = deduplicate_questions.is_duplicate_question(new_question, answered)

        assert is_dup is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
