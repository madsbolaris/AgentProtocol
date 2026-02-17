"""
State fixtures for testing.

Provides pre-configured WorkspaceState objects for common test scenarios.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts directory to path for imports
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))

from state.manager import WorkspaceState


def create_initial_state(
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    mode: str = "review",
    convergence_target: int = 80
) -> WorkspaceState:
    """
    Create initial state for iteration 1.

    Args:
        topic: Review topic
        experts: List of expert names (default: ["typescript", "python"])
        mode: Operation mode
        convergence_target: Target convergence percentage

    Returns:
        WorkspaceState object
    """
    if experts is None:
        experts = ["typescript", "python"]

    return WorkspaceState(
        topic=topic,
        experts=experts,
        iteration=1,
        mode=mode,
        convergence_target=convergence_target,
        convergence_percent=0,
        consensus_reached=False,
    )


def create_state_with_sessions(
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    sessions: Optional[Dict[str, str]] = None,
    iteration: int = 1
) -> WorkspaceState:
    """
    Create state with expert sessions configured.

    Args:
        topic: Review topic
        experts: List of expert names
        sessions: Expert session mapping {expert: session_id}
        iteration: Iteration number

    Returns:
        WorkspaceState with sessions
    """
    if experts is None:
        experts = ["typescript", "python"]

    if sessions is None:
        sessions = {expert: f"session-{expert}-123" for expert in experts}

    state = create_initial_state(topic, experts)
    state.iteration = iteration
    state.expert_sessions = sessions

    return state


def create_state_with_convergence(
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    convergence_percent: int = 75,
    consensus_reached: bool = False,
    high_agreement: int = 3,
    partial_agreement: int = 2,
    low_agreement: int = 1,
    iteration: int = 1
) -> WorkspaceState:
    """
    Create state with convergence metrics.

    Args:
        topic: Review topic
        experts: List of expert names
        convergence_percent: Convergence percentage
        consensus_reached: Whether consensus was reached
        high_agreement: Number of high-agreement items
        partial_agreement: Number of partial-agreement items
        low_agreement: Number of low-agreement items
        iteration: Iteration number

    Returns:
        WorkspaceState with convergence data
    """
    if experts is None:
        experts = ["typescript", "python"]

    state = create_initial_state(topic, experts)
    state.iteration = iteration
    state.convergence_percent = convergence_percent
    state.consensus_reached = consensus_reached
    state.high_agreement = high_agreement
    state.partial_agreement = partial_agreement
    state.low_agreement = low_agreement

    return state


def create_state_with_progress(
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    progress: Optional[Dict[str, Dict[str, any]]] = None,
    iteration: int = 1
) -> WorkspaceState:
    """
    Create state with expert progress tracking.

    Args:
        topic: Review topic
        experts: List of expert names
        progress: Expert progress mapping {expert: {status, duration, tokens, ...}}
        iteration: Iteration number

    Returns:
        WorkspaceState with progress data
    """
    if experts is None:
        experts = ["typescript", "python"]

    if progress is None:
        progress = {
            expert: {
                "status": "complete",
                "duration_seconds": 30.5,
                "total_tokens": 2000
            }
            for expert in experts
        }

    state = create_initial_state(topic, experts)
    state.iteration = iteration
    state.expert_progress = progress

    return state


def create_complete_state(
    topic: str = "Test API Design",
    experts: Optional[List[str]] = None,
    final_convergence: int = 85,
    total_iterations: int = 2
) -> WorkspaceState:
    """
    Create state representing a completed workflow.

    Args:
        topic: Review topic
        experts: List of expert names
        final_convergence: Final convergence percentage
        total_iterations: Total number of iterations

    Returns:
        WorkspaceState for completed workflow
    """
    if experts is None:
        experts = ["typescript", "python"]

    state = create_state_with_convergence(
        topic=topic,
        experts=experts,
        convergence_percent=final_convergence,
        consensus_reached=True,
        iteration=total_iterations
    )

    # Add sessions
    state.expert_sessions = {
        expert: f"session-{expert}-final"
        for expert in experts
    }

    # Add synthesis session
    state.synthesis_session_id = "synthesis-session-final"

    # Add artifact generation info
    state.artifact_generation_session_id = "artifact-session-final"
    state.artifact_generation_result = {
        "status": "success",
        "temp_adr_file": "temp-adr.md",
        "final_adr_file": "final-adr.md"
    }

    # Add completion timestamps
    state.start_time = "2026-02-15T10:00:00"
    state.complete_time = "2026-02-15T10:30:00"

    # Add token/cost metrics
    state.total_tokens = 25000
    state.total_cost = 5.50
    state.total_input_tokens = 15000
    state.total_output_tokens = 10000

    return state


def create_multiexpert_state(
    topic: str = "Test Complex System Design",
    num_experts: int = 5
) -> WorkspaceState:
    """
    Create state with multiple experts for load testing.

    Args:
        topic: Review topic
        num_experts: Number of experts to include

    Returns:
        WorkspaceState with many experts
    """
    available_experts = [
        "typescript",
        "python",
        "dotnet",
        "dx",
        "openai-sdk",
        "api-design",
        "security"
    ]

    experts = available_experts[:num_experts]

    return create_initial_state(topic=topic, experts=experts)
