"""
Validation logic for workflow revert functionality.

This module provides validation functions to ensure revert operations
are safe and valid before execution.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from state.manager import WorkspaceState


# Valid phases in execution order
PHASE_ORDER = [
    "spawning_experts",
    "consolidating",
    "synthesizing",  # Alias for consolidating
    "questions",
    "generating_artifact",
    "reviewing_artifact",
    "artifact_review",  # Alias for reviewing_artifact
    "completed"
]

VALID_PHASES = {
    "spawning_experts",
    "consolidating",
    "synthesizing",
    "questions",
    "generating_artifact",
    "reviewing_artifact",
    "artifact_review",
    "completed"
}

# Phase aliases for consistency
PHASE_ALIASES = {
    "synthesizing": "consolidating",
    "artifact_review": "reviewing_artifact"
}


def normalize_phase(phase: str) -> str:
    """
    Normalize phase name to canonical form.

    Args:
        phase: Phase name (may be alias)

    Returns:
        Canonical phase name
    """
    return PHASE_ALIASES.get(phase, phase)


def get_phase_index(phase: str) -> int:
    """
    Get index of phase in execution order.

    Args:
        phase: Phase name

    Returns:
        Index in PHASE_ORDER, or -1 if not found
    """
    normalized = normalize_phase(phase)
    try:
        return PHASE_ORDER.index(normalized)
    except ValueError:
        return -1


def parse_revert_target(target_str: str) -> Dict[str, Any]:
    """
    Parse revert target specification.

    Args:
        target_str: Target specification (e.g., "iteration=2", "phase=synthesizing",
                   "iteration=2,phase=spawning_experts", "init")

    Returns:
        Dictionary with 'iteration' and/or 'phase' keys

    Raises:
        ValueError: If target format is invalid

    Examples:
        >>> parse_revert_target("iteration=2")
        {'iteration': 2}

        >>> parse_revert_target("phase=synthesizing")
        {'phase': 'synthesizing'}

        >>> parse_revert_target("iteration=2,phase=spawning_experts")
        {'iteration': 2, 'phase': 'spawning_experts'}

        >>> parse_revert_target("init")
        {'iteration': 1, 'phase': 'spawning_experts'}
    """
    target = {}

    # Handle special "init" target
    if target_str.strip() == "init":
        return {'iteration': 1, 'phase': 'spawning_experts'}

    # Parse key=value pairs
    parts = target_str.split(',')

    for part in parts:
        part = part.strip()
        if '=' not in part:
            raise ValueError(
                f"Invalid target format: '{part}'. "
                f"Expected key=value (e.g., iteration=2 or phase=synthesizing)"
            )

        key, value = part.split('=', 1)
        key = key.strip()
        value = value.strip()

        if key == 'iteration':
            try:
                target['iteration'] = int(value)
            except ValueError:
                raise ValueError(
                    f"Invalid iteration number: '{value}'. Must be a positive integer."
                )

            if target['iteration'] < 1:
                raise ValueError(
                    f"Invalid iteration number: {target['iteration']}. Must be >= 1."
                )

        elif key == 'phase':
            if value not in VALID_PHASES:
                raise ValueError(
                    f"Invalid phase '{value}'. "
                    f"Valid phases: {sorted(VALID_PHASES)}"
                )
            target['phase'] = value

        else:
            raise ValueError(
                f"Invalid target key: '{key}'. Valid keys: iteration, phase"
            )

    if not target:
        raise ValueError(
            "Empty target specification. "
            "Use iteration=N, phase=NAME, or iteration=N,phase=NAME"
        )

    return target


def validate_revert_target(
    current_state: WorkspaceState,
    target_iteration: Optional[int],
    target_phase: Optional[str],
    workspace: Path
) -> Dict[str, Any]:
    """
    Validate revert target is safe and possible.

    Args:
        current_state: Current workspace state
        target_iteration: Target iteration (None means current)
        target_phase: Target phase (None means beginning of iteration)
        workspace: Workspace path

    Returns:
        {
            "valid": bool,
            "error": str | None,
            "warnings": List[str]
        }
    """
    warnings = []

    # Determine effective target
    target_iter = target_iteration if target_iteration is not None else current_state.iteration
    target_phase_name = target_phase if target_phase is not None else "spawning_experts"

    # Normalize phase name
    target_phase_name = normalize_phase(target_phase_name)

    # Check 1: Target iteration must not be in the future
    if target_iter > current_state.iteration:
        return {
            "valid": False,
            "error": (
                f"Cannot revert forward. "
                f"Target iteration {target_iter} > current {current_state.iteration}"
            ),
            "warnings": warnings
        }

    # Check 2: Phase must be valid
    if target_phase and target_phase not in VALID_PHASES:
        return {
            "valid": False,
            "error": (
                f"Invalid phase '{target_phase}'. "
                f"Valid phases: {sorted(VALID_PHASES)}"
            ),
            "warnings": warnings
        }

    # Check 3: Target iteration directory must exist (if past iteration)
    if target_iter < current_state.iteration:
        iter_dir = workspace / f"iteration-{target_iter}"
        if not iter_dir.exists():
            return {
                "valid": False,
                "error": (
                    f"Target iteration {target_iter} directory not found: {iter_dir}. "
                    f"Cannot revert to non-existent iteration."
                ),
                "warnings": warnings
            }

    # Check 4: Cannot revert to current state (no-op)
    current_phase = getattr(current_state, "phase", None)
    if current_phase:
        current_phase_normalized = normalize_phase(current_phase)
        target_phase_normalized = normalize_phase(target_phase_name)

        if target_iter == current_state.iteration and target_phase_normalized == current_phase_normalized:
            return {
                "valid": False,
                "error": (
                    f"Already at target state: iteration={target_iter}, phase={target_phase_name}. "
                    f"Nothing to revert."
                ),
                "warnings": warnings
            }

    # Check 5: Must be reverting backwards in phase order
    if target_iter == current_state.iteration and current_phase:
        current_phase_idx = get_phase_index(current_phase)
        target_phase_idx = get_phase_index(target_phase_name)

        if current_phase_idx >= 0 and target_phase_idx >= 0:
            if target_phase_idx >= current_phase_idx:
                return {
                    "valid": False,
                    "error": (
                        f"Cannot revert forward within iteration. "
                        f"Current phase: {current_phase}, target phase: {target_phase_name}"
                    ),
                    "warnings": warnings
                }

    # Check 6: Phase should have been reached in target iteration
    # (Only check for historical iterations, current iteration may be in progress)
    if target_iter < current_state.iteration:
        # For past iterations, we can check if phase was reached
        # This requires checking iteration history or phase completion markers
        state_dict = current_state.to_dict()
        phase_key = f"{target_phase_name}_iteration_{target_iter}_complete"

        # If we have explicit completion tracking and phase wasn't completed,
        # warn user (but don't block - state may not have full history)
        if phase_key in state_dict and not state_dict[phase_key]:
            warnings.append(
                f"Phase '{target_phase_name}' may not have been reached in iteration {target_iter}. "
                f"Revert will proceed but workflow state may be unusual."
            )

    return {
        "valid": True,
        "error": None,
        "warnings": warnings
    }


def get_phases_after(phase: str) -> List[str]:
    """
    Get list of phases that come after the given phase.

    Args:
        phase: Phase name

    Returns:
        List of phases that come after the given phase in execution order

    Example:
        >>> get_phases_after("synthesizing")
        ['questions', 'generating_artifact', 'reviewing_artifact', 'completed']
    """
    normalized = normalize_phase(phase)
    phase_idx = get_phase_index(normalized)

    if phase_idx < 0:
        return []

    return [p for p in PHASE_ORDER[phase_idx + 1:] if p in VALID_PHASES]


def should_clear_synthesis_session(target_phase: str) -> bool:
    """
    Determine if synthesis session should be cleared when reverting to target phase.

    Args:
        target_phase: Target phase name

    Returns:
        True if synthesis session should be cleared, False otherwise

    Logic:
        Clear synthesis session if reverting to phase before consolidating/synthesizing
    """
    target_phase_idx = get_phase_index(target_phase)
    synthesis_phase_idx = get_phase_index("consolidating")

    if target_phase_idx < 0 or synthesis_phase_idx < 0:
        return False

    return target_phase_idx < synthesis_phase_idx


def should_clear_artifact_session(target_phase: str) -> bool:
    """
    Determine if artifact generation session should be cleared when reverting to target phase.

    Args:
        target_phase: Target phase name

    Returns:
        True if artifact session should be cleared, False otherwise

    Logic:
        Clear artifact session if reverting to phase before generating_artifact
    """
    target_phase_idx = get_phase_index(target_phase)
    artifact_phase_idx = get_phase_index("generating_artifact")

    if target_phase_idx < 0 or artifact_phase_idx < 0:
        return False

    return target_phase_idx < artifact_phase_idx
