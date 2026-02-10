"""
Extended tests for validation scripts (scripts/validation/).

Tests additional validation scripts to increase coverage.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get path to scripts directory
SCRIPTS_DIR = Path(__file__).parent.parent
VALIDATION_DIR = SCRIPTS_DIR / "validation"


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


class TestValidateEchoM365s:
    """Test validate_echo_m365s.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_echo_m365s.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()


class TestValidateEnums:
    """Test validate_enums.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_enums.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateLinks:
    """Test validate_links.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_links.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCheckRoutes:
    """Test check_routes.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "check_routes.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCheckCrossReferences:
    """Test check_cross_references.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "check_cross_references.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCheckLineReferences:
    """Test check_line_references.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "check_line_references.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCheckOldPatterns:
    """Test check_old_patterns.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "check_old_patterns.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCheckTypespecTerms:
    """Test check_typespec_terms.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "check_typespec_terms.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateConsistency:
    """Test validate_consistency.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_consistency.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateDocsAgainstTypespec:
    """Test validate_docs_against_typespec.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_docs_against_typespec.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateModelDocs:
    """Test validate_model_docs.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_model_docs.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateTypespecDocs:
    """Test validate_typespec_docs.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_typespec_docs.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateApiDocsCompleteness:
    """Test validate_api_docs_completeness.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_api_docs_completeness.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestValidateTestInfrastructure:
    """Test validate_test_infrastructure.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "validate_test_infrastructure.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestDetectMisplacedContent:
    """Test detect_misplaced_content.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "detect_misplaced_content.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestExtractContentTypes:
    """Test extract_content_types.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "extract_content_types.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0


class TestCompareContentTypes:
    """Test compare_content_types.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        script = VALIDATION_DIR / "compare_content_types.py"
        if not script.exists():
            pytest.skip("Script not found")

        result = run_script(script, ["--help"])
        assert result.returncode == 0
