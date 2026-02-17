"""
Unit tests for error hierarchy.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from errors import (
    WorkflowError,
    ExpertTimeoutError,
    ExpertFailureError,
    ConsolidationFailureError,
    ParsingError,
    ConvergenceStallError,
    CircuitBreakerError,
    MinimumExpertsError
)


class TestWorkflowError:
    """Test base WorkflowError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = WorkflowError("Something went wrong", recoverable=True)
        assert error.message == "Something went wrong"
        assert error.recoverable is True
        assert str(error) == "Something went wrong"

    def test_default_recoverable(self):
        """Test default recoverable value."""
        error = WorkflowError("Error")
        assert error.recoverable is True


class TestExpertTimeoutError:
    """Test ExpertTimeoutError."""

    def test_creation(self):
        """Test error creation with expert and timeout."""
        error = ExpertTimeoutError(expert="typescript", timeout_seconds=900)
        assert error.expert == "typescript"
        assert error.timeout_seconds == 900
        assert error.recoverable is True
        assert "typescript" in str(error)
        assert "900" in str(error)


class TestExpertFailureError:
    """Test ExpertFailureError."""

    def test_creation(self):
        """Test error creation."""
        error = ExpertFailureError(expert="security", error="Connection timeout")
        assert error.expert == "security"
        assert error.error_detail == "Connection timeout"
        assert error.recoverable is True


class TestConsolidationFailureError:
    """Test ConsolidationFailureError."""

    def test_creation(self):
        """Test error creation."""
        error = ConsolidationFailureError(iteration=2, error="Parsing failed")
        assert error.iteration == 2
        assert error.error_detail == "Parsing failed"
        assert error.recoverable is False  # Consolidation failure is not recoverable


class TestParsingError:
    """Test ParsingError."""

    def test_creation(self):
        """Test error creation."""
        error = ParsingError(
            expert="typescript",
            markdown_path="/path/to/review.md",
            strategies_tried=3
        )
        assert error.expert == "typescript"
        assert error.markdown_path == "/path/to/review.md"
        assert error.strategies_tried == 3
        assert error.recoverable is False


class TestConvergenceStallError:
    """Test ConvergenceStallError."""

    def test_creation(self):
        """Test error creation."""
        error = ConvergenceStallError(stuck_iterations=2, current_convergence=75)
        assert error.stuck_iterations == 2
        assert error.current_convergence == 75
        assert error.recoverable is True


class TestCircuitBreakerError:
    """Test CircuitBreakerError."""

    def test_creation(self):
        """Test error creation."""
        diagnostic = {
            "consecutive_failures": 2,
            "stuck_iterations": 0,
            "convergence": 50
        }
        error = CircuitBreakerError(
            reason="Multiple consecutive failures",
            diagnostic_info=diagnostic
        )
        assert error.reason == "Multiple consecutive failures"
        assert error.diagnostic_info == diagnostic
        assert error.recoverable is True


class TestMinimumExpertsError:
    """Test MinimumExpertsError."""

    def test_creation(self):
        """Test error creation."""
        error = MinimumExpertsError(
            success_count=2,
            minimum_required=3,
            total_experts=5
        )
        assert error.success_count == 2
        assert error.minimum_required == 3
        assert error.total_experts == 5
        assert error.recoverable is False
        assert "2/5" in str(error)
        assert "minimum required: 3" in str(error)


class TestErrorInheritance:
    """Test error inheritance and exception handling."""

    def test_all_inherit_from_workflow_error(self):
        """Test that all errors inherit from WorkflowError."""
        errors = [
            ExpertTimeoutError("typescript", 900),
            ExpertFailureError("security", "timeout"),
            ConsolidationFailureError(1, "failed"),
            ParsingError("typescript", "/path", 1),
            ConvergenceStallError(2, 75),
            CircuitBreakerError("reason", {}),
            MinimumExpertsError(2, 3, 5)
        ]

        for error in errors:
            assert isinstance(error, WorkflowError)
            assert isinstance(error, Exception)

    def test_catching_specific_errors(self):
        """Test catching specific error types."""
        try:
            raise ExpertTimeoutError("typescript", 900)
        except ExpertTimeoutError as e:
            assert e.expert == "typescript"
        except WorkflowError:
            pytest.fail("Should catch specific error type")

    def test_catching_base_error(self):
        """Test catching all workflow errors."""
        try:
            raise MinimumExpertsError(2, 3, 5)
        except WorkflowError as e:
            assert e.recoverable is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
