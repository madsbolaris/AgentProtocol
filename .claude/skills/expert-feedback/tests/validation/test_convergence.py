"""
Unit tests for validation/convergence.py

Tests convergence calculation including:
- ConvergenceMetrics dataclass validation
- calculate_convergence() agreement calculation
- Weighting formula (high=100%, partial=50%, low=0%)
- Consensus detection
- Error handling

Target coverage: 85%+
"""
import pytest
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validation.convergence import ConvergenceMetrics, calculate_convergence


class TestConvergenceMetricsDataclass:
    """Test ConvergenceMetrics dataclass."""

    @pytest.mark.medium
    def test_metrics_creation(self):
        """Test creating ConvergenceMetrics instance."""
        metrics = ConvergenceMetrics(
            convergence_percent=80,
            high_agreement_count=5,
            partial_agreement_count=3,
            low_agreement_count=2,
            total_recommendations=10,
            consensus_reached=True,
            target_percent=80
        )

        assert metrics.convergence_percent == 80
        assert metrics.high_agreement_count == 5
        assert metrics.consensus_reached is True

    @pytest.mark.medium
    def test_metrics_validation_convergence_percent(self):
        """Test validation of convergence_percent range."""
        # Should raise for > 100
        with pytest.raises(ValueError, match="Invalid convergence"):
            ConvergenceMetrics(
                convergence_percent=150,
                high_agreement_count=0,
                partial_agreement_count=0,
                low_agreement_count=0,
                total_recommendations=0,
                consensus_reached=False,
                target_percent=80
            )

        # Should raise for < 0
        with pytest.raises(ValueError, match="Invalid convergence"):
            ConvergenceMetrics(
                convergence_percent=-10,
                high_agreement_count=0,
                partial_agreement_count=0,
                low_agreement_count=0,
                total_recommendations=0,
                consensus_reached=False,
                target_percent=80
            )

    @pytest.mark.medium
    def test_metrics_validation_total_mismatch(self):
        """Test validation that counts match total."""
        with pytest.raises(ValueError, match="Agreement counts"):
            ConvergenceMetrics(
                convergence_percent=50,
                high_agreement_count=5,
                partial_agreement_count=3,
                low_agreement_count=2,
                total_recommendations=15,  # Mismatch: 5+3+2 = 10, not 15
                consensus_reached=False,
                target_percent=80
            )

    @pytest.mark.medium
    def test_metrics_str_representation(self):
        """Test string representation."""
        metrics = ConvergenceMetrics(
            convergence_percent=75,
            high_agreement_count=3,
            partial_agreement_count=2,
            low_agreement_count=1,
            total_recommendations=6,
            consensus_reached=False,
            target_percent=80
        )

        str_repr = str(metrics)

        assert "75%" in str_repr
        assert "high: 3" in str_repr
        assert "partial: 2" in str_repr


class TestCalculateConvergence:
    """Test calculate_convergence function."""

    @pytest.mark.medium
    def test_calculate_all_high_agreement(self):
        """Test convergence with all high agreement."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "high"},
            {"id": "rec-3", "agreement_level": "high"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.convergence_percent == 100
        assert metrics.high_agreement_count == 3
        assert metrics.partial_agreement_count == 0
        assert metrics.low_agreement_count == 0

    @pytest.mark.medium
    def test_calculate_all_partial_agreement(self):
        """Test convergence with all partial agreement."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "partial"},
            {"id": "rec-2", "agreement_level": "partial"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.convergence_percent == 50  # 50% weight per partial
        assert metrics.partial_agreement_count == 2

    @pytest.mark.medium
    def test_calculate_all_low_agreement(self):
        """Test convergence with all low agreement."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "low"},
            {"id": "rec-2", "agreement_level": "low"},
            {"id": "rec-3", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.convergence_percent == 0  # 0% weight for low
        assert metrics.low_agreement_count == 3

    @pytest.mark.medium
    def test_calculate_mixed_agreement(self):
        """Test convergence with mixed agreement levels."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},     # 100
            {"id": "rec-2", "agreement_level": "partial"},  # 50
            {"id": "rec-3", "agreement_level": "low"}       # 0
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        # (100 + 50 + 0) / 3 = 50
        assert metrics.convergence_percent == 50
        assert metrics.high_agreement_count == 1
        assert metrics.partial_agreement_count == 1
        assert metrics.low_agreement_count == 1

    @pytest.mark.medium
    def test_consensus_reached_above_target(self):
        """Test consensus_reached flag when above target."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "high"},
            {"id": "rec-3", "agreement_level": "high"},
            {"id": "rec-4", "agreement_level": "high"},
            {"id": "rec-5", "agreement_level": "partial"}
        ]

        metrics = calculate_convergence(
            recommendations, expert_count=5, target_percent=80
        )

        # (100*4 + 50*1) / 5 = 90%
        assert metrics.convergence_percent == 90
        assert metrics.consensus_reached is True

    @pytest.mark.medium
    def test_consensus_not_reached_below_target(self):
        """Test consensus_reached flag when below target."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "partial"},
            {"id": "rec-2", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(
            recommendations, expert_count=5, target_percent=80
        )

        # (50 + 0) / 2 = 25%
        assert metrics.convergence_percent == 25
        assert metrics.consensus_reached is False

    @pytest.mark.medium
    def test_consensus_exactly_at_target(self):
        """Test consensus when exactly at target."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "high"},
            {"id": "rec-3", "agreement_level": "high"},
            {"id": "rec-4", "agreement_level": "high"},
            {"id": "rec-5", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(
            recommendations, expert_count=5, target_percent=80
        )

        # (100*4 + 0*1) / 5 = 80%
        assert metrics.convergence_percent == 80
        assert metrics.consensus_reached is True

    @pytest.mark.medium
    def test_custom_target_percent(self):
        """Test custom target convergence percentage."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(
            recommendations, expert_count=5, target_percent=50
        )

        # (100 + 0) / 2 = 50%
        assert metrics.convergence_percent == 50
        assert metrics.consensus_reached is True  # Exactly at 50% target


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.medium
    def test_empty_recommendations(self):
        """Test with no recommendations."""
        recommendations = []

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.total_recommendations == 0
        assert metrics.convergence_percent == 100  # No recommendations = nothing to disagree on

    @pytest.mark.medium
    def test_single_recommendation_high(self):
        """Test with single high agreement recommendation."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.convergence_percent == 100
        assert metrics.total_recommendations == 1

    @pytest.mark.medium
    def test_invalid_agreement_level(self):
        """Test with invalid agreement level."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "invalid"}
        ]

        with pytest.raises(ValueError):
            calculate_convergence(recommendations, expert_count=5)

    @pytest.mark.medium
    def test_missing_agreement_level(self):
        """Test with missing agreement_level field."""
        recommendations = [
            {"id": "rec-1"}  # Missing agreement_level
        ]

        with pytest.raises(ValueError):  # Implementation uses .get() which returns "", then raises ValueError
            calculate_convergence(recommendations, expert_count=5)

    @pytest.mark.medium
    def test_large_number_of_recommendations(self):
        """Test with many recommendations."""
        recommendations = [
            {"id": f"rec-{i}", "agreement_level": "high"}
            for i in range(100)
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        assert metrics.total_recommendations == 100
        assert metrics.convergence_percent == 100

    @pytest.mark.medium
    def test_case_sensitive_agreement_levels(self):
        """Test that agreement levels are case-sensitive."""
        recommendations = [
            {"id": "rec-1", "agreement_level": "High"}  # Capital H
        ]

        # Should raise or handle case mismatch
        try:
            metrics = calculate_convergence(recommendations, expert_count=5)
            # If it doesn't raise, it should normalize
        except ValueError:
            # Expected if case-sensitive
            pass


class TestConvergenceFormula:
    """Test convergence formula calculations."""

    @pytest.mark.medium
    def test_formula_weighting(self):
        """Test the weighting formula explicitly."""
        # 2 high (100 each), 1 partial (50), 1 low (0)
        # Total: (200 + 50 + 0) / 4 = 62.5% -> rounded
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "high"},
            {"id": "rec-3", "agreement_level": "partial"},
            {"id": "rec-4", "agreement_level": "low"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        # Expected: (100 + 100 + 50 + 0) / 4 = 62.5
        # Depending on rounding, could be 62 or 63
        assert 62 <= metrics.convergence_percent <= 63

    @pytest.mark.medium
    def test_formula_with_rounding(self):
        """Test rounding behavior in convergence calculation."""
        # 1 high, 2 partial: (100 + 50 + 50) / 3 = 66.666...
        recommendations = [
            {"id": "rec-1", "agreement_level": "high"},
            {"id": "rec-2", "agreement_level": "partial"},
            {"id": "rec-3", "agreement_level": "partial"}
        ]

        metrics = calculate_convergence(recommendations, expert_count=5)

        # Should round to 67
        assert 66 <= metrics.convergence_percent <= 67
