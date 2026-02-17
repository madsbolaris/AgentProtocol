#!/usr/bin/env python3
"""
Generate basic recordings for expert-feedback workflow.

These tests generate recordings in isolation to validate the recording system
before running the full workflow.

Run in record mode:
    EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_generate_basic_recordings.py -v -s

Run in replay mode:
    EXPERT_FEEDBACK_TEST_MODE=replay pytest tests/integration/test_generate_basic_recordings.py -v
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from state.manager import StateManager


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_expert_iteration_recordings(mock_claude_sdk, initialized_workspace):
    """
    Generate recordings for expert iterations with session continuity.

    Stages:
    1. Expert iteration 1 (CREATE sessions for 2 experts)
    2. Expert iteration 2 (RESUME sessions for 2 experts)

    Expected recordings: 4 (2 experts × 2 iterations)

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_generate_basic_recordings.py::test_generate_expert_iteration_recordings -v -s
    """
    from core.spawn_experts import spawn_all_experts
    from config import get_config
    from ui.progress_tracker import ProgressTracker
    
    workspace = initialized_workspace
    state_manager = StateManager(workspace)
    config = get_config()
    state_path = workspace / "state.json"

    print("\n" + "="*80)
    print("GENERATING EXPERT ITERATION RECORDINGS")
    print("="*80)

    # ITERATION 1: Create sessions
    print("\n📍 ITERATION 1: Creating expert sessions...")
    progress_1 = ProgressTracker(2, workspace)  # 2 experts (typescript, python)

    result_1 = await spawn_all_experts(
        experts=["typescript", "python"],
        review_context="Review SDK API design for client library",
        workspace=str(workspace),
        iteration=1,
        state_path=state_path,
        config=config,
        progress=progress_1,
        correlation_id="basic-recording-iter1"
    )

    print(f"✅ Iteration 1 complete: {result_1['success_count']} experts")
    assert result_1["success_count"] == 2

    # Verify sessions created
    state = state_manager.load()
    assert "typescript" in state.expert_sessions
    assert "python" in state.expert_sessions
    ts_session_1 = state.expert_sessions["typescript"]
    py_session_1 = state.expert_sessions["python"]
    print(f"   TypeScript session: {ts_session_1[:12]}...")
    print(f"   Python session: {py_session_1[:12]}...")

    # ITERATION 2: Resume sessions
    print("\n📍 ITERATION 2: Resuming expert sessions...")
    progress_2 = ProgressTracker(2, workspace)  # 2 experts (typescript, python)
    result_2 = await spawn_all_experts(
        experts=["typescript", "python"],
        review_context="Review SDK API design for client library",
        workspace=str(workspace),
        iteration=2,
        state_path=state_path,
        config=config,
        progress=progress_2,
        correlation_id="basic-recording-iter2"
    )

    print(f"✅ Iteration 2 complete: {result_2['success_count']} experts")
    assert result_2["success_count"] == 2

    # Verify session reuse (same IDs)
    state = state_manager.load()
    ts_session_2 = state.expert_sessions["typescript"]
    py_session_2 = state.expert_sessions["python"]

    assert ts_session_2 == ts_session_1, f"TypeScript session changed! {ts_session_1} → {ts_session_2}"
    assert py_session_2 == py_session_1, f"Python session changed! {py_session_1} → {py_session_2}"

    print(f"   TypeScript session REUSED: {ts_session_2[:12]}...")
    print(f"   Python session REUSED: {py_session_2[:12]}...")

    # Verify recordings exist
    recordings_dir = Path("tests/recordings")
    recording_files = list(recordings_dir.glob("*.response.json"))
    print(f"\n✅ Generated {len(recording_files)} total recordings")
    print(f"   Expected: 4+ recordings (2 experts × 2 iterations)")

    assert len(recording_files) >= 4, f"Expected 4+ recordings, got {len(recording_files)}"

    print("\n" + "="*80)
    print("SUCCESS: Expert iteration recordings generated with session continuity")
    print("="*80)


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_synthesis_recordings(mock_claude_sdk, initialized_workspace):
    """
    Generate recordings for synthesis workflow.

    Prerequisite: Expert iteration recordings must exist first!

    Expected recordings: 1-2 (synthesis iterations)

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_generate_basic_recordings.py::test_generate_synthesis_recordings -v -s
    """
    from core.synthesize import synthesize_feedback
    from state.manager import StateManager

    workspace = initialized_workspace
    state_manager = StateManager(workspace)

    print("\n" + "="*80)
    print("GENERATING SYNTHESIS RECORDINGS")
    print("="*80)

    # Create mock expert feedback files
    print("\n📍 Setting up mock expert feedback...")
    await _setup_mock_expert_feedback(workspace, iteration=1)

    # ITERATION 1: Synthesis
    print("\n📍 ITERATION 1: Running synthesis...")
    synthesis_1 = await synthesize_feedback(
        workspace=str(workspace),
        iteration=1
    )

    print(f"✅ Synthesis 1 complete:")
    print(f"   Convergence: {synthesis_1.get('convergence_percent', 0)}%")

    assert synthesis_1 is not None
    assert "convergence_percent" in synthesis_1

    # Verify synthesis session created
    state = state_manager.load()
    assert state.synthesis_session_id is not None
    print(f"   Synthesis session: {state.synthesis_session_id[:12]}...")

    # Verify recordings exist
    recordings_dir = Path("tests/recordings")
    recording_files = list(recordings_dir.glob("*.response.json"))
    print(f"\n✅ Total recordings: {len(recording_files)}")

    print("\n" + "="*80)
    print("SUCCESS: Synthesis recordings generated")
    print("="*80)


async def _setup_mock_expert_feedback(workspace: Path, iteration: int):
    """Create mock expert feedback files for synthesis testing."""
    from state.manager import WorkspaceState

    # Create iteration directory
    iter_dir = workspace / f"iteration-{iteration}"
    iter_dir.mkdir(parents=True, exist_ok=True)

    experts_dir = iter_dir / "experts"
    experts_dir.mkdir(parents=True, exist_ok=True)

    # Mock TypeScript expert feedback
    ts_feedback = {
        "expert": "typescript",
        "dx_rating": {"stars": 4, "rationale": "Good API design"},
        "concerns": [
            {
                "id": "ts-001",
                "title": "Type definitions need improvement",
                "severity": "medium",
                "description": "Some return types are unclear"
            }
        ],
        "recommendations": [
            {
                "id": "ts-rec-001",
                "title": "Add explicit return types",
                "priority": "high"
            }
        ]
    }
    (experts_dir / "state-typescript.json").write_text(json.dumps(ts_feedback, indent=2))

    # Mock Python expert feedback
    py_feedback = {
        "expert": "python",
        "dx_rating": {"stars": 3, "rationale": "Needs better error handling"},
        "concerns": [
            {
                "id": "py-001",
                "title": "Error messages are vague",
                "severity": "high",
                "description": "Exceptions don't provide enough context"
            }
        ],
        "recommendations": [
            {
                "id": "py-rec-001",
                "title": "Add detailed error messages",
                "priority": "high"
            }
        ]
    }
    (experts_dir / "state-python.json").write_text(json.dumps(py_feedback, indent=2))

    print("   ✅ Created mock expert feedback for typescript and python")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
