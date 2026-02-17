"""
Unit tests for file_io/workspace_utils.py

Tests workspace path utilities including:
- WorkspacePaths class methods
- Path construction and validation
- Directory structure verification
- Edge cases and error handling

Target coverage: 85%+ (HIGH priority module)
"""
import pytest
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from file_io.workspace_utils import WorkspacePaths, get_artifact_path, load_workspace_paths, list_iterations


class TestWorkspacePathsInit:
    """Test WorkspacePaths initialization."""

    @pytest.mark.high
    def test_init_with_path_object(self, test_workspace):
        """Test initialization with Path object."""
        paths = WorkspacePaths(test_workspace)

        assert paths.root == test_workspace
        assert isinstance(paths.root, Path)

    @pytest.mark.high
    def test_init_with_string_path(self, test_workspace):
        """Test initialization with string path."""
        paths = WorkspacePaths(str(test_workspace))

        assert paths.root == test_workspace
        assert isinstance(paths.root, Path)

    @pytest.mark.high
    def test_init_with_relative_path(self):
        """Test initialization with relative path."""
        paths = WorkspacePaths("./test-workspace")

        assert paths.root == Path("./test-workspace")


class TestStateFiles:
    """Test state file path methods."""

    @pytest.mark.high
    def test_state_path(self, test_workspace):
        """Test state.json path construction."""
        paths = WorkspacePaths(test_workspace)

        state_path = paths.state

        assert state_path == test_workspace / "state.json"
        assert state_path.name == "state.json"


class TestIterationDirectories:
    """Test iteration directory path methods."""

    @pytest.mark.high
    def test_iteration_dir_iteration_1(self, test_workspace):
        """Test iteration directory for iteration 1."""
        paths = WorkspacePaths(test_workspace)

        iter_dir = paths.iteration_dir(1)

        assert iter_dir == test_workspace / "iteration-1"
        assert "iteration-1" in str(iter_dir)

    @pytest.mark.high
    def test_iteration_dir_iteration_5(self, test_workspace):
        """Test iteration directory for iteration 5."""
        paths = WorkspacePaths(test_workspace)

        iter_dir = paths.iteration_dir(5)

        assert iter_dir == test_workspace / "iteration-5"

    @pytest.mark.high
    def test_experts_dir(self, test_workspace):
        """Test experts directory path."""
        paths = WorkspacePaths(test_workspace)

        experts_dir = paths.experts_dir(1)

        assert experts_dir == test_workspace / "iteration-1" / "experts"

    @pytest.mark.high
    def test_expert_dir_typescript(self, test_workspace):
        """Test expert-specific directory for TypeScript expert."""
        paths = WorkspacePaths(test_workspace)

        expert_dir = paths.expert_dir("typescript", 1)

        assert expert_dir == test_workspace / "iteration-1" / "experts" / "typescript"

    @pytest.mark.high
    def test_expert_dir_multiple_experts(self, test_workspace):
        """Test directory paths for multiple experts."""
        paths = WorkspacePaths(test_workspace)

        ts_dir = paths.expert_dir("typescript", 1)
        py_dir = paths.expert_dir("python", 1)
        sec_dir = paths.expert_dir("security", 1)

        assert "typescript" in str(ts_dir)
        assert "python" in str(py_dir)
        assert "security" in str(sec_dir)
        # All in same iteration
        assert ts_dir.parent == py_dir.parent == sec_dir.parent


class TestExpertFiles:
    """Test expert file path methods."""

    @pytest.mark.high
    def test_expert_review_md(self, test_workspace):
        """Test expert review markdown file path."""
        paths = WorkspacePaths(test_workspace)

        review_file = paths.expert_review_md("typescript", 1)

        expected = test_workspace / "iteration-1" / "experts" / "typescript" / "review-typescript.md"
        assert review_file == expected
        assert review_file.name == "review-typescript.md"

    @pytest.mark.high
    def test_expert_state_json(self, test_workspace):
        """Test expert state JSON file path."""
        paths = WorkspacePaths(test_workspace)

        state_file = paths.expert_state_json("python", 2)

        expected = test_workspace / "iteration-2" / "experts" / "python" / "state-python.json"
        assert state_file == expected

    @pytest.mark.high
    def test_expert_questions_json(self, test_workspace):
        """Test expert questions JSON file path."""
        paths = WorkspacePaths(test_workspace)

        questions_file = paths.expert_questions_json("security", 1)

        assert "questions-security.json" in str(questions_file)

    @pytest.mark.high
    def test_expert_scripts_dir(self, test_workspace):
        """Test expert scripts directory path."""
        paths = WorkspacePaths(test_workspace)

        scripts_dir = paths.expert_scripts_dir("typescript", 1)

        expected = test_workspace / "iteration-1" / "experts" / "typescript" / "scripts"
        assert scripts_dir == expected

    @pytest.mark.high
    def test_expert_scripts_outputs_dir(self, test_workspace):
        """Test expert scripts outputs directory path."""
        paths = WorkspacePaths(test_workspace)

        outputs_dir = paths.expert_scripts_outputs_dir("python", 1)

        assert "scripts" in str(outputs_dir)
        assert "outputs" in str(outputs_dir)


class TestConsolidationFiles:
    """Test consolidation and synthesis file paths."""

    @pytest.mark.high
    def test_synthesized_md(self, test_workspace):
        """Test synthesized markdown file path."""
        paths = WorkspacePaths(test_workspace)

        synthesized = paths.synthesized_md(1)

        expected = test_workspace / "iteration-1" / "synthesized.md"
        assert synthesized == expected

    @pytest.mark.high
    def test_questions_json(self, test_workspace):
        """Test consolidated questions JSON path."""
        paths = WorkspacePaths(test_workspace)

        questions = paths.questions_json(1)

        expected = test_workspace / "iteration-1" / "questions.json"
        assert questions == expected

    @pytest.mark.high
    def test_qa_answers_json(self, test_workspace):
        """Test QA answers JSON path."""
        paths = WorkspacePaths(test_workspace)

        qa_answers = paths.qa_answers_json(2)

        expected = test_workspace / "iteration-2" / "qa-answers.json"
        assert qa_answers == expected


class TestArtifactFiles:
    """Test artifact file paths."""

    @pytest.mark.high
    def test_artifacts_dir(self, test_workspace):
        """Test artifacts directory path."""
        paths = WorkspacePaths(test_workspace)

        artifacts_dir = paths.artifacts_dir

        expected = test_workspace / "artifacts"
        assert artifacts_dir == expected

    @pytest.mark.high
    def test_artifact_draft_adr(self, test_workspace):
        """Test draft ADR artifact path."""
        paths = WorkspacePaths(test_workspace)

        draft_adr = paths.artifact_path("draft-adr.md")

        expected = test_workspace / "artifacts" / "draft-adr.md"
        assert draft_adr == expected

    @pytest.mark.high
    def test_artifact_draft_plan(self, test_workspace):
        """Test draft implementation plan artifact path."""
        paths = WorkspacePaths(test_workspace)

        draft_plan = paths.artifact_path("draft-plan.md")

        assert "draft-plan.md" in str(draft_plan)

    @pytest.mark.high
    def test_artifact_final(self, test_workspace):
        """Test final artifact path."""
        paths = WorkspacePaths(test_workspace)

        final = paths.artifact_path("final-adr.md")

        assert "final-adr.md" in str(final)


class TestLogFiles:
    """Test log file paths."""

    @pytest.mark.high
    def test_logs_dir(self, test_workspace):
        """Test logs directory path."""
        paths = WorkspacePaths(test_workspace)

        logs_dir = paths.logs_dir

        expected = test_workspace / "logs"
        assert logs_dir == expected

    @pytest.mark.high
    def test_expert_log(self, test_workspace):
        """Test expert log file path."""
        paths = WorkspacePaths(test_workspace)

        log_file = paths.log_path("expert-typescript")

        expected = test_workspace / "logs" / "expert-typescript.log"
        assert log_file == expected

    @pytest.mark.high
    def test_synthesis_log(self, test_workspace):
        """Test synthesis log file path."""
        paths = WorkspacePaths(test_workspace)

        log_file = paths.log_path("synthesis")

        expected = test_workspace / "logs" / "synthesis.log"
        assert log_file == expected


class TestGetArtifactPath:
    """Test get_artifact_path helper function."""

    @pytest.mark.high
    def test_get_artifact_path_default(self, test_workspace):
        """Test get_artifact_path with default artifact type."""
        artifact_path = get_artifact_path(test_workspace)

        assert test_workspace in artifact_path.parents or artifact_path.parent == test_workspace
        assert artifact_path.suffix == ".md"

    @pytest.mark.high
    def test_get_artifact_path_adr(self, test_workspace):
        """Test get_artifact_path for ADR."""
        artifact_path = get_artifact_path(test_workspace, mode="adr")

        assert "adr" in str(artifact_path).lower()

    @pytest.mark.high
    def test_get_artifact_path_plan(self, test_workspace):
        """Test get_artifact_path for implementation plan."""
        artifact_path = get_artifact_path(test_workspace, mode="improve")

        assert "plan" in str(artifact_path).lower()


class TestPathIntegration:
    """Integration tests for workspace paths."""

    @pytest.mark.high
    def test_complete_iteration_structure(self, test_workspace):
        """Test constructing complete iteration structure."""
        paths = WorkspacePaths(test_workspace)

        # Construct all paths for iteration 1
        iter_dir = paths.iteration_dir(1)
        experts_dir = paths.experts_dir(1)
        ts_dir = paths.expert_dir("typescript", 1)
        ts_review = paths.expert_review_md("typescript", 1)
        synthesized = paths.synthesized_md(1)
        questions = paths.questions_json(1)

        # Verify hierarchy
        assert iter_dir in experts_dir.parents
        assert experts_dir in ts_dir.parents
        assert ts_dir in ts_review.parents
        assert iter_dir in synthesized.parents
        assert iter_dir in questions.parents

    @pytest.mark.high
    def test_multiple_iterations_different_paths(self, test_workspace):
        """Test that different iterations have different paths."""
        paths = WorkspacePaths(test_workspace)

        iter1_review = paths.expert_review_md("typescript", 1)
        iter2_review = paths.expert_review_md("typescript", 2)
        iter3_review = paths.expert_review_md("typescript", 3)

        assert iter1_review != iter2_review != iter3_review
        assert "iteration-1" in str(iter1_review)
        assert "iteration-2" in str(iter2_review)
        assert "iteration-3" in str(iter3_review)

    @pytest.mark.high
    def test_path_consistency(self, test_workspace):
        """Test that repeated calls return consistent paths."""
        paths = WorkspacePaths(test_workspace)

        # Call same method multiple times
        path1 = paths.expert_review_md("python", 1)
        path2 = paths.expert_review_md("python", 1)
        path3 = paths.expert_review_md("python", 1)

        assert path1 == path2 == path3


class TestEnsureStructure:
    """Test ensure_structure method for creating workspace directories."""

    @pytest.mark.high
    def test_ensure_structure_creates_directories(self, test_workspace):
        """Test ensure_structure creates all necessary directories."""
        paths = WorkspacePaths(test_workspace)
        experts = ["typescript", "python", "security"]

        paths.ensure_structure(experts, iteration=1)

        # Verify expert directories exist
        for expert in experts:
            expert_dir = paths.expert_dir(expert, 1)
            assert expert_dir.exists()
            assert expert_dir.is_dir()

            # Verify scripts/outputs directories
            outputs_dir = paths.expert_scripts_outputs_dir(expert, 1)
            assert outputs_dir.exists()
            assert outputs_dir.is_dir()

        # Verify artifacts and logs directories
        assert paths.artifacts_dir.exists()
        assert paths.logs_dir.exists()

    @pytest.mark.high
    def test_ensure_structure_idempotent(self, test_workspace):
        """Test ensure_structure can be called multiple times safely."""
        paths = WorkspacePaths(test_workspace)
        experts = ["typescript"]

        # Call twice
        paths.ensure_structure(experts, iteration=1)
        paths.ensure_structure(experts, iteration=1)

        # Should still work
        assert paths.expert_dir("typescript", 1).exists()


class TestLoadWorkspacePaths:
    """Test load_workspace_paths convenience function."""

    @pytest.mark.high
    def test_load_workspace_paths(self, test_workspace):
        """Test load_workspace_paths returns WorkspacePaths instance."""
        paths = load_workspace_paths(test_workspace)

        assert isinstance(paths, WorkspacePaths)
        assert paths.root == test_workspace


class TestListIterations:
    """Test list_iterations function."""

    @pytest.mark.high
    def test_list_iterations_empty_workspace(self, tmp_path):
        """Test list_iterations with no iteration directories."""
        # Use tmp_path directly, create a completely empty workspace
        empty_workspace = tmp_path / "empty-workspace"
        empty_workspace.mkdir()

        iterations = list_iterations(empty_workspace)

        assert iterations == []

    @pytest.mark.high
    def test_list_iterations_single_iteration(self, test_workspace):
        """Test list_iterations with one iteration."""
        # test_workspace fixture already creates iteration-1
        iterations = list_iterations(test_workspace)

        assert iterations == [1]

    @pytest.mark.high
    def test_list_iterations_multiple_iterations(self, tmp_path):
        """Test list_iterations with multiple iterations."""
        workspace = tmp_path / "multi-workspace"
        workspace.mkdir()
        (workspace / "iteration-1").mkdir(parents=True)
        (workspace / "iteration-2").mkdir(parents=True)
        (workspace / "iteration-5").mkdir(parents=True)

        iterations = list_iterations(workspace)

        assert iterations == [1, 2, 5]

    @pytest.mark.high
    def test_list_iterations_ignores_non_iteration_dirs(self, tmp_path):
        """Test list_iterations ignores non-iteration directories."""
        workspace = tmp_path / "mixed-workspace"
        workspace.mkdir()
        (workspace / "iteration-1").mkdir(parents=True)
        (workspace / "iteration-2").mkdir(parents=True)
        (workspace / "artifacts").mkdir(parents=True)
        (workspace / "logs").mkdir(parents=True)
        (workspace / "other-dir").mkdir(parents=True)

        iterations = list_iterations(workspace)

        assert iterations == [1, 2]

    @pytest.mark.high
    def test_list_iterations_ignores_invalid_format(self, tmp_path):
        """Test list_iterations ignores directories with invalid format."""
        workspace = tmp_path / "invalid-workspace"
        workspace.mkdir()
        (workspace / "iteration-1").mkdir(parents=True)
        (workspace / "iteration-abc").mkdir(parents=True)
        (workspace / "iteration-").mkdir(parents=True)

        iterations = list_iterations(workspace)

        assert iterations == [1]


class TestGetArtifactPathModes:
    """Test get_artifact_path for different modes."""

    @pytest.mark.high
    def test_get_artifact_path_review_mode(self, test_workspace):
        """Test get_artifact_path for review mode."""
        artifact_path = get_artifact_path(test_workspace, mode="review")

        assert artifact_path == test_workspace / "adr-data.json"
        assert artifact_path.suffix == ".json"

    @pytest.mark.high
    def test_get_artifact_path_create_mode(self, test_workspace):
        """Test get_artifact_path for create mode."""
        artifact_path = get_artifact_path(test_workspace, mode="create")

        assert artifact_path == test_workspace / "draft-plan.md"
        assert artifact_path.suffix == ".md"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_special_characters_in_expert_name(self, test_workspace):
        """Test handling expert names with special characters."""
        paths = WorkspacePaths(test_workspace)

        # Note: Real implementation may sanitize names
        expert_dir = paths.expert_dir("expert-with-dash", 1)

        assert "expert-with-dash" in str(expert_dir)

    @pytest.mark.high
    def test_zero_iteration_number(self, test_workspace):
        """Test iteration 0 (edge case)."""
        paths = WorkspacePaths(test_workspace)

        iter_dir = paths.iteration_dir(0)

        assert "iteration-0" in str(iter_dir)

    @pytest.mark.high
    def test_large_iteration_number(self, test_workspace):
        """Test large iteration numbers."""
        paths = WorkspacePaths(test_workspace)

        iter_dir = paths.iteration_dir(999)

        assert "iteration-999" in str(iter_dir)

    @pytest.mark.high
    def test_empty_expert_name(self, test_workspace):
        """Test empty expert name (edge case)."""
        paths = WorkspacePaths(test_workspace)

        expert_dir = paths.expert_dir("", 1)

        # Should still construct path (validation happens elsewhere)
        assert expert_dir.exists() is False  # Won't exist but path is valid
