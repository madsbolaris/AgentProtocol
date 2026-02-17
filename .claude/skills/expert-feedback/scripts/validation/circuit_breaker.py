"""
Circuit breaker for expert-feedback workflow.

Detects stuck convergence and repeated failures to prevent infinite loops
and wasted compute. Provides diagnostic information for debugging.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class CircuitBreakerState:
    """
    Tracks workflow health to detect stuck state and trigger intervention.

    The circuit breaker monitors:
    - Consecutive consolidation failures
    - Convergence stagnation (< 3% improvement)
    - Overall iteration progress

    When thresholds are exceeded, it triggers intervention to prevent
    infinite loops and alert the user.
    """

    consecutive_failures: int = 0
    last_convergence: int = 0
    stuck_iterations: int = 0
    max_consecutive_failures: int = 2
    max_stuck_iterations: int = 2
    convergence_improvement_threshold: int = 3  # Minimum % improvement

    def update(self, current_convergence: int, failed: bool) -> None:
        """
        Update circuit breaker state after an iteration.

        Args:
            current_convergence: Current convergence percentage (0-100)
            failed: Whether consolidation failed this iteration
        """
        # Track consecutive failures
        if failed:
            self.consecutive_failures += 1
        else:
            self.consecutive_failures = 0

        # Detect stalled convergence (< 3% improvement)
        improvement = abs(current_convergence - self.last_convergence)
        if improvement < self.convergence_improvement_threshold:
            self.stuck_iterations += 1
        else:
            self.stuck_iterations = 0

        self.last_convergence = current_convergence

    def should_break(self) -> tuple[bool, str]:
        """
        Check if circuit should break.

        Returns:
            (should_break, reason): True if circuit should break, with reason string
        """
        if self.consecutive_failures >= self.max_consecutive_failures:
            return True, f"Multiple consecutive failures ({self.consecutive_failures})"

        if self.stuck_iterations >= self.max_stuck_iterations:
            return True, f"Convergence stalled ({self.stuck_iterations} iterations)"

        return False, ""

    def reset(self) -> None:
        """Reset circuit breaker state (user chose to continue)."""
        self.consecutive_failures = 0
        self.stuck_iterations = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def save_diagnostic(self, workspace: Path, iteration: int, convergence: int) -> Path:
        """
        Save diagnostic report to workspace.

        Args:
            workspace: Workspace directory
            iteration: Current iteration number
            convergence: Current convergence percentage

        Returns:
            Path to diagnostic file
        """
        diagnostic_path = workspace / "circuit-breaker-diagnostic.json"

        diagnostic = {
            "reason": self.should_break()[1],
            "iteration": iteration,
            "convergence": convergence,
            "consecutive_failures": self.consecutive_failures,
            "stuck_iterations": self.stuck_iterations,
            "last_convergence": self.last_convergence,
            "state": self.to_dict()
        }

        diagnostic_path.write_text(json.dumps(diagnostic, indent=2))
        return diagnostic_path


def load_circuit_breaker(workspace: Path) -> Optional[CircuitBreakerState]:
    """
    Load circuit breaker state from workspace (for resume).

    Args:
        workspace: Workspace directory

    Returns:
        CircuitBreakerState if exists, None otherwise
    """
    diagnostic_path = workspace / "circuit-breaker-diagnostic.json"

    if not diagnostic_path.exists():
        return None

    try:
        with open(diagnostic_path) as f:
            data = json.load(f)

        state_data = data.get("state", {})
        return CircuitBreakerState(
            consecutive_failures=state_data.get("consecutive_failures", 0),
            last_convergence=state_data.get("last_convergence", 0),
            stuck_iterations=state_data.get("stuck_iterations", 0)
        )
    except Exception:
        # If loading fails, start fresh
        return None
