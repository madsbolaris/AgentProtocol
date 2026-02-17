"""
State machine for phase validation and transitions (Phase 1.4).

This module ensures the expert-feedback workflow follows valid state transitions,
preventing invalid states and making debugging easier.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class Phase(Enum):
    """
    Valid phases in expert-feedback workflow.

    Workflow progression:
    INIT → SPAWNING → SYNTHESIZING → QUESTIONS/FINALIZING
                                     ↓
                    SPAWNING ← QUESTIONS
                       ↓
                  SYNTHESIZING → FINALIZING → REVIEWING → COMPLETE
    """
    INIT = "init"
    SPAWNING = "spawning_experts"
    SYNTHESIZING = "synthesizing"
    QUESTIONS = "questions"
    FINALIZING = "finalizing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    ERROR = "error"


class InvalidTransitionError(Exception):
    """Raised when attempting invalid phase transition."""

    def __init__(self, current: Phase, attempted: Phase, allowed: List[Phase]):
        self.current = current
        self.attempted = attempted
        self.allowed = allowed
        message = (
            f"Invalid phase transition: {current.value} → {attempted.value}\n"
            f"Allowed transitions from {current.value}: {[p.value for p in allowed]}"
        )
        super().__init__(message)


@dataclass
class PhaseTransition:
    """Record of a phase transition for audit trail."""
    from_phase: str
    to_phase: str
    timestamp: str
    trigger: Optional[str] = None  # What caused the transition
    metadata: Optional[Dict[str, Any]] = None  # Additional context


class StateMachine:
    """
    Validates phase transitions to prevent invalid states.

    This state machine ensures the workflow progresses logically and prevents
    common errors like:
    - Finalizing before synthesis
    - Spawning experts after completion
    - Skipping required phases

    Usage:
        from state.manager import StateManager
        from expert_feedback.core.state_machine import StateMachine, Phase

        state_manager = StateManager(workspace)
        state_machine = StateMachine(state_manager)

        # Validate and transition
        state_machine.transition(Phase.SPAWNING, trigger="user_started_session")
        # Later...
        state_machine.transition(Phase.SYNTHESIZING, trigger="all_experts_complete")
    """

    # Valid transitions map
    TRANSITIONS: Dict[Phase, List[Phase]] = {
        Phase.INIT: [Phase.SPAWNING],
        Phase.SPAWNING: [Phase.SYNTHESIZING, Phase.ERROR],
        Phase.SYNTHESIZING: [Phase.QUESTIONS, Phase.FINALIZING, Phase.ERROR],
        Phase.QUESTIONS: [Phase.SPAWNING, Phase.FINALIZING, Phase.ERROR],  # Can iterate or finalize
        Phase.FINALIZING: [Phase.REVIEWING, Phase.ERROR],
        Phase.REVIEWING: [Phase.COMPLETE, Phase.SPAWNING, Phase.ERROR],  # Can complete or iterate
        Phase.COMPLETE: [],  # Terminal state
        Phase.ERROR: [Phase.INIT],  # Can restart from error
    }

    def __init__(self, state_manager: 'StateManager'):
        """
        Initialize state machine with state manager.

        Args:
            state_manager: StateManager instance for accessing/updating state
        """
        self.state_manager = state_manager

    def get_current_phase(self) -> Phase:
        """
        Get current phase from state.

        Returns:
            Current Phase enum value

        Raises:
            FileNotFoundError: If state doesn't exist
            ValueError: If phase value is invalid
        """
        state = self.state_manager.load()
        phase_str = getattr(state, 'phase', 'init')
        try:
            return Phase(phase_str)
        except ValueError:
            raise ValueError(f"Invalid phase in state: {phase_str}")

    def can_transition(self, to_phase: Phase) -> bool:
        """
        Check if transition to target phase is allowed.

        Args:
            to_phase: Desired target phase

        Returns:
            True if transition is valid, False otherwise
        """
        try:
            current = self.get_current_phase()
        except FileNotFoundError:
            # No state file yet - only INIT is allowed
            return to_phase == Phase.INIT

        allowed = self.TRANSITIONS.get(current, [])
        return to_phase in allowed

    def transition(
        self,
        to_phase: Phase,
        trigger: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> 'WorkspaceState':
        """
        Transition to new phase with validation.

        Args:
            to_phase: Target phase to transition to
            trigger: Optional description of what triggered transition
            metadata: Optional additional context
            force: If True, skip validation (use with caution!)

        Returns:
            Updated WorkspaceState

        Raises:
            InvalidTransitionError: If transition is not allowed
            FileNotFoundError: If state doesn't exist and not transitioning to INIT

        Example:
            # Start session
            state_machine.transition(
                Phase.SPAWNING,
                trigger="user_started_review",
                metadata={"num_experts": 7}
            )

            # Complete spawning
            state_machine.transition(
                Phase.SYNTHESIZING,
                trigger="all_experts_completed"
            )
        """
        try:
            current = self.get_current_phase()
        except FileNotFoundError:
            # First transition - must be to INIT
            if to_phase != Phase.INIT and not force:
                raise InvalidTransitionError(Phase.INIT, to_phase, [Phase.INIT])
            current = Phase.INIT

        # Validate transition (unless forced)
        if not force:
            allowed = self.TRANSITIONS.get(current, [])
            if to_phase not in allowed:
                raise InvalidTransitionError(current, to_phase, allowed)

        # Record transition in state
        transition_record = PhaseTransition(
            from_phase=current.value,
            to_phase=to_phase.value,
            timestamp=__import__('datetime').datetime.now().astimezone().isoformat(),
            trigger=trigger,
            metadata=metadata
        )

        # Update state with new phase
        def updater(state_dict):
            state_dict["phase"] = to_phase.value
            state_dict["phase_updated_at"] = transition_record.timestamp

            # Add to transition history
            if "phase_history" not in state_dict:
                state_dict["phase_history"] = []

            state_dict["phase_history"].append({
                "from": transition_record.from_phase,
                "to": transition_record.to_phase,
                "timestamp": transition_record.timestamp,
                "trigger": transition_record.trigger,
                "metadata": transition_record.metadata or {}
            })

            return state_dict

        from state.operations import update_state_atomic
        updated_dict = update_state_atomic(self.state_manager.state_path, updater)

        # Import here to avoid circular dependency
        from state.manager import WorkspaceState
        return WorkspaceState.from_dict(updated_dict)

    def require_phase(self, *required_phases: Phase) -> None:
        """
        Assert that current phase is one of the required phases.

        Args:
            *required_phases: One or more phases that are acceptable

        Raises:
            RuntimeError: If current phase is not in required phases

        Example:
            # Ensure synthesis has run before finalizing
            state_machine.require_phase(Phase.SYNTHESIZING, Phase.QUESTIONS)
            # Proceed with finalization...
        """
        current = self.get_current_phase()
        if current not in required_phases:
            required_names = [p.value for p in required_phases]
            raise RuntimeError(
                f"Operation requires phase: {required_names}\n"
                f"Current phase: {current.value}\n"
                f"Complete required phases before proceeding."
            )

    def get_transition_history(self) -> List[PhaseTransition]:
        """
        Get history of phase transitions for debugging/audit.

        Returns:
            List of PhaseTransition records in chronological order
        """
        state = self.state_manager.load()
        history_dicts = getattr(state, 'phase_history', [])

        return [
            PhaseTransition(
                from_phase=record["from"],
                to_phase=record["to"],
                timestamp=record["timestamp"],
                trigger=record.get("trigger"),
                metadata=record.get("metadata")
            )
            for record in history_dicts
        ]

    def get_next_phases(self) -> List[Phase]:
        """
        Get list of valid next phases from current state.

        Returns:
            List of Phase values that can be transitioned to

        Example:
            next_phases = state_machine.get_next_phases()
            print(f"Can transition to: {[p.value for p in next_phases]}")
        """
        current = self.get_current_phase()
        return self.TRANSITIONS.get(current, [])

    def is_terminal_phase(self) -> bool:
        """
        Check if current phase is a terminal state.

        Returns:
            True if no more transitions are possible
        """
        return len(self.get_next_phases()) == 0

    def reset_to_init(self, reason: str = "manual_reset") -> 'WorkspaceState':
        """
        Reset state machine to INIT phase.

        This is useful for restarting a failed workflow or beginning a new session.

        Args:
            reason: Reason for reset (for audit trail)

        Returns:
            Updated WorkspaceState

        Warning:
            This does NOT clear workspace data, only resets the phase.
            Use with caution in production!
        """
        return self.transition(
            Phase.INIT,
            trigger=f"reset_{reason}",
            force=True  # Allow reset from any phase
        )


# Export classes
__all__ = [
    "Phase",
    "InvalidTransitionError",
    "PhaseTransition",
    "StateMachine",
]
