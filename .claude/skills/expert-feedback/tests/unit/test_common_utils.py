"""
Tests for common.py utility functions.

Focuses on pure utility functions that don't require I/O or async operations.
"""
import pytest
import re
from pathlib import Path
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.agent_logger import generate_correlation_id
from agent_logging.token_tracker import extract_usage_from_sdk_result
from prompts.templates import expand_repo_paths


class TestGenerateCorrelationId:
    """Test correlation ID generation."""

    def test_generates_valid_format(self):
        """Test that correlation ID has valid format."""
        corr_id = generate_correlation_id()

        # Should be a string
        assert isinstance(corr_id, str)

        # Should have reasonable length (typically 8-16 chars)
        assert 8 <= len(corr_id) <= 32

        # Should be alphanumeric or contain hyphens
        assert re.match(r'^[a-zA-Z0-9\-]+$', corr_id)

    def test_generates_unique_ids(self):
        """Test that successive calls generate different IDs."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        assert id1 != id2

    def test_multiple_generations(self):
        """Test generating multiple IDs."""
        ids = [generate_correlation_id() for _ in range(100)]

        # All should be unique
        assert len(set(ids)) == 100

        # All should be non-empty
        assert all(ids)


class TestExtractUsageFromSdkResult:
    """Test SDK result usage extraction."""

    def test_extract_basic_usage(self):
        """Test extracting basic token usage."""
        result = {
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500
            }
        }

        usage = extract_usage_from_sdk_result(result)

        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.cache_creation_tokens == 0
        assert usage.cache_read_tokens == 0

    def test_extract_usage_with_cache(self):
        """Test extracting usage with cache metrics."""
        result = {
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_input_tokens": 200,  # SDK field name
                "cache_read_input_tokens": 300  # SDK field name
            }
        }

        usage = extract_usage_from_sdk_result(result)

        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.cache_creation_tokens == 200  # Our field name
        assert usage.cache_read_tokens == 300  # Our field name

    def test_extract_usage_missing_fields(self):
        """Test handling missing fields."""
        result = {
            "usage": {
                "input_tokens": 1000
                # output_tokens missing
            }
        }

        usage = extract_usage_from_sdk_result(result)

        assert usage.input_tokens == 1000
        assert usage.output_tokens == 0  # Should default to 0

    def test_extract_usage_empty_result(self):
        """Test handling empty result."""
        result = {}

        usage = extract_usage_from_sdk_result(result)

        # Should have all zeros
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0


class TestExpandRepoPaths:
    """Test repository path expansion."""

    def test_expand_single_repo(self):
        """Test expanding a single repo path."""
        repos = [
            {
                "path": "src/**/*.ts",
                "description": "TypeScript sources"
            }
        ]

        expanded = expand_repo_paths(repos)

        assert isinstance(expanded, list)
        assert len(expanded) >= 1
        # Original repo should be included
        assert any(r["path"] == "src/**/*.ts" for r in expanded)

    def test_expand_multiple_repos(self):
        """Test expanding multiple repo paths."""
        repos = [
            {"path": "src/**/*.ts", "description": "TypeScript"},
            {"path": "tests/**/*.test.ts", "description": "Tests"}
        ]

        expanded = expand_repo_paths(repos)

        assert len(expanded) >= 2
        # Both should be present
        assert any(r["path"] == "src/**/*.ts" for r in expanded)
        assert any(r["path"] == "tests/**/*.test.ts" for r in expanded)

    def test_preserves_repo_metadata(self):
        """Test that metadata is preserved during expansion."""
        repos = [
            {
                "path": "src/**/*.ts",
                "description": "TypeScript sources",
                "language": "typescript"
            }
        ]

        expanded = expand_repo_paths(repos)

        # Find the expanded repo
        ts_repo = next((r for r in expanded if "typescript" in r.get("path", "").lower() or r.get("language") == "typescript"), None)

        assert ts_repo is not None
        # Description should be preserved
        assert "description" in ts_repo or "language" in ts_repo

    def test_handles_empty_list(self):
        """Test handling empty repository list."""
        repos = []

        expanded = expand_repo_paths(repos)

        assert isinstance(expanded, list)
        assert len(expanded) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
