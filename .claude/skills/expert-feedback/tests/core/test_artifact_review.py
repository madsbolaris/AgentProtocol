"""
Unit tests for core/artifact_review.py

Tests artifact review logic including:
- Expert artifact reviewer spawning
- Parallel artifact review execution
- Veto synthesis and consolidation
- Minor tweaks consolidation
- Regeneration context creation
- Artifact concern synthesis
- Review status determination (approved/minor_tweaks/vetoed)

Target coverage: 80%+
"""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from core import artifact_review


class TestSpawnArtifactReviewer:
    """Test spawn_artifact_reviewer function."""

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_spawn_reviewer_success(self, test_workspace, tmp_path):
        """Test successful artifact review spawn."""
        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        # Mock parse_artifact_review
        mock_review_data = {
            "decision": "approve",
            "expert": "typescript",
            "summary": "Looks good"
        }

        # Mock spawn_agent result
        mock_spawn_result = Mock()
        mock_spawn_result.status = "complete"
        mock_spawn_result.session_id = "test-session-123"
        mock_spawn_result.error = None
        mock_spawn_result.tokens_used = 1000
        mock_spawn_result.duration_seconds = 45.0

        # Create mock review file
        expert_dir = experts_dir / "typescript"
        expert_dir.mkdir(parents=True, exist_ok=True)
        review_md = expert_dir / "artifact-review-typescript.md"
        review_md.write_text("# Review\n\nDecision: approve")

        # Mock the dynamic import of parse_artifact_review
        mock_parse_module = Mock()
        mock_parse_module.parse_artifact_review = Mock(return_value=mock_review_data)

        with patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn, \
             patch.dict('sys.modules', {'parse_artifact_review': mock_parse_module}):

            mock_spawn.return_value = mock_spawn_result

            result = await artifact_review.spawn_artifact_reviewer(
                expert_name="typescript",
                prompt="Review this artifact",
                workspace=test_workspace,
                experts_dir=experts_dir,
                config=mock_config,
                timeout_seconds=300
            )

        assert result["status"] == "complete"
        assert result["expert"] == "typescript"
        assert result["decision"] == "approve"
        assert result["session_id"] == "test-session-123"
        assert result["tokens_used"] == 1000
        assert result["duration_seconds"] == 45.0
        mock_spawn.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_spawn_reviewer_agent_failure(self, test_workspace, tmp_path):
        """Test handling of agent spawn failure."""
        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        mock_spawn_result = Mock()
        mock_spawn_result.status = "timeout"
        mock_spawn_result.error = "Agent timed out"
        mock_spawn_result.duration_seconds = 300.0

        with patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn:
            mock_spawn.return_value = mock_spawn_result

            result = await artifact_review.spawn_artifact_reviewer(
                expert_name="python",
                prompt="Review this artifact",
                workspace=test_workspace,
                experts_dir=experts_dir,
                config=mock_config,
                timeout_seconds=300
            )

        assert result["status"] == "timeout"
        assert result["expert"] == "python"
        assert "timed out" in result["error"].lower()
        assert result["duration_seconds"] == 300.0

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_spawn_reviewer_missing_review_file(self, test_workspace, tmp_path):
        """Test handling when review markdown file is not created."""
        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        mock_spawn_result = Mock()
        mock_spawn_result.status = "complete"
        mock_spawn_result.error = None
        mock_spawn_result.duration_seconds = 45.0

        with patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn:
            mock_spawn.return_value = mock_spawn_result

            result = await artifact_review.spawn_artifact_reviewer(
                expert_name="security",
                prompt="Review this artifact",
                workspace=test_workspace,
                experts_dir=experts_dir,
                config=mock_config,
                timeout_seconds=300
            )

        assert result["status"] == "error"
        assert result["expert"] == "security"
        assert "did not create review file" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_spawn_reviewer_parse_failure(self, test_workspace, tmp_path):
        """Test handling of review parse failure."""
        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        mock_spawn_result = Mock()
        mock_spawn_result.status = "complete"
        mock_spawn_result.error = None
        mock_spawn_result.duration_seconds = 45.0

        # Create mock review file
        expert_dir = experts_dir / "python"
        expert_dir.mkdir(parents=True, exist_ok=True)
        review_md = expert_dir / "artifact-review-python.md"
        review_md.write_text("Invalid markdown")

        # Mock the dynamic import to raise ValueError
        mock_parse_module = Mock()
        mock_parse_module.parse_artifact_review = Mock(side_effect=ValueError("Parse error"))

        with patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn, \
             patch.dict('sys.modules', {'parse_artifact_review': mock_parse_module}):

            mock_spawn.return_value = mock_spawn_result

            result = await artifact_review.spawn_artifact_reviewer(
                expert_name="python",
                prompt="Review this artifact",
                workspace=test_workspace,
                experts_dir=experts_dir,
                config=mock_config,
                timeout_seconds=300
            )

        assert result["status"] == "error"
        assert result["expert"] == "python"
        assert "Failed to parse review" in result["error"]


class TestSynthesizeVetoes:
    """Test synthesize_vetoes function."""

    @pytest.mark.critical
    def test_synthesize_single_veto(self, tmp_path):
        """Test synthesizing a single veto."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        vetoes = [{
            "expert": "typescript",
            "review_data": {
                "decision": "veto",
                "critical_issues": [
                    {
                        "issue": "Missing error handling",
                        "why_critical": "Could cause crashes",
                        "evidence": "Lines 45-67"
                    }
                ],
                "questions": [
                    {
                        "question": "How will errors be handled?",
                        "context": "Error handling strategy",
                        "importance": "high"
                    }
                ]
            }
        }]

        result = artifact_review.synthesize_critical_concerns(vetoes, iteration_dir)

        assert result["total_concerns"] == 1
        assert result["experts_with_concerns"] == ["typescript"]
        assert len(result["critical_issues"]) == 1
        assert len(result["questions_for_user"]) == 1
        assert result["requires_regeneration"] is True

        # Check that files were created
        concerns_questions_file = iteration_dir / "artifact-concerns-questions.json"
        assert concerns_questions_file.exists()

        summary_file = iteration_dir / "artifact-concerns-summary.md"
        assert summary_file.exists()

        summary_text = summary_file.read_text()
        assert "typescript" in summary_text
        assert "Missing error handling" in summary_text

    @pytest.mark.critical
    def test_synthesize_multiple_vetoes(self, tmp_path):
        """Test synthesizing multiple vetoes."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        vetoes = [
            {
                "expert": "typescript",
                "review_data": {
                    "critical_issues": [
                        {
                            "issue": "Type safety issues",
                            "why_critical": "Runtime errors likely",
                            "evidence": "Multiple any types"
                        }
                    ],
                    "questions": [
                        {
                            "question": "How to ensure type safety?",
                            "context": "Type system",
                            "importance": "high"
                        }
                    ]
                }
            },
            {
                "expert": "security",
                "review_data": {
                    "critical_issues": [
                        {
                            "issue": "SQL injection risk",
                            "why_critical": "Security vulnerability",
                            "evidence": "Line 89"
                        }
                    ],
                    "questions": [
                        {
                            "question": "How to prevent SQL injection?",
                            "context": "Database queries",
                            "importance": "high"
                        }
                    ]
                }
            }
        ]

        result = artifact_review.synthesize_critical_concerns(vetoes, iteration_dir)

        assert result["total_concerns"] == 2
        assert len(result["experts_with_concerns"]) == 2
        assert len(result["critical_issues"]) == 2
        assert len(result["questions_for_user"]) == 2

        summary_file = iteration_dir / "artifact-concerns-summary.md"
        summary_text = summary_file.read_text()
        assert "typescript" in summary_text
        assert "security" in summary_text

    @pytest.mark.critical
    def test_synthesize_vetoes_markdown_formatting(self, tmp_path):
        """Test that veto summary markdown is properly formatted."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        vetoes = [{
            "expert": "python",
            "review_data": {
                "critical_issues": [
                    {
                        "issue": "Poor performance",
                        "why_critical": "Blocks main thread",
                        "evidence": "Sync operations"
                    }
                ],
                "questions": [
                    {
                        "question": "Use async/await?",
                        "context": "Performance",
                        "importance": "medium"
                    }
                ]
            }
        }]

        artifact_review.synthesize_critical_concerns(vetoes, iteration_dir)

        summary_file = iteration_dir / "artifact-concerns-summary.md"
        summary_text = summary_file.read_text()

        # Check markdown structure
        assert "# Critical Concerns Summary" in summary_text
        assert "## Critical Issues" in summary_text
        assert "## Questions That Need Answers" in summary_text
        assert "🟡" in summary_text  # Medium importance emoji


class TestSynthesizeTweaks:
    """Test synthesize_tweaks function."""

    @pytest.mark.critical
    def test_synthesize_single_tweak(self, tmp_path):
        """Test synthesizing a single minor tweak."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        minor_tweaks = [{
            "expert": "typescript",
            "review_data": {
                "decision": "minor_tweaks",
                "tweaks": [
                    {
                        "section": "Type Definitions",
                        "issue": "Could be more specific",
                        "suggestion": "Use union types instead of any"
                    }
                ]
            }
        }]

        result = artifact_review.synthesize_tweaks(minor_tweaks, iteration_dir)

        assert result["total_tweaks"] == 1
        assert result["experts_with_tweaks"] == ["typescript"]
        assert len(result["tweaks"]) == 1
        assert result["requires_regeneration"] is False

        # Check that summary file was created
        summary_file = iteration_dir / "artifact-tweaks-summary.md"
        assert summary_file.exists()

        summary_text = summary_file.read_text()
        assert "typescript" in summary_text
        assert "Type Definitions" in summary_text

    @pytest.mark.critical
    def test_synthesize_multiple_tweaks(self, tmp_path):
        """Test synthesizing multiple minor tweaks from different experts."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        minor_tweaks = [
            {
                "expert": "typescript",
                "review_data": {
                    "tweaks": [
                        {
                            "section": "Types",
                            "issue": "Generic constraint needed",
                            "suggestion": "Add extends constraint"
                        }
                    ]
                }
            },
            {
                "expert": "python",
                "review_data": {
                    "tweaks": [
                        {
                            "section": "Docstrings",
                            "issue": "Missing parameter docs",
                            "suggestion": "Add Args section"
                        },
                        {
                            "section": "Type hints",
                            "issue": "Optional not specified",
                            "suggestion": "Use Optional[T]"
                        }
                    ]
                }
            }
        ]

        result = artifact_review.synthesize_tweaks(minor_tweaks, iteration_dir)

        assert result["total_tweaks"] == 2
        assert len(result["experts_with_tweaks"]) == 2
        assert len(result["tweaks"]) == 3  # Total individual tweaks

    @pytest.mark.critical
    def test_synthesize_tweaks_markdown_formatting(self, tmp_path):
        """Test that tweaks summary markdown is properly formatted."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        minor_tweaks = [{
            "expert": "security",
            "review_data": {
                "tweaks": [
                    {
                        "section": "Authentication",
                        "issue": "Rate limiting not mentioned",
                        "suggestion": "Add rate limiting section"
                    }
                ]
            }
        }]

        artifact_review.synthesize_tweaks(minor_tweaks, iteration_dir)

        summary_file = iteration_dir / "artifact-tweaks-summary.md"
        summary_text = summary_file.read_text()

        # Check markdown structure
        assert "# Suggested Minor Tweaks" in summary_text
        assert "## Suggested Changes" in summary_text
        assert "Authentication" in summary_text
        assert "security" in summary_text


class TestCreateRegenerationContext:
    """Test _create_regeneration_context function."""

    @pytest.mark.critical
    def test_create_context_with_patterns(self):
        """Test creating regeneration context with veto patterns."""
        concerns_data = {
            "concerns": [
                {
                    "id": "concern-1",
                    "title": "Type safety",
                    "theme": "Type System",
                    "expert": "typescript"
                },
                {
                    "id": "concern-2",
                    "title": "Type inference",
                    "theme": "Type System",
                    "expert": "python"
                },
                {
                    "id": "concern-3",
                    "title": "SQL injection",
                    "theme": "Security",
                    "expert": "security"
                }
            ]
        }

        expert_reviews = {
            "typescript": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Type System", "title": "Type safety"}
                ]
            },
            "python": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Type System", "title": "Type inference"}
                ]
            },
            "security": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Security", "title": "SQL injection"}
                ]
            }
        }

        result = artifact_review.create_regeneration_context(
            concerns_data,
            expert_reviews
        )

        assert result["total_concerns"] == 3
        assert result["themes_count"] == 2
        assert len(result["concern_patterns"]) >= 1  # Type System should be a pattern
        assert len(result["common_themes"]) >= 1  # Type System mentioned by 2+ experts

        # Verify Type System is identified as a pattern
        type_system_pattern = next(
            (p for p in result["concern_patterns"] if p["theme"] == "Type System"),
            None
        )
        assert type_system_pattern is not None
        assert type_system_pattern["concern_count"] == 2
        assert type_system_pattern["expert_count"] == 2

    @pytest.mark.critical
    def test_create_context_common_themes(self):
        """Test identification of common themes across experts."""
        concerns_data = {
            "concerns": [
                {"theme": "Performance", "expert": "python"},
                {"theme": "Performance", "expert": "typescript"},
                {"theme": "Testing", "expert": "python"}
            ]
        }

        expert_reviews = {
            "python": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Performance"},
                    {"theme": "Testing"}
                ]
            },
            "typescript": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Performance"}
                ]
            }
        }

        result = artifact_review.create_regeneration_context(
            concerns_data,
            expert_reviews
        )

        # Performance should be identified as common theme (2 experts)
        assert len(result["common_themes"]) >= 1

        performance_theme = next(
            (t for t in result["common_themes"] if t["theme"] == "Performance"),
            None
        )
        assert performance_theme is not None
        assert performance_theme["expert_count"] == 2
        assert set(performance_theme["experts"]) == {"python", "typescript"}

    @pytest.mark.critical
    def test_create_context_no_patterns(self):
        """Test regeneration context with no repeated patterns."""
        concerns_data = {
            "concerns": [
                {"theme": "Theme A", "expert": "typescript"},
                {"theme": "Theme B", "expert": "python"},
                {"theme": "Theme C", "expert": "security"}
            ]
        }

        expert_reviews = {
            "typescript": {"decision": "concerns_raised", "concerns": [{"theme": "Theme A"}]},
            "python": {"decision": "concerns_raised", "concerns": [{"theme": "Theme B"}]},
            "security": {"decision": "concerns_raised", "concerns": [{"theme": "Theme C"}]}
        }

        result = artifact_review.create_regeneration_context(
            concerns_data,
            expert_reviews
        )

        assert result["total_concerns"] == 3
        assert result["themes_count"] == 3
        # No patterns since each theme appears only once
        assert len(result["concern_patterns"]) == 0
        assert len(result["common_themes"]) == 0


class TestSynthesizeArtifactConcerns:
    """Test synthesize_artifact_concerns function."""

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_synthesize_concerns_success(self, test_workspace, tmp_path):
        """Test successful concern synthesis."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        # Create mock expert review files
        for expert in ["typescript", "python"]:
            expert_dir = experts_dir / expert
            expert_dir.mkdir(parents=True, exist_ok=True)
            review_json = expert_dir / f"artifact-review-{expert}.json"
            review_json.write_text(json.dumps({
                "decision": "veto",
                "concerns": [{"theme": "Testing", "title": f"{expert} concern"}]
            }))

        results = [
            {"expert": "typescript", "status": "complete"},
            {"expert": "python", "status": "complete"}
        ]

        mock_state = Mock()
        mock_state.mode = "adr"

        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        mock_concerns_data = {
            "concerns": [
                {"id": "c1", "theme": "Testing", "title": "Need more tests"}
            ]
        }

        mock_spawn_result = Mock()
        mock_spawn_result.status = "complete"
        mock_spawn_result.error = None

        # Create consolidated markdown file
        consolidated_md = iteration_dir / "synthesized-concerns.md"

        # Mock the dynamic import of parse_synthesized_concerns
        mock_parse_module = Mock()
        mock_parse_module.parse_synthesized_concerns = Mock(return_value=mock_concerns_data)

        # Create a side effect that writes the file before returning
        async def spawn_side_effect(*args, **kwargs):
            consolidated_md.write_text("# Synthesized Concerns")
            return mock_spawn_result

        with patch('core.artifact_review.render_template', return_value="Synthesis prompt"), \
             patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn, \
             patch.dict('sys.modules', {'parse_synthesized_concerns': mock_parse_module}):

            mock_spawn.side_effect = spawn_side_effect

            result = await artifact_review.synthesize_artifact_concerns(
                workspace=test_workspace,
                iteration_dir=iteration_dir,
                experts_dir=experts_dir,
                state=mock_state,
                results=results,
                config=mock_config
            )

        assert result["status"] == "complete"
        assert result["total_concerns"] == 1
        assert "concerns_file" in result

        # Check that regeneration context was created
        regen_context_file = iteration_dir / "regeneration-context.json"
        assert regen_context_file.exists()

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_synthesize_concerns_no_reviews(self, test_workspace, tmp_path):
        """Test handling when no expert reviews are found."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        results = [
            {"expert": "typescript", "status": "complete"}
        ]

        mock_state = Mock()
        mock_config = Mock()

        result = await artifact_review.synthesize_artifact_concerns(
            workspace=test_workspace,
            iteration_dir=iteration_dir,
            experts_dir=experts_dir,
            state=mock_state,
            results=results,
            config=mock_config
        )

        assert result["status"] == "error"
        assert "No expert reviews found" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_synthesize_concerns_agent_failure(self, test_workspace, tmp_path):
        """Test handling of synthesis agent failure."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        # Create mock expert review files
        expert_dir = experts_dir / "typescript"
        expert_dir.mkdir(parents=True, exist_ok=True)
        review_json = expert_dir / "artifact-review-typescript.json"
        review_json.write_text(json.dumps({"decision": "veto"}))

        results = [{"expert": "typescript", "status": "complete"}]
        mock_state = Mock()
        mock_state.mode = "adr"
        mock_config = Mock()
        mock_config.enable_transcript_logging = False

        mock_spawn_result = Mock()
        mock_spawn_result.status = "timeout"
        mock_spawn_result.error = "Agent timed out"

        with patch('core.artifact_review.render_template', return_value="Prompt"), \
             patch('core.artifact_review.spawn_agent', new_callable=AsyncMock) as mock_spawn:

            # No file creation on failure
            mock_spawn.return_value = mock_spawn_result

            result = await artifact_review.synthesize_artifact_concerns(
                workspace=test_workspace,
                iteration_dir=iteration_dir,
                experts_dir=experts_dir,
                state=mock_state,
                results=results,
                config=mock_config
            )

        assert result["status"] == "error"
        assert "Consolidation agent failed" in result["error"]


class TestReviewArtifact:
    """Test review_artifact function."""

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_all_approve(self, test_workspace):
        """Test artifact review when all experts approve."""
        # Create state.json file with draft_artifact fields stored as top-level keys
        # (as done by generator.py using a non-existent update() method)
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "topic": "Test Topic",
            "mode": "adr",
            "experts": ["typescript", "python"],
            "iteration": 1,
            "convergence_percent": 85,
            "convergence_target": 80,
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/draft-adr.md"
        }))

        # Create artifact file
        artifact_file = test_workspace / "iteration-1" / "draft-adr.md"
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_text("# ADR\n\nContent here")

        mock_config = Mock()

        mock_review_results = [
            {
                "expert": "typescript",
                "status": "complete",
                "decision": "approve",
                "review_data": {"decision": "approve"}
            },
            {
                "expert": "python",
                "status": "complete",
                "decision": "approve",
                "review_data": {"decision": "approve"}
            }
        ]

        with patch('core.artifact_review.load_expert_info', return_value={"background": "Expert bg"}), \
             patch('core.artifact_review.render_template', return_value="Review prompt"), \
             patch('asyncio.gather', new_callable=AsyncMock) as mock_gather:

            mock_gather.return_value = mock_review_results

            result = await artifact_review.review_artifact(test_workspace, mock_config)

        assert result["status"] == "approved"
        assert result["requires_regeneration"] is False
        assert "vetoes" not in result
        assert "tweaks" not in result

        # Check that result file was created
        result_file = test_workspace / "iteration-2" / "artifact-review-result.json"
        assert result_file.exists()

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_with_vetoes(self, test_workspace):
        """Test artifact review when some experts veto."""
        # Create state.json file
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "topic": "Test Topic",
            "mode": "adr",
            "experts": ["typescript", "python", "security"],
            "iteration": 1,
            "convergence_percent": 85,
            "convergence_target": 80,
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/draft-adr.md"
        }))

        # Create artifact file
        artifact_file = test_workspace / "iteration-1" / "draft-adr.md"
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_text("# ADR\n\nContent here")

        mock_config = Mock()

        mock_review_results = [
            {
                "expert": "typescript",
                "status": "complete",
                "decision": "approve",
                "review_data": {"decision": "approve"}
            },
            {
                "expert": "python",
                "status": "complete",
                "decision": "concerns_raised",
                "review_data": {
                    "decision": "concerns_raised",
                    "critical_issues": [{"issue": "Problem"}],
                    "questions": []
                }
            },
            {
                "expert": "security",
                "status": "complete",
                "decision": "concerns_raised",
                "review_data": {
                    "decision": "concerns_raised",
                    "critical_issues": [{"issue": "Security issue"}],
                    "questions": []
                }
            }
        ]

        with patch('core.artifact_review.load_expert_info', return_value={"background": "Expert bg"}), \
             patch('core.artifact_review.render_template', return_value="Review prompt"), \
             patch('asyncio.gather', new_callable=AsyncMock) as mock_gather, \
             patch('core.artifact_review.synthesize_artifact_concerns', new_callable=AsyncMock) as mock_synth:

            mock_gather.return_value = mock_review_results
            mock_synth.return_value = {"status": "complete", "total_concerns": 2}

            result = await artifact_review.review_artifact(test_workspace, mock_config)

        assert result["status"] == "concerns_raised"
        assert result["requires_regeneration"] is True
        assert "concerns" in result
        assert result["concerns"]["total_concerns"] == 2

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_minor_tweaks_only(self, test_workspace):
        """Test artifact review with only minor tweaks (no vetoes)."""
        # Create state.json file
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "topic": "Test Topic",
            "mode": "adr",
            "experts": ["typescript", "python"],
            "iteration": 1,
            "convergence_percent": 85,
            "convergence_target": 80,
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/draft-adr.md"
        }))

        # Create artifact file
        artifact_file = test_workspace / "iteration-1" / "draft-adr.md"
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_text("# ADR\n\nContent here")

        mock_config = Mock()

        mock_review_results = [
            {
                "expert": "typescript",
                "status": "complete",
                "decision": "minor_tweaks",
                "review_data": {
                    "decision": "minor_tweaks",
                    "tweaks": [{"section": "Types", "issue": "Minor issue"}]
                }
            },
            {
                "expert": "python",
                "status": "complete",
                "decision": "approve",
                "review_data": {"decision": "approve"}
            }
        ]

        with patch('core.artifact_review.load_expert_info', return_value={"background": "Expert bg"}), \
             patch('core.artifact_review.render_template', return_value="Review prompt"), \
             patch('asyncio.gather', new_callable=AsyncMock) as mock_gather, \
             patch('core.artifact_review.synthesize_artifact_concerns', new_callable=AsyncMock) as mock_synth:

            mock_gather.return_value = mock_review_results
            mock_synth.return_value = {"status": "complete", "total_concerns": 1}

            result = await artifact_review.review_artifact(test_workspace, mock_config)

        assert result["status"] == "minor_tweaks"
        assert result["requires_regeneration"] is False
        assert "tweaks" in result
        assert result["tweaks"]["total_tweaks"] == 1

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_mixed_results(self, test_workspace):
        """Test artifact review with mixed decisions including errors."""
        # Create state.json file
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "topic": "Test Topic",
            "mode": "adr",
            "experts": ["typescript", "python", "security"],
            "iteration": 1,
            "convergence_percent": 85,
            "convergence_target": 80,
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/draft-adr.md"
        }))

        # Create artifact file
        artifact_file = test_workspace / "iteration-1" / "draft-adr.md"
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_text("# ADR\n\nContent here")

        mock_config = Mock()

        mock_review_results = [
            {
                "expert": "typescript",
                "status": "complete",
                "decision": "approve",
                "review_data": {"decision": "approve"}
            },
            {
                "expert": "python",
                "status": "complete",
                "decision": "minor_tweaks",
                "review_data": {
                    "decision": "minor_tweaks",
                    "tweaks": [{"section": "Docs"}]
                }
            },
            {
                "expert": "security",
                "status": "error",
                "error": "Timeout"
            }
        ]

        with patch('core.artifact_review.load_expert_info', return_value={"background": "Expert bg"}), \
             patch('core.artifact_review.render_template', return_value="Review prompt"), \
             patch('asyncio.gather', new_callable=AsyncMock) as mock_gather, \
             patch('core.artifact_review.synthesize_artifact_concerns', new_callable=AsyncMock) as mock_synth:

            mock_gather.return_value = mock_review_results
            mock_synth.return_value = {"status": "complete", "total_concerns": 1}

            result = await artifact_review.review_artifact(test_workspace, mock_config)

        # Should handle error gracefully and proceed with minor_tweaks status
        assert result["status"] == "minor_tweaks"

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_missing_artifact(self, test_workspace):
        """Test handling when artifact file doesn't exist."""
        # Create state.json file
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/missing-adr.md",
            "mode": "adr",
            "experts": ["typescript"],
            "topic": "Test Topic",
            "iteration": 1,
            "convergence_percent": 85
        }))

        mock_config = Mock()

        result = await artifact_review.review_artifact(test_workspace, mock_config)

        assert result["status"] == "error"
        assert "Artifact not found" in result["error"]


class TestMain:
    """Test main() entry point."""

    @pytest.mark.critical
    def test_main_missing_arguments(self, monkeypatch):
        """Test main exits with error when arguments missing."""
        monkeypatch.setattr('sys.argv', ['artifact_review.py'])

        with pytest.raises(SystemExit):
            artifact_review.main()

    @pytest.mark.critical
    def test_main_with_valid_args(self, test_workspace, monkeypatch):
        """Test main with valid arguments."""
        monkeypatch.setattr('sys.argv', [
            'artifact_review.py',
            '--workspace', str(test_workspace)
        ])

        mock_result = {"status": "approved", "requires_regeneration": False}

        with patch('core.artifact_review.require_claude_auth'), \
             patch('core.artifact_review.get_config', return_value=Mock()), \
             patch('asyncio.run', return_value=mock_result), \
             patch('builtins.print') as mock_print:

            with pytest.raises(SystemExit) as exc_info:
                artifact_review.main()

            # Should exit with code 0 on success
            assert exc_info.value.code == 0
            # Should print JSON result
            mock_print.assert_called()

    @pytest.mark.critical
    def test_main_error_exit_code(self, test_workspace, monkeypatch):
        """Test main exits with error code on failure."""
        monkeypatch.setattr('sys.argv', [
            'artifact_review.py',
            '--workspace', str(test_workspace)
        ])

        mock_result = {"status": "error", "error": "Something went wrong"}

        with patch('core.artifact_review.require_claude_auth'), \
             patch('core.artifact_review.get_config', return_value=Mock()), \
             patch('asyncio.run', return_value=mock_result):

            with pytest.raises(SystemExit) as exc_info:
                artifact_review.main()

            assert exc_info.value.code == 1


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.critical
    def test_synthesize_vetoes_empty_issues(self, tmp_path):
        """Test veto synthesis with empty issues list."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        vetoes = [{
            "expert": "typescript",
            "review_data": {
                "critical_issues": [],
                "questions": []
            }
        }]

        result = artifact_review.synthesize_critical_concerns(vetoes, iteration_dir)

        assert result["total_concerns"] == 1
        assert len(result["critical_issues"]) == 0
        assert len(result["questions_for_user"]) == 0

    @pytest.mark.critical
    def test_synthesize_tweaks_empty_tweaks(self, tmp_path):
        """Test tweak synthesis with empty tweaks list."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        minor_tweaks = [{
            "expert": "typescript",
            "review_data": {
                "tweaks": []
            }
        }]

        result = artifact_review.synthesize_tweaks(minor_tweaks, iteration_dir)

        assert result["total_tweaks"] == 1
        assert len(result["tweaks"]) == 0

    @pytest.mark.critical
    def test_regeneration_context_empty_concerns(self):
        """Test regeneration context with no concerns."""
        concerns_data = {"concerns": []}
        expert_reviews = {}

        result = artifact_review.create_regeneration_context(
            concerns_data,
            expert_reviews
        )

        assert result["total_concerns"] == 0
        assert result["themes_count"] == 0
        assert len(result["concern_patterns"]) == 0
        assert len(result["common_themes"]) == 0

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_review_artifact_all_errors(self, test_workspace):
        """Test artifact review when all experts fail."""
        # Create state.json file
        state_file = test_workspace / "state.json"
        state_file.write_text(json.dumps({
            "topic": "Test Topic",
            "mode": "adr",
            "experts": ["typescript", "python"],
            "iteration": 1,
            "convergence_percent": 85,
            "convergence_target": 80,
            "draft_artifact_iteration": 1,
            "draft_artifact_path": "iteration-1/draft-adr.md"
        }))

        # Create artifact file
        artifact_file = test_workspace / "iteration-1" / "draft-adr.md"
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_text("# ADR\n\nContent here")

        mock_config = Mock()

        mock_review_results = [
            {"expert": "typescript", "status": "error", "error": "Failed"},
            {"expert": "python", "status": "timeout", "error": "Timeout"}
        ]

        with patch('core.artifact_review.load_expert_info', return_value={"background": "Expert bg"}), \
             patch('core.artifact_review.render_template', return_value="Review prompt"), \
             patch('asyncio.gather', new_callable=AsyncMock) as mock_gather:

            mock_gather.return_value = mock_review_results

            result = await artifact_review.review_artifact(test_workspace, mock_config)

        # Should return approved if no valid decisions (fail-open)
        assert result["status"] == "approved"

    @pytest.mark.critical
    def test_veto_pattern_single_expert_multiple_concerns(self):
        """Test veto pattern detection with single expert raising multiple concerns."""
        concerns_data = {
            "concerns": [
                {"theme": "Testing", "expert": "typescript", "id": "c1"},
                {"theme": "Testing", "expert": "typescript", "id": "c2"}
            ]
        }

        expert_reviews = {
            "typescript": {
                "decision": "concerns_raised",
                "concerns": [
                    {"theme": "Testing"},
                    {"theme": "Testing"}
                ]
            }
        }

        result = artifact_review.create_regeneration_context(
            concerns_data,
            expert_reviews
        )

        # Should identify as pattern (2+ concerns in same theme)
        assert len(result["concern_patterns"]) == 1
        assert result["concern_patterns"][0]["theme"] == "Testing"
        assert result["concern_patterns"][0]["concern_count"] == 2
        assert result["concern_patterns"][0]["expert_count"] == 1

    @pytest.mark.asyncio
    @pytest.mark.critical
    async def test_synthesize_concerns_with_invalid_json(self, test_workspace, tmp_path):
        """Test handling of corrupted expert review JSON files."""
        iteration_dir = tmp_path / "iteration-2"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        experts_dir = tmp_path / "experts"
        experts_dir.mkdir(parents=True, exist_ok=True)

        # Create invalid JSON file
        expert_dir = experts_dir / "typescript"
        expert_dir.mkdir(parents=True, exist_ok=True)
        review_json = expert_dir / "artifact-review-typescript.json"
        review_json.write_text("invalid json{")

        results = [{"expert": "typescript", "status": "complete"}]
        mock_state = Mock()
        mock_config = Mock()

        result = await artifact_review.synthesize_artifact_concerns(
            workspace=test_workspace,
            iteration_dir=iteration_dir,
            experts_dir=experts_dir,
            state=mock_state,
            results=results,
            config=mock_config
        )

        # Should handle gracefully and report error
        assert result["status"] == "error"
