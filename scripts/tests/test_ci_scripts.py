"""
Tests for CI scripts (scripts/ci/ and root scripts).

Tests CI and utility scripts to increase coverage.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get path to scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent


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


class TestRunCoverage:
    """Test run_coverage.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = SCRIPTS_DIR / "run_coverage.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_summary_flag_works(self):
        """--summary should work"""
        script = SCRIPTS_DIR / "run_coverage.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--summary"])
        # May have no results, but should not crash
        assert result.returncode == 0

    def test_scripts_flag_documented(self):
        """--scripts flag should be documented"""
        script = SCRIPTS_DIR / "run_coverage.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert "--scripts" in result.stdout
