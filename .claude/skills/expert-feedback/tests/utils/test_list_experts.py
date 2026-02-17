"""
Comprehensive tests for utils/list_experts.py

Tests expert listing functionality including:
- Category name and description generation
- Expert loading and categorization
- Text and JSON output formatting
- CLI interface
- Edge cases and error handling

Target coverage: 90%+
"""
import pytest
import json
from pathlib import Path
import sys
from io import StringIO
from unittest.mock import patch, mock_open

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from utils import list_experts


class TestGetCategoryName:
    """Test category name generation."""

    @pytest.mark.high
    def test_basic_category_name(self):
        """Test basic category name conversion."""
        assert list_experts.get_category_name("language-sdks") == "Language Sdks Experts"
        assert list_experts.get_category_name("llm-clients") == "Llm Clients Experts"

    @pytest.mark.high
    def test_single_word_category(self):
        """Test single word category."""
        assert list_experts.get_category_name("general") == "General Experts"
        assert list_experts.get_category_name("middleware") == "Middleware Experts"

    @pytest.mark.medium
    def test_multiple_dashes(self):
        """Test category with multiple dashes."""
        assert list_experts.get_category_name("multi-agent-frameworks") == "Multi Agent Frameworks Experts"

    @pytest.mark.low
    def test_empty_category(self):
        """Test empty category name."""
        assert list_experts.get_category_name("") == " Experts"


class TestGetCategoryDescription:
    """Test category description generation."""

    @pytest.mark.high
    def test_known_categories(self):
        """Test all known category descriptions."""
        descriptions = {
            "language-sdks": "Experts in language-specific SDK patterns and idioms",
            "llm-clients": "Experts in LLM provider client libraries (OpenAI, Anthropic, etc.)",
            "agent-frameworks": "Experts in agent orchestration frameworks (LangChain, etc.)",
            "autonomous-agents": "Experts in long-running AI agents for task automation and code generation",
            "multi-agent-frameworks": "Experts in multi-agent coordination, collaboration, and role-based orchestration",
            "agent-hosting": "Experts in agent hosting platforms (Microsoft 365 Agents, etc.)",
            "middleware": "Experts in middleware and integration frameworks",
            "prompt-formats": "Experts in agent serialization (Prompty, Semantic Kernel, etc.)",
            "chat-ui": "Experts in chat interface libraries (Bot Framework, etc.)",
            "evaluation": "Experts in LLM/agent evaluation frameworks",
            "observability": "Experts in LLM/agent monitoring and tracing",
            "api-specs": "Experts in LLM/agent REST API specifications",
            "general": "Cross-cutting expertise (DX, beginner-friendly, etc.)"
        }

        for cat_id, expected_desc in descriptions.items():
            assert list_experts.get_category_description(cat_id) == expected_desc

    @pytest.mark.medium
    def test_unknown_category_fallback(self):
        """Test fallback description for unknown categories."""
        assert list_experts.get_category_description("unknown-category") == "Experts in unknown-category"
        assert list_experts.get_category_description("custom") == "Experts in custom"

    @pytest.mark.low
    def test_empty_category_description(self):
        """Test empty category description."""
        assert list_experts.get_category_description("") == "Experts in "


class TestLoadExperts:
    """Test expert loading."""

    @pytest.mark.high
    def test_load_experts_success(self, monkeypatch, tmp_path):
        """Test successfully loading experts."""
        sample_experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "background": "TS specialist",
                "category": "language-sdks"
            }
        }

        # Mock load_json to return sample data
        def mock_load_json(path):
            return sample_experts

        monkeypatch.setattr("utils.list_experts.load_json", mock_load_json)

        experts = list_experts.load_experts()
        assert experts == sample_experts
        assert "typescript" in experts

    @pytest.mark.medium
    def test_load_experts_uses_correct_path(self, monkeypatch):
        """Test that load_experts constructs correct file path."""
        # Mock load_json to verify it's called with correct path structure
        called_paths = []

        def mock_load_json(path):
            called_paths.append(str(path))
            return {"test": {"name": "Test"}}

        monkeypatch.setattr("utils.list_experts.load_json", mock_load_json)

        list_experts.load_experts()

        # Verify load_json was called
        assert len(called_paths) == 1
        # Path should end with experts.json
        assert called_paths[0].endswith("experts.json")


class TestCategorizeExperts:
    """Test expert categorization."""

    @pytest.mark.high
    def test_categorize_single_expert(self):
        """Test categorizing a single expert."""
        experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "background": "TS specialist",
                "category": "language-sdks",
                "repos": [{"path": "src/**/*.ts"}]
            }
        }

        categorized = list_experts.categorize_experts(experts)

        assert "language-sdks" in categorized
        assert len(categorized["language-sdks"]) == 1
        assert categorized["language-sdks"][0]["id"] == "typescript"
        assert categorized["language-sdks"][0]["name"] == "TypeScript Expert"
        assert categorized["language-sdks"][0]["background"] == "TS specialist"
        assert categorized["language-sdks"][0]["repos"] == 1

    @pytest.mark.high
    def test_categorize_multiple_experts_same_category(self):
        """Test categorizing multiple experts in same category."""
        experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "category": "language-sdks"
            },
            "python": {
                "name": "Python Expert",
                "category": "language-sdks"
            }
        }

        categorized = list_experts.categorize_experts(experts)

        assert "language-sdks" in categorized
        assert len(categorized["language-sdks"]) == 2
        expert_ids = [e["id"] for e in categorized["language-sdks"]]
        assert "typescript" in expert_ids
        assert "python" in expert_ids

    @pytest.mark.high
    def test_categorize_multiple_categories(self):
        """Test categorizing experts across multiple categories."""
        experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "category": "language-sdks"
            },
            "openai": {
                "name": "OpenAI Expert",
                "category": "llm-clients"
            },
            "langchain": {
                "name": "LangChain Expert",
                "category": "agent-frameworks"
            }
        }

        categorized = list_experts.categorize_experts(experts)

        assert len(categorized) == 3
        assert "language-sdks" in categorized
        assert "llm-clients" in categorized
        assert "agent-frameworks" in categorized

    @pytest.mark.medium
    def test_categorize_missing_category_defaults_to_general(self):
        """Test that experts without category go to 'general'."""
        experts = {
            "expert1": {
                "name": "Expert Without Category"
            }
        }

        categorized = list_experts.categorize_experts(experts)

        assert "general" in categorized
        assert len(categorized["general"]) == 1
        assert categorized["general"][0]["id"] == "expert1"

    @pytest.mark.medium
    def test_categorize_missing_optional_fields(self):
        """Test handling of missing optional fields."""
        experts = {
            "minimal": {
                "name": "Minimal Expert"
                # Missing: background, repos, category
            }
        }

        categorized = list_experts.categorize_experts(experts)

        expert = categorized["general"][0]
        assert expert["background"] == ""
        assert expert["repos"] == 0

    @pytest.mark.medium
    def test_categorize_empty_repos_list(self):
        """Test expert with empty repos list."""
        experts = {
            "expert1": {
                "name": "Expert",
                "category": "general",
                "repos": []
            }
        }

        categorized = list_experts.categorize_experts(experts)
        assert categorized["general"][0]["repos"] == 0

    @pytest.mark.high
    def test_categorize_sorted_output(self):
        """Test that categories are sorted."""
        experts = {
            "e1": {"name": "E1", "category": "zzz"},
            "e2": {"name": "E2", "category": "aaa"},
            "e3": {"name": "E3", "category": "mmm"}
        }

        categorized = list_experts.categorize_experts(experts)
        categories = list(categorized.keys())

        assert categories == sorted(categories)
        assert categories == ["aaa", "mmm", "zzz"]

    @pytest.mark.low
    def test_categorize_empty_experts(self):
        """Test categorizing empty experts dict."""
        categorized = list_experts.categorize_experts({})
        assert categorized == {}


class TestFormatText:
    """Test text output formatting."""

    @pytest.mark.high
    def test_format_text_basic(self):
        """Test basic text formatting."""
        categorized = {
            "language-sdks": [
                {"id": "typescript", "name": "TypeScript Expert", "background": "TS", "repos": 1}
            ]
        }

        output = list_experts.format_text(categorized)

        assert "Available Expert Reviewers" in output
        assert "Language Sdks Experts" in output
        assert "typescript" in output
        assert "TypeScript Expert" in output
        assert "Total: 1 experts" in output

    @pytest.mark.high
    def test_format_text_multiple_categories(self):
        """Test text formatting with multiple categories."""
        categorized = {
            "language-sdks": [
                {"id": "typescript", "name": "TS Expert", "background": "", "repos": 0}
            ],
            "llm-clients": [
                {"id": "openai", "name": "OpenAI Expert", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_text(categorized)

        assert "Language Sdks Experts" in output
        assert "Llm Clients Experts" in output
        assert "typescript" in output
        assert "openai" in output
        assert "Total: 2 experts" in output

    @pytest.mark.medium
    def test_format_text_expert_sorting(self):
        """Test that experts within category are sorted by ID."""
        categorized = {
            "general": [
                {"id": "zzz", "name": "Z Expert", "background": "", "repos": 0},
                {"id": "aaa", "name": "A Expert", "background": "", "repos": 0},
                {"id": "mmm", "name": "M Expert", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_text(categorized)

        # Check that aaa appears before mmm appears before zzz
        aaa_pos = output.index("aaa")
        mmm_pos = output.index("mmm")
        zzz_pos = output.index("zzz")

        assert aaa_pos < mmm_pos < zzz_pos

    @pytest.mark.medium
    def test_format_text_category_descriptions(self):
        """Test that category descriptions are included."""
        categorized = {
            "language-sdks": [
                {"id": "ts", "name": "TS", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_text(categorized)

        assert "Experts in language-specific SDK patterns and idioms" in output

    @pytest.mark.low
    def test_format_text_empty_categories(self):
        """Test formatting with empty categories."""
        output = list_experts.format_text({})
        assert "Total: 0 experts" in output


class TestFormatJson:
    """Test JSON output formatting."""

    @pytest.mark.high
    def test_format_json_basic(self):
        """Test basic JSON formatting."""
        categorized = {
            "language-sdks": [
                {"id": "typescript", "name": "TypeScript Expert", "background": "TS", "repos": 1}
            ]
        }

        output = list_experts.format_json(categorized)
        data = json.loads(output)

        assert "categories" in data
        assert "experts" in data
        assert "total" in data
        assert data["total"] == 1

    @pytest.mark.high
    def test_format_json_structure(self):
        """Test complete JSON structure."""
        categorized = {
            "language-sdks": [
                {"id": "typescript", "name": "TS Expert", "background": "", "repos": 0}
            ],
            "llm-clients": [
                {"id": "openai", "name": "OpenAI Expert", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_json(categorized)
        data = json.loads(output)

        assert "language-sdks" in data["categories"]
        assert "llm-clients" in data["categories"]
        assert data["categories"]["language-sdks"]["name"] == "Language Sdks Experts"
        assert data["categories"]["llm-clients"]["name"] == "Llm Clients Experts"

    @pytest.mark.high
    def test_format_json_category_metadata(self):
        """Test category name and description in JSON."""
        categorized = {
            "language-sdks": [
                {"id": "ts", "name": "TS", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_json(categorized)
        data = json.loads(output)

        cat_meta = data["categories"]["language-sdks"]
        assert cat_meta["name"] == "Language Sdks Experts"
        assert cat_meta["description"] == "Experts in language-specific SDK patterns and idioms"

    @pytest.mark.medium
    def test_format_json_total_count(self):
        """Test that total count is correct."""
        categorized = {
            "cat1": [{"id": "e1", "name": "E1", "background": "", "repos": 0}],
            "cat2": [
                {"id": "e2", "name": "E2", "background": "", "repos": 0},
                {"id": "e3", "name": "E3", "background": "", "repos": 0}
            ]
        }

        output = list_experts.format_json(categorized)
        data = json.loads(output)

        assert data["total"] == 3

    @pytest.mark.medium
    def test_format_json_experts_preserved(self):
        """Test that expert data is preserved in JSON."""
        categorized = {
            "general": [
                {"id": "expert1", "name": "Expert One", "background": "BG", "repos": 5}
            ]
        }

        output = list_experts.format_json(categorized)
        data = json.loads(output)

        expert = data["experts"]["general"][0]
        assert expert["id"] == "expert1"
        assert expert["name"] == "Expert One"
        assert expert["background"] == "BG"
        assert expert["repos"] == 5

    @pytest.mark.low
    def test_format_json_valid_json(self):
        """Test that output is valid JSON."""
        categorized = {
            "general": [{"id": "e1", "name": "E1", "background": "", "repos": 0}]
        }

        output = list_experts.format_json(categorized)

        # Should not raise
        json.loads(output)

    @pytest.mark.low
    def test_format_json_empty(self):
        """Test JSON formatting with empty data."""
        output = list_experts.format_json({})
        data = json.loads(output)

        assert data["total"] == 0
        assert data["categories"] == {}
        assert data["experts"] == {}


class TestMain:
    """Test CLI main function."""

    @pytest.mark.high
    def test_main_text_format(self, monkeypatch, capsys):
        """Test main with text format (default)."""
        sample_experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "category": "language-sdks"
            }
        }

        def mock_load_json(path):
            return sample_experts

        monkeypatch.setattr("utils.list_experts.load_json", mock_load_json)
        monkeypatch.setattr("sys.argv", ["list_experts.py"])

        list_experts.main()

        captured = capsys.readouterr()
        assert "Available Expert Reviewers" in captured.out
        assert "typescript" in captured.out

    @pytest.mark.high
    def test_main_json_format(self, monkeypatch, capsys):
        """Test main with JSON format."""
        sample_experts = {
            "typescript": {
                "name": "TypeScript Expert",
                "category": "language-sdks"
            }
        }

        def mock_load_json(path):
            return sample_experts

        monkeypatch.setattr("utils.list_experts.load_json", mock_load_json)
        monkeypatch.setattr("sys.argv", ["list_experts.py", "--format", "json"])

        list_experts.main()

        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "categories" in data
        assert "experts" in data

    @pytest.mark.medium
    def test_main_error_handling(self, monkeypatch, capsys):
        """Test main error handling."""
        def mock_load_json(path):
            raise FileNotFoundError("experts.json not found")

        monkeypatch.setattr("utils.list_experts.load_json", mock_load_json)
        monkeypatch.setattr("sys.argv", ["list_experts.py"])

        with pytest.raises(SystemExit) as exc_info:
            list_experts.main()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        # Error should be in stderr as JSON
        error_data = json.loads(captured.err)
        assert error_data["status"] == "error"
        assert "experts.json not found" in error_data["error"]

    @pytest.mark.low
    def test_main_with_empty_experts(self, monkeypatch, capsys):
        """Test main with empty experts file."""
        monkeypatch.setattr("utils.list_experts.load_json", lambda p: {})
        monkeypatch.setattr("sys.argv", ["list_experts.py"])

        list_experts.main()

        captured = capsys.readouterr()
        assert "Total: 0 experts" in captured.out


class TestEdgeCases:
    """Test edge cases and special characters."""

    @pytest.mark.medium
    def test_special_characters_in_expert_name(self):
        """Test expert names with special characters."""
        experts = {
            "expert-special": {
                "name": "Expert with 'quotes' and \"double quotes\"",
                "category": "general"
            }
        }

        categorized = list_experts.categorize_experts(experts)
        text_output = list_experts.format_text(categorized)
        json_output = list_experts.format_json(categorized)

        assert "quotes" in text_output
        # JSON should handle special characters
        data = json.loads(json_output)
        assert "'" in data["experts"]["general"][0]["name"]

    @pytest.mark.medium
    def test_unicode_in_expert_data(self):
        """Test Unicode characters in expert data."""
        experts = {
            "expert-unicode": {
                "name": "Expert with émojis 🚀 and ñ",
                "category": "general",
                "background": "Specialist in TypeScript™"
            }
        }

        categorized = list_experts.categorize_experts(experts)
        text_output = list_experts.format_text(categorized)
        json_output = list_experts.format_json(categorized)

        assert "🚀" in text_output
        data = json.loads(json_output)
        assert "🚀" in data["experts"]["general"][0]["name"]

    @pytest.mark.low
    def test_very_long_expert_name(self):
        """Test handling of very long expert names."""
        experts = {
            "long": {
                "name": "A" * 200,
                "category": "general"
            }
        }

        categorized = list_experts.categorize_experts(experts)
        text_output = list_experts.format_text(categorized)

        # Should not crash
        assert "A" * 200 in text_output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
