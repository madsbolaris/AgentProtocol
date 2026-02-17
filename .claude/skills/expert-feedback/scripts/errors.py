"""
Structured error types for expert-feedback workflow.

This module defines a hierarchy of error types that represent different failure modes
in the workflow. Each error type indicates whether it's recoverable and provides
context for debugging and recovery.
"""


class WorkflowError(Exception):
    """Base class for all workflow errors."""

    def __init__(self, message: str, recoverable: bool = True):
        """
        Initialize workflow error.

        Args:
            message: Human-readable error description
            recoverable: Whether workflow can continue after this error
        """
        self.message = message
        self.recoverable = recoverable
        super().__init__(message)


class ExpertTimeoutError(WorkflowError):
    """Expert exceeded timeout."""

    def __init__(self, expert: str, timeout_seconds: int):
        """
        Initialize expert timeout error.

        Args:
            expert: Name of expert that timed out
            timeout_seconds: Configured timeout value
        """
        super().__init__(
            f"Expert '{expert}' timed out after {timeout_seconds}s",
            recoverable=True  # Can continue with other experts
        )
        self.expert = expert
        self.timeout_seconds = timeout_seconds


class ExpertFailureError(WorkflowError):
    """Expert failed to produce output."""

    def __init__(self, expert: str, error: str):
        """
        Initialize expert failure error.

        Args:
            expert: Name of expert that failed (or "multiple")
            error: Specific failure reason
        """
        super().__init__(
            f"Expert '{expert}' failed: {error}",
            recoverable=True  # Can continue with remaining experts
        )
        self.expert = expert
        self.error_detail = error


class ConsolidationFailureError(WorkflowError):
    """Consolidation failed."""

    def __init__(self, iteration: int, error: str):
        """
        Initialize consolidation failure error.

        Args:
            iteration: Iteration number where consolidation failed
            error: Specific failure reason
        """
        super().__init__(
            f"Consolidation failed at iteration {iteration}: {error}",
            recoverable=False  # Cannot continue without consolidation
        )
        self.iteration = iteration
        self.error_detail = error


class ParsingError(WorkflowError):
    """Failed to parse expert output."""

    def __init__(self, expert: str, markdown_path: str, strategies_tried: int = 1):
        """
        Initialize parsing error.

        Args:
            expert: Name of expert whose output failed to parse
            markdown_path: Path to markdown file that failed parsing
            strategies_tried: Number of parsing strategies attempted
        """
        super().__init__(
            f"Failed to parse review from expert '{expert}' at {markdown_path} "
            f"(tried {strategies_tried} parsing strategies)",
            recoverable=False  # Cannot continue without valid expert data
        )
        self.expert = expert
        self.markdown_path = markdown_path
        self.strategies_tried = strategies_tried


class ConvergenceStallError(WorkflowError):
    """Convergence hasn't improved across iterations."""

    def __init__(self, stuck_iterations: int, current_convergence: int):
        """
        Initialize convergence stall error.

        Args:
            stuck_iterations: Number of iterations without improvement
            current_convergence: Current convergence percentage
        """
        super().__init__(
            f"Convergence stalled for {stuck_iterations} iterations at {current_convergence}%",
            recoverable=True  # Can ask user whether to continue
        )
        self.stuck_iterations = stuck_iterations
        self.current_convergence = current_convergence


class CircuitBreakerError(WorkflowError):
    """Circuit breaker triggered due to repeated failures or stalls."""

    def __init__(self, reason: str, diagnostic_info: dict):
        """
        Initialize circuit breaker error.

        Args:
            reason: Why circuit breaker triggered
            diagnostic_info: Dictionary with diagnostic details
        """
        super().__init__(
            f"Circuit breaker triggered: {reason}",
            recoverable=True  # User can choose to continue
        )
        self.reason = reason
        self.diagnostic_info = diagnostic_info


class MinimumExpertsError(WorkflowError):
    """Insufficient experts succeeded to continue workflow."""

    def __init__(self, success_count: int, minimum_required: int, total_experts: int):
        """
        Initialize minimum experts error.

        Args:
            success_count: Number of experts that succeeded
            minimum_required: Minimum required experts
            total_experts: Total number of experts attempted
        """
        super().__init__(
            f"Only {success_count}/{total_experts} experts succeeded "
            f"(minimum required: {minimum_required})",
            recoverable=False  # Cannot continue without minimum experts
        )
        self.success_count = success_count
        self.minimum_required = minimum_required
        self.total_experts = total_experts
