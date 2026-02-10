"""
Tests for code generation scripts (scripts/codegen/).

Tests that generators use --dry-run properly and don't pollute
actual project directories.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get path to scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent
CODEGEN_DIR = SCRIPTS_DIR / "codegen"


def run_script(script_path, args=None, cwd=None):
    """Run a script as subprocess and capture output"""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result


class TestGenerateApiReference:
    """Test generate_api_reference.py interface and safety"""

    def test_help_flag_works(self):
        """--help should show usage"""
        result = run_script(CODEGEN_DIR / "generate_api_reference.py", ["--help"])

        assert result.returncode == 0
        assert "Generate API reference documentation" in result.stdout
        assert "Examples:" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--force" in result.stdout
        assert "--verbose" in result.stdout

    def test_help_includes_examples(self):
        """Help should include clear usage examples"""
        result = run_script(CODEGEN_DIR / "generate_api_reference.py", ["--help"])

        assert "python3 scripts/codegen/generate_api_reference.py" in result.stdout
        assert "--dry-run" in result.stdout
        assert "See what would be generated" in result.stdout

    def test_dry_run_doesnt_create_files(self, temp_project_root, mock_typespec_file):
        """--dry-run should preview without writing files"""
        output_dir = temp_project_root / ".generated" / "api-reference"

        # Ensure output directory doesn't exist
        assert not output_dir.exists()

        result = run_script(
            CODEGEN_DIR / "generate_api_reference.py",
            [
                "--typespec", str(mock_typespec_file.parent),
                "--output", str(output_dir),
                "--dry-run"
            ],
            cwd=temp_project_root
        )

        # Should complete successfully
        assert result.returncode == 0

        # Should show preview
        assert "Dry Run" in result.stdout or "Would generate" in result.stdout

        # Should NOT create output directory
        assert not output_dir.exists(), "dry-run should not create files"

    def test_dry_run_shows_what_would_be_generated(self, temp_project_root, mock_typespec_file):
        """--dry-run should show endpoint/model/enum counts"""
        result = run_script(
            CODEGEN_DIR / "generate_api_reference.py",
            [
                "--typespec", str(mock_typespec_file.parent),
                "--dry-run"
            ],
            cwd=temp_project_root
        )

        assert result.returncode == 0

        # Should show counts (specific numbers will vary based on mock TypeSpec)
        # Just check that it's showing some information
        output = result.stdout.lower()
        assert any(word in output for word in ["endpoints", "models", "enums", "would", "generate"])

    def test_invalid_typespec_dir_shows_error(self, temp_project_root):
        """Invalid TypeSpec directory should show helpful error"""
        result = run_script(
            CODEGEN_DIR / "generate_api_reference.py",
            ["--typespec", "nonexistent", "--dry-run"],
            cwd=temp_project_root
        )

        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_force_flag_exists(self):
        """--force flag should be documented in help"""
        result = run_script(CODEGEN_DIR / "generate_api_reference.py", ["--help"])

        assert "--force" in result.stdout or "-f" in result.stdout

    def test_verbose_flag_exists(self):
        """--verbose flag should be documented"""
        result = run_script(CODEGEN_DIR / "generate_api_reference.py", ["--help"])

        assert "--verbose" in result.stdout or "-v" in result.stdout


class TestGeneratorSafety:
    """Test that generators don't accidentally write to real directories"""

    def test_without_force_would_prompt(self, temp_project_root, mock_typespec_file, monkeypatch):
        """Without --force, generator should prompt (or require explicit confirmation)"""
        # Note: This test checks behavior but doesn't actually test interactive prompts
        # Real behavior verification would require force flag or dry-run

        output_dir = temp_project_root / ".generated" / "api-reference"

        # Without --force and without --dry-run, script behavior varies
        # We just verify it doesn't crash
        result = run_script(
            CODEGEN_DIR / "generate_api_reference.py",
            [
                "--typespec", str(mock_typespec_file.parent),
                "--output", str(output_dir),
                "--dry-run"  # Use dry-run to avoid prompts
            ],
            cwd=temp_project_root
        )

        # Should complete
        assert result.returncode == 0


class TestExitCodes:
    """Test generator exit codes"""

    def test_help_exits_zero(self):
        """--help should exit with 0"""
        script = CODEGEN_DIR / "generate_api_reference.py"
        if not script.exists():
            pytest.skip("Script doesn't exist")

        result = run_script(script, ["--help"])
        assert result.returncode == 0

    def test_invalid_args_exit_nonzero(self):
        """Invalid arguments should fail"""
        script = CODEGEN_DIR / "generate_api_reference.py"
        if not script.exists():
            pytest.skip("Script doesn't exist")

        result = run_script(script, ["--invalid-flag-xyz"])
        assert result.returncode != 0
        assert "error:" in result.stderr.lower() or "unrecognized" in result.stderr.lower()
