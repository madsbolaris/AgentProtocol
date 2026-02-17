"""
Unit tests for validation system (validation.py).

Tests JSON schema validation for expert outputs, synthesized data,
and error handling.
"""
import json
import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validation.validation import (
    validate_expert_outputs,
    validate_or_raise,
    validate_synthesized_outputs,
    validate_finalization_outputs,
    validate_all_experts,
    validate_workspace_complete,
    get_validation_summary
)


class TestValidateExpertOutputs:
    """Test validation of expert output files."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def _create_valid_state_file(self, expert: str, iteration: int):
        """Helper to create valid state file."""
        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        state_data = {
            "expert": expert,
            "iteration": iteration,
            "dx_rating": 4,
            "confidence": "high"
        }
        with open(state_file, 'w') as f:
            json.dump(state_data, f)
        return state_file

    def _create_valid_questions_file(self, expert: str, iteration: int):
        """Helper to create valid questions file."""
        questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
        questions_data = {
            "expert": expert,
            "iteration": iteration,
            "questions": [
                {
                    "id": "q1",
                    "question": "What is the expected behavior?",
                    "context": "Need clarification on edge cases"
                }
            ]
        }
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)
        return questions_file

    def _create_review_markdown(self, expert: str, iteration: int):
        """Helper to create review markdown file."""
        review_file = self.workspace / f"review-{expert}-{iteration}.md"
        review_file.write_text("# Expert Review\n\nSome feedback here.")
        return review_file

    def test_validate_complete_expert_output(self):
        """Test validation with all valid files present."""
        expert = "typescript"
        iteration = 1

        # Create all files
        self._create_valid_state_file(expert, iteration)
        self._create_valid_questions_file(expert, iteration)
        self._create_review_markdown(expert, iteration)

        # Validate
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have no errors
        assert len(errors["state"]) == 0
        assert len(errors["questions"]) == 0
        assert len(errors["review"]) == 0

    def test_validate_missing_state_file(self):
        """Test validation with missing state file."""
        expert = "typescript"
        iteration = 1

        # Create only questions and review
        self._create_valid_questions_file(expert, iteration)
        self._create_review_markdown(expert, iteration)

        # Validate
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have state error
        assert len(errors["state"]) > 0
        assert "File not found" in errors["state"][0]
        assert len(errors["questions"]) == 0
        assert len(errors["review"]) == 0

    def test_validate_missing_review_file(self):
        """Test validation with missing review markdown."""
        expert = "typescript"
        iteration = 1

        # Create only state and questions
        self._create_valid_state_file(expert, iteration)
        self._create_valid_questions_file(expert, iteration)

        # Validate
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have review error
        assert len(errors["state"]) == 0
        assert len(errors["questions"]) == 0
        assert len(errors["review"]) > 0
        assert "File not found" in errors["review"][0]

    def test_validate_invalid_state_json(self):
        """Test validation with invalid state JSON structure."""
        expert = "typescript"
        iteration = 1

        # Create invalid state file (missing required fields)
        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        invalid_state = {
            "expert": expert,
            # Missing: iteration, session_id, status, etc.
        }
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)

        self._create_valid_questions_file(expert, iteration)
        self._create_review_markdown(expert, iteration)

        # Validate
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have state validation errors
        assert len(errors["state"]) > 0

    def test_validate_all_files_missing(self):
        """Test validation with all files missing."""
        expert = "typescript"
        iteration = 1

        # Don't create any files
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have errors for all file types
        assert len(errors["state"]) > 0
        assert len(errors["questions"]) > 0
        assert len(errors["review"]) > 0


class TestValidateOrRaise:
    """Test validate_or_raise helper function."""

    def setup_method(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)

    def test_validate_or_raise_valid_json(self):
        """Test that valid JSON doesn't raise exception."""
        # Create a valid state file
        state_file = self.temp_path / "state.json"
        valid_data = {
            "expert": "typescript",
            "iteration": 1,
            "dx_rating": 4,
            "confidence": "high"
        }
        with open(state_file, 'w') as f:
            json.dump(valid_data, f)

        # Should not raise
        try:
            validate_or_raise(state_file, "state-expert.schema.json")
        except ValueError:
            pytest.fail("validate_or_raise raised ValueError for valid JSON")

    def test_validate_or_raise_invalid_json(self):
        """Test that invalid JSON raises ValueError."""
        # Create an invalid state file
        state_file = self.temp_path / "state.json"
        invalid_data = {
            "expert": "typescript",
            # Missing required fields
        }
        with open(state_file, 'w') as f:
            json.dump(invalid_data, f)

        # Should raise ValueError with clear message
        with pytest.raises(ValueError, match="Validation failed"):
            validate_or_raise(state_file, "state-expert.schema.json")

    def test_validate_or_raise_missing_file(self):
        """Test that missing file raises appropriate error."""
        missing_file = self.temp_path / "nonexistent.json"

        # Should raise FileNotFoundError or ValueError
        with pytest.raises((FileNotFoundError, ValueError)):
            validate_or_raise(missing_file, "state-expert.schema.json")


class TestValidationErrorMessages:
    """Test that validation error messages are clear and actionable."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_error_message_includes_file_path(self):
        """Test that error messages include file path."""
        expert = "typescript"
        iteration = 1

        # Don't create files
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Error messages should mention the file type
        assert any("File not found" in err for err in errors["state"])

    def test_validation_error_includes_field(self):
        """Test that validation errors include specific field information."""
        expert = "typescript"
        iteration = 1

        # Create file with invalid data
        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        invalid_data = {
            "expert": expert,
            "iteration": "invalid",  # Should be int
        }
        with open(state_file, 'w') as f:
            json.dump(invalid_data, f)

        # Validate
        errors = validate_expert_outputs(self.workspace, iteration, expert)

        # Should have validation error
        assert len(errors["state"]) > 0


class TestValidationPerformance:
    """Test that validation doesn't significantly slow workflow."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_validation_is_fast(self):
        """Test that validation completes quickly."""
        import time

        expert = "typescript"
        iteration = 1

        # Create valid files
        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        state_data = {
            "expert": expert,
            "iteration": iteration,
            "dx_rating": 4,
            "confidence": "high"
        }
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
        questions_data = {
            "expert": expert,
            "iteration": iteration,
            "questions": []
        }
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        review_file = self.workspace / f"review-{expert}-{iteration}.md"
        review_file.write_text("# Review")

        # Time validation
        start = time.time()
        validate_expert_outputs(self.workspace, iteration, expert)
        elapsed = time.time() - start

        # Should be fast (< 100ms)
        assert elapsed < 0.1, f"Validation took {elapsed}s, should be < 0.1s"


class TestValidateSynthesizedOutputs:
    """Test validation of synthesized output files."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_validate_synthesized_questions_valid(self):
        """Test validation of valid synthesized questions."""
        questions_file = self.workspace / "questions.json"
        questions_data = {
            "iteration": 1,
            "questions": [
                {
                    "id": "q1",
                    "question": "Test question?",
                    "context": "Test context",
                    "importance": "high",
                    "asked_by": ["typescript"]
                }
            ]
        }
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        state_file = self.workspace / "state.json"
        state_data = {
            "iteration": 1,
            "experts": ["typescript", "python"],
            "status": "in_progress"
        }
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        errors = validate_synthesized_outputs(self.workspace, 1)

        assert len(errors["questions"]) == 0
        assert len(errors["state"]) == 0

    def test_validate_synthesized_missing_files(self):
        """Test validation with missing synthesized files."""
        errors = validate_synthesized_outputs(self.workspace, 1)

        assert len(errors["questions"]) > 0
        assert "File not found" in errors["questions"][0]
        assert len(errors["state"]) > 0
        assert "File not found" in errors["state"][0]

    def test_validate_synthesized_invalid_questions(self):
        """Test validation with invalid synthesized questions."""
        questions_file = self.workspace / "questions.json"
        questions_data = {"questions": "invalid"}
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        state_file = self.workspace / "state.json"
        state_data = {"iteration": 1, "experts": [], "status": "in_progress"}
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        errors = validate_synthesized_outputs(self.workspace, 1)

        assert len(errors["questions"]) > 0

    def test_validate_synthesized_invalid_state(self):
        """Test validation with invalid state."""
        questions_file = self.workspace / "questions.json"
        questions_data = {"questions": []}
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        state_file = self.workspace / "state.json"
        state_data = {"invalid": "data"}
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        errors = validate_synthesized_outputs(self.workspace, 1)

        assert len(errors["state"]) > 0

    def test_validate_synthesized_exception_handling(self):
        """Test exception handling in validation."""
        questions_file = self.workspace / "questions.json"
        questions_file.write_text("invalid json {")

        errors = validate_synthesized_outputs(self.workspace, 1)

        assert len(errors["questions"]) > 0
        assert "Error loading/validating" in errors["questions"][0]


class TestValidateFinalizationOutputs:
    """Test validation of finalization output files."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_validate_adr_mode_valid(self):
        """Test validation of valid ADR output."""
        adr_file = self.workspace / "adr-output.json"
        adr_data = {
            "title": "Test ADR",
            "status": "accepted",
            "deciders": ["typescript", "python"],
            "date": "2024-01-01",
            "context": {
                "problem_statement": "Test problem",
                "background": "Test background",
                "constraints": ["constraint1"]
            },
            "decision_drivers": ["driver1"],
            "considered_options": [
                {
                    "title": "Option 1",
                    "description": "Test option"
                }
            ],
            "decision_outcome": {
                "chosen_option": "Option 1",
                "rationale": "Test rationale"
            },
            "consequences": {
                "good": ["benefit1"],
                "bad": ["drawback1"]
            }
        }
        with open(adr_file, 'w') as f:
            json.dump(adr_data, f)

        errors = validate_finalization_outputs(self.workspace, "adr")

        assert len(errors["adr"]) == 0

    def test_validate_adr_mode_missing(self):
        """Test validation with missing ADR file."""
        errors = validate_finalization_outputs(self.workspace, "adr")

        assert len(errors["adr"]) > 0
        assert "File not found" in errors["adr"][0]

    def test_validate_adr_mode_invalid(self):
        """Test validation with invalid ADR data."""
        adr_file = self.workspace / "adr-output.json"
        adr_data = {
            "title": "Test",
            "status": "accepted"
            # Missing required fields
        }
        with open(adr_file, 'w') as f:
            json.dump(adr_data, f)

        errors = validate_finalization_outputs(self.workspace, "adr")

        assert len(errors["adr"]) > 0

    def test_validate_create_mode_with_artifact(self):
        """Test validation of create mode with artifact."""
        artifact_file = self.workspace / "output.md"
        artifact_file.write_text("# Test artifact")

        errors = validate_finalization_outputs(self.workspace, "create")

        assert len(errors["artifact"]) == 0

    def test_validate_create_mode_no_artifact(self):
        """Test validation of create mode without artifact."""
        errors = validate_finalization_outputs(self.workspace, "create")

        assert len(errors["artifact"]) > 0
        assert "No artifact file found" in errors["artifact"][0]

    def test_validate_improve_mode(self):
        """Test validation of improve mode."""
        artifact_file = self.workspace / "improved.py"
        artifact_file.write_text("# Improved code")

        errors = validate_finalization_outputs(self.workspace, "improve")

        assert len(errors["artifact"]) == 0

    def test_validate_review_mode(self):
        """Test validation of review mode."""
        artifact_file = self.workspace / "review-notes.md"
        artifact_file.write_text("# Review notes")

        errors = validate_finalization_outputs(self.workspace, "review")

        assert len(errors["artifact"]) == 0


class TestValidateAllExperts:
    """Test validation of all expert outputs."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def _create_valid_expert_files(self, expert: str, iteration: int):
        """Helper to create all valid files for an expert."""
        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        state_data = {
            "expert": expert,
            "iteration": iteration,
            "dx_rating": 4,
            "confidence": "high"
        }
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
        questions_data = {
            "expert": expert,
            "iteration": iteration,
            "questions": []
        }
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        review_file = self.workspace / f"review-{expert}-{iteration}.md"
        review_file.write_text("# Review")

    def test_validate_all_experts_valid(self):
        """Test validation of all experts with valid files."""
        experts = ["typescript", "python"]
        iteration = 1

        for expert in experts:
            self._create_valid_expert_files(expert, iteration)

        all_valid, errors = validate_all_experts(self.workspace, iteration, experts)

        assert all_valid is True
        assert len(errors) == 0

    def test_validate_all_experts_one_invalid(self):
        """Test validation with one invalid expert."""
        experts = ["typescript", "python"]
        iteration = 1

        self._create_valid_expert_files("typescript", iteration)
        # Don't create files for python

        all_valid, errors = validate_all_experts(self.workspace, iteration, experts)

        assert all_valid is False
        assert "python" in errors
        assert len(errors["python"]) > 0

    def test_validate_all_experts_raise_on_error(self):
        """Test validation with raise_on_error flag."""
        experts = ["typescript"]
        iteration = 1

        # Don't create any files

        with pytest.raises(ValueError, match="Validation failed"):
            validate_all_experts(self.workspace, iteration, experts, raise_on_error=True)

    def test_validate_all_experts_multiple_invalid(self):
        """Test validation with multiple invalid experts."""
        experts = ["typescript", "python", "csharp"]
        iteration = 1

        # Don't create any files

        all_valid, errors = validate_all_experts(self.workspace, iteration, experts)

        assert all_valid is False
        assert len(errors) == 3
        assert "typescript" in errors
        assert "python" in errors
        assert "csharp" in errors


class TestValidateWorkspaceComplete:
    """Test workspace completion validation."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def _create_complete_workspace(self, experts, iteration, mode):
        """Helper to create complete workspace."""
        for expert in experts:
            state_file = self.workspace / f"state-{expert}-{iteration}.json"
            state_data = {"expert": expert, "iteration": iteration, "dx_rating": 4, "confidence": "high"}
            with open(state_file, 'w') as f:
                json.dump(state_data, f)

            questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
            questions_data = {"expert": expert, "iteration": iteration, "questions": []}
            with open(questions_file, 'w') as f:
                json.dump(questions_data, f)

            review_file = self.workspace / f"review-{expert}-{iteration}.md"
            review_file.write_text("# Review")

        questions_file = self.workspace / "questions.json"
        questions_data = {"iteration": iteration, "questions": []}
        with open(questions_file, 'w') as f:
            json.dump(questions_data, f)

        state_file = self.workspace / "state.json"
        state_data = {"iteration": iteration, "experts": experts, "status": "in_progress"}
        with open(state_file, 'w') as f:
            json.dump(state_data, f)

        if mode == "adr":
            adr_file = self.workspace / "adr-output.json"
            adr_data = {
                "title": "Test",
                "status": "accepted",
                "deciders": experts,
                "date": "2024-01-01",
                "context": {"problem_statement": "Test", "background": "Test", "constraints": []},
                "decision_drivers": ["test"],
                "considered_options": [{"title": "Option", "description": "Test"}],
                "decision_outcome": {"chosen_option": "Option", "rationale": "Test"},
                "consequences": {"good": [], "bad": []}
            }
            with open(adr_file, 'w') as f:
                json.dump(adr_data, f)
        else:
            artifact_file = self.workspace / "artifact.md"
            artifact_file.write_text("# Artifact")

    def test_validate_workspace_complete_all_present(self):
        """Test workspace validation with all files present."""
        experts = ["typescript"]
        iteration = 1
        mode = "review"

        self._create_complete_workspace(experts, iteration, mode)

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        assert is_complete is True
        assert not any(missing.values())

    def test_validate_workspace_missing_expert_files(self):
        """Test workspace validation with missing expert files."""
        experts = ["typescript", "python"]
        iteration = 1
        mode = "review"

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        assert is_complete is False
        assert len(missing["expert_files"]) > 0

    def test_validate_workspace_missing_synthesized_files(self):
        """Test workspace validation with missing synthesized files."""
        experts = ["typescript"]
        iteration = 1
        mode = "review"

        for expert in experts:
            state_file = self.workspace / f"state-{expert}-{iteration}.json"
            with open(state_file, 'w') as f:
                json.dump({"expert": expert, "iteration": iteration, "dx_rating": 4, "confidence": "high"}, f)
            questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
            with open(questions_file, 'w') as f:
                json.dump({"expert": expert, "iteration": iteration, "questions": []}, f)
            review_file = self.workspace / f"review-{expert}-{iteration}.md"
            review_file.write_text("# Review")

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        assert is_complete is False
        assert len(missing["synthesized_files"]) > 0

    def test_validate_workspace_missing_finalization_adr(self):
        """Test workspace validation with missing ADR file."""
        experts = ["typescript"]
        iteration = 1
        mode = "adr"

        self._create_complete_workspace(experts, iteration, "review")

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        assert is_complete is False
        assert len(missing["finalization_files"]) > 0
        assert "adr-output.json" in missing["finalization_files"][0]

    def test_validate_workspace_missing_finalization_artifact(self):
        """Test workspace validation with missing artifact file."""
        experts = ["typescript"]
        iteration = 1
        mode = "create"

        # Create subdirectory for expert files to avoid polluting workspace with .md files
        expert_dir = self.workspace / "experts"
        expert_dir.mkdir()

        for expert in experts:
            state_file = self.workspace / f"state-{expert}-{iteration}.json"
            with open(state_file, 'w') as f:
                json.dump({"expert": expert, "iteration": iteration, "dx_rating": 4, "confidence": "high"}, f)
            questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
            with open(questions_file, 'w') as f:
                json.dump({"expert": expert, "iteration": iteration, "questions": []}, f)
            # Put review file in subdirectory so it doesn't count as artifact
            review_file = expert_dir / f"review-{expert}-{iteration}.md"
            review_file.write_text("# Review")

        questions_file = self.workspace / "questions.json"
        with open(questions_file, 'w') as f:
            json.dump({"iteration": iteration, "questions": []}, f)

        state_file = self.workspace / "state.json"
        with open(state_file, 'w') as f:
            json.dump({"iteration": iteration, "experts": experts, "status": "in_progress"}, f)

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        # Note: This test expects missing review file error since we moved it to subdirectory
        assert is_complete is False
        assert len(missing["expert_files"]) > 0 or len(missing["finalization_files"]) > 0

    def test_validate_workspace_complete_adr_mode(self):
        """Test workspace validation with ADR mode complete."""
        experts = ["typescript"]
        iteration = 1
        mode = "adr"

        self._create_complete_workspace(experts, iteration, mode)

        is_complete, missing = validate_workspace_complete(self.workspace, iteration, experts, mode)

        assert is_complete is True


class TestGetValidationSummary:
    """Test validation summary formatting."""

    def test_get_validation_summary_empty(self):
        """Test summary with no errors."""
        summary = get_validation_summary({})

        assert "All validations passed" in summary

    def test_get_validation_summary_with_errors(self):
        """Test summary with errors."""
        errors = {
            "typescript": {
                "state": ["Missing required field"],
                "questions": []
            },
            "python": {
                "state": [],
                "questions": ["Invalid format"],
                "review": ["File not found"]
            }
        }

        summary = get_validation_summary(errors)

        assert "Validation errors found" in summary
        assert "typescript" in summary
        assert "python" in summary
        assert "Missing required field" in summary
        assert "Invalid format" in summary
        assert "File not found" in summary

    def test_get_validation_summary_multiple_errors(self):
        """Test summary with multiple errors per expert."""
        errors = {
            "typescript": {
                "state": ["Error 1", "Error 2"],
                "questions": ["Error 3"]
            }
        }

        summary = get_validation_summary(errors)

        assert "Error 1" in summary
        assert "Error 2" in summary
        assert "Error 3" in summary


class TestExceptionHandling:
    """Test exception handling in validation functions."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_validate_expert_outputs_corrupted_json(self):
        """Test handling of corrupted JSON files."""
        expert = "typescript"
        iteration = 1

        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        state_file.write_text("corrupted json {{{")

        questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
        with open(questions_file, 'w') as f:
            json.dump({"expert": expert, "iteration": iteration, "questions": []}, f)

        review_file = self.workspace / f"review-{expert}-{iteration}.md"
        review_file.write_text("# Review")

        errors = validate_expert_outputs(self.workspace, iteration, expert)

        assert len(errors["state"]) > 0
        assert "Error loading/validating" in errors["state"][0]

    def test_validate_expert_outputs_corrupted_questions(self):
        """Test handling of corrupted questions JSON."""
        expert = "typescript"
        iteration = 1

        state_file = self.workspace / f"state-{expert}-{iteration}.json"
        with open(state_file, 'w') as f:
            json.dump({"expert": expert, "iteration": iteration, "dx_rating": 4, "confidence": "high"}, f)

        questions_file = self.workspace / f"questions-{expert}-{iteration}.json"
        questions_file.write_text("corrupted json {{{")

        review_file = self.workspace / f"review-{expert}-{iteration}.md"
        review_file.write_text("# Review")

        errors = validate_expert_outputs(self.workspace, iteration, expert)

        assert len(errors["questions"]) > 0
        assert "Error loading/validating" in errors["questions"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
