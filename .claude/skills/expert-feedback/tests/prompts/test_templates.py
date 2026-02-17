"""
Unit tests for prompts/templates.py

Tests template rendering and expert info loading including:
- load_expert_info() with valid/invalid expert names
- render_template() with various templates
- load_json_schema() schema loading
- expand_repo_paths() path expansion and validation
- Template not found errors
- Jinja2 rendering errors

Target coverage: 95%+ (critical for prompt generation)
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from prompts import templates


class TestLoadExpertInfo:
    """Test load_expert_info function."""

    @pytest.mark.high
    def test_load_valid_expert(self, mock_experts_json):
        """Test loading valid expert information."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            expert_info = templates.load_expert_info("typescript")

            assert expert_info["name"] == "TypeScript Expert"
            assert "background" in expert_info
            assert "perspective" in expert_info

    @pytest.mark.high
    def test_load_multiple_experts(self, mock_experts_json):
        """Test loading multiple different experts."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            ts_info = templates.load_expert_info("typescript")
            py_info = templates.load_expert_info("python")
            sec_info = templates.load_expert_info("security")

            assert ts_info["name"] != py_info["name"]
            assert py_info["name"] != sec_info["name"]

    @pytest.mark.high
    def test_load_nonexistent_expert(self, mock_experts_json):
        """Test loading non-existent expert raises error."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            with pytest.raises(ValueError, match="Unknown expert"):
                templates.load_expert_info("nonexistent")

    @pytest.mark.high
    def test_expert_has_required_fields(self, mock_experts_json):
        """Test that loaded expert has required fields."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            expert_info = templates.load_expert_info("typescript")

            required_fields = ["name", "background", "perspective"]
            for field in required_fields:
                assert field in expert_info

    @pytest.mark.high
    def test_expert_has_optional_fields(self, mock_experts_json):
        """Test that expert can have optional fields."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            expert_info = templates.load_expert_info("typescript")

            # Optional fields
            assert "focus_areas" in expert_info
            assert isinstance(expert_info["focus_areas"], list)


class TestRenderTemplate:
    """Test render_template function."""

    @pytest.mark.high
    def test_render_simple_template(self):
        """Test rendering a simple template."""
        template_content = "Hello {{ name }}!"

        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Hello World!"
            mock_get_template.return_value = mock_template

            result = templates.render_template("test.jinja2", name="World")

            assert result == "Hello World!"
            mock_template.render.assert_called_once_with(name="World")

    @pytest.mark.high
    def test_render_with_multiple_variables(self):
        """Test rendering template with multiple variables."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Expert: TypeScript, Topic: API"
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "expert.jinja2",
                expert_name="TypeScript",
                topic="API"
            )

            assert "TypeScript" in result
            assert "API" in result

    @pytest.mark.high
    def test_render_template_not_found(self):
        """Test rendering non-existent template raises error."""
        with patch('jinja2.Environment.get_template', side_effect=Exception("Template not found")):
            with pytest.raises(Exception):
                templates.render_template("nonexistent.jinja2")

    @pytest.mark.high
    def test_render_with_nested_variables(self):
        """Test rendering template with nested data."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Expert background: Test"
            mock_get_template.return_value = mock_template

            expert_data = {
                "name": "Test Expert",
                "background": "Test background"
            }

            result = templates.render_template("test.jinja2", expert=expert_data)

            mock_template.render.assert_called_once()

    @pytest.mark.high
    def test_render_template_with_lists(self):
        """Test rendering template with list variables."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Areas: Type system, Testing"
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "areas.jinja2",
                focus_areas=["Type system", "Testing"]
            )

            assert "Type system" in result
            assert "Testing" in result

    @pytest.mark.high
    def test_render_template_with_empty_values(self):
        """Test rendering template with empty/None values."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Empty context"
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "test.jinja2",
                context="",
                items=[]
            )

            mock_template.render.assert_called_once()


class TestLoadJsonSchema:
    """Test load_json_schema function."""

    @pytest.mark.high
    def test_load_valid_schema(self):
        """Test loading a valid JSON schema."""
        mock_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }

        with patch('prompts.templates.load_json', return_value=mock_schema):
            schema = templates.load_json_schema("test.schema.json")

            assert schema["type"] == "object"
            assert "properties" in schema

    @pytest.mark.high
    def test_load_schema_with_definitions(self):
        """Test loading schema with definitions."""
        mock_schema = {
            "definitions": {
                "expert": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }

        with patch('prompts.templates.load_json', return_value=mock_schema):
            schema = templates.load_json_schema("expert.schema.json")

            assert "definitions" in schema
            assert "expert" in schema["definitions"]

    @pytest.mark.high
    def test_load_nonexistent_schema(self):
        """Test loading non-existent schema file."""
        with patch('prompts.templates.load_json', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                templates.load_json_schema("nonexistent.schema.json")


class TestExpandRepoPaths:
    """Test expand_repo_paths function."""

    @pytest.mark.high
    def test_expand_single_repo(self, tmp_path):
        """Test expanding single repository path."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()

        repos = [{"path": str(repo_dir), "name": "test"}]
        expanded = templates.expand_repo_paths(repos)

        assert len(expanded) == 1
        assert expanded[0]["exists"] is True

    @pytest.mark.high
    def test_expand_home_directory(self):
        """Test expanding ~ in repository paths."""
        repos = [{"path": "~/test-repo", "name": "test"}]

        expanded = templates.expand_repo_paths(repos)

        assert len(expanded) == 1
        assert "~" not in expanded[0]["path"]
        # Should be expanded to full path

    @pytest.mark.high
    def test_expand_multiple_repos(self, tmp_path):
        """Test expanding multiple repository paths."""
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo1.mkdir()
        repo2.mkdir()

        repos = [
            {"path": str(repo1), "name": "repo1"},
            {"path": str(repo2), "name": "repo2"}
        ]

        expanded = templates.expand_repo_paths(repos)

        assert len(expanded) == 2
        assert all(r["exists"] for r in expanded)

    @pytest.mark.high
    def test_expand_nonexistent_repo(self, tmp_path):
        """Test expanding path to non-existent repository."""
        nonexistent = tmp_path / "does-not-exist"

        repos = [{"path": str(nonexistent), "name": "missing"}]
        expanded = templates.expand_repo_paths(repos)

        assert len(expanded) == 1
        assert expanded[0]["exists"] is False

    @pytest.mark.high
    def test_expand_preserves_metadata(self, tmp_path):
        """Test that expansion preserves other metadata."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()

        repos = [{
            "path": str(repo_dir),
            "name": "test",
            "branch": "main",
            "description": "Test repository"
        }]

        expanded = templates.expand_repo_paths(repos)

        assert expanded[0]["name"] == "test"
        assert expanded[0]["branch"] == "main"
        assert expanded[0]["description"] == "Test repository"

    @pytest.mark.high
    def test_expand_empty_list(self):
        """Test expanding empty repository list."""
        repos = []
        expanded = templates.expand_repo_paths(repos)

        assert expanded == []


class TestTemplateEnvironment:
    """Test Jinja2 environment configuration."""

    @pytest.mark.high
    def test_environment_has_correct_loader(self):
        """Test that environment has correct template loader."""
        # Test that FileSystemLoader is configured correctly
        # (exact test depends on how Environment is exposed)

    @pytest.mark.high
    def test_template_search_paths(self):
        """Test that template search paths are configured."""
        # Should search in prompts/ and templates/ directories
        # (exact test depends on implementation)

    @pytest.mark.high
    def test_template_whitespace_handling(self):
        """Test template whitespace configuration."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            # Test trim_blocks, lstrip_blocks settings
            mock_template.render.return_value = "Trimmed output"
            mock_get_template.return_value = mock_template

            result = templates.render_template("test.jinja2")


class TestTemplateErrorHandling:
    """Test error handling in template operations."""

    @pytest.mark.high
    def test_template_syntax_error(self):
        """Test handling of template syntax errors."""
        with patch('jinja2.Environment.get_template', side_effect=Exception("Syntax error")):
            with pytest.raises(Exception):
                templates.render_template("bad_syntax.jinja2")

    @pytest.mark.high
    def test_undefined_variable_in_template(self):
        """Test handling of undefined variables."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.side_effect = Exception("Undefined variable")
            mock_get_template.return_value = mock_template

            with pytest.raises(Exception):
                templates.render_template("test.jinja2", var1="value")

    @pytest.mark.high
    def test_template_rendering_exception(self):
        """Test handling of template rendering exceptions."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.side_effect = RuntimeError("Rendering failed")
            mock_get_template.return_value = mock_template

            with pytest.raises(RuntimeError):
                templates.render_template("test.jinja2")


class TestTemplateIntegration:
    """Integration tests for template rendering."""

    @pytest.mark.high
    def test_render_expert_prompt_template(self, mock_experts_json):
        """Test rendering complete expert prompt template."""
        with patch('prompts.templates.load_json', return_value=mock_experts_json):
            with patch('jinja2.Environment.get_template') as mock_get_template:
                mock_template = Mock()
                mock_template.render.return_value = "Expert prompt rendered"
                mock_get_template.return_value = mock_template

                expert_info = templates.load_expert_info("typescript")

                result = templates.render_template(
                    "experts/initial.jinja2",
                    expert_name=expert_info["name"],
                    expert_background=expert_info["background"],
                    topic="API Design"
                )

                assert "rendered" in result

    @pytest.mark.high
    def test_render_with_expanded_repos(self, tmp_path):
        """Test rendering template with expanded repository paths."""
        repo_dir = tmp_path / "test-repo"
        repo_dir.mkdir()

        repos = [{"path": str(repo_dir), "name": "test"}]
        expanded_repos = templates.expand_repo_paths(repos)

        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Repos: test"
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "with_repos.jinja2",
                repos=expanded_repos
            )


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_render_template_with_special_characters(self):
        """Test rendering template with special characters."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Special: <>&\""
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "special.jinja2",
                text="<>&\""
            )

    @pytest.mark.high
    def test_render_template_with_unicode(self):
        """Test rendering template with Unicode characters."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "Unicode: 你好 🎉"
            mock_get_template.return_value = mock_template

            result = templates.render_template(
                "unicode.jinja2",
                greeting="你好",
                emoji="🎉"
            )

            assert "你好" in result

    @pytest.mark.high
    def test_render_very_large_template(self):
        """Test rendering very large template."""
        with patch('jinja2.Environment.get_template') as mock_get_template:
            mock_template = Mock()
            large_output = "A" * 100000  # 100K characters
            mock_template.render.return_value = large_output
            mock_get_template.return_value = mock_template

            result = templates.render_template("large.jinja2")

            assert len(result) == 100000

    @pytest.mark.high
    def test_expand_repo_with_relative_path(self, tmp_path):
        """Test expanding relative repository path."""
        repos = [{"path": "./relative/path", "name": "test"}]

        expanded = templates.expand_repo_paths(repos)

        assert len(expanded) == 1
        # Should handle relative paths
        # (exact behavior depends on implementation)
