"""
Additional unit tests for validation/convergence.py to improve coverage.

Tests previously uncovered functions:
- validate_llm_convergence()
- parse_recommendations_from_state()
- calculate_convergence_from_state()
- calculate_convergence() with logger parameter

Target: Improve convergence.py coverage from 49% to 75%+
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validation.convergence import (
    ConvergenceMetrics,
    calculate_convergence,
    validate_llm_convergence,
    parse_recommendations_from_state,
    calculate_convergence_from_state
)


class TestValidateLLMConvergence:
    """Test validate_llm_convergence() function."""

    @pytest.mark.medium
    def test_validate_within_tolerance(self):
        """Test validation when convergence is within tolerance."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=82,
            programmatic_convergence=80,
            tolerance=5
        )

        assert is_valid is True
        assert "validated" in msg.lower()
        assert "2%" in msg

    @pytest.mark.medium
    def test_validate_exact_match(self):
        """Test validation when convergences match exactly."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=75,
            programmatic_convergence=75,
            tolerance=5
        )

        assert is_valid is True
        assert "0%" in msg

    @pytest.mark.medium
    def test_validate_outside_tolerance(self):
        """Test validation when convergence is outside tolerance."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=90,
            programmatic_convergence=75,
            tolerance=10
        )

        assert is_valid is False
        assert "90%" in msg
        assert "75%" in msg
        assert "15%" in msg  # Difference

    @pytest.mark.medium
    def test_validate_at_tolerance_boundary(self):
        """Test validation at exact tolerance boundary."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=85,
            programmatic_convergence=80,
            tolerance=5
        )

        # Exactly at boundary should be valid (diff == tolerance)
        assert is_valid is True

    @pytest.mark.medium
    def test_validate_invalid_llm_convergence_negative(self):
        """Test with invalid negative LLM convergence."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=-10,
            programmatic_convergence=80,
            tolerance=5
        )

        assert is_valid is False
        assert "Invalid LLM convergence" in msg
        assert "-10%" in msg

    @pytest.mark.medium
    def test_validate_invalid_llm_convergence_over_100(self):
        """Test with invalid LLM convergence > 100."""
        is_valid, msg = validate_llm_convergence(
            llm_convergence=105,
            programmatic_convergence=80,
            tolerance=5
        )

        assert is_valid is False
        assert "Invalid LLM convergence" in msg
        assert "105%" in msg

    @pytest.mark.medium
    def test_validate_invalid_programmatic_convergence(self):
        """Test with invalid programmatic convergence."""
        mock_logger = Mock()

        is_valid, msg = validate_llm_convergence(
            llm_convergence=80,
            programmatic_convergence=150,
            tolerance=5,
            logger=mock_logger
        )

        assert is_valid is False
        assert "Invalid programmatic convergence" in msg
        assert "150%" in msg
        # Verify logger.error was called for invalid programmatic convergence
        assert mock_logger.error.called

    @pytest.mark.medium
    def test_validate_with_logger(self):
        """Test validation with logger parameter."""
        mock_logger = Mock()

        is_valid, msg = validate_llm_convergence(
            llm_convergence=82,
            programmatic_convergence=80,
            tolerance=5,
            logger=mock_logger
        )

        assert is_valid is True
        # Logger should have been called
        assert mock_logger.info.called

    @pytest.mark.medium
    def test_validate_with_logger_on_error(self):
        """Test that logger.error is called on validation error."""
        mock_logger = Mock()

        is_valid, msg = validate_llm_convergence(
            llm_convergence=105,  # Invalid
            programmatic_convergence=80,
            tolerance=5,
            logger=mock_logger
        )

        assert is_valid is False
        # Logger.error should have been called
        assert mock_logger.error.called

    @pytest.mark.medium
    def test_validate_with_logger_outside_tolerance(self):
        """Test that logger.warning is called when outside tolerance."""
        mock_logger = Mock()

        is_valid, msg = validate_llm_convergence(
            llm_convergence=90,
            programmatic_convergence=70,
            tolerance=10,
            logger=mock_logger
        )

        # Verify it returns False and logger.warning was called
        assert is_valid is False
        assert mock_logger.warning.called


class TestParseRecommendationsFromState:
    """Test parse_recommendations_from_state() function."""

    @pytest.mark.medium
    def test_parse_with_agreement_levels(self):
        """Test parsing recommendations that already have agreement_level."""
        state = {
            "recommendations": [
                {"id": "rec-1", "agreement_level": "high"},
                {"id": "rec-2", "agreement_level": "partial"}
            ]
        }

        recommendations = parse_recommendations_from_state(state)

        assert len(recommendations) == 2
        assert recommendations[0]["agreement_level"] == "high"
        assert recommendations[1]["agreement_level"] == "partial"

    @pytest.mark.medium
    def test_parse_with_empty_recommendations(self):
        """Test parsing state with no recommendations."""
        state = {"recommendations": []}

        recommendations = parse_recommendations_from_state(state)

        assert recommendations == []

    @pytest.mark.medium
    def test_parse_with_missing_recommendations_key(self):
        """Test parsing state without recommendations key."""
        state = {}

        recommendations = parse_recommendations_from_state(state)

        assert recommendations == []

    @pytest.mark.medium
    def test_parse_infers_high_agreement(self):
        """Test that high agreement is inferred from supporting_experts."""
        state = {
            "recommendations": [
                {
                    "id": "rec-1",
                    "supporting_experts": ["expert1", "expert2", "expert3", "expert4"]
                }
            ],
            "expert_count": 5
        }

        recommendations = parse_recommendations_from_state(state)

        # 4/5 experts = 80% > 75% threshold = high
        assert recommendations[0]["agreement_level"] == "high"

    @pytest.mark.medium
    def test_parse_infers_partial_agreement(self):
        """Test that partial agreement is inferred from supporting_experts."""
        # Use 7 experts with 4 supporting to get partial agreement
        # int(7*0.75)=5, so 4<5 (not high)
        # int(7*0.50)=3, so 4>=3 (partial)
        state = {
            "recommendations": [
                {
                    "id": "rec-1",
                    "supporting_experts": ["expert1", "expert2", "expert3", "expert4"]
                }
            ],
            "expert_count": 7
        }

        recommendations = parse_recommendations_from_state(state)

        # 4/7 experts = 57% → partial agreement
        assert recommendations[0]["agreement_level"] == "partial"

    @pytest.mark.medium
    def test_parse_infers_low_agreement(self):
        """Test that low agreement is inferred from supporting_experts."""
        state = {
            "recommendations": [
                {
                    "id": "rec-1",
                    "supporting_experts": ["expert1"]
                }
            ],
            "expert_count": 5
        }

        recommendations = parse_recommendations_from_state(state)

        # 1/5 experts = 20% < 50% = low
        assert recommendations[0]["agreement_level"] == "low"

    @pytest.mark.medium
    def test_parse_with_no_supporting_experts(self):
        """Test inference when supporting_experts is missing."""
        state = {
            "recommendations": [
                {"id": "rec-1"}  # No supporting_experts field
            ],
            "expert_count": 5
        }

        recommendations = parse_recommendations_from_state(state)

        # Should infer low (0 experts)
        assert recommendations[0]["agreement_level"] == "low"


class TestCalculateConvergenceFromState:
    """Test calculate_convergence_from_state() function."""

    @pytest.mark.medium
    def test_calculate_from_state(self):
        """Test calculating convergence directly from state."""
        state = {
            "recommendations": [
                {"id": "rec-1", "agreement_level": "high"},
                {"id": "rec-2", "agreement_level": "high"},
                {"id": "rec-3", "agreement_level": "partial"}
            ]
        }

        metrics = calculate_convergence_from_state(state, expert_count=5)

        # (100 + 100 + 50) / 3 = 83.33... = 83
        assert metrics.convergence_percent == 83
        assert metrics.high_agreement_count == 2
        assert metrics.partial_agreement_count == 1

    @pytest.mark.medium
    def test_calculate_from_state_with_target(self):
        """Test with custom target percentage."""
        state = {
            "recommendations": [
                {"id": "rec-1", "agreement_level": "high"}
            ]
        }

        metrics = calculate_convergence_from_state(
            state,
            expert_count=5,
            target_percent=90
        )

        assert metrics.convergence_percent == 100
        assert metrics.consensus_reached is True
        assert metrics.target_percent == 90

    @pytest.mark.medium
    def test_calculate_from_empty_state(self):
        """Test with empty recommendations in state."""
        state = {"recommendations": []}

        metrics = calculate_convergence_from_state(state, expert_count=5)

        # Empty = 100% convergence
        assert metrics.convergence_percent == 100
        assert metrics.total_recommendations == 0


class TestCalculateConvergenceWithLogger:
    """Test calculate_convergence() with logger parameter."""

    @pytest.mark.medium
    def test_calculate_with_logger(self):
        """Test that logger is called during calculation."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "partial"}
        ]

        metrics = calculate_convergence(
            recommendations,
            expert_count=5,
            logger=mock_logger
        )

        # Logger should have been called
        assert mock_logger.info.called
        # Should have logged initial message
        assert any("Calculating convergence" in str(call) for call in mock_logger.info.call_args_list)

    @pytest.mark.medium
    def test_calculate_empty_with_logger(self):
        """Test logger message for empty recommendations."""
        mock_logger = Mock()

        metrics = calculate_convergence(
            [],
            expert_count=5,
            logger=mock_logger
        )

        # Should log the "nothing to disagree on" message
        assert mock_logger.info.called
        logged_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("100%" in msg or "nothing to disagree on" in msg for msg in logged_messages)

    @pytest.mark.medium
    def test_calculate_with_logger_debug_messages(self):
        """Test that debug messages are logged for each recommendation."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(
            recommendations,
            expert_count=5,
            logger=mock_logger
        )

        # Debug should have been called for each recommendation
        assert mock_logger.debug.called

    @pytest.mark.medium
    def test_calculate_with_logger_invalid_level(self):
        """Test logger.error is called for invalid agreement_level."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "invalid"}
        ]

        with pytest.raises(ValueError):
            calculate_convergence(
                recommendations,
                expert_count=5,
                logger=mock_logger
            )

        # Logger.error should have been called
        assert mock_logger.error.called


class TestConvergenceEdgeCasesWithLogger:
    """Test edge cases with logger parameter."""

    @pytest.mark.medium
    def test_all_high_with_logger(self):
        """Test 100% convergence with logger."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "high"}
        ]

        metrics = calculate_convergence(
            recommendations,
            expert_count=5,
            logger=mock_logger
        )

        assert metrics.convergence_percent == 100
        assert mock_logger.info.called

    @pytest.mark.medium
    def test_consensus_reached_logging(self):
        """Test that consensus message is logged."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"}
        ]

        metrics = calculate_convergence(
            recommendations,
            expert_count=5,
            target_percent=80,
            logger=mock_logger
        )

        assert metrics.consensus_reached is True
        # Should have logged consensus result
        logged_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("consensus" in msg.lower() for msg in logged_messages)

    @pytest.mark.medium
    def test_consensus_not_reached_logging(self):
        """Test that non-consensus message is logged."""
        mock_logger = Mock()
        recommendations = [
            {"id": "rec-1", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(
            recommendations,
            expert_count=5,
            target_percent=80,
            logger=mock_logger
        )

        assert metrics.consensus_reached is False
        # Should have logged consensus result
        logged_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("need" in msg.lower() or "no" in msg.lower() for msg in logged_messages)
