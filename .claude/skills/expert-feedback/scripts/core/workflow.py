#!/usr/bin/env python3
"""
Orchestrate expert-feedback workflow without main agent involvement.

This script automates the complete workflow:
1. Spawn experts (parallel)
2. Consolidate feedback
3. Wait for user answers (via web UI → qa-answers.json)
4. If not converged, iterate (spawn → synthesize)
5. Generate artifact from expert feedback
6. Artifact review - experts review the draft artifact
7. Wait for user approval (via web UI → approvals.json)
8. Complete

User interaction happens entirely through web UI.
Main agent is not involved in orchestration.

Usage:
    python3 run_workflow.py --workspace /path --review-context "..." --mode review
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from file_io.json_ops import save_json, load_json
from agent_logging.agent_logger import generate_correlation_id, setup_agent_logger_v2
# Note: load_json now blocks state.json access (Phase 1.4)
# Use StateManager instead for all state operations
from config import get_config
from state.manager import StateManager as WorkspaceStateManager
from file_io.workspace_utils import (
    WorkspacePaths,
    get_artifact_path
)
# Robustness improvements
from validation.circuit_breaker import CircuitBreakerState
from errors import (
    MinimumExpertsError,
    CircuitBreakerError,
    ConsolidationFailureError
)
# Revert functionality
from core.revert import handle_revert
# Concern review functionality
from concern_review import artifact_concern_review
from synthesize_concerns import synthesize_concerns
from user_concern_review import user_concern_review_interactive
from address_concerns import address_concerns_iteration
from synthesize_concern_updates import synthesize_concern_updates
from regenerate_artifact_concerns import regenerate_artifact_with_concerns
# Autonomous execution functionality
from execute_autonomous import run_autonomous_execution
from test_coverage_agent import run_test_coverage_phase

# Add .claude to path
claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(claude_dir))


async def spawn_experts_iteration(
    workspace: Path,
    iteration: int,
    experts: List[str],
    review_context: str,
    correlation_id: Optional[str] = None,
    qa_answers_path: Optional[Path] = None,
    focus_files: Optional[List[str]] = None,
    focus_folders: Optional[List[str]] = None,
    focus_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Spawn all experts for an iteration.

    Returns:
        Result dictionary with success_count, error_count, results
    """
    print(f"\n🤖 Spawning {len(experts)} expert(s) in parallel...", file=sys.stderr)

    # Build command
    cmd = [
        "python3",
        str(Path(__file__).parent / "spawn-all-experts.py"),
        "--workspace", str(workspace),
        "--iteration", str(iteration),
        "--review-context", review_context,
        "--experts"
    ] + experts

    if correlation_id:
        cmd.extend(["--correlation-id", correlation_id])

    if qa_answers_path and qa_answers_path.exists():
        cmd.extend(["--qa-answers", str(qa_answers_path)])

    if focus_files:
        cmd.extend(["--focus-files"] + focus_files)

    if focus_folders:
        cmd.extend(["--focus-folders"] + focus_folders)

    if focus_context:
        cmd.extend(["--focus-context", focus_context])

    # Run subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    # Parse result
    try:
        result = json.loads(stdout.decode())
        return result
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse spawn-all-experts output", file=sys.stderr)
        print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
        print(f"STDERR: {stderr.decode()}", file=sys.stderr)
        return {
            "success_count": 0,
            "error_count": len(experts),
            "status": "error",
            "error": "Failed to spawn experts"
        }


async def synthesize_feedback(
    workspace: Path,
    iteration: int,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consolidate feedback from all experts for an iteration.

    Returns:
        Result dictionary with convergence_percent, consensus_reached
    """
    print(f"\n📈 Consolidating feedback...", file=sys.stderr)

    # Build command
    cmd = [
        "python3",
        str(Path(__file__).parent / "synthesize-feedback.py"),
        "--workspace", str(workspace),
        "--iteration", str(iteration)
    ]

    if correlation_id:
        cmd.extend(["--correlation-id", correlation_id])

    # Run subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    # Parse result
    try:
        result = json.loads(stdout.decode())
        return result
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse synthesize-feedback output", file=sys.stderr)
        print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
        print(f"STDERR: {stderr.decode()}", file=sys.stderr)
        return {
            "convergence_percent": 0,
            "consensus_reached": False,
            "status": "error",
            "error": "Failed to synthesize feedback"
        }


async def generate_artifact(
    workspace: Path,
    review_context: str,
    mode: str,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate final artifact (ADR or Implementation Plan).

    Returns:
        Result dictionary with temp_file, final_file, etc.
    """
    print(f"\n📝 Generating artifact...", file=sys.stderr)

    # Build command
    cmd = [
        "python3",
        str(Path(__file__).parent.parent / "artifacts" / "generator.py"),
        "--workspace", str(workspace),
        "--review-context", review_context,
        "--mode", mode
    ]

    if correlation_id:
        cmd.extend(["--correlation-id", correlation_id])

    # Run subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    # Parse result
    try:
        result = json.loads(stdout.decode())
        return result
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse generate_artifact output", file=sys.stderr)
        print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
        print(f"STDERR: {stderr.decode()}", file=sys.stderr)
        return {
            "status": "error",
            "error": "Failed to generate artifact"
        }


async def regenerate_artifact_with_concerns(
    workspace: Path,
    review_context: str,
    mode: str,
    concerns: Dict[str, Any],
    correlation_id: Optional[str] = None,
    attempt: int = 1
) -> Dict[str, Any]:
    """
    Regenerate artifact addressing critical concerns.

    This continues the artifact generation agent's conversation (session reuse)
    with the critical concerns feedback, allowing it to refine the artifact based on
    expert concerns.

    Args:
        workspace: Workspace path
        review_context: Original review context
        mode: Operation mode (review/improve/create)
        concerns: Critical concerns feedback dictionary with questions and issues
        correlation_id: Correlation ID for tracing
        attempt: Regeneration attempt number (1-indexed)

    Returns:
        Result dictionary with regenerated artifact info
    """
    print(f"\n🔄 Regenerating artifact with critical concerns feedback...", file=sys.stderr)

    # Build command with --regenerate flag and concerns feedback
    cmd = [
        "python3",
        str(Path(__file__).parent.parent / "artifacts" / "generator.py"),
        "--workspace", str(workspace),
        "--review-context", review_context,
        "--mode", mode,
        "--regenerate",  # Signal this is a regeneration
        "--regeneration-attempt", str(attempt)
    ]

    if correlation_id:
        cmd.extend(["--correlation-id", correlation_id])

    # Run subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    # Parse result
    try:
        result = json.loads(stdout.decode())
        return result
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse generate_artifact output", file=sys.stderr)
        print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
        print(f"STDERR: {stderr.decode()}", file=sys.stderr)
        return {
            "status": "error",
            "error": "Failed to regenerate artifact"
        }


async def wait_for_user_answers(workspace: Path, iteration: int) -> Optional[Dict[str, Any]]:
    """
    Wait for user to answer questions via web UI.

    Polls for qa-answers.json file to appear.

    Returns:
        Answers dictionary or None if user skipped
    """
    paths = WorkspacePaths(workspace)
    qa_answers_file = paths.qa_answers_json(iteration)

    print(f"\n⏳ Waiting for user to answer questions in web UI...", file=sys.stderr)
    print(f"   Check: http://localhost:8765", file=sys.stderr)

    # Check if answers already exist (e.g., from --resume)
    if qa_answers_file.exists():
        print("✅ Existing answers found (from previous session)", file=sys.stderr)
    else:
        # Poll for answers
        while not qa_answers_file.exists():
            await asyncio.sleep(2)

    print("✅ Answers received!", file=sys.stderr)

    # Load answers
    answers = load_json(qa_answers_file)

    # Check if user wants to skip iteration
    if answers.get("skip_iteration"):
        print("⏩ User skipped iteration, proceeding to artifact generation", file=sys.stderr)
        return None

    return answers


async def wait_for_user_approval(workspace: Path, recommendations_count: int) -> List[Dict[str, Any]]:
    """
    Wait for user to approve/reject recommendations via web UI.

    Polls for approvals.json file.

    Returns:
        List of approval decisions
    """
    approvals_file = workspace / "approvals.json"

    print(f"\n⏳ Waiting for user approval in web UI...", file=sys.stderr)
    print(f"   Check: http://localhost:8765", file=sys.stderr)

    while True:
        if not approvals_file.exists():
            await asyncio.sleep(2)
            continue

        approvals = load_json(approvals_file)

        # Check if all recommendations reviewed
        if len(approvals) >= recommendations_count:
            break

        await asyncio.sleep(2)

    print("✅ All recommendations reviewed!", file=sys.stderr)
    return approvals


async def run_concern_review_loop(
    workspace: Path,
    experts: List[str],
    review_context: str,
    mode: str,
    artifact_path: Path,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Run concern review loop until approved or max iterations reached.

    This loop allows experts to voice concerns about the generated artifact,
    presents those concerns to the user for review, and addresses agreed-upon
    concerns through expert iteration and artifact regeneration.

    Args:
        workspace: Workspace path
        experts: List of expert IDs
        review_context: Original review context/topic
        mode: Generation mode (review/improve/create)
        artifact_path: Path to current artifact
        correlation_id: Optional correlation ID for logging

    Returns:
        True if concerns were addressed and artifact regenerated, False if no concerns
    """
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    concern_iteration = 1
    max_concern_iterations = 5

    had_concerns = False

    while concern_iteration <= max_concern_iterations:
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"CONCERN REVIEW ITERATION {concern_iteration}", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)

        # Step 1: Expert concern review
        print(f"🔍 Step 1: Expert concern review...", file=sys.stderr)
        concern_result = await artifact_concern_review(
            workspace=workspace,
            experts=experts,
            artifact_path=artifact_path,
            review_context=review_context,
            correlation_id=correlation_id
        )

        if concern_result.get("status") == "error":
            print(f"❌ Concern review failed: {concern_result.get('error')}", file=sys.stderr)
            break

        # Step 2: Synthesize concerns
        print(f"\n📊 Step 2: Synthesizing concerns...", file=sys.stderr)
        concern_review_dir = Path(concern_result["concern_review_dir"])
        synthesized = await synthesize_concerns(
            workspace=workspace,
            concern_review_dir=concern_review_dir,
            experts=experts,
            correlation_id=correlation_id
        )

        # Step 3: Exit if no concerns
        total_concerns = synthesized.get("total_concerns", 0)
        if total_concerns == 0:
            print(f"\n✅ No concerns raised! Artifact approved by all experts.", file=sys.stderr)
            break

        print(f"\n   Found {total_concerns} concern(s) from {len(synthesized.get('experts_with_concerns', []))} expert(s)", file=sys.stderr)

        # Step 4: User review
        print(f"\n👤 Step 3: User concern review...", file=sys.stderr)
        user_decisions = user_concern_review_interactive(
            workspace=workspace,
            synthesized_concerns=synthesized
        )

        # Step 5: Exit if all disagreed
        if not user_decisions["should_iterate"]:
            print(f"\n✅ User disagreed with all concerns. Proceeding with current artifact.", file=sys.stderr)
            break

        had_concerns = True
        agreed_concerns = user_decisions["concerns_agreed"]
        print(f"\n   User agreed with {len(agreed_concerns)} concern(s)", file=sys.stderr)

        # Step 6: Address concerns
        print(f"\n🔧 Step 4: Experts addressing concerns...", file=sys.stderr)
        address_result = await address_concerns_iteration(
            workspace=workspace,
            experts=experts,
            agreed_concerns=agreed_concerns,
            artifact_path=artifact_path,
            concern_iteration=concern_iteration,
            correlation_id=correlation_id
        )

        if address_result.get("status") == "error":
            print(f"❌ Failed to address concerns: {address_result.get('error')}", file=sys.stderr)
            break

        # Step 7: Synthesize updates
        print(f"\n📊 Step 5: Synthesizing concern updates...", file=sys.stderr)
        concern_iteration_dir = Path(address_result["concern_iteration_dir"])
        synthesis_result = await synthesize_concern_updates(
            workspace=workspace,
            concern_iteration_dir=concern_iteration_dir,
            experts=experts,
            correlation_id=correlation_id
        )

        if synthesis_result.get("status") == "error":
            print(f"❌ Failed to synthesize updates: {synthesis_result.get('error')}", file=sys.stderr)
            break

        # Step 8: Regenerate artifact
        print(f"\n📝 Step 6: Regenerating artifact...", file=sys.stderr)
        user_decisions_file = concern_review_dir / "user-concern-decisions.json"
        consolidated_recs_file = concern_iteration_dir / "consolidated-recommendations.json"

        regeneration_result = await regenerate_artifact_with_concerns(
            workspace=workspace,
            mode=mode,
            previous_artifact_path=artifact_path,
            agreed_concerns=agreed_concerns,
            consolidated_recommendations=synthesis_result["consolidated_recommendations"],
            concern_iteration=concern_iteration,
            correlation_id=correlation_id
        )

        if regeneration_result.get("status") == "error":
            print(f"❌ Failed to regenerate artifact: {regeneration_result.get('error')}", file=sys.stderr)
            break

        # Update artifact path for next iteration
        artifact_path = Path(regeneration_result["artifact_path"])
        print(f"\n✅ Artifact regenerated successfully (version {regeneration_result['artifact_version']})", file=sys.stderr)

        # Increment concern iteration
        concern_iteration += 1

    if concern_iteration > max_concern_iterations:
        print(f"\n⚠️  Max concern iterations reached ({max_concern_iterations})", file=sys.stderr)

    return had_concerns


async def run_workflow(
    workspace: Path,
    review_context: str,
    mode: str,
    resume: bool = False,
    focus_files: Optional[List[str]] = None,
    focus_folders: Optional[List[str]] = None,
    focus_context: Optional[str] = None
) -> None:
    """
    Run complete expert feedback workflow.

    Args:
        resume: If True, skip completed phases and resume from first incomplete phase
    """
    config = get_config()

    # Generate correlation ID for end-to-end tracing (Phase 4)
    correlation_id = generate_correlation_id()

    # Setup logger with correlation ID
    logger = setup_agent_logger_v2(workspace, "workflow", correlation_id=correlation_id)
    logger.info(f"Workflow started: mode={mode}, correlation_id={correlation_id}")

    paths = WorkspacePaths(workspace)
    state_file = paths.state
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager

    experts = state.get("experts", [])
    max_iterations = config.max_iterations
    convergence_target = state.get("convergence_target", config.convergence_target)
    minimum_experts = max(3, int(len(experts) * 0.5))  # At least 3 or 50% of experts

    print(f"\n🎯 Expert Feedback Workflow", file=sys.stderr)
    print(f"   Topic: {state.get('topic', 'Unknown')}", file=sys.stderr)
    print(f"   Mode: {mode}", file=sys.stderr)
    print(f"   Experts: {', '.join(experts)}", file=sys.stderr)
    print(f"   Max iterations: {max_iterations}", file=sys.stderr)
    print(f"   Convergence target: {convergence_target}%", file=sys.stderr)
    print(f"   Minimum experts required: {minimum_experts}", file=sys.stderr)
    if resume:
        print(f"   Resume: Enabled (will skip completed phases)", file=sys.stderr)

    # Initialize circuit breaker to detect stuck convergence
    circuit_breaker = CircuitBreakerState()
    print(f"   Circuit breaker: Enabled (will detect stalls)", file=sys.stderr)

    # Iteration loop
    for iteration in range(1, max_iterations + 1):
        logger.info(f"Starting iteration {iteration}/{max_iterations}")
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"📊 Iteration {iteration}/{max_iterations}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        # Determine if this is a resume (iteration > 1)
        qa_answers_path = None
        if iteration > 1:
            paths = WorkspacePaths(workspace)
            qa_answers_path = paths.qa_answers_json(iteration - 1)  # Previous iteration's answers

        # Step 1: Spawn experts
        spawning_phase = f"spawning_iteration_{iteration}"
        if resume and state_manager.is_phase_complete(spawning_phase):
            print(f"✅ Experts already spawned for iteration {iteration}, skipping", file=sys.stderr)
            # Reload state in case it was updated
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager
        else:
            # Update phase: spawning experts
            state_manager.set_phase("spawning_experts")
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager

            expert_result = await spawn_experts_iteration(
                workspace=workspace,
                iteration=iteration,
                experts=experts,
                review_context=review_context,
                correlation_id=correlation_id,
                qa_answers_path=qa_answers_path,
                focus_files=focus_files,
                focus_folders=focus_folders,
                focus_context=focus_context
            )

            success_count = expert_result.get('success_count', 0)
            error_count = expert_result.get("error_count", 0)

            if error_count > 0:
                failed_experts = expert_result.get("failed_experts", [])
                print(f"⚠️ {error_count} expert(s) failed: {', '.join(failed_experts)}", file=sys.stderr)

                # Check if we have enough successful experts to continue
                if success_count < minimum_experts:
                    raise MinimumExpertsError(
                        success_count=success_count,
                        minimum_required=minimum_experts,
                        total_experts=len(experts)
                    )
                else:
                    print(f"✅ Continuing with {success_count} experts (minimum: {minimum_experts})", file=sys.stderr)
            else:
                print(f"✅ {success_count} expert(s) completed", file=sys.stderr)

            # Use atomic updates to prevent race condition with spawn-all-experts.py
            # (spawn-all-experts.py may still be writing expert_results/expert_progress)
            state_manager.update_sessions(expert_result.get("expert_sessions", {}))
            state_manager.set_phase("consolidating")

            # Reload state after atomic updates to get expert_results
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager
            print(f"📝 Updated state with {len(state.get('expert_results', {}))} expert results", file=sys.stderr)

            # Mark phase complete
            state_manager.mark_phase_complete(spawning_phase, {
                "success_count": expert_result.get('success_count', 0),
                "error_count": expert_result.get('error_count', 0)
            })

        # Step 2: Consolidate
        synthesis_phase = f"synthesizing_iteration_{iteration}"
        if resume and state_manager.is_phase_complete(synthesis_phase):
            print(f"✅ Consolidation already complete for iteration {iteration}, skipping", file=sys.stderr)
            # Reload state to get convergence results
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager
            synthesis_result = state_manager.get_phase_result(synthesis_phase)
        else:
            synthesis_result = await synthesize_feedback(
                workspace=workspace,
                iteration=iteration,
                correlation_id=correlation_id
            )

        # Check if consolidation had an error
        if synthesis_result.get("status") == "error":
            print(f"❌ Synthesis failed: {synthesis_result.get('error')}", file=sys.stderr)
            # Reload state in case parse_and_update() succeeded before error
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager
            convergence = state.get("convergence_percent", 0)
            consensus_reached = state.get("consensus_reached", False)
        else:
            convergence = synthesis_result.get("convergence_percent", 0)
            consensus_reached = synthesis_result.get("consensus_reached", False)

            # Update state with convergence from synthesis (atomic updates)
            state_manager.update_convergence(
                convergence_percent=convergence,
                consensus_reached=consensus_reached
            )
            state_manager.set_phase("questions")  # Will ask questions if needed

            # Reload state after atomic updates
            state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager

        print(f"📊 Convergence: {convergence}%", file=sys.stderr)

        # Update circuit breaker after synthesis
        synthesis_failed = (synthesis_result.get("status") == "error")
        circuit_breaker.update(
            current_convergence=convergence,
            failed=synthesis_failed
        )

        # Check if circuit breaker should trigger
        should_break, break_reason = circuit_breaker.should_break()
        if should_break:
            logger.warning(
                f"Circuit breaker triggered: {break_reason}, "
                f"convergence={convergence}%, iteration={iteration}/{max_iterations}"
            )
            print(f"\n⚠️ Circuit breaker triggered: {break_reason}", file=sys.stderr)
            print(f"   Current convergence: {convergence}%", file=sys.stderr)
            print(f"   Iteration: {iteration}/{max_iterations}", file=sys.stderr)

            # Save diagnostic report
            diagnostic_path = circuit_breaker.save_diagnostic(workspace, iteration, convergence)
            print(f"   Diagnostic saved: {diagnostic_path}", file=sys.stderr)

            # For now, raise error to stop workflow
            # TODO: In future, prompt user via web UI whether to continue
            raise CircuitBreakerError(
                reason=break_reason,
                diagnostic_info=circuit_breaker.to_dict()
            )

        # Step 3: Check for consensus
        if consensus_reached or convergence >= convergence_target:
            logger.info(f"Consensus reached: convergence={convergence}%, target={convergence_target}%")
            print(f"✅ Consensus reached! (convergence: {convergence}%)", file=sys.stderr)
            # IMPORTANT: Still ask questions even if consensus reached
            # User input improves final artifact

        # Step 4: Wait for user answers (via web UI)
        # Skip Q&A on last iteration if consensus reached
        if iteration < max_iterations:
            answers = await wait_for_user_answers(workspace, iteration)

            if answers is None:
                # User skipped iteration
                break

            # Continue to next iteration with user answers
            print(f"\n🔄 Starting iteration {iteration + 1}...", file=sys.stderr)
        else:
            print(f"\n⏭️ Max iterations reached, proceeding to artifact generation", file=sys.stderr)
            break

    # Step 5: Finalize artifact
    # Note: generate_artifact.py will set phase to "generating_artifact" internally
    artifact_generation_result = await generate_artifact(
        workspace=workspace,
        review_context=review_context,
        mode=mode,
        correlation_id=correlation_id
    )

    if artifact_generation_result.get("status") == "error":
        print(f"❌ Artifact generation failed: {artifact_generation_result.get('error')}", file=sys.stderr)
        sys.exit(1)

    # Update state with artifact generation result (atomic updates)
    state_manager.set_artifact_generation_result(artifact_generation_result)
    state_manager.set_phase("artifact_review")

    # Track initial artifact generation attempt (Context Gap Fix 2.1)
    state_manager.increment_artifact_generation_attempt()

    # Reload state after atomic updates
    state = state_manager.load().to_dict()  # Phase 1.4: Use StateManager

    temp_file = artifact_generation_result.get("temp_adr_file") or artifact_generation_result.get("temp_plan_file")
    final_file = artifact_generation_result.get("final_adr_file") or artifact_generation_result.get("final_plan_file")

    print(f"✅ Draft created: {temp_file}", file=sys.stderr)
    print(f"   Will be moved to: {final_file}", file=sys.stderr)

    # Step 5.5: Concern Review Phase - Experts voice concerns and user reviews
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"CONCERN REVIEW PHASE", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    had_concerns_addressed = await run_concern_review_loop(
        workspace=workspace,
        experts=config["experts"],
        review_context=review_context,
        mode=mode,
        artifact_path=Path(temp_file),
        correlation_id=correlation_id
    )

    # After concern review, update artifact path if regenerated
    if had_concerns_addressed:
        # Get the latest artifact version
        state = state_manager.load()
        artifact_version = state.concern_review.get("current_artifact_version", 1)

        # Update paths to point to latest version
        if mode == "review":
            temp_file = str(workspace / "artifact" / f"draft-adr-v{artifact_version}.md")
        elif mode == "improve":
            temp_file = str(workspace / "artifact" / f"improvement-plan-v{artifact_version}.md")
        elif mode == "create":
            temp_file = str(workspace / "artifact" / f"architecture-v{artifact_version}.md")

        print(f"\n✅ Using regenerated artifact: {Path(temp_file).name}", file=sys.stderr)

    # Step 6: Artifact Review - Experts review the draft (Concern Review)
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"📋 Step 6: Expert Artifact Review (Concern Check)", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Spawning experts to review the draft artifact...", file=sys.stderr)

    # Run artifact review
    artifact_review_cmd = [
        "python3",
        str(Path(__file__).parent / "artifact-review.py"),
        "--workspace", str(workspace)
    ]

    if correlation_id:
        artifact_review_cmd.extend(["--correlation-id", correlation_id])

    process = await asyncio.create_subprocess_exec(
        *artifact_review_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    try:
        review_result = json.loads(stdout.decode())
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse artifact review output", file=sys.stderr)
        print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
        print(f"STDERR: {stderr.decode()}", file=sys.stderr)
        review_result = {"status": "error", "error": "Failed to parse review results"}

    # Track initial artifact review result (Context Gap Fix 2.1)
    initial_status = review_result.get("status")
    if initial_status == "concerns_raised":
        concerns_count = review_result.get('concerns', {}).get('total_concerns', 0)
        concerns_data = review_result.get('concerns', {})
        critical_concerns = []
        if 'critical_issues' in concerns_data:
            critical_concerns = [issue.get('title', issue.get('summary', 'Unknown'))
                           for issue in concerns_data['critical_issues']]
        state_manager.record_artifact_generation_result(
            attempt=1,
            result="concerns_raised",
            concerns_count=concerns_count,
            concerns=critical_concerns
        )
    elif initial_status == "minor_tweaks":
        state_manager.record_artifact_generation_result(
            attempt=1,
            result="minor_tweaks",
            concerns_count=0,
            concerns=[]
        )
    elif initial_status == "approved":
        state_manager.record_artifact_generation_result(
            attempt=1,
            result="approved",
            concerns_count=0,
            concerns=[]
        )

    # Handle review results - Implement concern resolution loop (Priority 1 Gap 1)
    if review_result.get("status") == "concerns_raised":
        print(f"\n❌ {review_result.get('total_concerns', 0)} expert(s) raised critical concerns about the artifact", file=sys.stderr)
        print(f"   Critical issues identified - artifact needs revision", file=sys.stderr)

        # Implement concern resolution loop with max 2 attempts
        max_regeneration_attempts = 2
        for regeneration_attempt in range(1, max_regeneration_attempts + 1):
            print(f"\n🔄 Regeneration Attempt {regeneration_attempt}/{max_regeneration_attempts}", file=sys.stderr)
            print(f"   Addressing critical concerns...", file=sys.stderr)

            # Load concerns feedback for regeneration
            concerns = review_result.get("concerns", {})
            concern_questions = concerns.get("questions_for_user", [])
            critical_issues = concerns.get("critical_issues", [])

            # Regenerate artifact with concerns feedback
            regeneration_result = await regenerate_artifact_with_concerns(
                workspace=workspace,
                review_context=review_context,
                mode=mode,
                concerns=concerns,
                correlation_id=correlation_id,
                attempt=regeneration_attempt
            )

            if regeneration_result.get("status") == "error":
                print(f"   ❌ Regeneration failed: {regeneration_result.get('error')}", file=sys.stderr)
                # Track failed regeneration (Context Gap Fix 2.1)
                state_manager.record_artifact_generation_result(
                    attempt=regeneration_attempt + 1,
                    result="error",
                    concerns_count=0,
                    concerns=["Regeneration failed with error"]
                )
                sys.exit(1)

            print(f"   ✅ Regenerated artifact: {regeneration_result.get('temp_adr_file') or regeneration_result.get('temp_plan_file')}", file=sys.stderr)

            # Track regeneration attempt (Context Gap Fix 2.1)
            state_manager.increment_artifact_generation_attempt()

            # Re-review the regenerated artifact
            print(f"\n📋 Re-reviewing regenerated artifact...", file=sys.stderr)
            artifact_review_cmd = [
                "python3",
                str(Path(__file__).parent / "artifact-review.py"),
                "--workspace", str(workspace)
            ]

            if correlation_id:
                artifact_review_cmd.extend(["--correlation-id", correlation_id])

            process = await asyncio.create_subprocess_exec(
                *artifact_review_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            try:
                review_result = json.loads(stdout.decode())
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse artifact review output", file=sys.stderr)
                print(f"STDOUT: {stdout.decode()}", file=sys.stderr)
                print(f"STDERR: {stderr.decode()}", file=sys.stderr)
                review_result = {"status": "error", "error": "Failed to parse review results"}

            # Check if concerns were addressed
            if review_result.get("status") != "concerns_raised":
                print(f"\n✅ Critical concerns addressed!", file=sys.stderr)
                # Track successful regeneration (Context Gap Fix 2.1)
                state_manager.record_artifact_generation_result(
                    attempt=regeneration_attempt + 1,
                    result="approved",
                    concerns_count=0,
                    concerns=[]
                )
                break
            else:
                concerns_count = review_result.get('concerns', {}).get('total_concerns', 0)
                print(f"\n⚠️ Still {concerns_count} critical concern(s) remaining", file=sys.stderr)

                # Extract critical concerns for tracking
                critical_concerns = []
                concerns_data = review_result.get('concerns', {})
                if 'critical_issues' in concerns_data:
                    critical_concerns = [issue.get('title', issue.get('summary', 'Unknown'))
                                   for issue in concerns_data['critical_issues']]

                # Track concerns regeneration (Context Gap Fix 2.1)
                state_manager.record_artifact_generation_result(
                    attempt=regeneration_attempt + 1,
                    result="concerns_raised",
                    concerns_count=concerns_count,
                    concerns=critical_concerns
                )

                if regeneration_attempt == max_regeneration_attempts:
                    print(f"\n❌ Max regeneration attempts reached", file=sys.stderr)
                    print(f"   Manual intervention required", file=sys.stderr)
                    print(f"   See: {workspace}/artifact-concerns-summary.md", file=sys.stderr)
                    sys.exit(1)
    elif review_result.get("status") == "minor_tweaks":
        print(f"\n⚠️  {review_result.get('total_tweaks', 0)} expert(s) suggested minor tweaks", file=sys.stderr)
        print(f"   See: {workspace}/artifact-tweaks-summary.md", file=sys.stderr)
        print(f"   Proceeding to user approval with expert feedback", file=sys.stderr)
    else:
        print(f"\n✅ All experts approved the artifact", file=sys.stderr)

    # Step 7: Wait for user approval (via web UI)
    recommendations_count = len(artifact_generation_result.get("recommendations", []))

    if recommendations_count > 0:
        approvals = await wait_for_user_approval(workspace, recommendations_count)

        approved_recs = [a for a in approvals if a.get("status") == "approved"]
        rejected_recs = [a for a in approvals if a.get("status") == "rejected"]

        print(f"\n✅ {len(approved_recs)}/{len(approvals)} recommendation(s) approved", file=sys.stderr)
        if rejected_recs:
            print(f"❌ {len(rejected_recs)} recommendation(s) rejected", file=sys.stderr)
    else:
        print(f"\n⏩ No recommendations to approve, proceeding", file=sys.stderr)

    # Step 8: Autonomous Execution Phase (NEW)
    execution_result = None
    if config.enable_auto_execution:
        print(f"\n{'='*70}", file=sys.stderr)
        print("AUTONOMOUS EXECUTION PHASE", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)

        try:
            execution_result = await run_autonomous_execution(
                workspace=workspace,
                artifact_path=Path(temp_file),
                mode=mode,
                correlation_id=correlation_id
            )

            if execution_result["status"] == "complete":
                print(f"\n✅ Autonomous execution completed successfully", file=sys.stderr)
                print(f"   Iterations: {execution_result.get('iterations', 'N/A')}", file=sys.stderr)
                print(f"   Steps completed: {execution_result.get('steps_completed', 'N/A')}", file=sys.stderr)
                print(f"   Files modified: {len(execution_result.get('files_modified', []))}", file=sys.stderr)
                if execution_result.get('deferred_questions_count', 0) > 0:
                    print(f"   Deferred questions: {execution_result['deferred_questions_count']}", file=sys.stderr)

            elif execution_result["status"] == "blocked":
                print(f"\n⏸️  Execution paused - user input required", file=sys.stderr)
                print(f"   Reason: {execution_result.get('reason', 'Unknown')}", file=sys.stderr)
                print(f"   Deferred questions: {execution_result.get('deferred_questions_count', 0)}", file=sys.stderr)
                print(f"\n   To answer questions and resume:", file=sys.stderr)
                print(f"   python3 {Path(__file__).parent / 'answer_questions.py'} --workspace {workspace}", file=sys.stderr)

            elif execution_result["status"] == "timeout":
                print(f"\n⏱️  Execution timeout reached", file=sys.stderr)
                print(f"   Reason: {execution_result.get('reason', 'Maximum time exceeded')}", file=sys.stderr)
                print(f"   Progress: {execution_result.get('progress_percent', 0)}%", file=sys.stderr)
                print(f"   Steps completed: {execution_result.get('steps_completed', 0)}", file=sys.stderr)

            elif execution_result["status"] == "incomplete":
                print(f"\n⚠️  Execution incomplete", file=sys.stderr)
                print(f"   Reason: {execution_result.get('reason', 'Maximum iterations reached')}", file=sys.stderr)
                print(f"   Progress: {execution_result.get('progress_percent', 0)}%", file=sys.stderr)
                print(f"   Iterations: {execution_result.get('iterations', 0)}", file=sys.stderr)

            elif execution_result["status"] == "error":
                print(f"\n❌ Execution failed: {execution_result.get('error', 'Unknown error')}", file=sys.stderr)

            elif execution_result["status"] == "skipped":
                print(f"\nℹ️  Autonomous execution skipped: {execution_result.get('message', 'Disabled in config')}", file=sys.stderr)

        except Exception as e:
            print(f"\n❌ Execution phase error: {e}", file=sys.stderr)
            logger.error(f"Autonomous execution failed: {e}")
            import traceback
            traceback.print_exc()
            execution_result = {
                "status": "error",
                "error": str(e)
            }
    else:
        print(f"\nℹ️  Autonomous execution disabled (enable_auto_execution=False)", file=sys.stderr)

    # Step 9: Test Coverage Phase (NEW)
    coverage_result = None
    if execution_result and execution_result["status"] == "complete" and config.enable_test_coverage_agent:
        print(f"\n{'='*70}", file=sys.stderr)
        print("TEST COVERAGE PHASE", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)

        try:
            coverage_result = await run_test_coverage_phase(
                workspace=workspace,
                target_coverage=config.target_test_coverage,
                correlation_id=correlation_id
            )

            if coverage_result["status"] == "complete":
                print(f"\n✅ Test coverage target met!", file=sys.stderr)
                print(f"   Final coverage: {coverage_result.get('final_coverage', 'N/A')}%", file=sys.stderr)
                print(f"   Target: {coverage_result.get('target_coverage', 'N/A')}%", file=sys.stderr)
                print(f"   Tests written: {coverage_result.get('tests_written', 0)}", file=sys.stderr)
                if 'unit_coverage' in coverage_result:
                    print(f"   Unit coverage: {coverage_result['unit_coverage']}%", file=sys.stderr)
                if 'integration_coverage' in coverage_result:
                    print(f"   Integration coverage: {coverage_result['integration_coverage']}%", file=sys.stderr)

            elif coverage_result["status"] == "incomplete":
                print(f"\n⚠️  Coverage target not met", file=sys.stderr)
                print(f"   Final coverage: {coverage_result.get('final_coverage', 'N/A')}%", file=sys.stderr)
                print(f"   Target: {coverage_result.get('target_coverage', 'N/A')}%", file=sys.stderr)
                print(f"   Iterations: {coverage_result.get('iterations', 0)}", file=sys.stderr)

            elif coverage_result["status"] == "error":
                print(f"\n❌ Test coverage phase failed: {coverage_result.get('error', 'Unknown error')}", file=sys.stderr)

            elif coverage_result["status"] == "skipped":
                print(f"\nℹ️  Test coverage phase skipped: {coverage_result.get('message', 'No tests to run')}", file=sys.stderr)

        except Exception as e:
            print(f"\n❌ Test coverage phase error: {e}", file=sys.stderr)
            logger.error(f"Test coverage phase failed: {e}")
            import traceback
            traceback.print_exc()
            coverage_result = {
                "status": "error",
                "error": str(e)
            }
    elif execution_result and execution_result["status"] == "complete":
        print(f"\nℹ️  Test coverage phase disabled (enable_test_coverage_agent=False)", file=sys.stderr)

    # Step 10: Complete
    logger.info(f"Workflow complete: final_convergence={state.get('convergence_percent', 0)}%")
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"🎉 Workflow Complete!", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"\n📄 Draft artifact: {temp_file}", file=sys.stderr)
    print(f"📁 Workspace: {workspace}", file=sys.stderr)

    # Add execution summary if it ran
    if execution_result:
        print(f"\n📊 Execution Summary:", file=sys.stderr)
        print(f"   Status: {execution_result.get('status', 'Unknown')}", file=sys.stderr)
        if execution_result.get('status') == 'complete':
            print(f"   Implementation: ✅ Complete", file=sys.stderr)
            if coverage_result:
                print(f"   Test Coverage: {coverage_result.get('final_coverage', 'N/A')}%", file=sys.stderr)
        elif execution_result.get('status') in ['blocked', 'incomplete', 'timeout']:
            print(f"   Implementation: ⚠️  Partial ({execution_result.get('progress_percent', 0)}%)", file=sys.stderr)
        else:
            print(f"   Implementation: ❌ Failed", file=sys.stderr)

    print(f"\nNext steps:", file=sys.stderr)
    if execution_result and execution_result.get('status') in ['blocked', 'incomplete', 'timeout']:
        print(f"1. Address execution issues (see above)", file=sys.stderr)
        print(f"2. Review the draft artifact", file=sys.stderr)
    else:
        print(f"1. Review the draft artifact and implementation", file=sys.stderr)
        print(f"2. Type 'approve' to move it to final location", file=sys.stderr)
        print(f"3. Or type 'reject: [reason]' to send back to experts", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Run expert-feedback workflow")
    parser.add_argument("--workspace", type=Path, required=True, help="Workspace path")
    parser.add_argument("--review-context", type=str, help="Review context for experts")
    parser.add_argument("--mode", type=str, default="review", choices=["review", "improve", "create"], help="Operation mode")
    parser.add_argument("--resume", action="store_true", help="Resume from last incomplete phase (skip completed phases)")
    parser.add_argument("--focus-files", nargs="*", help="Specific files to focus on")
    parser.add_argument("--focus-folders", nargs="*", help="Specific folders to focus on")
    parser.add_argument("--focus-context", type=str, help="Context about what changed in focus areas")
    parser.add_argument("--revert-to", type=str, help="Revert to previous state (e.g., iteration=2, phase=synthesizing, or iteration=2,phase=spawning_experts)")
    parser.add_argument("--dry-run", action="store_true", help="Preview revert changes without applying (use with --revert-to)")

    args = parser.parse_args()

    # Validate workspace
    if not args.workspace.exists():
        print(json.dumps({
            "error": f"Workspace not found: {args.workspace}",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    # Handle revert before running normal workflow
    if args.revert_to:
        result = handle_revert(
            workspace=args.workspace,
            revert_target=args.revert_to,
            dry_run=args.dry_run
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == "success" else 1)

    # Validate required arguments for normal workflow
    if not args.review_context:
        print(json.dumps({
            "error": "--review-context is required for normal workflow (not needed for --revert-to)",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    # Run workflow
    try:
        asyncio.run(run_workflow(
            workspace=args.workspace,
            review_context=args.review_context,
            mode=args.mode,
            resume=args.resume,
            focus_files=args.focus_files,
            focus_folders=args.focus_folders,
            focus_context=args.focus_context
        ))
    except KeyboardInterrupt:
        print("\n\n⏸️ Workflow interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
