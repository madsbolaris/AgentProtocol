"""
Unit tests for prompts/builders.py

Tests prompt construction functions including:
- build_expert_prompt() with all parameter combinations
- build_refinement_prompt() with various inputs
- focus_files/focus_folders handling
- focus_context integration
- Template rendering with proper variables

Target coverage: 90%+
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from prompts import builders


class TestBuildExpertPrompt:
    """Test build_expert_prompt function."""

    @pytest.mark.high
    def test_build_basic_prompt(self, test_workspace, mock_experts_json):
        """Test building basic expert prompt."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Rendered prompt"):

            prompt = builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1
            )

            assert isinstance(prompt, str)
            assert len(prompt) > 0

    @pytest.mark.high
    def test_build_prompt_with_focus_files(self, test_workspace, mock_experts_json):
        """Test building prompt with focus files."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt with files") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1,
                focus_files=["src/main.ts", "src/types.ts"]
            )

            # Verify focus_files was passed to template
            call_kwargs = mock_render.call_args[1]
            assert "focus_files" in call_kwargs
            assert "src/main.ts" in call_kwargs["focus_files"]

    @pytest.mark.high
    def test_build_prompt_with_focus_folders(self, test_workspace, mock_experts_json):
        """Test building prompt with focus folders."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt with folders") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1,
                focus_folders=["src/", "tests/"]
            )

            call_kwargs = mock_render.call_args[1]
            assert "focus_folders" in call_kwargs

    @pytest.mark.high
    def test_build_prompt_with_focus_context(self, test_workspace, mock_experts_json):
        """Test building prompt with focus context."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt with context") as mock_render:

            context = "Focus on error handling patterns"

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1,
                focus_context=context
            )

            call_kwargs = mock_render.call_args[1]
            assert "focus_context" in call_kwargs
            assert call_kwargs["focus_context"] == context

    @pytest.mark.high
    def test_build_prompt_with_repos(self, test_workspace, mock_experts_json):
        """Test building prompt with repository paths."""
        mock_repos = [
            {"path": "/path/to/repo", "exists": True, "name": "test-repo"}
        ]

        with patch('prompts.builders.expand_repo_paths', return_value=mock_repos), \
             patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            expert_info_with_repos = mock_experts_json["typescript"].copy()
            expert_info_with_repos["repos"] = [{"path": "/path/to/repo"}]

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=expert_info_with_repos,
                review_context="API Design",
                workspace=test_workspace,
                iteration=1
            )

            call_kwargs = mock_render.call_args[1]
            assert "repos" in call_kwargs

    @pytest.mark.high
    def test_build_prompt_first_iteration(self, test_workspace, mock_experts_json):
        """Test building prompt for first iteration."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="First iteration") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1
            )

            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["iteration"] == 1

    @pytest.mark.high
    def test_build_prompt_later_iteration(self, test_workspace, mock_experts_json):
        """Test building prompt for later iterations."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Later iteration") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=3
            )

            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["iteration"] == 3


class TestBuildRefinementPrompt:
    """Test build_refinement_prompt function."""

    @pytest.mark.high
    def test_build_refinement_basic(self, test_workspace):
        """Test building basic refinement prompt."""
        qa_answers = {
            "answers": [
                {"question": "What pattern?", "answer": "Repository pattern"}
            ]
        }

        with patch('prompts.builders.render_template', return_value="Refinement prompt"):

            prompt = builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2
            )

            assert isinstance(prompt, str)
            assert len(prompt) > 0

    @pytest.mark.high
    def test_build_refinement_with_qa_answers(self, test_workspace):
        """Test refinement prompt with QA answers."""
        qa_answers = {
            "answers": [
                {"question": "Q1", "answer": "A1"},
                {"question": "Q2", "answer": "A2"}
            ]
        }

        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="python",
                workspace=test_workspace,
                iteration=2
            )

            call_kwargs = mock_render.call_args[1]
            assert "questions" in call_kwargs
            # Note: template expects "questions" not "answers"
            assert len(call_kwargs["questions"]) == 2

    @pytest.mark.high
    def test_build_refinement_with_synthesized_questions(self, test_workspace):
        """Test refinement with synthesized questions."""
        qa_answers = {"answers": []}
        synthesized = [
            {"question": "Synthesized Q1", "priority": "high"}
        ]

        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2,
                synthesized_questions=synthesized
            )

            call_kwargs = mock_render.call_args[1]
            assert "synthesized_questions" in call_kwargs

    @pytest.mark.high
    def test_build_refinement_with_convergence_data(self, test_workspace):
        """Test refinement with convergence data."""
        qa_answers = {"answers": []}
        convergence = {
            "convergence_percent": 75,
            "consensus_reached": False
        }

        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2,
                convergence_data=convergence
            )

            call_kwargs = mock_render.call_args[1]
            assert "convergence_data" in call_kwargs

    @pytest.mark.high
    def test_build_refinement_empty_qa_answers(self, test_workspace):
        """Test refinement with no QA answers."""
        qa_answers = None

        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2
            )

            call_kwargs = mock_render.call_args[1]
            # Should handle None gracefully
            assert "questions" in call_kwargs


class TestPromptTemplateSelection:
    """Test template selection logic."""

    @pytest.mark.high
    def test_uses_initial_template_for_first_iteration(self, test_workspace, mock_experts_json):
        """Test that initial template is used for iteration 1."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1
            )

            # Should use experts/initial.jinja2 or similar
            template_name = mock_render.call_args[0][0]
            assert "initial" in template_name.lower() or "expert" in template_name.lower()

    @pytest.mark.high
    def test_uses_refinement_template(self, test_workspace):
        """Test that refinement template is used."""
        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers={"answers": []},
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2
            )

            template_name = mock_render.call_args[0][0]
            assert "refinement" in template_name.lower()


class TestPromptVariables:
    """Test that correct variables are passed to templates."""

    @pytest.mark.high
    def test_expert_prompt_has_required_variables(self, test_workspace, mock_experts_json):
        """Test that expert prompt includes all required variables."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1
            )

            call_kwargs = mock_render.call_args[1]

            required_vars = [
                "expert_name",
                "expert_background",
                "expert_perspective",
                "review_context",
                "workspace",
                "iteration"
            ]

            for var in required_vars:
                assert var in call_kwargs

    @pytest.mark.high
    def test_refinement_prompt_has_required_variables(self, test_workspace):
        """Test that refinement prompt includes required variables."""
        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers={"answers": []},
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2
            )

            call_kwargs = mock_render.call_args[1]

            required_vars = ["questions", "expert", "workspace", "iteration"]

            for var in required_vars:
                assert var in call_kwargs


class TestErrorHandling:
    """Test error handling in prompt building."""

    @pytest.mark.high
    def test_build_prompt_template_error(self, test_workspace, mock_experts_json):
        """Test handling of template rendering errors."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', side_effect=Exception("Template error")):

            with pytest.raises(Exception):
                builders.build_expert_prompt(
                    expert_name="typescript",
                    expert_info=mock_experts_json["typescript"],
                    review_context="API Design",
                    workspace=test_workspace,
                    iteration=1
                )

    @pytest.mark.high
    def test_build_prompt_missing_expert_info(self, test_workspace):
        """Test handling of missing expert info."""
        incomplete_info = {"name": "Test"}  # Missing required fields

        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt"):

            # Should either handle gracefully or raise
            try:
                builders.build_expert_prompt(
                    expert_name="test",
                    expert_info=incomplete_info,
                    review_context="Test",
                    workspace=test_workspace,
                    iteration=1
                )
            except (KeyError, AttributeError):
                # Expected if validation is strict
                pass


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_build_prompt_with_empty_topic(self, test_workspace, mock_experts_json):
        """Test building prompt with empty topic."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt"):

            prompt = builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="",
                workspace=test_workspace,
                iteration=1
            )

            assert isinstance(prompt, str)

    @pytest.mark.high
    def test_build_prompt_with_special_characters_in_topic(self, test_workspace, mock_experts_json):
        """Test building prompt with special characters in topic."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt"):

            special_topic = "API Design: <>&\""

            prompt = builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context=special_topic,
                workspace=test_workspace,
                iteration=1
            )

    @pytest.mark.high
    def test_build_prompt_with_many_focus_files(self, test_workspace, mock_experts_json):
        """Test building prompt with many focus files."""
        focus_files = [f"file{i}.ts" for i in range(100)]

        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt"):

            prompt = builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="API Design",
                workspace=test_workspace,
                iteration=1,
                focus_files=focus_files
            )

    @pytest.mark.high
    def test_build_refinement_with_many_qa_pairs(self, test_workspace):
        """Test refinement with many QA pairs."""
        qa_answers = {
            "answers": [
                {"question": f"Q{i}", "answer": f"A{i}"}
                for i in range(50)
            ]
        }

        with patch('prompts.builders.render_template', return_value="Prompt"):

            prompt = builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="typescript",
                workspace=test_workspace,
                iteration=2
            )


class TestDefaultParameterHandling:
    """Test default parameter handling."""

    @pytest.mark.medium
    def test_expert_prompt_defaults_empty_repos(self, test_workspace):
        """Test that missing repos defaults to empty list."""
        expert_info_no_repos = {
            "name": "Test Expert",
            "background": "Testing",
            "perspective": "QA",
        }

        with patch('prompts.builders.expand_repo_paths', return_value=[]) as mock_expand, \
             patch('prompts.builders.render_template', return_value="Prompt"):

            builders.build_expert_prompt(
                expert_name="test",
                expert_info=expert_info_no_repos,
                review_context="Test",
                workspace=test_workspace,
                iteration=1
            )

            # Should call expand_repo_paths with empty list
            mock_expand.assert_called_once_with([])

    @pytest.mark.medium
    def test_expert_prompt_defaults_optional_fields(self, test_workspace):
        """Test that optional fields default correctly."""
        expert_info = {
            "name": "Test Expert",
            "background": "Testing",
            "perspective": "QA",
        }

        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_expert_prompt(
                expert_name="test",
                expert_info=expert_info,
                review_context="Test",
                workspace=test_workspace,
                iteration=1
            )

            call_kwargs = mock_render.call_args[1]
            # Optional fields should default to empty lists/strings
            assert call_kwargs["focus_files"] == []
            assert call_kwargs["focus_folders"] == []
            assert call_kwargs["focus_context"] == ""

    @pytest.mark.medium
    def test_refinement_prompt_none_synthesized_questions(self, test_workspace):
        """Test refinement with None synthesized questions."""
        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers={"answers": []},
                expert_name="test",
                workspace=test_workspace,
                iteration=2,
                synthesized_questions=None
            )

            call_kwargs = mock_render.call_args[1]
            # Should default to empty list
            assert call_kwargs["synthesized_questions"] == []

    @pytest.mark.medium
    def test_refinement_prompt_none_convergence_data(self, test_workspace):
        """Test refinement with None convergence data."""
        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers={"answers": []},
                expert_name="test",
                workspace=test_workspace,
                iteration=2,
                convergence_data=None
            )

            call_kwargs = mock_render.call_args[1]
            # Should pass None as is
            assert call_kwargs["convergence_data"] is None


class TestTemplateNameUsage:
    """Test correct template names are used."""

    @pytest.mark.high
    def test_expert_prompt_uses_correct_template(self, test_workspace, mock_experts_json):
        """Test that expert prompt uses correct template path."""
        with patch('prompts.builders.expand_repo_paths', return_value=[]), \
             patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="Test",
                workspace=test_workspace,
                iteration=1
            )

            # Should use experts/01-review-topic.jinja2
            template_name = mock_render.call_args[0][0]
            assert template_name == "experts/01-review-topic.jinja2"

    @pytest.mark.high
    def test_refinement_prompt_uses_correct_template(self, test_workspace):
        """Test that refinement prompt uses correct template path."""
        with patch('prompts.builders.render_template', return_value="Prompt") as mock_render:

            builders.build_refinement_prompt(
                qa_answers={"answers": []},
                expert_name="test",
                workspace=test_workspace,
                iteration=2
            )

            # Should use experts/refinement.jinja2
            template_name = mock_render.call_args[0][0]
            assert template_name == "experts/refinement.jinja2"


class TestCompleteIntegration:
    """Test complete integration with all parameters."""

    @pytest.mark.high
    def test_expert_prompt_all_parameters(self, test_workspace, mock_experts_json):
        """Test expert prompt with all parameters provided."""
        with patch('prompts.builders.expand_repo_paths', return_value=[{"path": "test"}]), \
             patch('prompts.builders.render_template', return_value="Full prompt") as mock_render:

            prompt = builders.build_expert_prompt(
                expert_name="typescript",
                expert_info=mock_experts_json["typescript"],
                review_context="Complete Test",
                workspace=test_workspace,
                iteration=2,
                focus_files=["file1.ts", "file2.ts"],
                focus_folders=["src/", "tests/"],
                focus_context="Focus on everything"
            )

            assert prompt == "Full prompt"

            call_kwargs = mock_render.call_args[1]
            # Verify all parameters were passed
            assert call_kwargs["iteration"] == 2
            assert len(call_kwargs["focus_files"]) == 2
            assert len(call_kwargs["focus_folders"]) == 2
            assert call_kwargs["focus_context"] == "Focus on everything"

    @pytest.mark.high
    def test_refinement_prompt_all_parameters(self, test_workspace):
        """Test refinement prompt with all parameters provided."""
        qa_answers = {"answers": [{"q": "Q", "a": "A"}]}
        synthesized = [{"question": "SQ"}]
        convergence = {"percent": 80}

        with patch('prompts.builders.render_template', return_value="Full refinement") as mock_render:

            prompt = builders.build_refinement_prompt(
                qa_answers=qa_answers,
                expert_name="test",
                workspace=test_workspace,
                iteration=3,
                synthesized_questions=synthesized,
                convergence_data=convergence
            )

            assert prompt == "Full refinement"

            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["iteration"] == 3
            assert len(call_kwargs["synthesized_questions"]) == 1
            assert call_kwargs["convergence_data"]["percent"] == 80


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
