#!/usr/bin/env python3
"""
Consolidate feedback from multiple experts using Claude Agent SDK.

Instead of manual similarity matching, this spawns an agent to analyze
all feedback and produce consolidated recommendations with convergence metrics.

Usage:
    python3 consolidate-feedback.py --workspace /path --iteration 1
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from file_io.json_ops import load_json
from agent_logging.agent_logger import setup_agent_logger
from agents.spawn import AgentSpawnConfig, spawn_agent
# Caching removed - never worked in Claude Agent SDK (Issue #89)
from prompts.templates import render_template
from config import get_config, get_config_with_overrides
from state.manager import StateManager as WorkspaceStateManager
from ui.progress_tracker import ProgressTracker
from validation.validation import validate_synthesized_outputs, validate_or_raise
from file_io.workspace_utils import (
    WorkspacePaths
)

# Add .claude to path for sdk_auth
claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(claude_dir))
from sdk_auth import require_claude_auth

try:
    from claude_agent_sdk import query, ClaudeAgentOptions
except ImportError:
    print(json.dumps({
        "error": "claude-agent-sdk not installed",
        "message": "Please run: pip3 install claude-agent-sdk",
        "status": "error"
    }), file=sys.stderr)
    sys.exit(1)


def find_experts(workspace: Path, iteration: int) -> List[str]:
    """
    Find all experts who have provided feedback for this iteration.

    Supports both new structure (iteration-N/experts/) and old structure (flat files).
    """
    experts = []

    # Try new structure (iteration-N/experts/{expert}/state.json)
    paths = WorkspacePaths(workspace)
    expert_dir = paths.experts_dir(iteration)
    if expert_dir.exists():
        for subdir in expert_dir.iterdir():
            if subdir.is_dir():
                state_file = subdir / "state.json"
                if state_file.exists():
                    experts.append(subdir.name)

    return sorted(experts)


def build_synthesis_prompt(workspace: Path, iteration: int, use_refinement: bool = False) -> str:
    """
    Build synthesis prompt from Jinja2 template.

    Args:
        workspace: Workspace directory path
        iteration: Current iteration number
        use_refinement: If True and iteration > 1, use consolidate-refinement template (for session reuse)

    Returns:
        Rendered prompt string
    """
    # Find all experts who provided feedback
    experts = find_experts(workspace, iteration)

    if not experts:
        raise ValueError(f"No expert feedback found in {workspace} for iteration {iteration}")

    # Load state to get convergence target (Phase 5.2)
    state_manager = WorkspaceStateManager(workspace)
    convergence_target = 80  # default
    try:
        workspace_state = state_manager.load()
        convergence_target = workspace_state.convergence_target
    except Exception:
        pass  # Use default

    # Determine which template to use (Session-Preserved Architecture)
    # Map iterations to numbered prompts for clear conversation flow
    convergence_percent = 0
    try:
        workspace_state = state_manager.load()
        convergence_percent = workspace_state.convergence_percent
    except Exception:
        pass

    if iteration == 1:
        # Turn 1: Initial synthesis
        template_name = "synthesis/01-initial-synthesis.jinja2"
    elif iteration == 2:
        # Turn 2: Refine synthesis
        template_name = "synthesis/02-refine-synthesis.jinja2"
    elif iteration >= 3:
        # Turn 3+: Final synthesis (check if approaching finalization)
        if convergence_percent >= 60:  # Approaching convergence
            template_name = "synthesis/03-final-synthesis.jinja2"
        else:
            # Still need more refinement
            template_name = "synthesis/02-refine-synthesis.jinja2"
    else:
        # Fallback to legacy templates
        template_name = "synthesis/initial.jinja2"

    template_vars = {
        "iteration": iteration,
        "workspace": str(workspace),
        "experts": experts,
        "convergence_target": convergence_target  # Phase 5.2
    }

    # Load previous synthesis if this is iteration 2+
    if iteration > 1:
        paths = WorkspacePaths(workspace)
        prev_file = paths.synthesized_md(iteration - 1)

        # Session reuse is always enabled for iteration 2+ with numbered prompts
        if use_refinement:
            # Already set template_name above based on iteration
            pass

            # Load previous state for refinement context
            state_manager = WorkspaceStateManager(workspace)
            try:
                prev_state = state_manager.load()
                template_vars.update({
                    "previous_convergence": prev_state.convergence_percent,
                    "previous_consensus": prev_state.consensus_reached,
                    "previous_high_agreement": getattr(prev_state, 'high_agreement_count', 0),
                    "previous_partial_agreement": getattr(prev_state, 'partial_agreement_count', 0),
                    "previous_individual": getattr(prev_state, 'individual_count', 0)
                })
            except Exception:
                # Fall back to basic template if state loading fails
                template_name = "synthesis/initial.jinja2"

            # Load QA answers from previous iteration if they exist
            paths = WorkspacePaths(workspace)
            qa_file = paths.qa_answers_json(iteration - 1) if iteration > 1 else paths.qa_answers_json(iteration)
            if qa_file.exists():
                qa_answers = load_json(qa_file)
                template_vars["qa_answers"] = qa_answers.get("answers", [])  # Note: 'answers' not 'questions'
                # Logging happens in synthesize_feedback() after logger is set up

        # For non-refinement template, pass structured summary instead of full markdown
        # This reduces context from 40KB+ to ~2KB (67% reduction)
        if template_name == "synthesis/initial.jinja2" and prev_file.exists():
            try:
                # Load previous state for summary
                prev_state = state_manager.load()

                # Build compact summary with only essential information
                template_vars["previous_summary"] = {
                    "iteration": iteration - 1,
                    "convergence_percent": prev_state.convergence_percent,
                    "consensus_reached": prev_state.consensus_reached,
                    "high_agreement_count": getattr(prev_state, 'high_agreement_count', 0),
                    "partial_agreement_count": getattr(prev_state, 'partial_agreement_count', 0),
                    "individual_count": getattr(prev_state, 'individual_count', 0),
                    "convergence_trend": getattr(prev_state, 'convergence_trend', 'unknown')
                }
            except Exception as e:
                # Fall back to no summary if state loading fails
                if progress:
                    progress.log_warning(f"Could not load previous state for summary: {e}")
                template_vars["previous_summary"] = None

    # Render template with Jinja2
    prompt = render_template(template_name, **template_vars)

    return prompt


async def synthesize_feedback(
    workspace: Path,
    iteration: int,
    config: Any,
    progress: Optional[ProgressTracker] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Consolidate feedback using Claude Agent SDK with session reuse support."""
    start_time = time.time()

    # Setup workspace-specific logger
    logger = setup_agent_logger(workspace, "consolidation")
    logger.info(f"Starting synthesis for iteration {iteration}")

    # Use StateManager for type-safe state operations
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)

    # Update phase for web UI
    state_manager.set_phase("consolidating")

    # PHASE 0.2 & 0.3: Check if synthesis already complete using centralized state
    paths = WorkspacePaths(workspace)
    synthesized_file = paths.synthesized_md(iteration)
    questions_file = paths.questions_json(iteration)
    state_file = paths.state

    # Use centralized state manager to check phase completion (Phase 0.3)
    phase_name = f"consolidating_iteration_{iteration}"
    if state_manager.is_phase_complete(phase_name):
        logger.info(f"✅ Synthesis already complete for iteration {iteration} (from state)")
        if progress:
            progress.log_info(f"Synthesis already complete, skipping")

        # Get cached result from state
        cached_result = state_manager.get_phase_result(phase_name)
        if cached_result:
            duration_seconds = int(time.time() - start_time)
            cached_result["duration_seconds"] = duration_seconds
            cached_result["skipped"] = True
            logger.info(f"Returning cached synthesis result: {cached_result.get('convergence_percent')}% convergence")
            return cached_result

        # Fallback: result not cached but phase marked complete
        try:
            workspace_state = state_manager.load()
            duration_seconds = int(time.time() - start_time)

            return {
                "status": "complete",
                "iteration": iteration,
                "convergence_percent": workspace_state.convergence_percent,
                "consensus_reached": workspace_state.consensus_reached,
                "summary": workspace_state.to_dict().get("summary", ""),
                "questions_file": str(questions_file) if questions_file.exists() else None,
                "synthesized_file": str(synthesized_file) if synthesized_file.exists() else None,
                "state_file": str(state_file),
                "duration_seconds": duration_seconds,
                "tokens_used": 0,  # No new tokens used
                "session_id": workspace_state.synthesis_session_id,
                "skipped": True  # Indicate this was skipped
            }
        except Exception as e:
            logger.warning(f"Could not load existing state: {e}, will re-run consolidation")
            # Fall through to re-run consolidation

    # Check for existing synthesis session (User Issue 9)
    # Only reuse session for iteration 2+ (iteration 1 should always start fresh)
    session_id = None
    if config.reuse_synthesis_session and iteration > 1:
        try:
            workspace_state = state_manager.load()
            session_id = workspace_state.synthesis_session_id
            if session_id and progress:
                progress.log_info(f"Resuming synthesis session: {session_id[:8]}...")
        except Exception:
            pass  # No existing session

    transcript = None  # Initialize for exception handler
    try:
        # Find all experts who provided feedback
        experts = find_experts(workspace, iteration)

        # Load convergence target from state
        convergence_target = 80  # default
        try:
            workspace_state = state_manager.load()
            convergence_target = workspace_state.convergence_target
        except Exception:
            pass  # Use default

        # Load previous summary for iteration 2+ (for context)
        previous_summary = None
        qa_answers = None
        if iteration > 1:
            paths = WorkspacePaths(workspace)
            prev_file = paths.synthesized_md(iteration - 1)
            prev_state_file = paths.state

            # Load previous state for summary
            try:
                prev_state = state_manager.load()
                previous_summary = {
                    "iteration": iteration - 1,
                    "convergence_percent": prev_state.convergence_percent,
                    "consensus_reached": prev_state.consensus_reached,
                    "high_agreement_count": getattr(prev_state, 'high_agreement_count', 0),
                    "partial_agreement_count": getattr(prev_state, 'partial_agreement_count', 0),
                    "individual_count": getattr(prev_state, 'individual_count', 0),
                    "convergence_trend": getattr(prev_state, 'convergence_trend', 'unknown')
                }
            except Exception:
                pass  # Fall back to no summary

            # Load QA answers from previous iteration
            paths = WorkspacePaths(workspace)
            qa_file = paths.qa_answers_json(iteration - 1)
            if qa_file.exists():
                qa_data = load_json(qa_file)
                qa_answers = qa_data.get("answers", [])

        # Build synthesis prompt (caching removed - never worked in Claude Agent SDK)
        use_refinement = iteration > 1
        template_name = "synthesis/02-refine-synthesis.jinja2" if use_refinement else "synthesis/01-initial-synthesis.jinja2"

        synthesis_prompt = render_template(
            template_name,
            workspace=str(workspace),
            iteration=iteration,
            experts=experts,
            previous_summary=previous_summary,
            qa_answers=qa_answers or [],
            convergence_target=convergence_target
        )

        # Log prompt details
        logger.info(f"Context size: {len(synthesis_prompt)} characters")
        logger.info(f"Template: {'refinement' if use_refinement else 'initial'}")

        if progress:
            progress.synthesis_started(iteration, len(experts))
            if use_refinement:
                progress.log_info("Using synthesis refinement template with caching")

        # Expected file already calculated at the beginning (Phase 0.2)
        expected_file = synthesized_file
        logger.info(f"File watcher monitoring: {expected_file}")
        logger.info(f"File exists at start: {expected_file.exists()}")

        # Spawn synthesis agent using unified function
        spawn_config = AgentSpawnConfig(
            agent_type="consolidation",
            agent_name="consolidation",
            prompt=synthesis_prompt,
            workspace=workspace,
            session_id=session_id if config.reuse_synthesis_session else None,
            enable_session_reuse=config.reuse_synthesis_session,
            expected_files=[expected_file],
            enable_file_watching=True,
            file_watch_delay_seconds=5,  # Give agent time to start before checking
            enable_transcript_logging=config.enable_transcript_logging,
            allowed_tools=["Read", "Write", "Glob", "Grep"],
            timeout_seconds=config.expert_timeout_seconds,
            logger=logger  # Pass workspace-specific logger for prompt logging
        )

        result = await spawn_agent(spawn_config)

        # Save session ID for reuse if captured (User Issue 9)
        if result.session_id and config.reuse_synthesis_session:
            try:
                state_manager.set_synthesis_session(result.session_id)
                # Also store by iteration for precise revert support
                state_manager.update_synthesis_session_for_iteration(iteration, result.session_id)
            except Exception as e:
                if progress:
                    progress.log_warning(f"Could not save synthesis session ID: {e}")

        # Check if agent succeeded
        if result.status != "complete":
            return {
                "error": result.error or f"Agent failed with status: {result.status}",
                "status": "error",
                "workspace": str(workspace),
                "iteration": iteration,
                "duration_seconds": result.duration_seconds
            }

        input_tokens = result.input_tokens
        output_tokens = result.output_tokens

        # After agent completes, check if consolidated markdown was created
        # Files already defined at the beginning (Phase 0.2)

        # Check if consolidated markdown was created
        if not synthesized_file.exists():
            return {
                "error": f"Synthesis agent did not create consolidated markdown: {synthesized_file}",
                "status": "error",
                "workspace": str(workspace),
                "iteration": iteration
            }

        # Parse consolidated markdown to update state.json and generate questions.json
        try:
            from parsers.synthesized import parse_and_update
            parse_and_update(
                markdown_path=synthesized_file,
                workspace=workspace,
                iteration=iteration
            )
            if progress:
                progress.log_info("✅ Parsed consolidated markdown → state.json + questions.json")
        except Exception as e:
            # Parsing failed, but markdown exists
            if progress:
                progress.log_warning(f"⚠️ Failed to parse consolidated markdown: {e}")
                progress.log_warning(f"   Markdown file exists at: {synthesized_file}")
            return {
                "error": f"Consolidated markdown parsing failed: {e}",
                "status": "error",
                "workspace": str(workspace),
                "iteration": iteration,
                "synthesized_file": str(synthesized_file)
            }

        # Load state.json (should have been updated by parser)
        if not state_file.exists():
            return {
                "error": "Markdown parsing did not update state.json",
                "status": "error",
                "workspace": str(workspace),
                "iteration": iteration
            }

        # Use StateManager to load state
        workspace_state = state_manager.load()

        # Deduplicate questions (remove already-answered questions) - Issue #BUG-DUPLICATION
        if iteration > 1 and questions_file.exists():
            logger.info("Deduplicating questions against previous answers...")
            try:
                import subprocess
                dedup_result = subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).parent / "deduplicate_questions.py"),
                        "--questions-file", str(questions_file),
                        "--workspace", str(workspace),
                        "--iteration", str(iteration)
                    ],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"✅ Deduplicated questions")
                # Log summary from stdout
                if progress:
                    for line in dedup_result.stdout.split('\n'):
                        if 'Duplicates removed:' in line or 'Unique questions:' in line:
                            progress.log_info(line.strip())
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ Question deduplication failed: {e}")
                logger.warning(f"Continuing with unfiltered questions...")
                # Don't fail synthesis if deduplication fails
            except Exception as e:
                logger.warning(f"⚠️ Question deduplication error: {e}")

        # Validate question count (removed 10-question limit per Issue 5)
        # NOTE: We still validate against schema but schema should not have maxItems
        if questions_file.exists():
            questions_data = load_json(questions_file)
            question_count = len(questions_data.get("questions", []))

            if progress and question_count > 0:
                progress.log_info(f"Synthesis produced {question_count} questions")

        # Validate consolidated outputs using new validation module
        if config.verbose_logging and progress:
            progress.log_info("Validating consolidated outputs...")

        validation_errors = validate_synthesized_outputs(workspace, iteration)
        has_errors = any(error_list for error_list in validation_errors.values())

        if has_errors and progress:
            progress.log_warning("Validation issues found in consolidated outputs:")
            for file_type, error_list in validation_errors.items():
                if error_list:
                    progress.log_warning(f"  {file_type}: {', '.join(error_list)}")

        duration_seconds = int(time.time() - start_time)

        # Token tracking now handled by spawn_agent() with automatic fallback
        total_tokens = input_tokens + output_tokens

        # Update token metrics in state
        if total_tokens > 0:
            cost = result.accurate_cost if hasattr(result, 'accurate_cost') else 0.0
            state_manager.update_token_metrics(total_tokens, cost)

        # Record iteration summary for context propagation (Context Gap Fix 1.1)
        try:
            expert_summaries = {}
            iteration_dir = workspace / f"iteration-{iteration}" / "experts"
            if iteration_dir.exists():
                for expert_file in iteration_dir.glob("state-*.json"):
                    expert_name = expert_file.stem.replace("state-", "")
                    try:
                        expert_data = load_json(expert_file)
                        expert_summaries[expert_name] = {
                            "dx_rating": expert_data.get("dx_rating", {}).get("stars", 0),
                            "concerns_count": len(expert_data.get("concerns", [])),
                            "top_concern": expert_data.get("concerns", [{}])[0].get("title", "None") if expert_data.get("concerns") else "None",
                            "recommendations_count": len(expert_data.get("recommendations", []))
                        }
                    except Exception as e:
                        logger.warning(f"Could not load summary for {expert_name}: {e}")

            # Record iteration summary in state for next iteration's context
            if expert_summaries:
                state_manager.record_iteration_summary(
                    iteration=iteration,
                    convergence_percent=workspace_state.convergence_percent,
                    agreement_breakdown={
                        "high": workspace_state.high_agreement,
                        "partial": workspace_state.partial_agreement,
                        "low": workspace_state.low_agreement
                    },
                    expert_summaries=expert_summaries
                )
                logger.info(f"Recorded iteration {iteration} summary for {len(expert_summaries)} experts")
        except Exception as e:
            logger.warning(f"Could not record iteration summary: {e}")
            # Don't fail synthesis if we can't record summary

        # Log completion
        logger.info(f"Synthesis completed in {duration_seconds}s")
        logger.info(f"Total tokens: {total_tokens} (input: {input_tokens}, output: {output_tokens})")
        logger.info(f"Convergence: {workspace_state.convergence_percent}%")
        logger.info(f"Consensus: {workspace_state.consensus_reached}")

        if progress:
            progress.synthesis_complete(
                workspace_state.convergence_percent,
                workspace_state.consensus_reached,
                total_tokens
            )

        result_dict = {
            "status": "complete",
            "iteration": iteration,
            "convergence_percent": workspace_state.convergence_percent,
            "consensus_reached": workspace_state.consensus_reached,
            "summary": workspace_state.to_dict().get("summary", ""),
            "questions_file": str(questions_file) if questions_file.exists() else None,
            "synthesized_file": str(synthesized_file) if synthesized_file.exists() else None,
            "state_file": str(state_file),
            "duration_seconds": duration_seconds,
            "tokens_used": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "session_id": result.session_id or session_id
        }

        # Mark phase complete for future runs (Phase 0.3)
        phase_name = f"consolidating_iteration_{iteration}"
        try:
            state_manager.mark_phase_complete(phase_name, result_dict)
            logger.info(f"Marked phase '{phase_name}' as complete in state")
        except Exception as e:
            logger.warning(f"Could not mark phase complete: {e}")
            # Don't fail the whole operation if we can't mark it complete

        # Update phase for web UI (questions phase comes next)
        state_manager.set_phase("questions")

        return result_dict

    except Exception as e:
        duration_seconds = int(time.time() - start_time)
        logger.error(f"Synthesis failed after {duration_seconds}s: {e}", exc_info=True)

        if transcript:
            transcript.log_error(str(e))
        return {
            "error": str(e),
            "status": "error",
            "workspace": str(workspace),
            "iteration": iteration,
            "duration_seconds": duration_seconds
        }


def main():
    parser = argparse.ArgumentParser(description="Consolidate expert feedback")
    parser.add_argument("--workspace", required=True, help="Workspace directory path")
    parser.add_argument("--iteration", type=int, required=True, help="Iteration number")
    parser.add_argument("--correlation-id", dest="correlation_id", default=None,
                       help="Correlation ID for end-to-end workflow tracing")

    args = parser.parse_args()

    # Setup authentication and unset CLAUDECODE for nested execution
    require_claude_auth(verbose=True)

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(json.dumps({
            "error": f"Workspace not found: {workspace}",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    # Load configuration (with optional workspace-specific overrides)
    config = get_config()
    state_manager = WorkspaceStateManager(workspace, correlation_id=args.correlation_id)

    if state_manager.exists():
        try:
            workspace_state = state_manager.load()
            if workspace_state.convergence_target != config.convergence_target:
                # Use workspace-specific convergence target
                config = get_config_with_overrides(convergence_target=workspace_state.convergence_target)
        except Exception:
            pass  # Use default config

    # Initialize progress tracker (estimate 1 "expert" for consolidation)
    progress = ProgressTracker(1, workspace)

    # Run async function
    result = asyncio.run(synthesize_feedback(workspace, args.iteration, config, progress, correlation_id=args.correlation_id))

    # Output JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
