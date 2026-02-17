"""
Core revert functionality for expert-feedback workflow.

This module provides revert operations that allow rolling back to previous
phases and iterations for testing and debugging purposes.
"""
import json
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from state.manager import StateManager, WorkspaceState
from validation.revert_validation import (
    parse_revert_target,
    validate_revert_target,
    get_phases_after,
    should_clear_synthesis_session,
    should_clear_artifact_session,
    normalize_phase,
    get_phase_index
)
from file_io.json_ops import save_json
from state.operations import update_state_atomic


def archive_for_revert(
    workspace: Path,
    current_state: WorkspaceState,
    target_iteration: int,
    target_phase: str
) -> Dict[str, Any]:
    """
    Archive data that will be removed by revert operation.

    Args:
        workspace: Workspace directory path
        current_state: Current workspace state
        target_iteration: Target iteration to revert to
        target_phase: Target phase to revert to

    Returns:
        {
            "archive_dir": Path to archive directory,
            "archived_items": List of archived paths,
            "manifest_path": Path to manifest file
        }

    Creates:
        workspace/.archive/revert-{timestamp}/
            ├── revert-manifest.json
            ├── state.json (before revert)
            ├── iteration-N/ (for iterations after target)
            └── artifacts/ (if generated after target)
    """
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    archive_dir = workspace / ".archive" / f"revert-{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived_items = []

    # Archive state.json
    state_file = workspace / "state.json"
    if state_file.exists():
        shutil.copy2(state_file, archive_dir / "state.json")
        archived_items.append("state.json")

    # Archive iterations after target
    for iteration in range(target_iteration + 1, current_state.iteration + 1):
        iter_dir = workspace / f"iteration-{iteration}"
        if iter_dir.exists():
            shutil.copytree(iter_dir, archive_dir / f"iteration-{iteration}")
            archived_items.append(f"iteration-{iteration}/")

    # Archive artifacts if generated after target iteration
    artifacts_dir = workspace / "artifacts"
    if artifacts_dir.exists() and target_phase:
        # Check if we're reverting before artifact generation
        artifact_phase_idx = get_phase_index("generating_artifact")
        target_phase_idx = get_phase_index(target_phase)

        if target_phase_idx < artifact_phase_idx or target_iteration < current_state.iteration:
            # Archive artifacts directory
            archive_artifacts_dir = archive_dir / "artifacts"
            archive_artifacts_dir.mkdir(exist_ok=True)

            for artifact_file in artifacts_dir.iterdir():
                if artifact_file.is_file():
                    shutil.copy2(artifact_file, archive_artifacts_dir / artifact_file.name)
                    archived_items.append(f"artifacts/{artifact_file.name}")

    # Create manifest
    manifest = {
        "revert_timestamp": datetime.now().isoformat(),
        "reverted_from": {
            "iteration": current_state.iteration,
            "phase": getattr(current_state, "phase", "unknown")
        },
        "reverted_to": {
            "iteration": target_iteration,
            "phase": target_phase
        },
        "archived_items": archived_items,
        "restoration_instructions": (
            "To restore this state:\n"
            "1. Copy state.json back to workspace root\n"
            "2. Copy iteration directories back to workspace root\n"
            "3. Copy artifacts back to workspace/artifacts/"
        )
    }

    manifest_path = archive_dir / "revert-manifest.json"
    save_json(manifest, manifest_path)

    return {
        "archive_dir": str(archive_dir),
        "archived_items": archived_items,
        "manifest_path": str(manifest_path)
    }


def cleanup_reverted_data(
    workspace: Path,
    current_iteration: int,
    target_iteration: int
) -> List[str]:
    """
    Remove data after archiving.

    Args:
        workspace: Workspace directory path
        current_iteration: Current iteration number
        target_iteration: Target iteration to revert to

    Returns:
        List of removed paths
    """
    removed = []

    # Remove iteration directories after target
    for iteration in range(target_iteration + 1, current_iteration + 1):
        iter_dir = workspace / f"iteration-{iteration}"
        if iter_dir.exists():
            shutil.rmtree(iter_dir)
            removed.append(f"iteration-{iteration}/")

    # Note: We keep logs for debugging
    # Note: Artifacts are handled separately by state restoration

    return removed


def filter_valid_sessions(
    expert_sessions: Dict[str, str],
    expert_sessions_by_iteration: Dict[int, Dict[str, str]],
    target_iteration: int,
    target_phase: str
) -> Dict[str, str]:
    """
    Determine which expert sessions are still valid after revert.

    Args:
        expert_sessions: Current expert sessions dict
        expert_sessions_by_iteration: Per-iteration session tracking
        target_iteration: Target iteration
        target_phase: Target phase

    Returns:
        Dictionary of valid expert sessions

    Logic:
        - If reverting to spawning_experts, clear all sessions (will re-spawn)
        - Otherwise, use sessions from target iteration if available
        - Fall back to current sessions if no per-iteration tracking
    """
    if target_phase == "spawning_experts":
        # Will re-spawn, clear all sessions
        return {}

    # Try to get sessions from target iteration
    if expert_sessions_by_iteration and target_iteration in expert_sessions_by_iteration:
        return expert_sessions_by_iteration[target_iteration].copy()

    # Fall back to current sessions (conservative - may be reused)
    return expert_sessions.copy()


def restore_state_to_target(
    state_dict: Dict[str, Any],
    current_iteration: int,
    target_iteration: int,
    target_phase: str
) -> Dict[str, Any]:
    """
    Restore state dictionary to target iteration/phase.

    Args:
        state_dict: Current state dictionary
        current_iteration: Current iteration number
        target_iteration: Target iteration
        target_phase: Target phase

    Returns:
        Updated state dictionary

    Modifications:
        - Sets iteration and phase
        - Clears completion flags for phases after target
        - Preserves valid session IDs
        - Updates convergence to target iteration's values
        - Adds revert history entry
    """
    old_phase = state_dict.get("phase", "unknown")

    # Set iteration and phase
    state_dict["iteration"] = target_iteration
    state_dict["phase"] = target_phase

    # Normalize phase for consistency
    normalized_phase = normalize_phase(target_phase)

    # Clear completion flags for phases after target in target iteration
    for phase in get_phases_after(normalized_phase):
        # Clear both iteration-specific and global completion markers
        phase_key = f"{phase}_complete"
        phase_result_key = f"{phase}_result"

        state_dict.pop(phase_key, None)
        state_dict.pop(phase_result_key, None)

        # Also clear iteration-specific markers
        iter_complete_key = f"{phase}_iteration_{target_iteration}_complete"
        iter_result_key = f"{phase}_iteration_{target_iteration}_result"

        state_dict.pop(iter_complete_key, None)
        state_dict.pop(iter_result_key, None)

    # Clear completion flags for all phases in later iterations
    for iter_num in range(target_iteration + 1, current_iteration + 1):
        for phase in ["spawning_experts", "consolidating", "synthesizing",
                      "questions", "generating_artifact", "reviewing_artifact", "completed"]:
            iter_complete_key = f"{phase}_iteration_{iter_num}_complete"
            iter_result_key = f"{phase}_iteration_{iter_num}_result"

            state_dict.pop(iter_complete_key, None)
            state_dict.pop(iter_result_key, None)

    # Preserve session IDs based on target
    expert_sessions = state_dict.get("expert_sessions", {})
    expert_sessions_by_iteration = state_dict.get("expert_sessions_by_iteration", {})

    preserved_sessions = filter_valid_sessions(
        expert_sessions,
        expert_sessions_by_iteration,
        target_iteration,
        target_phase
    )

    state_dict["expert_sessions"] = preserved_sessions

    # Clear synthesis session if reverting before synthesis
    if should_clear_synthesis_session(target_phase):
        state_dict["synthesis_session_id"] = None

    # Clear artifact generation session if reverting before artifact generation
    if should_clear_artifact_session(target_phase):
        state_dict["artifact_generation_session_id"] = None
        state_dict["artifact_generation_result"] = None
        state_dict["artifact_review_needed"] = False

    # Update convergence to target iteration's values
    # Look for synthesis result from target iteration
    synthesis_result_key = f"consolidating_iteration_{target_iteration}_result"
    if synthesis_result_key in state_dict:
        synthesis_result = state_dict[synthesis_result_key]
        if synthesis_result and isinstance(synthesis_result, dict):
            state_dict["convergence_percent"] = synthesis_result.get("convergence_percent", 0)
            state_dict["consensus_reached"] = synthesis_result.get("consensus_reached", False)

    # Trim iteration_history to target iteration
    iteration_history = state_dict.get("iteration_history", [])
    if iteration_history:
        state_dict["iteration_history"] = [
            entry for entry in iteration_history
            if entry.get("iteration", 0) <= target_iteration
        ]

    # Trim artifact_regeneration_history if reverting before artifacts
    if should_clear_artifact_session(target_phase):
        state_dict["artifact_regeneration_history"] = []
        state_dict["artifact_generation_attempts"] = 0

    # Add revert history
    if "revert_history" not in state_dict:
        state_dict["revert_history"] = []

    state_dict["revert_history"].append({
        "timestamp": datetime.now().isoformat(),
        "from": {"iteration": current_iteration, "phase": old_phase},
        "to": {"iteration": target_iteration, "phase": target_phase},
        "reason": "user_initiated_revert"
    })

    return state_dict


def execute_revert(
    workspace: Path,
    current_state: WorkspaceState,
    target: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute revert operation.

    Args:
        workspace: Workspace directory path
        current_state: Current workspace state
        target: Target specification (from parse_revert_target)

    Returns:
        {
            "status": "success" | "error",
            "reverted_from": {"iteration": 3, "phase": "artifact_review"},
            "reverted_to": {"iteration": 2, "phase": "synthesizing"},
            "archived": {...},
            "removed": [...],
            "preserved_sessions": {...}
        }
    """
    target_iteration = target.get("iteration", current_state.iteration)
    target_phase = target.get("phase", "spawning_experts")

    # Archive data before modification
    try:
        archive_result = archive_for_revert(
            workspace=workspace,
            current_state=current_state,
            target_iteration=target_iteration,
            target_phase=target_phase
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to archive data: {e}",
            "traceback": traceback.format_exc()
        }

    # Remove data from workspace
    try:
        removed = cleanup_reverted_data(
            workspace=workspace,
            current_iteration=current_state.iteration,
            target_iteration=target_iteration
        )
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to cleanup data: {e}",
            "traceback": traceback.format_exc(),
            "note": f"Data was archived to {archive_result['archive_dir']}"
        }

    # Restore state atomically
    try:
        state_manager = StateManager(workspace)

        def state_updater(state_dict: Dict[str, Any]) -> Dict[str, Any]:
            return restore_state_to_target(
                state_dict=state_dict,
                current_iteration=current_state.iteration,
                target_iteration=target_iteration,
                target_phase=target_phase
            )

        updated_state_dict = update_state_atomic(
            state_path=workspace / "state.json",
            update_fn=state_updater
        )

        preserved_sessions = updated_state_dict.get("expert_sessions", {})

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to update state: {e}",
            "traceback": traceback.format_exc(),
            "note": (
                f"Data was archived to {archive_result['archive_dir']}. "
                "You may need to manually restore state.json from archive."
            )
        }

    return {
        "status": "success",
        "reverted_from": {
            "iteration": current_state.iteration,
            "phase": getattr(current_state, "phase", "unknown")
        },
        "reverted_to": {
            "iteration": target_iteration,
            "phase": target_phase
        },
        "archived": archive_result,
        "removed": removed,
        "preserved_sessions": preserved_sessions
    }


def preview_revert(
    workspace: Path,
    current_state: WorkspaceState,
    target: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Preview what a revert operation would do (dry-run).

    Args:
        workspace: Workspace directory path
        current_state: Current workspace state
        target: Target specification

    Returns:
        {
            "status": "success",
            "current_state": {...},
            "target_state": {...},
            "would_archive": [...],
            "would_remove": [...],
            "would_clear_sessions": [...],
            "would_preserve_sessions": [...]
        }
    """
    target_iteration = target.get("iteration", current_state.iteration)
    target_phase = target.get("phase", "spawning_experts")

    # Determine what would be archived
    would_archive = []

    # State file
    would_archive.append("state.json")

    # Iterations after target
    for iteration in range(target_iteration + 1, current_state.iteration + 1):
        iter_dir = workspace / f"iteration-{iteration}"
        if iter_dir.exists():
            would_archive.append(f"iteration-{iteration}/")

    # Artifacts if reverting before artifact generation
    if should_clear_artifact_session(target_phase):
        artifacts_dir = workspace / "artifacts"
        if artifacts_dir.exists():
            for artifact_file in artifacts_dir.iterdir():
                if artifact_file.is_file():
                    would_archive.append(f"artifacts/{artifact_file.name}")

    # Determine which sessions would be preserved/cleared
    expert_sessions = current_state.expert_sessions
    expert_sessions_by_iteration = getattr(current_state, "expert_sessions_by_iteration", {})

    preserved_sessions = filter_valid_sessions(
        expert_sessions,
        expert_sessions_by_iteration,
        target_iteration,
        target_phase
    )

    cleared_sessions = [
        expert for expert in expert_sessions
        if expert not in preserved_sessions
    ]

    return {
        "status": "success",
        "current_state": {
            "iteration": current_state.iteration,
            "phase": getattr(current_state, "phase", "unknown"),
            "convergence_percent": current_state.convergence_percent
        },
        "target_state": {
            "iteration": target_iteration,
            "phase": target_phase
        },
        "would_archive": would_archive,
        "would_remove": [
            f"iteration-{i}/" for i in range(target_iteration + 1, current_state.iteration + 1)
        ],
        "would_clear_synthesis_session": should_clear_synthesis_session(target_phase),
        "would_clear_artifact_session": should_clear_artifact_session(target_phase),
        "would_clear_sessions": cleared_sessions,
        "would_preserve_sessions": list(preserved_sessions.keys())
    }


def handle_revert(
    workspace: Path,
    revert_target: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Handle --revert-to parameter (main entry point).

    Args:
        workspace: Workspace path
        revert_target: Target specification (e.g., "iteration=2,phase=synthesizing")
        dry_run: If True, preview changes without applying

    Returns:
        Result dictionary with status and details

    Examples:
        >>> handle_revert(Path("/workspace"), "iteration=2")
        {"status": "success", "reverted_to": {"iteration": 2, "phase": "spawning_experts"}, ...}

        >>> handle_revert(Path("/workspace"), "phase=synthesizing", dry_run=True)
        {"status": "success", "would_archive": [...], ...}
    """
    # Parse target
    try:
        target = parse_revert_target(revert_target)
    except ValueError as e:
        return {
            "status": "error",
            "error": f"Invalid revert target: {e}"
        }

    # Load current state
    state_manager = StateManager(workspace)
    try:
        current_state = state_manager.load()
    except FileNotFoundError:
        return {
            "status": "error",
            "error": "No state file found - nothing to revert"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to load state: {e}"
        }

    # Validate revert target
    validation = validate_revert_target(
        current_state=current_state,
        target_iteration=target.get("iteration"),
        target_phase=target.get("phase"),
        workspace=workspace
    )

    if not validation["valid"]:
        return {
            "status": "error",
            "error": validation["error"],
            "current_state": {
                "iteration": current_state.iteration,
                "phase": getattr(current_state, "phase", "unknown")
            }
        }

    # Show warnings if any
    if validation.get("warnings"):
        for warning in validation["warnings"]:
            print(f"⚠️  Warning: {warning}")

    # Dry run - show what would happen
    if dry_run:
        return preview_revert(
            workspace=workspace,
            current_state=current_state,
            target=target
        )

    # Execute revert
    try:
        result = execute_revert(
            workspace=workspace,
            current_state=current_state,
            target=target
        )
        return result
    except Exception as e:
        return {
            "status": "error",
            "error": f"Revert failed: {e}",
            "traceback": traceback.format_exc()
        }
