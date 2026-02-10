"""
Extended tests for code generation scripts (scripts/codegen/).

Tests additional codegen scripts to increase coverage.
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


class TestExtractDocExamples:
    """Test extract_doc_examples.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = CODEGEN_DIR / "extract_doc_examples.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_dry_run_flag_required(self):
        """MUST have --dry-run - file-modifying scripts require it"""
        script = CODEGEN_DIR / "extract_doc_examples.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert "--dry-run" in result.stdout, \
            "extract_doc_examples.py modifies files and MUST have --dry-run flag"


class TestGenerateForTypescript:
    """Test generate_for_typescript.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = CODEGEN_DIR / "generate_for_typescript.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestGenerateSdk:
    """Test generate_sdk.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = CODEGEN_DIR / "generate_sdk.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0

    def test_dry_run_flag_required(self):
        """MUST have --dry-run - file-modifying scripts require it"""
        script = CODEGEN_DIR / "generate_sdk.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert "--dry-run" in result.stdout, \
            "generate_sdk.py modifies files and MUST have --dry-run flag"


class TestMergeApiDocs:
    """Test merge_api_docs.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = CODEGEN_DIR / "merge_api_docs.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
