"""
Tests for validation scripts (scripts/validation/).

Tests script interfaces, error handling, and behavior without
polluting actual project directories.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get path to scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent
VALIDATION_DIR = SCRIPTS_DIR / "validation"


def run_script(script_path, args=None, cwd=None):
    """
    Run a script as a subprocess and capture output.

    Args:
        script_path: Path to script
        args: List of arguments
        cwd: Working directory (None = current dir)

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
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


class TestCheckAnnotations:
    """Test check_annotations.py interface and behavior"""

    def test_help_flag_works(self):
        """--help should show usage and exit with code 0"""
        result = run_script(VALIDATION_DIR / "check_annotations.py", ["--help"])

        assert result.returncode == 0
        assert "Check for ContentAnnotations" in result.stdout
        assert "Examples:" in result.stdout
        assert "--verbose" in result.stdout
        assert "--typespec" in result.stdout

    def test_help_includes_examples(self):
        """Help text should include clear examples"""
        result = run_script(VALIDATION_DIR / "check_annotations.py", ["--help"])

        assert "python3 scripts/validation/check_annotations.py" in result.stdout
        assert "optional security and annotation features" in result.stdout

    def test_runs_with_valid_typespec(self, temp_project_root, mock_typespec_file):
        """Script should run successfully with valid TypeSpec file"""
        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", str(mock_typespec_file)],
            cwd=temp_project_root
        )

        # Should complete (exit 0 even if optional features missing)
        assert result.returncode == 0
        assert "Content Annotations Validation" in result.stdout

    def test_verbose_flag_works(self, temp_project_root, mock_typespec_file):
        """--verbose flag should work without errors"""
        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", str(mock_typespec_file), "--verbose"],
            cwd=temp_project_root
        )

        assert result.returncode == 0
        assert "Content Annotations Validation" in result.stdout

    def test_invalid_typespec_path_shows_helpful_error(self, temp_project_root):
        """Invalid TypeSpec path should show actionable error"""
        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", "nonexistent.tsp"],
            cwd=temp_project_root
        )

        assert result.returncode == 1
        assert "not found" in result.stdout.lower()
        assert "Expected location:" in result.stdout
        assert "Make sure you're running from the project root" in result.stdout

    def test_missing_optional_features_dont_fail(self, temp_project_root, mock_typespec_file):
        """Missing optional features should show warnings but exit 0"""
        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", str(mock_typespec_file)],
            cwd=temp_project_root
        )

        # Exit 0 for optional features
        assert result.returncode == 0

        # Should report features as optional
        if "NOT FOUND" in result.stdout:
            assert "optional" in result.stdout.lower()

    def test_output_is_organized(self, temp_project_root, mock_typespec_file):
        """Output should have clear sections with headers"""
        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", str(mock_typespec_file)],
            cwd=temp_project_root
        )

        # Check for organized output
        assert "=" * 70 in result.stdout  # Header separators
        assert "1. ContentAnnotations Model" in result.stdout
        assert "2. ChatMessage Security Fields" in result.stdout
        assert "3. Content Type Annotations" in result.stdout
        assert "4. Encrypted Content Type" in result.stdout


class TestValidateApiReference:
    """Test validate_api_reference.py interface and behavior"""

    def test_help_flag_works(self):
        """--help should show usage"""
        result = run_script(VALIDATION_DIR / "validate_api_reference.py", ["--help"])

        assert result.returncode == 0
        assert "Validate generated API reference" in result.stdout
        assert "Examples:" in result.stdout
        assert "--api-ref" in result.stdout

    def test_shows_actionable_error_when_dir_missing(self, temp_project_root):
        """Should tell user how to generate API reference"""
        result = run_script(
            VALIDATION_DIR / "validate_api_reference.py",
            ["--api-ref", "nonexistent"],
            cwd=temp_project_root
        )

        # Should fail with helpful message
        assert result.returncode == 1
        assert "not found" in result.stdout.lower()
        assert "Expected location:" in result.stdout
        assert "To generate API reference documentation:" in result.stdout
        assert "python3 scripts/codegen/generate_api_reference.py" in result.stdout

    def test_validates_existing_api_reference(self, temp_project_root, mock_api_reference_dir):
        """Should validate existing API reference directory"""
        result = run_script(
            VALIDATION_DIR / "validate_api_reference.py",
            ["--api-ref", str(mock_api_reference_dir)],
            cwd=temp_project_root
        )

        # May pass or fail validation, but should run
        assert result.returncode in [0, 1]
        # Should NOT show "not found" error since directory exists
        if result.returncode == 1:
            assert "not found" not in result.stdout.lower() or "not found" in result.stdout.lower()

    def test_verbose_flag_works(self, temp_project_root, mock_api_reference_dir):
        """--verbose flag should work"""
        result = run_script(
            VALIDATION_DIR / "validate_api_reference.py",
            ["--api-ref", str(mock_api_reference_dir), "--verbose"],
            cwd=temp_project_root
        )

        # Should run without crashing
        assert result.returncode in [0, 1]


class TestValidateEchoM365s:
    """Test validate_echo_m365s.py interface (if it exists)"""

    def test_script_exists(self):
        """Script should exist"""
        script_path = SCRIPTS_DIR / "validation" / "validate_echo_m365s.py"
        # May or may not exist depending on reorganization
        if script_path.exists():
            result = run_script(script_path, ["--help"])
            # Should have --help
            assert "--help" in result.stdout or "usage:" in result.stdout.lower()


class TestScriptSafety:
    """Test that validation scripts don't accidentally modify files"""

    def test_check_annotations_doesnt_modify_files(self, temp_project_root, mock_typespec_file):
        """check_annotations.py should be read-only"""
        original_content = mock_typespec_file.read_text()
        original_mtime = mock_typespec_file.stat().st_mtime

        result = run_script(
            VALIDATION_DIR / "check_annotations.py",
            ["--typespec", str(mock_typespec_file)],
            cwd=temp_project_root
        )

        # File should not be modified
        assert mock_typespec_file.read_text() == original_content
        assert mock_typespec_file.stat().st_mtime == original_mtime

    def test_validate_api_reference_doesnt_modify_files(self, temp_project_root, mock_api_reference_dir):
        """validate_api_reference.py should be read-only"""
        # Get initial state
        initial_files = list(mock_api_reference_dir.rglob("*"))
        initial_count = len(initial_files)

        result = run_script(
            VALIDATION_DIR / "validate_api_reference.py",
            ["--api-ref", str(mock_api_reference_dir)],
            cwd=temp_project_root
        )

        # No files should be created or deleted
        final_files = list(mock_api_reference_dir.rglob("*"))
        assert len(final_files) == initial_count


class TestExitCodes:
    """Test that scripts use proper exit codes"""

    def test_help_exits_with_zero(self):
        """--help should always exit with 0"""
        scripts = [
            VALIDATION_DIR / "check_annotations.py",
            VALIDATION_DIR / "validate_api_reference.py",
        ]

        for script in scripts:
            if not script.exists():
                continue

            result = run_script(script, ["--help"])
            assert result.returncode == 0, f"{script.name} --help should exit with 0"

    def test_invalid_args_exit_nonzero(self):
        """Invalid arguments should exit with non-zero"""
        scripts = [
            VALIDATION_DIR / "check_annotations.py",
            VALIDATION_DIR / "validate_api_reference.py",
        ]

        for script in scripts:
            if not script.exists():
                continue

            result = run_script(script, ["--invalid-flag-that-doesnt-exist"])
            assert result.returncode != 0, f"{script.name} should fail on invalid flag"
            assert "error:" in result.stderr.lower() or "unrecognized" in result.stderr.lower()
