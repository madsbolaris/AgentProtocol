#!/usr/bin/env python3
"""
Spawn multiple experts in parallel using asyncio.

Usage:
    python3 spawn-all-experts.py --experts typescript python dx --review-context "..." --workspace /path --iteration 1
    python3 spawn-all-experts.py --experts typescript python --review-context "..." --workspace /path --iteration 2 --qa-answers qa-answers.json
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from file_io.json_ops import load_json, save_json
from state.operations import update_state_atomic
from agent_logging.token_tracker import extract_usage_from_sdk_result
from agent_logging.agent_logger import setup_agent_logger
from agents.spawn import AgentSpawnConfig, spawn_agent
# Caching removed - never worked in Claude Agent SDK (Issue #89)
from prompts.templates import (
    load_expert_info,
    build_expert_prompt,
    build_refinement_prompt
)
from core.test_control import inject_test_control
from agents.conversational_session import (
    ConversationalSession,
    get_next_prompt_name
)
from agents.session_lifecycle import SessionManager
from config import get_config, get_config_with_overrides
from state.manager import StateManager as WorkspaceStateManager, WorkspaceState
from ui.progress_tracker import ProgressTracker
from validation.validation import validate_expert_outputs, validate_all_experts, get_validation_summary
from file_io.workspace_utils import WorkspacePaths
from analysis.iteration_diff import generate_iteration_diff  # Context Gap Fix 1.2
from parsers.expert_review import parse_expert_review

# Add .claude to path
claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(claude_dir))
from sdk_auth import require_claude_auth

# Phase 1.3: Accurate cost calculation
# sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# from expert_feedback.core.cost import TokenUsage, calculate_cost

try:
    from claude_agent_sdk import query, ClaudeAgentOptions
except ImportError:
    print(json.dumps({
        "error": "claude-agent-sdk not installed",
        "message": "Please run: pip3 install claude-agent-sdk",
        "status": "error"
    }), file=sys.stderr)
    sys.exit(1)


def _load_iteration_context(
    workspace: Path,
    current_iteration: int,
    expert_name: str,
    state_manager: WorkspaceStateManager
) -> Dict[str, Any]:
    """
    Load all context needed for expert refinement in iteration 2+ (Context Gap Fix 1.1).

    Args:
        workspace: Workspace path
        current_iteration: Current iteration number
        expert_name: Name of the expert
        state_manager: StateManager instance

    Returns:
        Dictionary with:
        - consolidated_questions: Questions from synthesis
        - convergence_data: Convergence metrics and trends
        - other_experts: Summaries of peer expert reviews
        - previous_dx_rating: This expert's DX rating from iteration 1
    """
    logger = logging.getLogger(__name__)

    context = {
        "consolidated_questions": [],
        "convergence_data": None,
        "other_experts": [],
        "previous_dx_rating": None
    }

    if current_iteration == 1:
        return context  # No context for iteration 1

    state = state_manager.load()

    # Load previous iteration summary
    if state.iteration_history:
        prev_iteration = current_iteration - 1
        prev_summary = next(
            (h for h in state.iteration_history if h["iteration"] == prev_iteration),
            None
        )

        if prev_summary:
            # Convergence data with trend analysis
            context["convergence_data"] = {
                "convergence_percent": prev_summary["convergence_percent"],
                "target": state.convergence_target,
                "high_agreement": prev_summary["high_agreement"],
                "partial_agreement": prev_summary["partial_agreement"],
                "low_agreement": prev_summary["low_agreement"],
            }

            # Other experts' summaries (exclude current expert)
            context["other_experts"] = [
                {"name": name, **summary}
                for name, summary in prev_summary.get("expert_summaries", {}).items()
                if name != expert_name
            ]

            # This expert's previous DX rating
            if expert_name in prev_summary.get("expert_summaries", {}):
                context["previous_dx_rating"] = prev_summary["expert_summaries"][expert_name].get("dx_rating")

    # Load consolidated questions from previous iteration
    prev_questions_file = workspace / f"iteration-{current_iteration - 1}" / "questions.json"
    if prev_questions_file.exists():
        try:
            questions_data = load_json(prev_questions_file)
            context["consolidated_questions"] = questions_data.get("questions", [])
        except Exception as e:
            logger.warning(f"Could not load consolidated questions: {e}")

    # Generate iteration diff showing what changed (Context Gap Fix 1.2)
    try:
        iteration_diff = generate_iteration_diff(
            workspace=workspace,
            expert_name=expert_name,
            current_iteration=current_iteration,
            state_manager=state_manager
        )
        context["iteration_diff"] = iteration_diff
        logger.info(f"Generated iteration diff for {expert_name}: {len(iteration_diff)} sections")
    except Exception as e:
        logger.warning(f"Could not generate iteration diff: {e}")
        context["iteration_diff"] = {}

    logger.info(
        f"Loaded iteration context for {expert_name}: "
        f"convergence_data={'present' if context['convergence_data'] else 'absent'}, "
        f"other_experts={len(context['other_experts'])}, "
        f"questions={len(context['consolidated_questions'])}, "
        f"iteration_diff={'present' if context.get('iteration_diff') else 'absent'}"
    )

    return context


async def spawn_expert_with_timeout(
    expert_name: str,
    review_context: str,
    workspace: str,
    iteration: int,
    progress: ProgressTracker,
    config: Any,
    session_id: Optional[str] = None,
    qa_answers_path: Optional[str] = None,
    focus_files: Optional[List[str]] = None,
    focus_folders: Optional[List[str]] = None,
    focus_context: Optional[str] = None,
    correlation_id: Optional[str] = None,
    state_manager: Optional[WorkspaceStateManager] = None,  # Context Gap Fix 1.1
    test_control: Optional[Dict[str, Any]] = None  # Test control for deterministic recordings
) -> Dict[str, Any]:
    """
    Spawn or resume a single expert using unified spawn_agent() system.

    This wraps the expert execution with:
    - Unified spawn_agent() call
    - Progressive timeout warnings (at 10 min, then every 1 min)
    - Proper session management
    """
    start_time = time.time()

    # Setup logger
    logger = setup_agent_logger(Path(workspace), f"expert-{expert_name}")
    logger.info(f"Starting expert {expert_name} for iteration {iteration}")
    if session_id:
        logger.info(f"Resuming session: {session_id[:8]}...")
    if qa_answers_path:
        logger.info(f"QA answers provided: {qa_answers_path}")

    # Build expert prompt
    workspace_path = Path(workspace)

    # Load QA answers if provided
    qa_answers = None
    if qa_answers_path:
        try:
            qa_answers_file = workspace_path / qa_answers_path
            if qa_answers_file.exists():
                qa_answers = load_json(qa_answers_file)
        except Exception as e:
            logger.warning(f"Failed to load QA answers: {e}")

    # Load expert info (needed for both initial and refinement)
    expert_info = load_expert_info(expert_name)

    # Build prompt based on iteration
    if iteration == 1:
        # Initial expert review prompt
        prompt = build_expert_prompt(
            expert_name=expert_name,
            expert_info=expert_info,
            review_context=review_context,
            workspace=str(workspace_path),
            iteration=iteration,
            focus_files=focus_files,
            focus_folders=focus_folders,
            focus_context=focus_context
        )
    else:
        # Refinement prompt for iterations 2+ WITH iteration context (Context Gap Fix 1.1)
        # Load iteration context from StateManager
        if state_manager:
            iteration_context = _load_iteration_context(
                workspace_path,
                iteration,
                expert_name,
                state_manager
            )
        else:
            # Fallback if state_manager not provided (backward compatibility)
            logger.warning("state_manager not provided, iteration context will be empty")
            iteration_context = {
                "consolidated_questions": [],
                "convergence_data": None,
                "other_experts": [],
                "previous_dx_rating": None
            }

        prompt = build_refinement_prompt(
            qa_answers=qa_answers,
            expert_name=expert_name,
            workspace=str(workspace_path),
            iteration=iteration,
            synthesized_questions=iteration_context["consolidated_questions"],
            convergence_data=iteration_context["convergence_data"]
        )

    # Inject test controls if in recording mode
    prompt = inject_test_control(prompt, test_control)

    # Get expected output file
    expected_review_file = workspace_path / f"iteration-{iteration}" / "experts" / f"review-{expert_name}.md"

    # Create spawn config
    spawn_config = AgentSpawnConfig(
        agent_type="expert",
        agent_name=expert_name,
        prompt=prompt,
        workspace=workspace_path,
        session_id=session_id,
        enable_session_reuse=True,
        expected_files=[expected_review_file],
        enable_file_watching=True,
        file_watch_delay_seconds=5,
        enable_transcript_logging=config.enable_transcript_logging,
        allowed_tools=["Read", "Grep", "Glob", "Write", "Bash"],
        timeout_seconds=config.expert_timeout_seconds,
        logger=logger,  # Pass workspace-specific logger for prompt logging
        correlation_id=correlation_id  # Phase 4: Pass correlation ID for end-to-end tracing
    )

    async def timeout_monitor():
        """Monitor elapsed time and send progressive warnings."""
        warning_sent_at_first = False
        last_warning_time = 0

        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            elapsed = time.time() - start_time

            # First warning at configured time (default 10 minutes)
            if elapsed >= config.expert_warning_first and not warning_sent_at_first:
                warning_sent_at_first = True
                minutes_elapsed = int(elapsed / 60)
                progress.expert_timeout_warning(expert_name, minutes_elapsed)

            # Subsequent warnings every interval (default 1 minute)
            elif warning_sent_at_first and elapsed - last_warning_time >= config.expert_warning_interval:
                last_warning_time = elapsed
                remaining = config.expert_timeout_seconds - elapsed
                minutes_remaining = int(remaining / 60)
                if minutes_remaining >= 0:
                    progress.expert_timeout_warning(expert_name, minutes_elapsed=int(elapsed / 60), minutes_remaining=minutes_remaining)

    # Start monitoring task
    monitor_task = asyncio.create_task(timeout_monitor())

    try:
        # Spawn agent using unified system
        result = await spawn_agent(spawn_config)

        # Cancel monitor task on success
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        # Log completion
        logger.info(f"Expert completed in {result.duration_seconds}s with status: {result.status}")
        if result.tokens_used > 0:
            logger.info(f"Tokens used: {result.tokens_used} (input: {result.input_tokens}, output: {result.output_tokens})")

        # Parse markdown review to JSON if expert completed successfully
        if result.status == "complete" and expected_review_file.exists():
            try:
                output_dir = expected_review_file.parent
                parse_expert_review(
                    markdown_path=expected_review_file,
                    output_dir=output_dir,
                    expert_name=expert_name,
                    iteration=iteration,
                    workspace=Path(workspace) if iteration > 1 else None
                )
                logger.info(f"Successfully parsed review to JSON: state-{expert_name}.json")
            except Exception as e:
                logger.error(f"Failed to parse expert review to JSON: {e}")
                # Don't fail the expert if parsing fails - synthesis can still use markdown

        # Return result in expected format
        return {
            "expert": expert_name,
            "status": result.status,
            "duration": result.duration_seconds,
            "duration_seconds": result.duration_seconds,
            "tokens_used": result.tokens_used,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "accurate_cost": result.accurate_cost,
            "session_id": result.session_id,
            "output_file": str(expected_review_file) if expected_review_file.exists() else None,
            "error": result.error
        }

    except asyncio.TimeoutError:
        # Cancel monitor task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        timeout_minutes = int(config.expert_timeout_seconds / 60)
        logger.error(f"Expert timed out after {timeout_minutes} minutes")
        progress.expert_timeout(expert_name)

        # Update state with timeout status
        state_manager_timeout = WorkspaceStateManager(workspace_path)
        state_manager_timeout.update_expert_progress(expert_name, "timeout")

        return {
            "expert": expert_name,
            "status": "timeout",
            "error": f"Expert exceeded timeout of {config.expert_timeout_seconds} seconds",
            "duration_seconds": int(time.time() - start_time)
        }

    except Exception as e:
        # Cancel monitor task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        # Print full traceback to stderr for debugging
        import traceback
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"EXPERT FAILURE TRACEBACK for {expert_name}:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(f"{'='*80}\n", file=sys.stderr)

        logger.error(f"Expert failed with exception: {e}", exc_info=True)
        return {
            "expert": expert_name,
            "status": "error",
            "error": str(e),
            "duration_seconds": int(time.time() - start_time)
        }


async def spawn_expert_async(
    expert_name: str,
    review_context: str,
    workspace: str,
    iteration: int,
    progress: ProgressTracker,
    config: Any,
    session_id: Optional[str] = None,
    qa_answers_path: Optional[str] = None,
    focus_files: Optional[List[str]] = None,
    focus_folders: Optional[List[str]] = None,
    focus_context: Optional[str] = None,
    correlation_id: Optional[str] = None,
    test_control: Optional[Dict[str, Any]] = None  # Test control for deterministic recordings
) -> Dict[str, Any]:
    """Spawn or resume a single expert with progress tracking and timeout."""
    progress.expert_started(expert_name)

    # ADD THIS: Update state to show expert is running
    state_manager = WorkspaceStateManager(Path(workspace))
    state_manager.update_expert_progress(
        expert_name,
        "running",
        {"start_time": datetime.now().astimezone().isoformat()}
    )

    result = await spawn_expert_with_timeout(
        expert_name,
        review_context,
        workspace,
        iteration,
        progress,
        config,
        session_id,
        qa_answers_path,
        focus_files,
        focus_folders,
        focus_context,
        correlation_id=correlation_id,
        state_manager=state_manager,  # Context Gap Fix 1.1: Pass state_manager for iteration context
        test_control=test_control  # Test control for deterministic recordings
    )

    # DEBUG: Log what spawn_expert_with_timeout returned
    progress.log_info(f"DEBUG spawn_expert_async: {expert_name} returned status={result.get('status')}, session_id={result.get('session_id', 'MISSING')[:12] if result.get('session_id') else 'NONE'}")

    # Log completion
    if result.get("status") == "complete":
        duration = result.get("duration_seconds", 0)
        tokens = result.get("tokens_used", 0)
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)
        accurate_cost = result.get("accurate_cost", 0.0)

        progress.expert_completed(
            expert_name,
            duration,
            tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            accurate_cost=accurate_cost
        )

        # ADD THIS: Update state with completion metadata
        state_manager.update_expert_progress(
            expert_name,
            "complete",
            {
                "duration_seconds": duration,
                "total_tokens": tokens,
                "end_time": datetime.now().astimezone().isoformat()
            }
        )
    elif result.get("status") == "error":
        progress.expert_failed(expert_name, result.get("error", "Unknown error"))

        # ADD THIS: Update state with error status
        state_manager.update_expert_progress(expert_name, "error")
    elif result.get("status") == "timeout":
        # Already logged by timeout handler
        pass
    elif result.get("status") == "cancelled":
        progress.expert_cancelled(expert_name, result.get("error", "Unknown reason"))

    return result


async def spawn_all_experts(
    experts: List[str],
    review_context: str,
    workspace: str,
    iteration: int,
    state_path: Path,
    config: Any,
    progress: ProgressTracker,
    qa_answers_path: Optional[str] = None,
    focus_files: Optional[List[str]] = None,
    focus_folders: Optional[List[str]] = None,
    focus_context: Optional[str] = None,
    correlation_id: Optional[str] = None,
    test_control: Optional[Dict[str, Any]] = None  # Test control for deterministic recordings
) -> Dict[str, Any]:
    """Spawn all experts in parallel with lifecycle management, timeout, and progress tracking."""

    # Use StateManager for type-safe state operations
    state_manager = WorkspaceStateManager(Path(workspace), correlation_id=correlation_id)

    # Load state to check for existing sessions
    state = {}
    expert_sessions = {}  # Maps expert_id -> SDK session_id
    conversation_sessions = {}  # Maps expert_id -> ConversationalSession object

    if state_path.exists():
        workspace_state = state_manager.load()
        expert_sessions = workspace_state.expert_sessions

        # If iteration > 1, load ConversationalSession objects for resumption
        if iteration > 1:
            for expert in experts:
                if expert in expert_sessions:
                    try:
                        conv_session = ConversationalSession.load(expert, Path(workspace))
                        conversation_sessions[expert] = conv_session
                    except ValueError:
                        # Session not found, will create new one
                        pass

    # Get session manager for cleanup tracking
    session_mgr = SessionManager.get_instance()

    # Show session start
    progress.session_started()

    # Wrapper to update state immediately when expert completes
    async def spawn_and_update_state(expert: str, session_id: Optional[str]):
        """Spawn expert and update state immediately upon completion."""

        # Determine if we're continuing a conversation
        conv_session = conversation_sessions.get(expert)
        is_continuation = conv_session is not None

        # Get turn number for this expert
        turn = conv_session.turn_count + 1 if conv_session else 1

        result = await spawn_expert_async(
            expert,
            review_context,
            workspace,
            iteration,
            progress,
            config,
            session_id,
            qa_answers_path,
            focus_files,
            focus_folders,
            focus_context,
            correlation_id=correlation_id,
            test_control=test_control
        )

        # Update ConversationalSession with result
        if result.get("status") == "complete" and result.get("session_id"):
            if not conv_session:
                # Create new session tracking
                conv_session = ConversationalSession("expert", expert, Path(workspace))

            # Update session with turn info
            conv_session.session_id = result["session_id"]
            conv_session.turn_count = turn

            # Determine which prompt was used
            prompt_used = get_next_prompt_name("expert", iteration)

            # Save session ID to state.json
            conv_session._save_session_id()

        # Update state immediately (progressive updates for web UI)
        if state_path.exists() and result.get("expert"):
            try:
                # Build result dict with basic data
                expert_result = {
                    "status": result.get("status"),
                    "total_tokens": result.get("tokens_used", 0),
                    "duration_seconds": result.get("duration_seconds", 0),
                    "iteration": iteration,
                    # ADD THESE:
                    "start_time": result.get("start_time"),
                    "end_time": result.get("end_time"),
                    "cost": result.get("accurate_cost", 0.0)  # Use accurate cost from spawn result
                }

                # If expert completed successfully, read rich analysis data from state file
                if result.get("status") == "complete":
                    expert_state_file = Path(workspace) / f"iteration-{iteration}" / "experts" / expert / "state.json"
                    if expert_state_file.exists():
                        try:
                            expert_data = json.loads(expert_state_file.read_text())
                            expert_result.update({
                                "dx_rating": expert_data.get("dx_rating", {}),
                                "concerns_count": len(expert_data.get("concerns", [])),
                                "recommendations_count": len(expert_data.get("recommendations", [])),
                                "questions_count": len(expert_data.get("questions", [])),
                                "strengths_count": len(expert_data.get("strengths", []))
                            })
                        except Exception as e:
                            progress.log_warning(f"Could not read state file for {expert}: {e}")

                state_manager.add_expert_result(result["expert"], expert_result)
            except Exception as e:
                # Don't fail expert if state update fails
                progress.log_warning(f"Failed to update state for {expert}: {e}")

        # DEBUG: Log what we're returning from spawn_and_update_state
        progress.log_info(f"DEBUG spawn_and_update_state: returning {expert} with status={result.get('status')}, session_id={result.get('session_id', 'MISSING')[:12] if result.get('session_id') else 'NONE'}")

        return result

    # Create tasks for all experts
    tasks = []
    for expert in experts:
        session_id = expert_sessions.get(expert)

        # Wrap each expert spawn with state update
        coro = spawn_and_update_state(expert, session_id)

        # Track the task for cleanup
        task = session_mgr.spawn_with_cleanup(coro)
        tasks.append(task)

    # Run all in parallel with proper exception handling
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        progress.log_warning("Expert spawning cancelled")
        return {
            "status": "cancelled",
            "experts": experts,
            "iteration": iteration,
            "success_count": 0,
            "error_count": len(experts),
            "results": [],
            "expert_sessions": {}
        }

    # Process results, handling exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Log the full exception details for debugging
            import traceback
            progress.log_error(f"Expert {experts[i]} raised exception:")
            progress.log_error(f"  Type: {type(result).__name__}")
            progress.log_error(f"  Message: {str(result)}")
            progress.log_error(f"  Traceback: {''.join(traceback.format_exception(type(result), result, result.__traceback__))}")
            processed_results.append({
                "expert": experts[i],
                "status": "error",
                "error": str(result)
            })
        else:
            processed_results.append(result)

    # Aggregate results
    success_count = sum(1 for r in processed_results if r.get("status") == "complete")
    error_count = sum(1 for r in processed_results if r.get("status") in ["error", "timeout"])
    cancelled_count = sum(1 for r in processed_results if r.get("status") == "cancelled")

    # DEBUG: Log what's in results
    progress.log_info(f"DEBUG: Processed {len(processed_results)} results")
    for r in processed_results:
        progress.log_info(f"  - {r.get('expert')}: status={r.get('status')}, session_id={r.get('session_id', 'NONE')[:12] if r.get('session_id') else 'NONE'}")

    # Extract and track session IDs
    new_sessions = {}
    for result in processed_results:
        session_id = result.get("session_id")
        if session_id is None:
            continue  # Expected for errors
        elif session_id == "":
            # Warn about suspicious empty session ID
            progress.log_warning(f"Expert {result['expert']} returned empty session_id")
            continue
        else:
            new_sessions[result["expert"]] = session_id
            session_mgr.track_session(session_id)

            # Update ConversationalSession tracking
            expert_id = result["expert"]
            conv_session = conversation_sessions.get(expert_id)
            if not conv_session:
                # Create session tracking if not exists
                conv_session = ConversationalSession("expert", expert_id, Path(workspace))
                conversation_sessions[expert_id] = conv_session

            # Update session metadata
            prompt_used = get_next_prompt_name("expert", iteration)
            conv_session.session_id = session_id
            conv_session.turn_count = iteration

            # Save conversation history
            conv_session._save_conversation_history()

    # Update state.json with captured session IDs using StateManager
    if state_path.exists():
        state_manager.update_sessions(new_sessions)

        # Also store sessions by iteration for precise revert support
        state_manager.update_expert_sessions_for_iteration(iteration, new_sessions)

        # Update token metrics (cumulative update after all complete)
        total_tokens = sum(r.get("tokens_used", 0) for r in processed_results)
        total_cost = sum(r.get("accurate_cost", 0.0) for r in processed_results)
        if total_tokens > 0:
            state_manager.update_token_metrics(total_tokens, total_cost)

        # Note: Expert results are now added progressively in spawn_and_update_state()
        # No need to update them here again

    # Validate expert outputs (non-blocking - just report issues)
    if config.verbose_logging and success_count > 0:
        progress.log_info("Validating expert outputs...")
        workspace_path = Path(workspace)
        completed_experts = [r["expert"] for r in processed_results if r.get("status") == "complete"]

        all_valid, validation_errors = validate_all_experts(
            workspace_path,
            iteration,
            completed_experts,
            raise_on_error=False
        )

        if not all_valid:
            progress.log_warning(f"Validation issues found in {len(validation_errors)} experts")
            if config.verbose_logging:
                progress.log_info(get_validation_summary(validation_errors))

    return {
        "status": "complete" if success_count > 0 else "error",
        "experts": experts,
        "iteration": iteration,
        "success_count": success_count,
        "error_count": error_count,
        "cancelled_count": cancelled_count,
        "results": processed_results,
        "expert_sessions": new_sessions
    }


def validate_expert_count(experts: List[str], config: Any) -> None:
    """
    Warn if expert count seems suboptimal (Phase 5.1).

    Args:
        experts: List of expert names
        config: Skill configuration
    """
    count = len(experts)

    if count < 3:
        print(f"⚠️  Warning: Only {count} expert(s). Consider adding more for better coverage.", file=sys.stderr)
        print(f"   Recommended: 5-7 experts for standard reviews", file=sys.stderr)
        print(f"   Tip: Include language SDKs, DX expert, and domain experts", file=sys.stderr)

    elif count > 12:
        estimated_cost = count * 0.20 * 2  # $0.20 per expert per iteration, 2 iterations
        print(f"⚠️  Warning: {count} experts may be excessive.", file=sys.stderr)
        print(f"   Estimated cost: ${estimated_cost:.2f} for 2 iterations", file=sys.stderr)
        print(f"   Consider: Do you need all these perspectives?", file=sys.stderr)
        print(f"   Tip: 5-7 experts is optimal for most reviews", file=sys.stderr)

    elif 7 <= count <= 12:
        estimated_cost = count * 0.20 * 2
        print(f"ℹ️  Note: {count} experts (comprehensive review mode)", file=sys.stderr)
        print(f"   Estimated cost: ${estimated_cost:.2f} for 2 iterations", file=sys.stderr)

    elif 3 <= count <= 6:
        estimated_cost = count * 0.20 * 2
        print(f"✓ {count} experts (standard review mode)", file=sys.stderr)
        print(f"   Estimated cost: ${estimated_cost:.2f} for 2 iterations", file=sys.stderr)


async def main_async(args) -> Dict[str, Any]:
    """Async main function with lifecycle management."""
    workspace = Path(args.workspace).resolve()
    paths = WorkspacePaths(workspace)
    state_path = paths.state

    # Load configuration (with optional overrides from state)
    config = get_config()

    # Validate expert count (Phase 5.1)
    validate_expert_count(args.experts, config)

    # Handle convergence target (Phase 5.2)
    convergence_target = args.convergence_target if args.convergence_target is not None else config.convergence_target

    # Check if state has custom convergence target or set new one
    if state_path.exists():
        state_manager = WorkspaceStateManager(workspace, correlation_id=args.correlation_id)
        try:
            workspace_state = state_manager.load()
            # Use existing convergence target unless explicitly overridden
            if args.convergence_target is None:
                convergence_target = workspace_state.convergence_target
            else:
                # Update state with new convergence target
                state_manager.update({"convergence_target": convergence_target})
                print(f"📊 Updated convergence target to {convergence_target}%", file=sys.stderr)
        except Exception:
            pass  # Use default config
    else:
        # For new workspace (iteration 1), store convergence target in state
        if args.iteration == 1 and convergence_target != config.convergence_target:
            print(f"📊 Using custom convergence target: {convergence_target}%", file=sys.stderr)

    # Apply convergence target to config
    if convergence_target != config.convergence_target:
        config = get_config_with_overrides(convergence_target=convergence_target)

    # Initialize progress tracker
    progress = ProgressTracker(len(args.experts), workspace)

    manager = SessionManager.get_instance()

    try:
        # Run expert spawning with progress tracking
        result = await spawn_all_experts(
            args.experts,
            args.review_context,
            str(workspace),
            args.iteration,
            state_path,
            config,
            progress,
            args.qa_answers,
            args.focus_files,
            args.focus_folders,
            args.focus_context,
            correlation_id=args.correlation_id
        )
        return result
    finally:
        # Cleanup sessions when done
        await manager.cleanup()


def main():
    require_claude_auth()

    parser = argparse.ArgumentParser(description="Spawn multiple experts in parallel")
    parser.add_argument("--experts", nargs="+", required=True,
                       help="Expert names to spawn")
    parser.add_argument("--review-context", dest="review_context",
                       help="Detailed context for review (paragraphs OK, include: what, why, problem, background)")
    parser.add_argument("--topic", dest="review_context",
                       help="(DEPRECATED: use --review-context) Topic to review")
    parser.add_argument("--workspace", required=True,
                       help="Workspace directory path")
    parser.add_argument("--iteration", type=int, required=True,
                       help="Iteration number")
    parser.add_argument("--qa-answers", help="Path to Q&A answers JSON (optional)")
    parser.add_argument("--focus-files", nargs="*",
                       help="Specific files to focus on")
    parser.add_argument("--focus-folders", nargs="*",
                       help="Specific folders to focus on")
    parser.add_argument("--focus-context",
                       help="Additional context about what to focus on")
    parser.add_argument("--convergence-target", type=int, default=None,
                       help="Custom convergence target percentage for this session (default: 80)")
    parser.add_argument("--correlation-id", dest="correlation_id", default=None,
                       help="Correlation ID for end-to-end workflow tracing")

    args = parser.parse_args()

    # Validate that either --review-context or --topic was provided
    if not args.review_context:
        parser.error("--review-context is required (or use deprecated --topic)")

    # Run with lifecycle management (signal handlers, cleanup)
    result = SessionManager.run_with_lifecycle(main_async(args))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
