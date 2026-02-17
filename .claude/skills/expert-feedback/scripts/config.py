"""
Centralized configuration system for expert-feedback skill.

This module provides a single source of truth for all configurable parameters,
with support for environment variable overrides.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os


@dataclass
class SkillConfig:
    """Configuration for expert-feedback skill with sensible defaults."""

    # Convergence settings
    convergence_target: int = 80  # percentage
    max_questions_per_iteration: Optional[int] = None  # REMOVED LIMIT (Issue 5)
    default_expert_count: int = 7  # Priority 6: reduced from 10-12
    max_iterations: int = 3

    # Timeout settings (Priority 9 + User Issue 1)
    expert_timeout_seconds: int = 900  # 15 minutes (configurable)
    expert_warning_first: int = 600  # 10 minutes - send "hurry up" message
    expert_warning_interval: int = 60  # 1 minute - countdown warnings

    # Repository freshness (Priority 8)
    repo_staleness_days: int = 7
    auto_update_repos: bool = True

    # Workspace settings
    workspace_base: Path = field(default_factory=lambda: Path(".workspace"))
    organize_by_iteration: bool = True  # User Issue 3

    # Mode defaults
    default_mode: str = "review"

    # Cost calculation settings (Phase 1.3)
    use_accurate_cost_calculation: bool = True  # Use src.expert_feedback.core.cost module
    default_model: str = "claude-sonnet-4-20250514"  # Model for pricing

    # Session management
    cleanup_sessions_on_complete: bool = True
    reuse_synthesis_session: bool = True  # User Issue 9
    reuse_artifact_generation_session: bool = True  # User Issue 9

    # Expert execution
    parallel_execution: bool = True
    max_concurrent_experts: Optional[int] = None  # None = no limit

    # Output settings
    verbose_logging: bool = False
    show_workspace_link: bool = True  # User Issue 2
    show_progress_timestamps: bool = True
    show_token_costs: bool = True
    enable_transcript_logging: bool = True  # Human-readable debug logs for agent activity

    # Enhanced logging settings (Phase 1)
    log_to_console: bool = False  # Also log to stderr (in addition to files)
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_state_transitions: bool = True  # Log StateManager operations
    log_convergence_details: bool = True  # Log convergence calculations

    # Autonomous Execution settings
    enable_auto_execution: bool = False  # Opt-in for autonomous execution phase
    execution_max_iterations: int = 50  # Max autonomous execution iterations
    execution_max_time_hours: float = 8.0  # Max execution time in hours (8h overnight)
    execution_health_check_interval: int = 5  # Run health checks every N iterations
    max_deferred_questions: int = 20  # Max questions before marking as blocked
    question_deferral_strategy: str = "aggressive"  # "aggressive" | "conservative"

    # Test Coverage settings
    enable_test_coverage_agent: bool = True  # Run test coverage agent after execution
    target_test_coverage: float = 90.0  # Target coverage percentage
    test_coverage_max_iterations: int = 20  # Max test generation iterations

    @classmethod
    def from_env(cls) -> 'SkillConfig':
        """
        Load configuration from environment variables.

        Environment variables:
        - EXPERT_CONVERGENCE_TARGET: Target convergence percentage (default: 80)
        - EXPERT_TIMEOUT: Expert timeout in seconds (default: 900)
        - EXPERT_WARNING_FIRST: First warning time in seconds (default: 600)
        - EXPERT_WARNING_INTERVAL: Warning interval in seconds (default: 60)
        - EXPERT_MAX_ITERATIONS: Maximum iterations (default: 3)
        - EXPERT_DEFAULT_COUNT: Default number of experts (default: 7)
        - EXPERT_REPO_STALENESS_DAYS: Days before repo is stale (default: 7)
        - EXPERT_AUTO_UPDATE_REPOS: Auto-update repos (default: true)
        - EXPERT_WORKSPACE_BASE: Base workspace directory (default: .workspace)
        - EXPERT_ORGANIZE_BY_ITERATION: Organize by iteration (default: true)
        - EXPERT_DEFAULT_MODE: Default mode (default: review)
        - EXPERT_VERBOSE_LOGGING: Enable verbose logging (default: false)
        - EXPERT_SHOW_WORKSPACE_LINK: Show workspace link (default: true)
        - EXPERT_SHOW_PROGRESS_TIMESTAMPS: Show timestamps (default: true)
        - EXPERT_SHOW_TOKEN_COSTS: Show token costs (default: true)
        - EXPERT_CLEANUP_SESSIONS: Cleanup sessions on complete (default: true)
        - EXPERT_REUSE_SYNTHESIS: Reuse synthesis session (default: true)
        - EXPERT_REUSE_ARTIFACT_GENERATION: Reuse artifact generation session (default: true)
        - EXPERT_MAX_CONCURRENT: Max concurrent experts (default: None)
        - EXPERT_ENABLE_TRANSCRIPT: Enable transcript logging (default: true)
        - EXPERT_LOG_TO_CONSOLE: Also log to stderr (default: false)
        - EXPERT_LOG_LEVEL: Log level - DEBUG/INFO/WARNING/ERROR (default: INFO)
        - EXPERT_LOG_STATE_TRANSITIONS: Log StateManager operations (default: true)
        - EXPERT_LOG_CONVERGENCE_DETAILS: Log convergence calculations (default: true)
        - EXPERT_ENABLE_AUTO_EXECUTION: Enable autonomous execution (default: false)
        - EXPERT_EXECUTION_MAX_ITERATIONS: Max execution iterations (default: 50)
        - EXPERT_EXECUTION_MAX_TIME_HOURS: Max execution time in hours (default: 8.0)
        - EXPERT_EXECUTION_HEALTH_CHECK_INTERVAL: Health check interval (default: 5)
        - EXPERT_MAX_DEFERRED_QUESTIONS: Max deferred questions (default: 20)
        - EXPERT_QUESTION_DEFERRAL_STRATEGY: Question deferral strategy (default: aggressive)
        - EXPERT_ENABLE_TEST_COVERAGE: Enable test coverage agent (default: true)
        - EXPERT_TARGET_TEST_COVERAGE: Target coverage percentage (default: 90.0)
        - EXPERT_TEST_COVERAGE_MAX_ITERATIONS: Max test generation iterations (default: 20)

        Returns:
            SkillConfig instance with values from env or defaults
        """
        return cls(
            convergence_target=int(os.getenv("EXPERT_CONVERGENCE_TARGET", "80")),
            max_questions_per_iteration=None,  # Removed limit
            default_expert_count=int(os.getenv("EXPERT_DEFAULT_COUNT", "7")),
            max_iterations=int(os.getenv("EXPERT_MAX_ITERATIONS", "3")),
            expert_timeout_seconds=int(os.getenv("EXPERT_TIMEOUT", "900")),
            expert_warning_first=int(os.getenv("EXPERT_WARNING_FIRST", "600")),
            expert_warning_interval=int(os.getenv("EXPERT_WARNING_INTERVAL", "60")),
            repo_staleness_days=int(os.getenv("EXPERT_REPO_STALENESS_DAYS", "7")),
            auto_update_repos=os.getenv("EXPERT_AUTO_UPDATE_REPOS", "true").lower() == "true",
            workspace_base=Path(os.getenv("EXPERT_WORKSPACE_BASE", ".workspace")),
            organize_by_iteration=os.getenv("EXPERT_ORGANIZE_BY_ITERATION", "true").lower() == "true",
            default_mode=os.getenv("EXPERT_DEFAULT_MODE", "review"),
            verbose_logging=os.getenv("EXPERT_VERBOSE_LOGGING", "false").lower() == "true",
            show_workspace_link=os.getenv("EXPERT_SHOW_WORKSPACE_LINK", "true").lower() == "true",
            show_progress_timestamps=os.getenv("EXPERT_SHOW_PROGRESS_TIMESTAMPS", "true").lower() == "true",
            show_token_costs=os.getenv("EXPERT_SHOW_TOKEN_COSTS", "true").lower() == "true",
            cleanup_sessions_on_complete=os.getenv("EXPERT_CLEANUP_SESSIONS", "true").lower() == "true",
            reuse_synthesis_session=os.getenv("EXPERT_REUSE_SYNTHESIS", "true").lower() == "true",
            reuse_artifact_generation_session=os.getenv("EXPERT_REUSE_ARTIFACT_GENERATION", "true").lower() == "true",
            max_concurrent_experts=int(os.getenv("EXPERT_MAX_CONCURRENT")) if os.getenv("EXPERT_MAX_CONCURRENT") else None,
            enable_transcript_logging=os.getenv("EXPERT_ENABLE_TRANSCRIPT", "true").lower() == "true",
            log_to_console=os.getenv("EXPERT_LOG_TO_CONSOLE", "false").lower() == "true",
            log_level=os.getenv("EXPERT_LOG_LEVEL", "INFO").upper(),
            log_state_transitions=os.getenv("EXPERT_LOG_STATE_TRANSITIONS", "true").lower() == "true",
            log_convergence_details=os.getenv("EXPERT_LOG_CONVERGENCE_DETAILS", "true").lower() == "true",
            enable_auto_execution=os.getenv("EXPERT_ENABLE_AUTO_EXECUTION", "false").lower() == "true",
            execution_max_iterations=int(os.getenv("EXPERT_EXECUTION_MAX_ITERATIONS", "50")),
            execution_max_time_hours=float(os.getenv("EXPERT_EXECUTION_MAX_TIME_HOURS", "8.0")),
            execution_health_check_interval=int(os.getenv("EXPERT_EXECUTION_HEALTH_CHECK_INTERVAL", "5")),
            max_deferred_questions=int(os.getenv("EXPERT_MAX_DEFERRED_QUESTIONS", "20")),
            question_deferral_strategy=os.getenv("EXPERT_QUESTION_DEFERRAL_STRATEGY", "aggressive"),
            enable_test_coverage_agent=os.getenv("EXPERT_ENABLE_TEST_COVERAGE", "true").lower() == "true",
            target_test_coverage=float(os.getenv("EXPERT_TARGET_TEST_COVERAGE", "90.0")),
            test_coverage_max_iterations=int(os.getenv("EXPERT_TEST_COVERAGE_MAX_ITERATIONS", "20")),
        )

    def validate(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        if not (0 < self.convergence_target <= 100):
            raise ValueError(f"convergence_target must be between 1 and 100, got {self.convergence_target}")

        if self.expert_timeout_seconds <= 0:
            raise ValueError(f"expert_timeout_seconds must be positive, got {self.expert_timeout_seconds}")

        if self.expert_warning_first >= self.expert_timeout_seconds:
            raise ValueError(f"expert_warning_first ({self.expert_warning_first}) must be less than timeout ({self.expert_timeout_seconds})")

        if self.expert_warning_interval <= 0:
            raise ValueError(f"expert_warning_interval must be positive, got {self.expert_warning_interval}")

        if self.max_iterations <= 0:
            raise ValueError(f"max_iterations must be positive, got {self.max_iterations}")

        if self.default_expert_count <= 0:
            raise ValueError(f"default_expert_count must be positive, got {self.default_expert_count}")

        if self.repo_staleness_days < 0:
            raise ValueError(f"repo_staleness_days must be non-negative, got {self.repo_staleness_days}")

        if self.default_mode not in ["review", "adr", "create", "improve"]:
            raise ValueError(f"default_mode must be one of review/adr/create/improve, got {self.default_mode}")

        if self.max_concurrent_experts is not None and self.max_concurrent_experts <= 0:
            raise ValueError(f"max_concurrent_experts must be positive if set, got {self.max_concurrent_experts}")


# Singleton instance
_config_instance: Optional[SkillConfig] = None


def get_config() -> SkillConfig:
    """
    Get the singleton configuration instance.

    On first call, loads configuration from environment variables.
    Subsequent calls return the cached instance.

    Returns:
        SkillConfig singleton instance

    Example:
        config = get_config()
        print(f"Convergence target: {config.convergence_target}%")
        print(f"Expert timeout: {config.expert_timeout_seconds}s")
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = SkillConfig.from_env()
        _config_instance.validate()
    return _config_instance


def reset_config() -> None:
    """
    Reset the configuration singleton (useful for testing).

    After calling this, the next call to get_config() will reload
    configuration from environment variables.
    """
    global _config_instance
    _config_instance = None


def get_config_with_overrides(**overrides) -> SkillConfig:
    """
    Get a configuration instance with specific overrides.

    This does NOT affect the singleton - it creates a new instance.
    Useful for per-session configuration (e.g., custom convergence target).

    Args:
        **overrides: Configuration fields to override

    Returns:
        New SkillConfig instance with overrides applied

    Example:
        # Get config with custom convergence target for this session
        config = get_config_with_overrides(convergence_target=70)
    """
    base_config = get_config()
    config_dict = base_config.__dict__.copy()
    config_dict.update(overrides)
    config = SkillConfig(**config_dict)
    config.validate()
    return config
