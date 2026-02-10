"""
Extended tests for test generation scripts (scripts/testgen/).

Tests additional testgen scripts to increase coverage.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get path to scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent
TESTGEN_DIR = SCRIPTS_DIR / "testgen"


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


class TestGenerateEvalDatasets:
    """Test generate_eval_datasets.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = TESTGEN_DIR / "generate_eval_datasets.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_dry_run_flag_required(self):
        """MUST have --dry-run - file-modifying scripts require it"""
        script = TESTGEN_DIR / "generate_eval_datasets.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert "--dry-run" in result.stdout, \
            "generate_eval_datasets.py modifies files and MUST have --dry-run flag"


class TestGenerateGoldenDatasets:
    """Test generate_golden_datasets.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = TESTGEN_DIR / "generate_golden_datasets.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0

    def test_dry_run_flag_required(self):
        """MUST have --dry-run - file-modifying scripts require it"""
        script = TESTGEN_DIR / "generate_golden_datasets.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert "--dry-run" in result.stdout, \
            "generate_golden_datasets.py modifies files and MUST have --dry-run flag"


class TestReorganizeTestStructure:
    """Test reorganize_test_structure.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = TESTGEN_DIR / "reorganize_test_structure.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestVerifyReorganization:
    """Test verify_reorganization.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = TESTGEN_DIR / "verify_reorganization.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
