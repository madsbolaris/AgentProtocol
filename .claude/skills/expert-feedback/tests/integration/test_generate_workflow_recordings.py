"""
Generate multi-turn conversation recordings using Simple Calculator mock project.

This test generates recordings for the fast integration test workflow using a minimal
~100 LOC mock project that experts can analyze quickly (<30s).

Usage:
    # Generate recordings (makes real API calls)
    EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/test_generate_workflow_recordings.py -v -s

    # Test replay (fast, no API calls)
    EXPERT_FEEDBACK_TEST_MODE=replay pytest tests/integration/test_generate_workflow_recordings.py -v

Recordings generated:
    - Iteration 1: 2 expert reviews (typescript, python)
    - Iteration 1: 1 synthesis (with questions)
    - Question consolidation: 1 synthesis recording

Total: 4 recordings (~30s generation time with parallel expert execution)
"""
import pytest
import sys
import shutil
from pathlib import Path

# Add scripts and tests directories to path
# IMPORTANT: scripts must come FIRST to avoid shadowing state module
_scripts_dir = Path(__file__).parent.parent.parent / "scripts"
_tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_tests_dir))  # Add tests second (will be at index 1)
sys.path.insert(0, str(_scripts_dir))  # Add scripts first (will be at index 0)


def copy_mock_project_to_workspace(workspace: Path, project_name: str) -> None:
    """
    Copy mock project to workspace for expert analysis.

    Args:
        workspace: Test workspace directory
        project_name: Name of mock project (e.g., "simple-calculator")
    """
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "mock-projects"
    mock_project = fixtures_dir / project_name

    if not mock_project.exists():
        raise FileNotFoundError(f"Mock project not found: {mock_project}")

    # Copy project to workspace
    dest = workspace / project_name
    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(mock_project, dest)
    print(f"  📁 Copied {project_name} to {dest}")


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_iteration_1_with_questions(
    mock_claude_sdk,
    initialized_workspace
):
    """
    Generate iteration 1 recordings with expert questions using Simple Calculator.

    TEST CONTROL: None (natural behavior)
    - Experts naturally find issues in flawed code
    - No test controls needed - experts will find obvious problems
    - See plan Section 3.5 for test control usage in other branches

    Stages:
    1. Copy Simple Calculator mock project to workspace
    2. Iteration 1: Spawn 2 experts (typescript, python) to review calculator
    3. Synthesis: Consolidate expert feedback and extract questions

    Expected recordings: 3 (2 experts + 1 synthesis)
    Expected questions: 2-4 total (about numeric ranges, error handling, etc.)
    Time estimate: ~30s with parallel execution

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record \\
        ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \\
        pytest tests/integration/test_generate_workflow_recordings.py::test_generate_iteration_1_with_questions -v -s
    """
    # Import AFTER mock is set up
    from core.spawn_experts import spawn_all_experts
    from core.synthesize import synthesize_feedback
    from config import get_config
    from ui.progress_tracker import ProgressTracker
    from file_io.json_ops import save_json

    workspace = initialized_workspace
    config = get_config()
    state_path = workspace / "state.json"

    # Copy Simple Calculator mock project
    print(f"\n{'='*80}")
    print(f"🎬 Recording Iteration 1 Workflow - Simple Calculator")
    print(f"{'='*80}")
    copy_mock_project_to_workspace(workspace, "simple-calculator")

    experts = ["typescript", "python"]
    review_context = """Review the simple-calculator API for production readiness.

This is a basic calculator REST API with add, multiply, divide, and subtract operations.
The code is ~100 lines and located in the `simple-calculator/` directory.

**Focus Areas:**
- Input validation and error handling
- Type safety and API contracts
- Test coverage and code quality
- Security vulnerabilities
- Documentation completeness

**Known Issues to Identify:**
- Missing input validation (accepts any types)
- No error handling (crashes on invalid input)
- Zero test coverage
- TypeScript uses `any` types (no type safety)
- Python uses eval() for calculations (CRITICAL security issue)
- No function documentation

**Goal:** Identify all production-readiness gaps and provide actionable recommendations."""

    print(f"Workspace: {workspace}")
    print(f"Experts: {', '.join(experts)}")
    print(f"Review Context: {review_context[:80]}...")
    print(f"Mode: {mock_claude_sdk.mode if mock_claude_sdk else 'record'}")
    print(f"{'='*80}\n")

    # ========== ITERATION 1: Initial Reviews ==========
    print("\n🔹 ITERATION 1: Initial Expert Reviews")
    print("-" * 60)

    progress = ProgressTracker(1, workspace)

    result = await spawn_all_experts(
        experts=experts,
        review_context=review_context,
        workspace=str(workspace),
        iteration=1,
        state_path=state_path,
        config=config,
        progress=progress,
        correlation_id="simple-calc-iter1-experts"
    )

    print(f"\n✅ Iteration 1 experts complete:")
    for expert_result in result.get("results", []):
        expert = expert_result.get("expert")
        status = expert_result.get("status")
        duration = expert_result.get("duration_seconds", 0)
        session_id = expert_result.get("session_id", "N/A")
        print(f"  - {expert}: {status} ({duration:.1f}s, session: {session_id[:12]}...)")

    # Verify success
    assert result.get("success_count", 0) == len(experts), \
        f"Expected {len(experts)} successful experts, got {result.get('success_count', 0)}"

    # ========== SUMMARY ==========
    print(f"\n{'='*80}")
    print("✅ Recording Generation Complete!")
    print(f"{'='*80}")
    print(f"Workspace: {workspace}")
    print(f"\nRecordings generated:")
    print(f"  - Iteration 1: {len(experts)} expert reviews")
    print(f"  - Total: {len(experts)} recordings")
    print(f"{'='*80}\n")

    # Save workspace snapshot in record mode
    if mock_claude_sdk and mock_claude_sdk.mode == "record":
        from pathlib import Path
        from fixtures.workspace_snapshot import snapshot_workspace
        snapshot_workspace(
            test_name="test_generate_iteration_1_with_questions",
            workspace=workspace,
            recordings_dir=Path(__file__).parent.parent / "recordings"
        )
        print("  📸 Workspace snapshot saved\n")

    # Verify at least some recordings were made
    if mock_claude_sdk:
        print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
        assert mock_claude_sdk.call_count >= len(experts), \
            f"Should have made at least {len(experts)} LLM calls for experts"


@pytest.mark.asyncio
@pytest.mark.recording
async def test_generate_synthesis_iteration_1(
    mock_claude_sdk,
    initialized_workspace
):
    """
    Generate iteration 1 synthesis recording that consolidates expert feedback.

    TEST CONTROL: None (natural behavior)
    - Synthesis consolidates feedback from expert reviews
    - Questions extracted from expert reviews (NOT user answers)
    - Convergence calculated automatically

    Prerequisites:
    - Expert reviews must exist from iteration 1 (test_generate_iteration_1_with_questions)
    - This can be run standalone if expert review files are in workspace

    Stages:
    1. Copy Simple Calculator and run experts (if not already present)
    2. Synthesis: Consolidate expert feedback, extract questions, calculate convergence

    Expected recordings: 1 (synthesis only)
    Expected questions: 2-4 extracted from expert reviews
    Expected convergence: 20-40% (first iteration, experts agree on some basics)
    Time estimate: ~45s

    Run with:
        EXPERT_FEEDBACK_TEST_MODE=record \\
        ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \\
        pytest tests/integration/test_generate_workflow_recordings.py::test_generate_synthesis_iteration_1 -v -s
    """
    # Import AFTER mock is set up
    from core.spawn_experts import spawn_all_experts
    from core.synthesize import synthesize_feedback
    from config import get_config
    from ui.progress_tracker import ProgressTracker
    from file_io.json_ops import save_json, load_json
    from file_io.workspace_utils import WorkspacePaths

    workspace = initialized_workspace
    config = get_config()
    state_path = workspace / "state.json"
    paths = WorkspacePaths(workspace)

    print(f"\n{'='*80}")
    print(f"🎬 Recording Iteration 1 Synthesis - Simple Calculator")
    print(f"{'='*80}")

    # DEBUG: Log workspace details
    print(f"\n🔍 DEBUG: Workspace Setup")
    print(f"   Workspace path: {workspace}")
    print(f"   Workspace exists: {workspace.exists()}")
    if workspace.exists():
        print(f"   Workspace contents: {list(workspace.iterdir())[:5]}")

    # Try to restore predecessor's workspace snapshot
    from pathlib import Path
    from fixtures.workspace_snapshot import has_snapshot, restore_workspace

    predecessor = "test_generate_iteration_1_with_questions"
    recordings_base = Path(__file__).parent.parent / "recordings"

    # DEBUG: Log snapshot lookup details
    print(f"\n🔍 DEBUG: Snapshot Lookup")
    print(f"   Looking for: {predecessor}")
    print(f"   Recordings base: {recordings_base}")
    print(f"   Recordings base (absolute): {recordings_base.absolute()}")
    print(f"   Recordings base exists: {recordings_base.exists()}")

    snapshot_path = recordings_base / predecessor / "workspace"
    print(f"   Expected snapshot path: {snapshot_path}")
    print(f"   Snapshot path exists: {snapshot_path.exists()}")

    has_snap = has_snapshot(predecessor, recordings_base)
    print(f"   has_snapshot() result: {has_snap}")

    if has_snap:
        print("\n  ✅ Restoring expert reviews from snapshot")

        # DEBUG: Check workspace before restoration
        print(f"\n🔍 DEBUG: Before Restoration")
        experts_dir_before = workspace / "iteration-1" / "experts"
        print(f"   iteration-1/experts/ exists: {experts_dir_before.exists()}")
        if experts_dir_before.exists():
            print(f"   Contents: {list(experts_dir_before.iterdir())}")

        restore_workspace(predecessor, workspace, recordings_base)

        # DEBUG: Check workspace after restoration
        print(f"\n🔍 DEBUG: After Restoration")
        experts_dir_after = workspace / "iteration-1" / "experts"
        print(f"   iteration-1/experts/ exists: {experts_dir_after.exists()}")
        if experts_dir_after.exists():
            contents = list(experts_dir_after.iterdir())
            print(f"   Contents ({len(contents)} items):")
            for item in sorted(contents):
                if item.is_dir():
                    subcontents = list(item.iterdir())
                    print(f"     {item.name}/ ({len(subcontents)} items)")
                else:
                    print(f"     {item.name}")
    else:
        # Fallback: run experts (maintains standalone capability)
        print("\n  ⚠️  No snapshot found, running experts as fallback...")

        experts = ["typescript", "python"]
        review_context = """Review the simple-calculator API for production readiness.

This is a basic calculator REST API with add, multiply, divide, and subtract operations.
The code is ~100 lines and located in the `simple-calculator/` directory.

**Focus Areas:**
- Input validation and error handling
- Type safety and API contracts
- Test coverage and code quality
- Security vulnerabilities
- Documentation completeness

**Known Issues to Identify:**
- Missing input validation (accepts any types)
- No error handling (crashes on invalid input)
- Zero test coverage
- TypeScript uses `any` types (no type safety)
- Python uses eval() for calculations (CRITICAL security issue)
- No function documentation

**Goal:** Identify all production-readiness gaps and provide actionable recommendations."""

        copy_mock_project_to_workspace(workspace, "simple-calculator")

        progress = ProgressTracker(1, workspace)
        result = await spawn_all_experts(
            experts=experts,
            review_context=review_context,
            workspace=str(workspace),
            iteration=1,
            state_path=state_path,
            config=config,
            progress=progress,
            correlation_id="synthesis-fallback-experts"
        )

        print(f"  ✅ Fallback experts complete: {result.get('success_count')}/{len(experts)}")

    # ========== SYNTHESIS ==========
    print("\n🔹 SYNTHESIS: Consolidate Feedback & Extract Questions")
    print("-" * 60)

    # DEBUG: Check workspace structure before synthesis
    print(f"\n🔍 DEBUG: Before Synthesis - Workspace Structure")
    experts_check = workspace / "iteration-1" / "experts"
    if experts_check.exists():
        print(f"   iteration-1/experts/ exists: ✅")
        subdirs = [item for item in experts_check.iterdir() if item.is_dir()]
        print(f"   Subdirectories: {[d.name for d in subdirs]}")
        for item in subdirs:
            state_file = item / "state.json"
            print(f"     {item.name}/ - state.json exists: {state_file.exists()}")
    else:
        print(f"   iteration-1/experts/ does NOT exist: ❌")

    progress = ProgressTracker(1, workspace)

    result = await synthesize_feedback(
        workspace=workspace,
        iteration=1,
        config=config,
        progress=progress,
        correlation_id="synthesis-test-consolidation"
    )

    print(f"\n✅ Synthesis complete:")
    print(f"  - Status: {result.get('status')}")
    print(f"  - Convergence: {result.get('convergence_percent', 0)}%")
    print(f"  - Consensus: {result.get('consensus_reached', False)}")
    print(f"  - Duration: {result.get('duration_seconds', 0):.1f}s")
    print(f"  - Session: {result.get('session_id', 'N/A')[:12]}...")

    # Verify synthesis produced expected outputs
    assert result.get("status") == "complete", "Synthesis should complete successfully"

    synthesized_file = result.get("synthesized_file")
    questions_file = result.get("questions_file")

    assert synthesized_file and Path(synthesized_file).exists(), \
        f"Synthesized file should exist: {synthesized_file}"

    print(f"  - Synthesized: {synthesized_file}")

    if questions_file:
        questions_path = Path(questions_file)
        if questions_path.exists():
            questions_data = load_json(questions_path)
            question_count = len(questions_data.get("questions", []))
            print(f"  - Questions: {question_count} extracted {'(0 is valid - synthesis may not need questions)' if question_count == 0 else ''}")
            # Note: 0 questions is valid if synthesis determines everything is clear

    # ========== SUMMARY ==========
    print(f"\n{'='*80}")
    print("✅ Iteration 1 Synthesis Recording Complete!")
    print(f"{'='*80}")
    print(f"Workspace: {workspace}")
    print(f"\nRecordings generated:")
    print(f"  - Iteration 1 Synthesis: 1 recording")
    print(f"  - Total: 1 recording")
    print(f"{'='*80}\n")

    # Save workspace snapshot in record mode
    if mock_claude_sdk and mock_claude_sdk.mode == "record":
        from fixtures.workspace_snapshot import snapshot_workspace
        snapshot_workspace(
            test_name="test_generate_synthesis_iteration_1",
            workspace=workspace,
            recordings_dir=recordings_base
        )
        print("  📸 Workspace snapshot saved\n")

    # Verify recording was made
    if mock_claude_sdk:
        print(f"📊 Total LLM calls made: {mock_claude_sdk.call_count}")
        assert mock_claude_sdk.call_count >= 1, \
            "Should have made at least 1 LLM call for synthesis"

