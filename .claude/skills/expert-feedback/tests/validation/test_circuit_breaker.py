"""
Unit tests for validation/circuit_breaker.py

Tests circuit breaker safety mechanism including:
- CircuitBreakerState initialization
- update() state tracking
- should_break() trigger detection
- reset() state clearing
- save_diagnostic() diagnostic file creation
- load_circuit_breaker() state loading

Target coverage: 85%+
"""
import pytest
import json
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from validation.circuit_breaker import CircuitBreakerState, load_circuit_breaker


class TestCircuitBreakerStateInit:
    """Test CircuitBreakerState initialization."""

    @pytest.mark.medium
    def test_default_initialization(self):
        """Test default initialization values."""
        breaker = CircuitBreakerState()

        assert breaker.consecutive_failures == 0
        assert breaker.last_convergence == 0
        assert breaker.stuck_iterations == 0
        assert breaker.max_consecutive_failures == 2
        assert breaker.max_stuck_iterations == 2
        assert breaker.convergence_improvement_threshold == 3

    @pytest.mark.medium
    def test_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        breaker = CircuitBreakerState(
            max_consecutive_failures=5,
            max_stuck_iterations=3,
            convergence_improvement_threshold=5
        )

        assert breaker.max_consecutive_failures == 5
        assert breaker.max_stuck_iterations == 3
        assert breaker.convergence_improvement_threshold == 5


class TestUpdateMethod:
    """Test update() method."""

    @pytest.mark.medium
    def test_update_with_success(self):
        """Test updating with successful iteration."""
        breaker = CircuitBreakerState()

        breaker.update(current_convergence=50, failed=False)

        assert breaker.consecutive_failures == 0
        assert breaker.last_convergence == 50

    @pytest.mark.medium
    def test_update_with_failure(self):
        """Test updating with failed iteration."""
        breaker = CircuitBreakerState()

        breaker.update(current_convergence=30, failed=True)

        assert breaker.consecutive_failures == 1

    @pytest.mark.medium
    def test_update_multiple_failures(self):
        """Test consecutive failures tracking."""
        breaker = CircuitBreakerState()

        breaker.update(30, failed=True)
        breaker.update(30, failed=True)
        breaker.update(30, failed=True)

        assert breaker.consecutive_failures == 3

    @pytest.mark.medium
    def test_update_resets_failures_on_success(self):
        """Test that success resets failure count."""
        breaker = CircuitBreakerState()

        breaker.update(30, failed=True)
        breaker.update(30, failed=True)
        assert breaker.consecutive_failures == 2

        breaker.update(40, failed=False)
        assert breaker.consecutive_failures == 0

    @pytest.mark.medium
    def test_update_detects_stalled_convergence(self):
        """Test detection of stalled convergence."""
        breaker = CircuitBreakerState(convergence_improvement_threshold=3)

        # First update sets baseline
        breaker.update(50, failed=False)
        assert breaker.stuck_iterations == 0

        # Small improvement (< 3%) should increment stuck counter
        breaker.update(51, failed=False)  # Only 1% improvement
        assert breaker.stuck_iterations == 1

        breaker.update(51, failed=False)  # No improvement
        assert breaker.stuck_iterations == 2

    @pytest.mark.medium
    def test_update_resets_stuck_on_good_improvement(self):
        """Test that good improvement resets stuck counter."""
        breaker = CircuitBreakerState(convergence_improvement_threshold=3)

        breaker.update(50, failed=False)
        breaker.update(51, failed=False)  # Small improvement
        assert breaker.stuck_iterations == 1

        breaker.update(55, failed=False)  # 4% improvement
        assert breaker.stuck_iterations == 0

    @pytest.mark.medium
    def test_update_with_decreasing_convergence(self):
        """Test that convergence decrease is detected."""
        breaker = CircuitBreakerState(convergence_improvement_threshold=3)

        breaker.update(80, failed=False)
        breaker.update(75, failed=False)  # 5% decrease (abs = 5 > 3)

        # Large change (even negative) should reset stuck
        assert breaker.stuck_iterations == 0


class TestShouldBreakMethod:
    """Test should_break() trigger detection."""

    @pytest.mark.medium
    def test_should_not_break_initially(self):
        """Test that circuit doesn't break initially."""
        breaker = CircuitBreakerState()

        should_break, reason = breaker.should_break()

        assert should_break is False
        assert reason == ""

    @pytest.mark.medium
    def test_should_break_on_max_failures(self):
        """Test breaking on max consecutive failures."""
        breaker = CircuitBreakerState(max_consecutive_failures=2)

        breaker.update(30, failed=True)
        breaker.update(30, failed=True)

        should_break, reason = breaker.should_break()

        assert should_break is True
        assert "consecutive failures" in reason.lower()

    @pytest.mark.medium
    def test_should_break_on_stuck_convergence(self):
        """Test breaking on stuck convergence."""
        breaker = CircuitBreakerState(
            max_stuck_iterations=2,
            convergence_improvement_threshold=3
        )

        breaker.update(50, failed=False)
        breaker.update(50, failed=False)  # No improvement
        breaker.update(51, failed=False)  # Tiny improvement (< 3%)

        should_break, reason = breaker.should_break()

        assert should_break is True
        assert "stalled" in reason.lower()

    @pytest.mark.medium
    def test_should_not_break_below_threshold(self):
        """Test not breaking when below thresholds."""
        breaker = CircuitBreakerState(
            max_consecutive_failures=3,
            max_stuck_iterations=3
        )

        breaker.update(50, failed=True)
        breaker.update(50, failed=False)
        breaker.update(51, failed=False)

        should_break, reason = breaker.should_break()

        assert should_break is False


class TestResetMethod:
    """Test reset() state clearing."""

    @pytest.mark.medium
    def test_reset_clears_failures(self):
        """Test that reset clears failure count."""
        breaker = CircuitBreakerState()

        breaker.update(30, failed=True)
        breaker.update(30, failed=True)
        assert breaker.consecutive_failures == 2

        breaker.reset()

        assert breaker.consecutive_failures == 0

    @pytest.mark.medium
    def test_reset_clears_stuck_iterations(self):
        """Test that reset clears stuck counter."""
        breaker = CircuitBreakerState(convergence_improvement_threshold=3)

        breaker.update(50, failed=False)
        breaker.update(50, failed=False)
        assert breaker.stuck_iterations == 1

        breaker.reset()

        assert breaker.stuck_iterations == 0

    @pytest.mark.medium
    def test_reset_preserves_last_convergence(self):
        """Test that reset preserves convergence value."""
        breaker = CircuitBreakerState()

        breaker.update(75, failed=False)
        breaker.reset()

        # Last convergence should be preserved
        assert breaker.last_convergence == 75


class TestToDictMethod:
    """Test to_dict() serialization."""

    @pytest.mark.medium
    def test_to_dict_structure(self):
        """Test dictionary structure."""
        breaker = CircuitBreakerState(
            consecutive_failures=2,
            last_convergence=60,
            stuck_iterations=1
        )

        data = breaker.to_dict()

        assert isinstance(data, dict)
        assert data["consecutive_failures"] == 2
        assert data["last_convergence"] == 60
        assert data["stuck_iterations"] == 1


class TestSaveDiagnostic:
    """Test save_diagnostic() method."""

    @pytest.mark.medium
    def test_save_diagnostic_creates_file(self, tmp_path):
        """Test that diagnostic file is created."""
        breaker = CircuitBreakerState()
        breaker.update(50, failed=True)
        breaker.update(50, failed=True)

        diagnostic_path = breaker.save_diagnostic(
            workspace=tmp_path,
            iteration=2,
            convergence=50
        )

        assert diagnostic_path.exists()
        assert diagnostic_path.name == "circuit-breaker-diagnostic.json"

    @pytest.mark.medium
    def test_save_diagnostic_content(self, tmp_path):
        """Test diagnostic file content."""
        breaker = CircuitBreakerState()
        breaker.update(50, failed=True)
        breaker.update(50, failed=True)

        diagnostic_path = breaker.save_diagnostic(
            workspace=tmp_path,
            iteration=3,
            convergence=55
        )

        with open(diagnostic_path) as f:
            data = json.load(f)

        assert data["iteration"] == 3
        assert data["convergence"] == 55
        assert data["consecutive_failures"] == 2
        assert "state" in data

    @pytest.mark.medium
    def test_save_diagnostic_overwrites(self, tmp_path):
        """Test that diagnostic file is overwritten."""
        breaker = CircuitBreakerState()

        # Save first diagnostic
        breaker.save_diagnostic(tmp_path, iteration=1, convergence=40)

        # Save second diagnostic
        breaker.update(45, failed=False)
        path = breaker.save_diagnostic(tmp_path, iteration=2, convergence=45)

        with open(path) as f:
            data = json.load(f)

        # Should have latest values
        assert data["iteration"] == 2
        assert data["convergence"] == 45


class TestLoadCircuitBreaker:
    """Test load_circuit_breaker() function."""

    @pytest.mark.medium
    def test_load_nonexistent_returns_none(self, tmp_path):
        """Test loading when no diagnostic file exists."""
        result = load_circuit_breaker(tmp_path)

        assert result is None

    @pytest.mark.medium
    def test_load_existing_state(self, tmp_path):
        """Test loading existing circuit breaker state."""
        # Create diagnostic file
        breaker = CircuitBreakerState()
        breaker.update(60, failed=True)
        breaker.update(60, failed=True)
        breaker.save_diagnostic(tmp_path, iteration=2, convergence=60)

        # Load state
        loaded = load_circuit_breaker(tmp_path)

        assert loaded is not None
        assert loaded.consecutive_failures == 2
        assert loaded.last_convergence == 60

    @pytest.mark.medium
    def test_load_corrupted_file_returns_none(self, tmp_path, capsys):
        """Test loading corrupted diagnostic file."""
        # Create invalid JSON file
        diagnostic_path = tmp_path / "circuit-breaker-diagnostic.json"
        diagnostic_path.write_text("invalid json {")

        result = load_circuit_breaker(tmp_path)

        # Should return None on error
        assert result is None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.medium
    def test_zero_convergence(self):
        """Test with zero convergence."""
        breaker = CircuitBreakerState()

        breaker.update(0, failed=False)

        assert breaker.last_convergence == 0

    @pytest.mark.medium
    def test_hundred_percent_convergence(self):
        """Test with 100% convergence."""
        breaker = CircuitBreakerState()

        breaker.update(100, failed=False)

        assert breaker.last_convergence == 100

    @pytest.mark.medium
    def test_exact_threshold_improvement(self):
        """Test improvement exactly at threshold."""
        breaker = CircuitBreakerState(convergence_improvement_threshold=3)

        breaker.update(50, failed=False)
        breaker.update(53, failed=False)  # Exactly 3% improvement

        # At threshold should reset stuck counter
        assert breaker.stuck_iterations == 0

    @pytest.mark.medium
    def test_many_iterations_no_break(self):
        """Test many successful iterations."""
        breaker = CircuitBreakerState()

        for i in range(10):
            breaker.update(50 + i*5, failed=False)

        should_break, _ = breaker.should_break()
        assert should_break is False

    @pytest.mark.medium
    def test_alternating_success_failure(self):
        """Test alternating success and failure."""
        breaker = CircuitBreakerState(max_consecutive_failures=3, max_stuck_iterations=999)

        breaker.update(50, failed=True)
        breaker.update(55, failed=False)
        breaker.update(60, failed=True)
        breaker.update(65, failed=False)

        # Failures not consecutive, should not break
        should_break, _ = breaker.should_break()
        assert should_break is False
        assert breaker.consecutive_failures == 0
