"""
Unit tests for utils/init_workspace.py

Tests workspace initialization including:
- slugify() text to slug conversion
- find_repo_root() repository root detection
- create_workspace() workspace structure creation
- Directory creation and state file generation
- README generation and content verification
- main() CLI argument parsing

Target coverage: 80%+
"""
import pytest
from pathlib import Path
import sys
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from utils import init_workspace


class TestSlugify:
    """Test slugify function."""

    def test_basic_slugify(self):
        """Test basic text slugification."""
        result = init_workspace.slugify("My Test Topic")
        assert result == "my-test-topic"

    def test_special_characters(self):
        """Test slugify with special characters."""
        result = init_workspace.slugify("Test: API & Design!")
        assert result == "test-api-design"

    def test_multiple_spaces(self):
        """Test slugify with multiple spaces."""
        result = init_workspace.slugify("Test   Multiple    Spaces")
        assert result == "test-multiple-spaces"

    def test_length_limit(self):
        """Test that slug is limited to 50 chars."""
        long_text = "A" * 100
        result = init_workspace.slugify(long_text)
        assert len(result) <= 50

    def test_leading_trailing_hyphens(self):
        """Test removal of leading/trailing hyphens."""
        result = init_workspace.slugify("  Test Topic  ")
        assert not result.startswith("-")
        assert not result.endswith("-")

    def test_unicode_characters(self):
        """Test slugify with Unicode characters."""
        result = init_workspace.slugify("Test 测试 тест")
        assert "test" in result
        # Unicode chars should be removed
        assert len(result) == 4  # "test"

    def test_empty_string(self):
        """Test slugify with empty string."""
        result = init_workspace.slugify("")
        assert result == ""

    def test_only_special_chars(self):
        """Test slugify with only special characters."""
        result = init_workspace.slugify("!@#$%^&*()")
        assert result == ""

    def test_numbers_preserved(self):
        """Test that numbers are preserved in slug."""
        result = init_workspace.slugify("Test 123 API")
        assert result == "test-123-api"

    def test_underscores_converted(self):
        """Test that underscores are converted to hyphens."""
        result = init_workspace.slugify("test_api_design")
        assert result == "test-api-design"

    def test_consecutive_hyphens_collapsed(self):
        """Test that consecutive hyphens are collapsed."""
        result = init_workspace.slugify("test---api---design")
        assert result == "test-api-design"


class TestFindRepoRoot:
    """Test find_repo_root function."""

    def test_find_repo_root_with_git(self, tmp_path):
        """Test finding repo root when .git exists."""
        # Create .git directory
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Create subdirectory
        subdir = tmp_path / "sub" / "dir"
        subdir.mkdir(parents=True)

        # Change to subdirectory and find root
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            root = init_workspace.find_repo_root()
            # Should find parent with .git
            assert root.resolve() == tmp_path.resolve()
        finally:
            os.chdir(original_cwd)

    def test_find_repo_root_without_git(self, tmp_path):
        """Test fallback when no .git exists."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            root = init_workspace.find_repo_root()
            # Should fallback to current directory
            assert root.resolve() == tmp_path.resolve()
        finally:
            os.chdir(original_cwd)

    def test_find_repo_root_nested_deep(self, tmp_path):
        """Test finding repo root in deeply nested structure."""
        # Create .git at root
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Create deeply nested structure
        deep_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)

        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(deep_dir)
            root = init_workspace.find_repo_root()
            assert root.resolve() == tmp_path.resolve()
        finally:
            os.chdir(original_cwd)


class TestCreateWorkspace:
    """Test create_workspace function."""

    def test_create_workspace_basic(self, tmp_path, capsys):
        """Test basic workspace creation."""
        workspace = init_workspace.create_workspace(
            topic="Test Topic",
            experts=["typescript", "python"],
            mode="review",
            base_dir=tmp_path
        )

        assert workspace.exists()
        assert "expert-feedback" in workspace.name
        assert "test-topic" in workspace.name

        # Check stdout
        captured = capsys.readouterr()
        assert "Workspace created" in captured.out

    def test_create_workspace_creates_iteration(self, tmp_path, capsys):
        """Test that iteration-1 directory is created."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        iter1_dir = workspace / "iteration-1"
        assert iter1_dir.exists()
        assert iter1_dir.is_dir()

    def test_create_workspace_creates_experts_dir(self, tmp_path, capsys):
        """Test that experts directory is created."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        experts_dir = workspace / "iteration-1" / "experts"
        assert experts_dir.exists()
        assert experts_dir.is_dir()

    def test_create_workspace_creates_expert_folders(self, tmp_path, capsys):
        """Test that individual expert folders are created."""
        experts = ["typescript", "python", "dx"]
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=experts,
            base_dir=tmp_path
        )

        experts_dir = workspace / "iteration-1" / "experts"
        for expert in experts:
            expert_dir = experts_dir / expert
            assert expert_dir.exists()
            assert (expert_dir / "scripts").exists()
            assert (expert_dir / "scripts" / "outputs").exists()

    def test_create_workspace_creates_logs_dir(self, tmp_path, capsys):
        """Test that logs directory is created."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        logs_dir = workspace / "logs"
        assert logs_dir.exists()
        assert logs_dir.is_dir()

    def test_create_workspace_creates_state_file(self, tmp_path, capsys):
        """Test that state.json is created with correct content."""
        workspace = init_workspace.create_workspace(
            topic="Test Topic",
            experts=["typescript", "python"],
            mode="review",
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        assert state_file.exists()

        # Verify state content
        with open(state_file) as f:
            state = json.load(f)

        assert state["topic"] == "Test Topic"
        assert "typescript" in state["experts"]
        assert "python" in state["experts"]
        assert state["mode"] == "review"
        assert state["iteration"] == 1
        assert state["convergence_percent"] == 0.0
        assert state["consensus_reached"] is False
        assert state["phase"] == "spawning_experts"
        assert "expert_results" in state
        assert "created_at" in state
        assert state["convergence_target"] == 80

    def test_create_workspace_creates_readme(self, tmp_path, capsys):
        """Test that README.md is created with correct content."""
        workspace = init_workspace.create_workspace(
            topic="Test Topic",
            experts=["typescript", "python"],
            mode="review",
            base_dir=tmp_path
        )

        readme_file = workspace / "README.md"
        assert readme_file.exists()

        readme_content = readme_file.read_text()
        assert "# Expert Feedback Session: Test Topic" in readme_content
        assert "**Mode:** review" in readme_content
        assert "typescript" in readme_content
        assert "python" in readme_content
        assert "Workspace Structure" in readme_content
        assert "state.json" in readme_content
        assert "Web UI" in readme_content

    def test_create_workspace_dated_structure(self, tmp_path, capsys):
        """Test that workspace uses dated directory structure."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        # Should have YYYY/MM/DD structure
        parts = workspace.relative_to(tmp_path).parts
        assert len(parts) >= 4  # YYYY/MM/DD/workspace-name

        # Verify date components
        now = datetime.now()
        assert parts[0] == f"{now.year:04d}"
        assert parts[1] == f"{now.month:02d}"
        assert parts[2] == f"{now.day:02d}"

    def test_create_workspace_multiple_modes(self, tmp_path, capsys):
        """Test workspace creation with different modes."""
        for mode in ["review", "improve", "create"]:
            workspace = init_workspace.create_workspace(
                topic=f"Test {mode}",
                experts=["typescript"],
                mode=mode,
                base_dir=tmp_path
            )

            state_file = workspace / "state.json"
            with open(state_file) as f:
                state = json.load(f)

            assert state["mode"] == mode

    def test_create_workspace_idempotent(self, tmp_path, capsys):
        """Test that creating workspace twice doesn't fail."""
        workspace1 = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        # Creating again should work (exist_ok=True)
        workspace2 = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        # Both should exist
        assert workspace1.exists()
        assert workspace2.exists()

    def test_create_workspace_default_base_dir(self, tmp_path, capsys):
        """Test workspace creation without base_dir uses find_repo_root."""
        with patch('utils.init_workspace.find_repo_root') as mock_find_repo:
            mock_find_repo.return_value = tmp_path

            workspace = init_workspace.create_workspace(
                topic="Test",
                experts=["typescript"],
                base_dir=None
            )

            # Should have called find_repo_root
            mock_find_repo.assert_called_once()

            # Workspace should be under .workspace
            assert workspace.exists()
            assert ".workspace" in str(workspace)

    def test_create_workspace_default_mode(self, tmp_path, capsys):
        """Test that default mode is 'review'."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        with open(state_file) as f:
            state = json.load(f)

        assert state["mode"] == "review"

    def test_create_workspace_prints_output(self, tmp_path, capsys):
        """Test that workspace creation prints expected output."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        captured = capsys.readouterr()
        assert "✅ Workspace created:" in captured.out
        assert "📁 Structure:" in captured.out
        assert "State:" in captured.out
        assert "Iteration:" in captured.out
        assert "Experts:" in captured.out
        assert "Logs:" in captured.out


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_topic(self, tmp_path, capsys):
        """Test workspace creation with empty topic."""
        workspace = init_workspace.create_workspace(
            topic="",
            experts=["typescript"],
            base_dir=tmp_path
        )

        assert workspace.exists()
        # Empty slug should still create workspace
        assert "expert-feedback" in workspace.name

    def test_empty_experts_list(self, tmp_path, capsys):
        """Test workspace creation with no experts raises UnboundLocalError (bug)."""
        # This test documents a bug in the source code where
        # creating workspace with empty experts list causes UnboundLocalError
        # because 'expert' variable is used in f-string without being defined
        with pytest.raises(UnboundLocalError):
            workspace = init_workspace.create_workspace(
                topic="Test",
                experts=[],
                base_dir=tmp_path
            )

    def test_special_characters_in_topic(self, tmp_path, capsys):
        """Test topic with special characters."""
        workspace = init_workspace.create_workspace(
            topic="Test: API & Design!",
            experts=["typescript"],
            base_dir=tmp_path
        )

        assert workspace.exists()
        # Special characters should be slugified
        assert ":" not in workspace.name
        assert "&" not in workspace.name
        assert "test-api-design" in workspace.name

    def test_long_expert_list(self, tmp_path, capsys):
        """Test with many experts."""
        experts = [f"expert-{i}" for i in range(20)]

        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=experts,
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        with open(state_file) as f:
            state = json.load(f)

        assert len(state["experts"]) == 20

        # Verify all expert directories exist
        experts_dir = workspace / "iteration-1" / "experts"
        for expert in experts:
            assert (experts_dir / expert).exists()

    def test_very_long_topic(self, tmp_path, capsys):
        """Test workspace with very long topic name."""
        long_topic = "A" * 200
        workspace = init_workspace.create_workspace(
            topic=long_topic,
            experts=["typescript"],
            base_dir=tmp_path
        )

        assert workspace.exists()
        # Slug should be limited to 50 chars
        slug_part = workspace.name.replace("expert-feedback-", "")
        assert len(slug_part) <= 50

    def test_expert_with_special_chars(self, tmp_path, capsys):
        """Test expert names with special characters."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["type-script", "py_thon", "dx!"],
            base_dir=tmp_path
        )

        experts_dir = workspace / "iteration-1" / "experts"
        # Expert names used as-is for directory creation
        assert (experts_dir / "type-script").exists()
        assert (experts_dir / "py_thon").exists()
        assert (experts_dir / "dx!").exists()


class TestMain:
    """Test main() CLI function."""

    def test_main_basic_args(self, tmp_path, capsys):
        """Test main with basic arguments."""
        with patch('sys.argv', [
            'init_workspace.py',
            '--topic', 'Test Topic',
            '--experts', 'typescript', 'python',
            '--base-dir', str(tmp_path)
        ]):
            result = init_workspace.main()

            assert result == 0
            captured = capsys.readouterr()
            assert "WORKSPACE=" in captured.out

    def test_main_with_mode(self, tmp_path, capsys):
        """Test main with mode argument."""
        with patch('sys.argv', [
            'init_workspace.py',
            '--topic', 'Test',
            '--experts', 'typescript',
            '--mode', 'improve',
            '--base-dir', str(tmp_path)
        ]):
            result = init_workspace.main()
            assert result == 0

    def test_main_default_mode(self, tmp_path, capsys):
        """Test main with default mode."""
        with patch('sys.argv', [
            'init_workspace.py',
            '--topic', 'Test',
            '--experts', 'typescript',
            '--base-dir', str(tmp_path)
        ]):
            result = init_workspace.main()
            assert result == 0

            # Verify default mode is 'review'
            captured = capsys.readouterr()
            workspace_line = [line for line in captured.out.split('\n') if 'WORKSPACE=' in line][0]
            workspace_path = Path(workspace_line.replace('WORKSPACE=', ''))

            state_file = workspace_path / "state.json"
            with open(state_file) as f:
                state = json.load(f)
            assert state["mode"] == "review"

    def test_main_multiple_experts(self, tmp_path, capsys):
        """Test main with multiple experts."""
        with patch('sys.argv', [
            'init_workspace.py',
            '--topic', 'Test',
            '--experts', 'typescript', 'python', 'dx', 'api',
            '--base-dir', str(tmp_path)
        ]):
            result = init_workspace.main()
            assert result == 0

    def test_main_prints_workspace_path(self, tmp_path, capsys):
        """Test that main prints WORKSPACE= for script capture."""
        with patch('sys.argv', [
            'init_workspace.py',
            '--topic', 'Test',
            '--experts', 'typescript',
            '--base-dir', str(tmp_path)
        ]):
            result = init_workspace.main()

            captured = capsys.readouterr()
            assert "WORKSPACE=" in captured.out

            # Extract and verify workspace path
            workspace_line = [line for line in captured.out.split('\n') if 'WORKSPACE=' in line][0]
            workspace_path = workspace_line.replace('WORKSPACE=', '').strip()
            assert Path(workspace_path).exists()


class TestStateJsonStructure:
    """Test state.json structure and fields."""

    def test_state_has_all_required_fields(self, tmp_path, capsys):
        """Test that state.json has all required fields."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            mode="review",
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        with open(state_file) as f:
            state = json.load(f)

        required_fields = [
            "topic", "mode", "experts", "iteration",
            "convergence_percent", "consensus_reached",
            "phase", "expert_results", "created_at",
            "convergence_target"
        ]

        for field in required_fields:
            assert field in state, f"Missing required field: {field}"

    def test_state_created_at_is_valid_iso(self, tmp_path, capsys):
        """Test that created_at is valid ISO format."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        with open(state_file) as f:
            state = json.load(f)

        # Should be parseable as ISO datetime
        from datetime import datetime
        created_at = datetime.fromisoformat(state["created_at"])
        assert created_at is not None

    def test_state_expert_results_is_dict(self, tmp_path, capsys):
        """Test that expert_results is initialized as empty dict."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        state_file = workspace / "state.json"
        with open(state_file) as f:
            state = json.load(f)

        assert isinstance(state["expert_results"], dict)
        assert len(state["expert_results"]) == 0


class TestReadmeContent:
    """Test README.md content and formatting."""

    def test_readme_includes_all_sections(self, tmp_path, capsys):
        """Test that README includes all expected sections."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        readme = workspace / "README.md"
        content = readme.read_text()

        sections = [
            "# Expert Feedback Session:",
            "**Mode:**",
            "**Experts:**",
            "**Created:**",
            "## Workspace Structure",
            "## Web UI",
            "## Progress"
        ]

        for section in sections:
            assert section in content, f"Missing section: {section}"

    def test_readme_includes_file_descriptions(self, tmp_path, capsys):
        """Test that README documents all workspace files."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        readme = workspace / "README.md"
        content = readme.read_text()

        files = [
            "state.json",
            "qa-answers.json",
            "approvals.json",
            "iteration-N/",
            "consolidated.md",
            "logs/",
            "draft-"
        ]

        for file_ref in files:
            assert file_ref in content

    def test_readme_includes_expert_name_example(self, tmp_path, capsys):
        """Test that README uses actual expert names in structure."""
        workspace = init_workspace.create_workspace(
            topic="Test",
            experts=["typescript"],
            base_dir=tmp_path
        )

        readme = workspace / "README.md"
        content = readme.read_text()

        # README should include actual expert name, not placeholder
        assert "typescript/" in content
        assert "review-typescript.md" in content
        assert "state-typescript.json" in content
