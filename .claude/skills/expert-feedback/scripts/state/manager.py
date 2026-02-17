"""
Type-safe state management for expert-feedback skill.

This module provides a StateManager class that encapsulates all state
operations with type safety and atomic updates.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from pathlib import Path
from file_io.json_ops import load_json, save_json
from state.operations import update_state_atomic


@dataclass
class WorkspaceState:
    """
    Type-safe workspace state.

    This represents the complete state of an expert-feedback session,
    tracking experts, iterations, convergence, and session IDs for resumption.
    """
    topic: str
    experts: List[str]
    iteration: int
    mode: str = "review"
    phase: Optional[str] = None  # Current workflow phase
    convergence_percent: int = 0
    consensus_reached: bool = False
    convergence_target: int = 80  # Priority 7: per-session configurable
    expert_sessions: Dict[str, str] = field(default_factory=dict)
    synthesis_session_id: Optional[str] = None  # User Issue 9
    artifact_generation_session_id: Optional[str] = None  # User Issue 9
    artifact_generation_result: Optional[Dict[str, Any]] = None
    artifact_review_needed: bool = False  # User Issue 12 (revised)
    draft_artifact_path: Optional[str] = None  # Path to draft artifact (ADR/plan)
    draft_artifact_iteration: Optional[int] = None  # Iteration where draft was created

    # Additional metadata
    total_tokens: int = 0
    total_cost: float = 0.0
    start_time: Optional[str] = None
    complete_time: Optional[str] = None

    # Token metrics
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    # Convergence history
    high_agreement: int = 0
    partial_agreement: int = 0
    low_agreement: int = 0

    # Expert results tracking
    expert_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    expert_progress: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Iteration history tracking (Context Gap Fix 1.1)
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    """
    Tracks synthesis results across iterations for context propagation.
    Format: [{
        "iteration": 1,
        "convergence_percent": 45,
        "high_agreement": 3,
        "partial_agreement": 5,
        "low_agreement": 2,
        "synthesized_file": "iteration-1/synthesized.md",
        "questions_file": "iteration-1/questions.json",
        "expert_summaries": {
            "typescript": {
                "dx_rating": 4,
                "concerns_count": 3,
                "top_concern": "Complex type system",
                "recommendations_count": 5
            }
        },
        "timestamp": "2026-02-15T14:30:22Z"
    }]
    """

    # Artifact regeneration tracking (Context Gap Fix 2.1)
    artifact_generation_attempts: int = 0
    artifact_regeneration_history: List[Dict[str, Any]] = field(default_factory=list)
    """
    Tracks all artifact generation attempts.
    Format: [{
        "attempt": 1,
        "timestamp": "2026-02-15T14:30:22Z",
        "result": "concerns_raised",
        "concerns_count": 2,
        "concerns": ["Missing security section", "Unclear migration path"]
    }]
    """

    # Per-iteration session tracking for precise revert
    expert_sessions_by_iteration: Dict[int, Dict[str, str]] = field(default_factory=dict)
    """
    Track expert sessions per iteration for precise revert.
    Format: {
        1: {"typescript": "sess_abc", "python": "sess_def"},
        2: {"typescript": "sess_ghi", "python": "sess_jkl"}
    }
    """

    synthesis_session_by_iteration: Dict[int, str] = field(default_factory=dict)
    """Track synthesis session per iteration."""

    # Revert history tracking
    revert_history: List[Dict[str, Any]] = field(default_factory=list)
    """
    Tracks revert operations for debugging and audit.
    Format: [{
        "timestamp": "2026-02-15T14:30:22Z",
        "from": {"iteration": 3, "phase": "artifact_review"},
        "to": {"iteration": 2, "phase": "synthesizing"},
        "reason": "user_initiated_revert"
    }]
    """

    # Concern review tracking
    concern_review: Dict[str, Any] = field(default_factory=dict)
    """
    Tracks concern review loop state.
    Format: {
        "iteration": 1,
        "status": "in_progress" | "approved" | "addressing_concerns" | "max_iterations_reached",
        "concerns_raised": 4,
        "concerns_agreed": 2,
        "concerns_disagreed": 2,
        "current_artifact_version": 2,
        "history": [
            {
                "iteration": 1,
                "concerns_raised": 4,
                "concerns_agreed": 2,
                "concerns_disagreed": 2,
                "timestamp": "2026-02-16T14:30:22Z"
            }
        ]
    }
    """

    # Autonomous execution tracking
    execution: Dict[str, Any] = field(default_factory=dict)
    """
    Tracks autonomous execution phase.
    Format: {
        "status": "not_started" | "running" | "paused" | "completed" | "failed",
        "session_id": "sess-executor-xyz",
        "started_at": "2026-02-16T01:00:00Z",
        "last_activity": "2026-02-16T03:30:15Z",
        "iterations": 15,
        "steps_completed": 42,
        "files_modified": ["src/api.ts", "tests/api.test.ts"],
        "deferred_questions_count": 3,
        "answered_questions_count": 0,
        "progress_percent": 68,
        "history": [
            {
                "iteration": 1,
                "timestamp": "2026-02-16T01:15:00Z",
                "steps": ["Created API endpoint", "Added tests"],
                "files": ["src/api.ts"],
                "status": "in_progress"
            }
        ]
    }
    """

    # Test coverage tracking
    test_coverage: Dict[str, Any] = field(default_factory=dict)
    """
    Tracks test coverage agent phase.
    Format: {
        "status": "not_started" | "running" | "completed" | "failed",
        "session_id": "sess-test-agent-xyz",
        "started_at": "2026-02-16T07:00:00Z",
        "initial_coverage": 67.5,
        "current_coverage": 85.2,
        "target_coverage": 90.0,
        "iterations": 5,
        "tests_written": 12,
        "history": [
            {
                "iteration": 1,
                "coverage": 72.0,
                "tests_written": ["test_api_validation", "test_error_handling"],
                "timestamp": "2026-02-16T07:15:00Z"
            }
        ]
    }
    """

    def __post_init__(self):
        """Initialize mutable default values if None."""
        if self.expert_sessions is None:
            object.__setattr__(self, 'expert_sessions', {})
        if self.expert_results is None:
            object.__setattr__(self, 'expert_results', {})
        if self.expert_progress is None:
            object.__setattr__(self, 'expert_progress', {})
        if self.iteration_history is None:
            object.__setattr__(self, 'iteration_history', [])
        if self.artifact_regeneration_history is None:
            object.__setattr__(self, 'artifact_regeneration_history', [])
        if self.expert_sessions_by_iteration is None:
            object.__setattr__(self, 'expert_sessions_by_iteration', {})
        if self.synthesis_session_by_iteration is None:
            object.__setattr__(self, 'synthesis_session_by_iteration', {})
        if self.revert_history is None:
            object.__setattr__(self, 'revert_history', [])
        if self.concern_review is None:
            object.__setattr__(self, 'concern_review', {})
        if self.execution is None:
            object.__setattr__(self, 'execution', {})
        if self.test_coverage is None:
            object.__setattr__(self, 'test_coverage', {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceState':
        """
        Create WorkspaceState from dictionary.

        Handles missing fields with sensible defaults.
        """
        # Required fields
        topic = data.get("topic")
        experts = data.get("experts", [])
        iteration = data.get("iteration", 1)

        if not topic:
            raise ValueError("State must have 'topic' field")

        # Optional fields with defaults
        return cls(
            topic=topic,
            experts=experts,
            iteration=iteration,
            mode=data.get("mode", "review"),
            phase=data.get("phase"),
            convergence_percent=data.get("convergence_percent", 0),
            consensus_reached=data.get("consensus_reached", False),
            convergence_target=data.get("convergence_target", 80),
            expert_sessions=data.get("expert_sessions", {}),
            synthesis_session_id=data.get("synthesis_session_id"),
            artifact_generation_session_id=data.get("artifact_generation_session_id"),
            artifact_generation_result=data.get("artifact_generation_result"),
            artifact_review_needed=data.get("artifact_review_needed", False),
            draft_artifact_path=data.get("draft_artifact_path"),
            draft_artifact_iteration=data.get("draft_artifact_iteration"),
            total_tokens=data.get("total_tokens", 0),
            total_cost=data.get("total_cost", 0.0),
            start_time=data.get("start_time"),
            complete_time=data.get("complete_time"),
            total_input_tokens=data.get("total_input_tokens", 0),
            total_output_tokens=data.get("total_output_tokens", 0),
            high_agreement=data.get("high_agreement", 0),
            partial_agreement=data.get("partial_agreement", 0),
            low_agreement=data.get("low_agreement", 0),
            expert_results=data.get("expert_results", {}),
            expert_progress=data.get("expert_progress", {}),
            iteration_history=data.get("iteration_history", []),
            artifact_generation_attempts=data.get("artifact_generation_attempts", 0),
            artifact_regeneration_history=data.get("artifact_regeneration_history", []),
            expert_sessions_by_iteration=data.get("expert_sessions_by_iteration", {}),
            synthesis_session_by_iteration=data.get("synthesis_session_by_iteration", {}),
            revert_history=data.get("revert_history", []),
            concern_review=data.get("concern_review", {}),
            execution=data.get("execution", {}),
            test_coverage=data.get("test_coverage", {}),
        )


class StateManager:
    """
    Manage workspace state with type safety and atomic updates.

    This class provides a high-level interface for all state operations,
    ensuring consistency and preventing race conditions with file locking.

    Example:
        manager = StateManager(workspace_path)
        state = manager.load()
        print(f"Iteration: {state.iteration}, Convergence: {state.convergence_percent}%")

        # Update sessions atomically
        manager.update_sessions({"typescript": "sess_abc123"})

        # Increment iteration
        manager.increment_iteration()
    """

    def __init__(self, workspace: Path, correlation_id: Optional[str] = None):
        """
        Initialize StateManager for a workspace.

        Args:
            workspace: Path to workspace directory
            correlation_id: Optional correlation ID for logging
        """
        self.workspace = Path(workspace)
        self.state_path = self.workspace / "state.json"
        self.correlation_id = correlation_id

        # Setup logger if state transitions should be logged
        from config import get_config
        config = get_config()
        if config.log_state_transitions:
            from agent_logging.agent_logger import setup_agent_logger_v2
            self.logger = setup_agent_logger_v2(
                workspace,
                "state-manager",
                correlation_id=correlation_id
            )
        else:
            self.logger = None

    def load(self) -> WorkspaceState:
        """
        Load state with validation.

        Returns:
            WorkspaceState instance

        Raises:
            FileNotFoundError: If state.json doesn't exist
            ValueError: If state is invalid
        """
        if self.logger:
            self.logger.debug(f"Loading state from {self.state_path}")

        if not self.state_path.exists():
            if self.logger:
                self.logger.error(f"State file not found: {self.state_path}")
            raise FileNotFoundError(f"State file not found: {self.state_path}")

        # Read state.json directly (don't use load_json which blocks state.json access)
        import json
        data = json.loads(self.state_path.read_text())
        state = WorkspaceState.from_dict(data)

        if self.logger:
            self.logger.info(
                f"Loaded state: iteration={state.iteration}, "
                f"convergence={state.convergence_percent}%, "
                f"experts={len(state.experts)}"
            )

        return state

    def save(self, state: WorkspaceState) -> None:
        """
        Save state atomically.

        Args:
            state: WorkspaceState to save
        """
        if self.logger:
            self.logger.debug(
                f"Saving state: iteration={state.iteration}, "
                f"convergence={state.convergence_percent}%"
            )

        # Write state.json directly (don't use save_json which blocks state.json access)
        import json
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False))

        if self.logger:
            self.logger.info(f"State saved successfully to {self.state_path}")

    def create(self, state: WorkspaceState) -> None:
        """
        Create new state file.

        Args:
            state: Initial WorkspaceState

        Raises:
            FileExistsError: If state.json already exists
        """
        if self.state_path.exists():
            raise FileExistsError(f"State file already exists: {self.state_path}")

        self.workspace.mkdir(parents=True, exist_ok=True)
        self.save(state)

    def exists(self) -> bool:
        """Check if state file exists."""
        return self.state_path.exists()

    def update(self, fields: Dict[str, Any]) -> WorkspaceState:
        """
        Generic update method for arbitrary state fields.

        Args:
            fields: Dictionary of field names to values

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info(f"Updating state fields: {list(fields.keys())}")

        def updater(state_dict):
            state_dict.update(fields)
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        state = WorkspaceState.from_dict(updated_dict)

        if self.logger:
            self.logger.info(f"State fields updated successfully")

        return state

    def update_sessions(self, sessions: Dict[str, str]) -> WorkspaceState:
        """
        Atomically update expert sessions (preserving existing).

        Args:
            sessions: Dictionary of {expert_name: session_id} to add/update

        Returns:
            Updated WorkspaceState

        Example:
            manager.update_sessions({
                "typescript": "sess_abc123",
                "python": "sess_def456"
            })
        """
        if self.logger:
            self.logger.info(f"Updating sessions for {len(sessions)} experts: {list(sessions.keys())}")

        def updater(state_dict):
            if "expert_sessions" not in state_dict:
                state_dict["expert_sessions"] = {}
            state_dict["expert_sessions"].update(sessions)
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        state = WorkspaceState.from_dict(updated_dict)

        if self.logger:
            self.logger.info(f"Sessions updated. Total expert sessions: {len(state.expert_sessions)}")

        return state

    def set_synthesis_session(self, session_id: str) -> WorkspaceState:
        """
        Set synthesis session ID for reuse (User Issue 9).

        Args:
            session_id: Synthesis agent session ID

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info(f"Setting synthesis session: {session_id[:12]}...")

        def updater(state_dict):
            state_dict["synthesis_session_id"] = session_id
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)

        if self.logger:
            self.logger.info("Synthesis session saved for reuse")

        return WorkspaceState.from_dict(updated_dict)

    def set_artifact_generation_session(self, session_id: str) -> WorkspaceState:
        """
        Set artifact generation session ID for reuse (User Issue 9).

        Args:
            session_id: Artifact generation agent session ID

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info(f"Setting artifact generation session: {session_id[:12]}...")

        def updater(state_dict):
            state_dict["artifact_generation_session_id"] = session_id
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)

        if self.logger:
            self.logger.info("Finalization session saved for reuse")

        return WorkspaceState.from_dict(updated_dict)

    def update_convergence(
        self,
        convergence_percent: int,
        consensus_reached: bool,
        high_agreement: int = 0,
        partial_agreement: int = 0,
        low_agreement: int = 0
    ) -> WorkspaceState:
        """
        Update convergence metrics.

        Args:
            convergence_percent: Overall convergence percentage
            consensus_reached: Whether consensus target was met
            high_agreement: Number of high-agreement recommendations
            partial_agreement: Number of partial-agreement recommendations
            low_agreement: Number of low-agreement recommendations

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info(
                f"Updating convergence: {convergence_percent}% "
                f"(high={high_agreement}, partial={partial_agreement}, low={low_agreement}), "
                f"consensus={'YES' if consensus_reached else 'NO'}"
            )

        def updater(state_dict):
            state_dict["convergence_percent"] = convergence_percent
            state_dict["consensus_reached"] = consensus_reached
            state_dict["high_agreement"] = high_agreement
            state_dict["partial_agreement"] = partial_agreement
            state_dict["low_agreement"] = low_agreement
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        state = WorkspaceState.from_dict(updated_dict)

        if self.logger:
            self.logger.info(
                f"Convergence updated successfully: "
                f"{state.convergence_percent}% (target: {state.convergence_target}%)"
            )

        return state

    def set_iteration(self, iteration: int) -> WorkspaceState:
        """
        Set iteration counter to a specific value.

        Args:
            iteration: Iteration number to set

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info(f"Setting iteration to {iteration}")

        def updater(state_dict):
            state_dict["iteration"] = iteration
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        state = WorkspaceState.from_dict(updated_dict)

        if self.logger:
            self.logger.info(f"Iteration set to {state.iteration}")

        return state

    def increment_iteration(self) -> WorkspaceState:
        """
        Increment iteration counter.

        Returns:
            Updated WorkspaceState
        """
        if self.logger:
            self.logger.info("Incrementing iteration counter")

        def updater(state_dict):
            old_iteration = state_dict.get("iteration", 1)
            state_dict["iteration"] = old_iteration + 1
            if self.logger:
                self.logger.debug(f"Iteration: {old_iteration} → {state_dict['iteration']}")
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        state = WorkspaceState.from_dict(updated_dict)

        if self.logger:
            self.logger.info(f"Iteration incremented to {state.iteration}")

        return state

    def add_expert_result(
        self,
        expert: str,
        result: Dict[str, Any]
    ) -> WorkspaceState:
        """
        Add or update expert result.

        Args:
            expert: Expert name
            result: Result dictionary (status, tokens, duration, etc.)

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            if "expert_results" not in state_dict:
                state_dict["expert_results"] = {}
            state_dict["expert_results"][expert] = result
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def update_expert_progress(self, expert: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> WorkspaceState:
        """Update expert progress status (pending → running → complete/error/timeout).

        Args:
            expert: Expert name
            status: One of: pending, running, complete, error, timeout
            metadata: Optional dict with duration_seconds, total_tokens, start_time, end_time
        """
        def updater(state_dict):
            if "expert_progress" not in state_dict:
                state_dict["expert_progress"] = {}

            progress_data = {"status": status}
            if metadata:
                progress_data.update(metadata)

            state_dict["expert_progress"][expert] = progress_data
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def update_token_metrics(
        self,
        tokens_delta: int,
        cost_delta: float
    ) -> WorkspaceState:
        """
        Update cumulative token and cost metrics.

        Args:
            tokens_delta: Tokens to add to total
            cost_delta: Cost to add to total

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            state_dict["total_tokens"] = state_dict.get("total_tokens", 0) + tokens_delta
            state_dict["total_cost"] = state_dict.get("total_cost", 0.0) + cost_delta
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def update_token_metrics(
        self,
        input_tokens: int,
        output_tokens: int,
        cost: float = 0.0
    ) -> WorkspaceState:
        """
        Update token metrics.

        This method tracks input/output tokens separately for accurate
        cost calculation and monitoring.

        Args:
            input_tokens: Input tokens
            output_tokens: Output tokens generated
            cost: Actual cost in USD (calculated with correct pricing)

        Returns:
            Updated WorkspaceState

        Example:
            # After expert completes
            usage = extract_usage_from_sdk_result(result)
            state_manager.update_token_metrics(
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                cost=calculate_cost(usage["input_tokens"], usage["output_tokens"])
            )
        """
        def updater(state_dict):
            # Update individual token counts
            state_dict["total_input_tokens"] = state_dict.get("total_input_tokens", 0) + input_tokens
            state_dict["total_output_tokens"] = state_dict.get("total_output_tokens", 0) + output_tokens

            # Update aggregate metrics
            total_tokens = input_tokens + output_tokens
            state_dict["total_tokens"] = state_dict.get("total_tokens", 0) + total_tokens
            state_dict["total_cost"] = state_dict.get("total_cost", 0.0) + cost

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def set_artifact_review_needed(self, needed: bool) -> WorkspaceState:
        """
        Set whether artifact review is needed.

        Args:
            needed: True if artifact needs review

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            state_dict["artifact_review_needed"] = needed
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def set_artifact_generation_result(self, result: Dict[str, Any]) -> WorkspaceState:
        """
        Set artifact generation result.

        Args:
            result: Artifact generation result dictionary

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            state_dict["artifact_generation_result"] = result
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def mark_complete(self, complete_time: str) -> WorkspaceState:
        """
        Mark session as complete.

        Args:
            complete_time: ISO format timestamp of completion

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            state_dict["complete_time"] = complete_time
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def set_start_time(self, start_time: str) -> WorkspaceState:
        """
        Set session start time.

        Args:
            start_time: ISO format timestamp of start

        Returns:
            Updated WorkspaceState
        """
        def updater(state_dict):
            state_dict["start_time"] = start_time
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def set_phase(self, phase: str) -> WorkspaceState:
        """
        Set current workflow phase for web UI with validation.

        Args:
            phase: Phase name ('spawning_experts', 'consolidating', 'questions',
                   'generating_artifact', 'reviewing_artifact', 'completed')

        Returns:
            Updated WorkspaceState

        Raises:
            ValueError: If phase is invalid

        Example:
            state_manager.set_phase("consolidating")
        """
        # Define valid phases
        VALID_PHASES = {
            'spawning_experts',
            'consolidating',
            'questions',
            'generating_artifact',
            'reviewing_artifact',
            'completed',
            'artifact_review'  # Alias for reviewing_artifact
        }

        if phase not in VALID_PHASES:
            raise ValueError(
                f"Invalid phase '{phase}'. "
                f"Valid phases: {sorted(VALID_PHASES)}"
            )

        def updater(state_dict):
            state_dict["phase"] = phase
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def is_phase_complete(self, phase: str) -> bool:
        """
        Check if workflow phase is complete (Phase 0.3).

        Args:
            phase: Phase name (e.g., "spawning_experts", "consolidating", "generating_artifact")

        Returns:
            True if phase is complete, False otherwise

        Example:
            if state_manager.is_phase_complete("consolidating"):
                print("Consolidation already done, skipping")
        """
        if not self.exists():
            return False

        try:
            import json
            state_dict = json.loads(self.state_path.read_text())
            return state_dict.get(f"{phase}_complete", False)
        except Exception:
            return False

    def mark_phase_complete(self, phase: str, result: Dict[str, Any]) -> WorkspaceState:
        """
        Mark phase complete and save result (Phase 0.3).

        Args:
            phase: Phase name
            result: Phase result dictionary to save

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.mark_phase_complete("consolidating", {
                "convergence_percent": 85,
                "consensus_reached": True,
                "tokens_used": 15000
            })
        """
        def updater(state_dict):
            state_dict[f"{phase}_complete"] = True
            state_dict[f"{phase}_result"] = result
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def get_phase_result(self, phase: str) -> Optional[Dict[str, Any]]:
        """
        Get result from completed phase (Phase 0.3).

        Args:
            phase: Phase name

        Returns:
            Phase result dictionary if available, None otherwise

        Example:
            result = state_manager.get_phase_result("consolidating")
            if result:
                print(f"Convergence: {result['convergence_percent']}%")
        """
        if not self.exists():
            return None

        try:
            import json
            state_dict = json.loads(self.state_path.read_text())
            return state_dict.get(f"{phase}_result")
        except Exception:
            return None

    def register_script_intent(self, expert: str, script_name: str) -> bool:
        """
        Register intent to create a script (Phase 3.3).

        Prevents duplicate script creation across experts by registering
        who is working on which script.

        Args:
            expert: Expert name
            script_name: Name of script (without .py extension)

        Returns:
            True if this expert can proceed (no one else working on it)
            False if another expert already working on it

        Example:
            if state_manager.register_script_intent("typescript", "analyze_types"):
                # Proceed with creating script
                pass
            else:
                # Another expert is already working on this script
                print("Script already in progress by another expert")
        """
        # First check if someone else owns it
        current_owner = self.get_script_owner(script_name)
        if current_owner is not None and current_owner != expert:
            # Another expert already registered
            return False

        # Register this expert
        def updater(state_dict):
            if "script_registry" not in state_dict:
                state_dict["script_registry"] = {}

            state_dict["script_registry"][script_name] = expert
            return state_dict

        try:
            update_state_atomic(self.state_path, updater)
            return True
        except Exception:
            # If update failed, assume conflict
            return False

    def complete_script(
        self,
        expert: str,
        script_name: str,
        output_path: Path
    ) -> WorkspaceState:
        """
        Mark script complete and share with other experts (Phase 3.3).

        Args:
            expert: Expert name
            script_name: Name of script (without .py extension)
            output_path: Path to completed script

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.complete_script(
                "typescript",
                "analyze_types",
                workspace / "iteration-1/experts/typescript/scripts/analyze_types.py"
            )
        """
        from datetime import datetime

        def updater(state_dict):
            if "completed_scripts" not in state_dict:
                state_dict["completed_scripts"] = {}

            state_dict["completed_scripts"][script_name] = {
                "expert": expert,
                "path": str(output_path),
                "completed_at": datetime.now().isoformat()
            }

            # Remove from registry (no longer in-progress)
            if "script_registry" in state_dict:
                if script_name in state_dict["script_registry"]:
                    del state_dict["script_registry"][script_name]

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def get_script_owner(self, script_name: str) -> Optional[str]:
        """
        Get expert who is currently working on a script (Phase 3.3).

        Args:
            script_name: Name of script (without .py extension)

        Returns:
            Expert name if someone is working on it, None otherwise

        Example:
            owner = state_manager.get_script_owner("analyze_types")
            if owner:
                print(f"{owner} is working on this script")
        """
        if not self.exists():
            return None

        try:
            import json
            state_dict = json.loads(self.state_path.read_text())
            registry = state_dict.get("script_registry", {})
            return registry.get(script_name)
        except Exception:
            return None

    def get_completed_scripts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all completed scripts (Phase 3.3).

        Returns:
            Dictionary mapping script names to completion info:
            - expert: Expert who created it
            - path: Path to script
            - completed_at: ISO timestamp

        Example:
            scripts = state_manager.get_completed_scripts()
            for script_name, info in scripts.items():
                print(f"{script_name}: created by {info['expert']}")
        """
        if not self.exists():
            return {}

        try:
            import json
            state_dict = json.loads(self.state_path.read_text())
            return state_dict.get("completed_scripts", {})
        except Exception:
            return {}

    def record_iteration_summary(
        self,
        iteration: int,
        convergence_percent: int,
        agreement_breakdown: Dict[str, int],
        expert_summaries: Dict[str, Dict[str, Any]]
    ) -> WorkspaceState:
        """
        Record iteration summary for context propagation to next iteration (Context Gap Fix 1.1).

        Args:
            iteration: Iteration number
            convergence_percent: Convergence percentage for this iteration
            agreement_breakdown: Dict with "high", "partial", "low" counts
            expert_summaries: Dict mapping expert names to summary data:
                - dx_rating: DX rating stars (0-5)
                - concerns_count: Number of concerns raised
                - top_concern: Title of top concern
                - recommendations_count: Number of recommendations

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.record_iteration_summary(
                iteration=1,
                convergence_percent=45,
                agreement_breakdown={"high": 3, "partial": 5, "low": 2},
                expert_summaries={
                    "typescript": {
                        "dx_rating": 4,
                        "concerns_count": 3,
                        "top_concern": "Complex type system"
                    }
                }
            )
        """
        from datetime import datetime

        def updater(state_dict):
            if "iteration_history" not in state_dict:
                state_dict["iteration_history"] = []

            state_dict["iteration_history"].append({
                "iteration": iteration,
                "convergence_percent": convergence_percent,
                "high_agreement": agreement_breakdown.get("high", 0),
                "partial_agreement": agreement_breakdown.get("partial", 0),
                "low_agreement": agreement_breakdown.get("low", 0),
                "synthesized_file": f"iteration-{iteration}/synthesized.md",
                "questions_file": f"iteration-{iteration}/questions.json",
                "expert_summaries": expert_summaries,
                "timestamp": datetime.now().isoformat()
            })
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(
                f"Recorded iteration {iteration} summary: "
                f"convergence={convergence_percent}%, experts={len(expert_summaries)}"
            )
        return WorkspaceState.from_dict(updated_dict)

    def increment_artifact_generation_attempt(self) -> WorkspaceState:
        """
        Increment artifact generation attempt counter (Context Gap Fix 2.1).

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.increment_artifact_generation_attempt()
        """
        def updater(state_dict):
            current = state_dict.get("artifact_generation_attempts", 0)
            state_dict["artifact_generation_attempts"] = current + 1
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(f"Incremented artifact generation attempt to {updated_dict['artifact_generation_attempts']}")
        return WorkspaceState.from_dict(updated_dict)

    def record_artifact_generation_result(
        self,
        attempt: int,
        result: str,
        concerns_count: int = 0,
        concerns: Optional[List[str]] = None
    ) -> WorkspaceState:
        """
        Record artifact generation attempt result (Context Gap Fix 2.1).

        Args:
            attempt: Attempt number (1-based)
            result: Result status ("initial", "concerns_raised", "approved", "regenerated")
            concerns_count: Number of concerns raised (if concerns_raised)
            concerns: List of concern titles (if concerns_raised)

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.record_artifact_generation_result(
                attempt=1,
                result="concerns_raised",
                concerns_count=2,
                concerns=["Missing security", "Unclear migration"]
            )
        """
        from datetime import datetime

        def updater(state_dict):
            if "artifact_regeneration_history" not in state_dict:
                state_dict["artifact_regeneration_history"] = []

            state_dict["artifact_regeneration_history"].append({
                "attempt": attempt,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "concerns_count": concerns_count,
                "concerns": concerns or []
            })
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(
                f"Recorded artifact generation attempt {attempt}: "
                f"result={result}, concerns_count={concerns_count}"
            )
        return WorkspaceState.from_dict(updated_dict)

    def update_expert_sessions_for_iteration(
        self,
        iteration: int,
        expert_sessions: Dict[str, str]
    ) -> WorkspaceState:
        """
        Store expert sessions for specific iteration.

        Args:
            iteration: Iteration number
            expert_sessions: Dict mapping expert names to session IDs

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.update_expert_sessions_for_iteration(
                iteration=2,
                expert_sessions={"typescript": "sess_abc", "python": "sess_def"}
            )
        """
        def updater(state_dict):
            if "expert_sessions_by_iteration" not in state_dict:
                state_dict["expert_sessions_by_iteration"] = {}

            state_dict["expert_sessions_by_iteration"][iteration] = expert_sessions

            # Also update current expert_sessions for backward compatibility
            state_dict["expert_sessions"] = expert_sessions

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(
                f"Updated expert sessions for iteration {iteration}: "
                f"{len(expert_sessions)} experts"
            )
        return WorkspaceState.from_dict(updated_dict)

    def update_synthesis_session_for_iteration(
        self,
        iteration: int,
        session_id: str
    ) -> WorkspaceState:
        """
        Store synthesis session for specific iteration.

        Args:
            iteration: Iteration number
            session_id: Synthesis session ID

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.update_synthesis_session_for_iteration(
                iteration=2,
                session_id="sess_xyz"
            )
        """
        def updater(state_dict):
            if "synthesis_session_by_iteration" not in state_dict:
                state_dict["synthesis_session_by_iteration"] = {}

            state_dict["synthesis_session_by_iteration"][iteration] = session_id

            # Also update current synthesis_session_id for backward compatibility
            state_dict["synthesis_session_id"] = session_id

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(
                f"Updated synthesis session for iteration {iteration}: {session_id}"
            )
        return WorkspaceState.from_dict(updated_dict)

    def get_expert_sessions_for_iteration(
        self,
        iteration: int
    ) -> Dict[str, str]:
        """
        Get expert sessions for specific iteration.

        Args:
            iteration: Iteration number

        Returns:
            Dict mapping expert names to session IDs, or empty dict if not found
        """
        state = self.load()
        # Keys are strings in JSON, convert iteration to string
        return state.expert_sessions_by_iteration.get(str(iteration), {})

    def get_synthesis_session_for_iteration(
        self,
        iteration: int
    ) -> Optional[str]:
        """
        Get synthesis session for specific iteration.

        Args:
            iteration: Iteration number

        Returns:
            Session ID or None if not found
        """
        state = self.load()
        # Keys are strings in JSON, convert iteration to string
        return state.synthesis_session_by_iteration.get(str(iteration))

    def initialize_concern_review_state(self) -> Dict[str, Any]:
        """
        Initialize concern review state with default values.

        Returns:
            Dict with default concern review state
        """
        return {
            "iteration": 0,
            "status": "not_started",
            "concerns_raised": 0,
            "concerns_agreed": 0,
            "concerns_disagreed": 0,
            "current_artifact_version": 1,
            "history": []
        }

    def update_concern_review_state(
        self,
        iteration: int,
        status: str,
        concerns_raised: int,
        concerns_agreed: int,
        concerns_disagreed: int
    ) -> WorkspaceState:
        """
        Update concern review state atomically.

        Args:
            iteration: Concern review iteration number
            status: Status (in_progress/approved/addressing_concerns/max_iterations_reached)
            concerns_raised: Total number of concerns raised
            concerns_agreed: Number of concerns user agreed with
            concerns_disagreed: Number of concerns user disagreed with

        Returns:
            Updated WorkspaceState

        Example:
            state_manager.update_concern_review_state(
                iteration=1,
                status="in_progress",
                concerns_raised=4,
                concerns_agreed=2,
                concerns_disagreed=2
            )
        """
        from datetime import datetime

        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "concern_review" not in state_dict:
                state_dict["concern_review"] = self.initialize_concern_review_state()

            state_dict["concern_review"].update({
                "iteration": iteration,
                "status": status,
                "concerns_raised": concerns_raised,
                "concerns_agreed": concerns_agreed,
                "concerns_disagreed": concerns_disagreed
            })

            # Add to history
            if "history" not in state_dict["concern_review"]:
                state_dict["concern_review"]["history"] = []

            state_dict["concern_review"]["history"].append({
                "iteration": iteration,
                "concerns_raised": concerns_raised,
                "concerns_agreed": concerns_agreed,
                "concerns_disagreed": concerns_disagreed,
                "timestamp": datetime.utcnow().isoformat()
            })

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        if self.logger:
            self.logger.info(
                f"Updated concern review state: iteration={iteration}, status={status}, "
                f"raised={concerns_raised}, agreed={concerns_agreed}, disagreed={concerns_disagreed}"
            )
        return WorkspaceState.from_dict(updated_dict)

    def get_concern_review_state(self) -> Dict[str, Any]:
        """
        Get current concern review state.

        Returns:
            Dict with concern review state, or default if not initialized
        """
        state = self.load()
        if hasattr(state, 'concern_review') and state.concern_review:
            return state.concern_review
        return self.initialize_concern_review_state()

    def increment_artifact_version(self) -> int:
        """
        Increment artifact version counter atomically.

        Returns:
            New artifact version number

        Example:
            new_version = state_manager.increment_artifact_version()
            print(f"Artifact regenerated to version {new_version}")
        """
        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "concern_review" not in state_dict:
                state_dict["concern_review"] = self.initialize_concern_review_state()

            current_version = state_dict["concern_review"].get("current_artifact_version", 1)
            new_version = current_version + 1
            state_dict["concern_review"]["current_artifact_version"] = new_version
            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        new_version = updated_dict["concern_review"]["current_artifact_version"]

        if self.logger:
            self.logger.info(f"Incremented artifact version to {new_version}")

        return new_version

    # ============================================================================
    # Autonomous Execution Management
    # ============================================================================

    def initialize_execution_state(self) -> Dict[str, Any]:
        """
        Initialize execution state with default values.

        Returns:
            Dict with default execution state
        """
        from datetime import datetime
        return {
            "status": "not_started",
            "session_id": None,
            "started_at": None,
            "last_activity": None,
            "iterations": 0,
            "steps_completed": 0,
            "files_modified": [],
            "deferred_questions_count": 0,
            "answered_questions_count": 0,
            "progress_percent": 0,
            "history": []
        }

    def update_execution_progress(
        self,
        status: str,
        iterations: int = None,
        steps_completed: int = None,
        files_modified: List[str] = None,
        session_id: str = None,
        deferred_questions_count: int = None,
        answered_questions_count: int = None,
        progress_percent: int = None
    ) -> WorkspaceState:
        """
        Update execution progress atomically.

        Args:
            status: Execution status (running|paused|completed|failed)
            iterations: Number of execution iterations completed
            steps_completed: Number of implementation steps completed
            files_modified: List of modified file paths
            session_id: Execution session ID
            deferred_questions_count: Number of deferred questions
            answered_questions_count: Number of answered questions
            progress_percent: Progress percentage (0-100)

        Returns:
            Updated WorkspaceState
        """
        from datetime import datetime

        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "execution" not in state_dict or not state_dict["execution"]:
                state_dict["execution"] = self.initialize_execution_state()

            # Update fields if provided
            if status is not None:
                state_dict["execution"]["status"] = status
            if iterations is not None:
                state_dict["execution"]["iterations"] = iterations
            if steps_completed is not None:
                state_dict["execution"]["steps_completed"] = steps_completed
            if files_modified is not None:
                state_dict["execution"]["files_modified"] = files_modified
            if session_id is not None:
                state_dict["execution"]["session_id"] = session_id
            if deferred_questions_count is not None:
                state_dict["execution"]["deferred_questions_count"] = deferred_questions_count
            if answered_questions_count is not None:
                state_dict["execution"]["answered_questions_count"] = answered_questions_count
            if progress_percent is not None:
                state_dict["execution"]["progress_percent"] = progress_percent

            # Update timestamps
            state_dict["execution"]["last_activity"] = datetime.utcnow().isoformat()

            if state_dict["execution"]["started_at"] is None:
                state_dict["execution"]["started_at"] = datetime.utcnow().isoformat()

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)

        if self.logger:
            self.logger.info(
                f"Updated execution progress: status={status}, "
                f"iterations={iterations}, steps={steps_completed}"
            )

        return WorkspaceState.from_dict(updated_dict)

    def add_execution_history_entry(
        self,
        iteration: int,
        steps: List[str],
        files: List[str],
        status: str
    ) -> WorkspaceState:
        """
        Add entry to execution history.

        Args:
            iteration: Current iteration number
            steps: Steps completed in this iteration
            files: Files modified in this iteration
            status: Status after this iteration

        Returns:
            Updated WorkspaceState
        """
        from datetime import datetime

        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "execution" not in state_dict:
                state_dict["execution"] = self.initialize_execution_state()

            if "history" not in state_dict["execution"]:
                state_dict["execution"]["history"] = []

            state_dict["execution"]["history"].append({
                "iteration": iteration,
                "timestamp": datetime.utcnow().isoformat(),
                "steps": steps,
                "files": files,
                "status": status
            })

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def get_execution_state(self) -> Dict[str, Any]:
        """
        Get current execution state.

        Returns:
            Dict with execution state, or default if not initialized
        """
        state = self.load()
        if hasattr(state, 'execution') and state.execution:
            return state.execution
        return self.initialize_execution_state()

    # ============================================================================
    # Test Coverage Management
    # ============================================================================

    def initialize_test_coverage_state(self) -> Dict[str, Any]:
        """
        Initialize test coverage state with default values.

        Returns:
            Dict with default test coverage state
        """
        return {
            "status": "not_started",
            "session_id": None,
            "started_at": None,
            "initial_coverage": 0.0,
            "current_coverage": 0.0,
            "target_coverage": 90.0,
            "iterations": 0,
            "tests_written": 0,
            "history": []
        }

    def update_test_coverage_progress(
        self,
        status: str,
        current_coverage: float = None,
        iterations: int = None,
        tests_written: int = None,
        session_id: str = None,
        initial_coverage: float = None,
        target_coverage: float = None
    ) -> WorkspaceState:
        """
        Update test coverage progress atomically.

        Args:
            status: Coverage status (running|completed|failed)
            current_coverage: Current coverage percentage
            iterations: Number of test generation iterations
            tests_written: Number of tests written
            session_id: Test agent session ID
            initial_coverage: Initial coverage before test generation
            target_coverage: Target coverage percentage

        Returns:
            Updated WorkspaceState
        """
        from datetime import datetime

        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "test_coverage" not in state_dict or not state_dict["test_coverage"]:
                state_dict["test_coverage"] = self.initialize_test_coverage_state()

            # Update fields if provided
            if status is not None:
                state_dict["test_coverage"]["status"] = status
            if current_coverage is not None:
                state_dict["test_coverage"]["current_coverage"] = current_coverage
            if iterations is not None:
                state_dict["test_coverage"]["iterations"] = iterations
            if tests_written is not None:
                state_dict["test_coverage"]["tests_written"] = tests_written
            if session_id is not None:
                state_dict["test_coverage"]["session_id"] = session_id
            if initial_coverage is not None:
                state_dict["test_coverage"]["initial_coverage"] = initial_coverage
            if target_coverage is not None:
                state_dict["test_coverage"]["target_coverage"] = target_coverage

            # Update timestamp
            if state_dict["test_coverage"].get("started_at") is None:
                state_dict["test_coverage"]["started_at"] = datetime.utcnow().isoformat()

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)

        if self.logger:
            self.logger.info(
                f"Updated test coverage progress: status={status}, "
                f"coverage={current_coverage}%, iterations={iterations}"
            )

        return WorkspaceState.from_dict(updated_dict)

    def add_test_coverage_history_entry(
        self,
        iteration: int,
        coverage: float,
        tests_written: List[str]
    ) -> WorkspaceState:
        """
        Add entry to test coverage history.

        Args:
            iteration: Current iteration number
            coverage: Coverage percentage achieved
            tests_written: List of test names written

        Returns:
            Updated WorkspaceState
        """
        from datetime import datetime

        def updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            if "test_coverage" not in state_dict:
                state_dict["test_coverage"] = self.initialize_test_coverage_state()

            if "history" not in state_dict["test_coverage"]:
                state_dict["test_coverage"]["history"] = []

            state_dict["test_coverage"]["history"].append({
                "iteration": iteration,
                "coverage": coverage,
                "tests_written": tests_written,
                "timestamp": datetime.utcnow().isoformat()
            })

            return state_dict

        updated_dict = update_state_atomic(self.state_path, updater)
        return WorkspaceState.from_dict(updated_dict)

    def get_test_coverage_state(self) -> Dict[str, Any]:
        """
        Get current test coverage state.

        Returns:
            Dict with test coverage state, or default if not initialized
        """
        state = self.load()
        if hasattr(state, 'test_coverage') and state.test_coverage:
            return state.test_coverage
        return self.initialize_test_coverage_state()
