"""
Workspace fixtures for testing.

Provides utilities to create and configure test workspaces with
proper directory structure and initial state.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add scripts directory to path for imports
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from state.manager import StateManager, WorkspaceState


def create_test_workspace(
    tmp_path: Path,
    workspace_name: str = "test-workspace"
) -> Path:
    """
    Create a test workspace directory structure.

    Args:
        tmp_path: Temporary directory from pytest
        workspace_name: Name for the workspace

    Returns:
        Path to created workspace
    """
    workspace = tmp_path / workspace_name
    workspace.mkdir(parents=True, exist_ok=True)

    # Create standard subdirectories
    (workspace / "logs").mkdir(exist_ok=True)
    (workspace / "iteration-1").mkdir(exist_ok=True)

    return workspace


def setup_workspace_with_state(
    workspace: Path,
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    iteration: int = 1,
    mode: str = "review",
    convergence_target: int = 80,
    **kwargs
) -> StateManager:
    """
    Create workspace with initialized state.

    Args:
        workspace: Workspace directory path
        topic: Review topic
        experts: List of expert names (default: ["typescript", "python"])
        iteration: Starting iteration number
        mode: Operation mode (review/improve/create)
        convergence_target: Target convergence percentage
        **kwargs: Additional state fields

    Returns:
        StateManager with initialized state
    """
    if experts is None:
        experts = ["typescript", "python"]

    # Create state manager
    state_manager = StateManager(workspace)

    # Create initial state
    state = WorkspaceState(
        topic=topic,
        experts=experts,
        iteration=iteration,
        mode=mode,
        convergence_target=convergence_target,
        **kwargs
    )

    # Save state
    state_manager.create(state)

    return state_manager


def create_iteration_structure(
    workspace: Path,
    iteration: int,
    experts: Optional[List[str]] = None
) -> None:
    """
    Create directory structure for an iteration.

    Args:
        workspace: Workspace directory
        iteration: Iteration number
        experts: List of expert names
    """
    iteration_dir = workspace / f"iteration-{iteration}"
    iteration_dir.mkdir(exist_ok=True)

    # Create expert subdirectories if specified
    if experts:
        for expert in experts:
            expert_dir = iteration_dir / "experts" / expert
            expert_dir.mkdir(parents=True, exist_ok=True)


def add_qa_answers(
    workspace: Path,
    iteration: int,
    answers: dict,
    skip_iteration: bool = False
) -> Path:
    """
    Add Q&A answers file to workspace.

    Args:
        workspace: Workspace directory
        iteration: Iteration number
        answers: Answer dictionary
        skip_iteration: Whether user wants to skip iteration

    Returns:
        Path to created answers file
    """
    from file_io.json_ops import save_json

    iteration_dir = workspace / f"iteration-{iteration}"
    iteration_dir.mkdir(exist_ok=True)

    qa_file = iteration_dir / "qa-answers.json"

    qa_data = {
        "skip_iteration": skip_iteration,
        **answers
    }

    save_json(qa_data, qa_file)

    return qa_file


def add_expert_result(
    workspace: Path,
    iteration: int,
    expert: str,
    recommendations: List[dict],
    concerns: Optional[List[str]] = None,
    questions: Optional[List[str]] = None
) -> Path:
    """
    Add expert result file to workspace.

    Args:
        workspace: Workspace directory
        iteration: Iteration number
        expert: Expert name
        recommendations: List of recommendations
        concerns: List of concerns
        questions: List of questions

    Returns:
        Path to created result file
    """
    from file_io.json_ops import save_json

    iteration_dir = workspace / f"iteration-{iteration}"
    iteration_dir.mkdir(exist_ok=True)

    result_file = iteration_dir / f"state-{expert}-{iteration}.json"

    result_data = {
        "expert": expert,
        "analysis": f"Mock analysis from {expert}",
        "recommendations": recommendations,
        "concerns": concerns or [],
        "questions": questions or []
    }

    save_json(result_data, result_file)

    return result_file


def add_synthesized_feedback(
    workspace: Path,
    iteration: int,
    convergence_percent: int,
    consensus_reached: bool,
    high_agreement: Optional[List[dict]] = None,
    partial_agreement: Optional[List[dict]] = None,
    low_agreement: Optional[List[dict]] = None
) -> Path:
    """
    Add synthesized feedback file to workspace.

    Args:
        workspace: Workspace directory
        iteration: Iteration number
        convergence_percent: Convergence percentage
        consensus_reached: Whether consensus was reached
        high_agreement: High agreement recommendations
        partial_agreement: Partial agreement recommendations
        low_agreement: Low agreement recommendations

    Returns:
        Path to created synthesis file
    """
    from file_io.json_ops import save_json

    iteration_dir = workspace / f"iteration-{iteration}"
    iteration_dir.mkdir(exist_ok=True)

    synthesis_file = iteration_dir / f"synthesized-{iteration}.json"

    synthesis_data = {
        "convergence_percent": convergence_percent,
        "consensus_reached": consensus_reached,
        "high_agreement": high_agreement or [],
        "partial_agreement": partial_agreement or [],
        "low_agreement": low_agreement or []
    }

    save_json(synthesis_data, synthesis_file)

    return synthesis_file
