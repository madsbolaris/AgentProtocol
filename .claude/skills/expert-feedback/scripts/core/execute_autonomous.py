#!/usr/bin/env python3
"""
Autonomous execution script for implementing approved artifacts/plans.

This script runs a continuous loop that prompts an agent to implement code autonomously,
handling questions through deferral, and continuing until the implementation is complete.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.conversational_session import ConversationalSession
from state.manager import StateManager
from execution_monitor import ExecutionMonitor
from questions.question_classifier import (
    extract_questions_from_response,
    add_classification_to_question,
    should_defer_question
)
from questions.deferred_questions_handler import (
    save_deferred_question,
    load_pending_questions,
    check_for_new_answers,
    load_and_process_answers
)
from config import get_config


async def run_autonomous_execution(
    workspace: Path,
    artifact_path: Path,
    mode: str,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Entry point for autonomous execution phase.

    Args:
        workspace: Workspace directory path
        artifact_path: Path to approved artifact/plan to implement
        mode: Generation mode (review/improve/create)
        correlation_id: Optional correlation ID for logging

    Returns:
        Execution result dictionary
    """
    config = get_config()

    if not config.enable_auto_execution:
        return {
            "status": "skipped",
            "message": "Autonomous execution disabled in config"
        }

    print(f"\n{'='*70}", file=sys.stderr)
    print("AUTONOMOUS EXECUTION PHASE", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    # Load artifact content
    if not artifact_path.exists():
        return {
            "status": "error",
            "error": f"Artifact not found: {artifact_path}"
        }

    artifact_content = artifact_path.read_text()

    # Initialize state and monitor
    state_manager = StateManager(workspace, correlation_id=correlation_id)
    monitor = ExecutionMonitor(workspace)
    monitor.start_execution()

    # Create or resume execution session
    try:
        session = ConversationalSession.load(
            agent_id="executor",
            workspace=workspace
        )
        print(f"📝 Resuming executor session (turn {session.turn_count + 1})...", file=sys.stderr)
    except ValueError:
        session = ConversationalSession(
            agent_type="executor",
            agent_id="executor",
            workspace=workspace
        )
        print("📝 Created new executor session", file=sys.stderr)

    # Update state
    state_manager.update_execution_progress(
        status="running",
        session_id=session.session_id
    )

    # Run continuous execution loop
    result = await continuous_execution_loop(
        session=session,
        workspace=workspace,
        artifact_content=artifact_content,
        mode=mode,
        state_manager=state_manager,
        monitor=monitor,
        max_iterations=config.execution_max_iterations,
        max_time_hours=config.execution_max_time_hours,
        correlation_id=correlation_id
    )

    # Update final state
    final_status = "completed" if result["status"] == "complete" else "failed"
    state_manager.update_execution_progress(
        status=final_status,
        iterations=monitor.metrics.iterations,
        steps_completed=monitor.metrics.steps_completed,
        files_modified=monitor.metrics.files_modified,
        progress_percent=monitor.get_progress_percent()
    )

    # Print final report
    print("\n" + monitor.generate_progress_report(), file=sys.stderr)

    return result


async def continuous_execution_loop(
    session: ConversationalSession,
    workspace: Path,
    artifact_content: str,
    mode: str,
    state_manager: StateManager,
    monitor: ExecutionMonitor,
    max_iterations: int = 50,
    max_time_hours: float = 8.0,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Continuously prompts agent to keep working until done or limits reached.

    Args:
        session: Conversational session for executor agent
        workspace: Workspace path
        artifact_content: Content of artifact to implement
        mode: Generation mode
        state_manager: State manager
        monitor: Execution monitor
        max_iterations: Maximum execution iterations
        max_time_hours: Maximum execution time in hours
        correlation_id: Optional correlation ID

    Returns:
        Execution result dictionary
    """
    config = get_config()
    start_time = time.time()
    iteration = 0

    # Build initial context
    context = {
        "artifact_content": artifact_content,
        "recommendations": [],  # TODO: Load from state
        "mode": mode,
        "codebase_structure": _get_codebase_structure(workspace),
        "iteration_number": 1,
        "steps_completed": [],
        "files_modified": [],
        "deferred_questions_count": 0,
        "time_elapsed": "0m"
    }

    while iteration < max_iterations:
        iteration += 1
        monitor.increment_iteration()

        # Check time limit
        elapsed_hours = (time.time() - start_time) / 3600
        if elapsed_hours > max_time_hours:
            print(f"\n⏱️ Max time limit reached ({max_time_hours}h)", file=sys.stderr)
            return {
                "status": "timeout",
                "reason": "Maximum time exceeded",
                "iterations": iteration,
                "progress_percent": monitor.get_progress_percent(),
                "steps_completed": monitor.metrics.steps_completed,
                "files_modified": monitor.metrics.files_modified
            }

        # Update context
        context["iteration_number"] = iteration
        context["time_elapsed"] = monitor.get_elapsed_time()

        # Determine which prompt to use
        if iteration == 1:
            prompt_template = "01-start-implementation.jinja2"
            print(f"\n🚀 Starting implementation (iteration {iteration})...", file=sys.stderr)
        else:
            # Check if user provided answers
            if check_for_new_answers(workspace):
                prompt_template = "03-refine-with-answers.jinja2"
                print(f"\n🔄 Refining with user answers (iteration {iteration})...", file=sys.stderr)

                # Load and process answers
                answers = load_and_process_answers(workspace)
                context["user_answers"] = answers
                context["progress_percent"] = monitor.get_progress_percent()

                # Update monitor
                for _ in answers:
                    monitor.add_answered_question()
            else:
                prompt_template = "02-continue-implementation.jinja2"
                print(f"\n⏭️  Continuing implementation (iteration {iteration})...", file=sys.stderr)
                context["next_steps"] = context.get("next_steps", [])

        # Send turn to agent
        try:
            response = await session.send_turn(
                prompt_template=prompt_template,
                context=context,
                timeout=900  # 15 minutes per turn
            )
        except Exception as e:
            print(f"\n❌ Agent call failed: {e}", file=sys.stderr)
            monitor.record_error(str(e))
            return {
                "status": "error",
                "error": f"Agent call failed: {e}",
                "iterations": iteration,
                "progress_percent": monitor.get_progress_percent()
            }

        # Parse response
        try:
            agent_output = json.loads(response["content"])
        except json.JSONDecodeError as e:
            print(f"\n⚠️ Could not parse agent response as JSON: {e}", file=sys.stderr)
            print(f"Response content preview: {response['content'][:200]}...", file=sys.stderr)
            # Try to extract status from text
            agent_output = _parse_text_response(response["content"])

        # Intercept and defer questions
        questions = agent_output.get("questions", [])
        if questions:
            deferred_count = intercept_and_defer_questions(
                questions=questions,
                workspace=workspace,
                iteration=iteration,
                agent_id="executor"
            )
            monitor.metrics.deferred_questions += deferred_count
            context["deferred_questions_count"] = monitor.metrics.deferred_questions

        # Update progress
        steps = agent_output.get("steps_completed", [])
        files = agent_output.get("files_modified", [])
        if steps or files:
            monitor.update_progress(
                steps_completed=steps,
                files_modified=files
            )

            # Update context for next iteration
            context["steps_completed"].extend(steps)
            for file in files:
                if file not in context["files_modified"]:
                    context["files_modified"].append(file)

        # Update state
        state_manager.update_execution_progress(
            status="running",
            iterations=iteration,
            steps_completed=monitor.metrics.steps_completed,
            files_modified=monitor.metrics.files_modified,
            deferred_questions_count=monitor.metrics.deferred_questions,
            progress_percent=monitor.get_progress_percent()
        )

        # Check status
        status = detect_agent_status(agent_output)

        if status == "done":
            print(f"\n✅ Agent reports implementation complete!", file=sys.stderr)

            # Run final validation
            print(f"\n🔍 Running final validation...", file=sys.stderr)
            validation_context = {
                **context,
                "iterations": iteration,
                "implementation_summary": agent_output
            }

            validation_response = await session.send_turn(
                prompt_template="04-final-validation.jinja2",
                context=validation_context,
                timeout=600  # 10 minutes for validation
            )

            try:
                validation_result = json.loads(validation_response["content"])
            except json.JSONDecodeError:
                validation_result = {"validation_status": "unknown"}

            return {
                "status": "complete",
                "iterations": iteration,
                "steps_completed": monitor.metrics.steps_completed,
                "files_modified": monitor.metrics.files_modified,
                "deferred_questions_count": monitor.metrics.deferred_questions,
                "validation": validation_result,
                "progress_percent": 100
            }

        elif status == "blocked":
            print(f"\n⏸️ Agent blocked - user input required", file=sys.stderr)
            return {
                "status": "blocked",
                "reason": agent_output.get("block_reason", "Agent requires user input"),
                "iterations": iteration,
                "progress_percent": monitor.get_progress_percent(),
                "deferred_questions": load_pending_questions(workspace)
            }

        # Status is "in_progress" - continue to next iteration
        context["next_steps"] = agent_output.get("next_steps", [])

        # Health check every N iterations
        if iteration % config.execution_health_check_interval == 0:
            health = monitor.check_implementation_health()
            if health["overall_status"] == "unhealthy":
                print(f"\n⚠️  Health check failed: {health['errors']}", file=sys.stderr)
                return {
                    "status": "failed",
                    "reason": "Health check failed",
                    "health": health,
                    "iterations": iteration
                }

        # Brief progress update
        print(f"   Steps: {len(steps)}, Files: {len(files)}, Progress: {monitor.get_progress_percent()}%", file=sys.stderr)

    # Max iterations reached
    print(f"\n⚠️ Max iterations reached ({max_iterations})", file=sys.stderr)
    return {
        "status": "incomplete",
        "reason": "Maximum iterations reached",
        "iterations": iteration,
        "progress_percent": monitor.get_progress_percent(),
        "steps_completed": monitor.metrics.steps_completed,
        "files_modified": monitor.metrics.files_modified
    }


def detect_agent_status(agent_response: Dict[str, Any]) -> str:
    """
    Determine if agent is done, needs to continue, or is blocked.

    Args:
        agent_response: Parsed agent response dictionary

    Returns:
        "done" | "in_progress" | "blocked"
    """
    # Check explicit status field
    if "status" in agent_response:
        return agent_response["status"]

    # Infer from content
    content = str(agent_response)

    done_indicators = [
        "implementation complete",
        "all steps finished",
        "ready for review",
        "no remaining tasks",
        "implementation is complete"
    ]

    blocked_indicators = [
        "cannot proceed without",
        "critical decision needed",
        "must have user input",
        "blocked on"
    ]

    content_lower = content.lower()

    # Check for blocking first (more specific)
    if any(indicator in content_lower for indicator in blocked_indicators):
        return "blocked"

    # Then check for done
    if any(indicator in content_lower for indicator in done_indicators):
        return "done"

    # Default to in_progress
    return "in_progress"


def intercept_and_defer_questions(
    questions: List[Dict[str, Any]],
    workspace: Path,
    iteration: int,
    agent_id: str
) -> int:
    """
    Intercept questions from agent and defer them.

    Args:
        questions: List of question dictionaries from agent
        workspace: Workspace path
        iteration: Current execution iteration
        agent_id: Agent identifier

    Returns:
        Number of questions deferred
    """
    deferred_count = 0

    for question in questions:
        # Classify question
        classified = add_classification_to_question(question)

        # Check if should defer
        if should_defer_question(classified):
            save_deferred_question(
                question=classified,
                workspace=workspace,
                iteration=iteration,
                agent_id=agent_id
            )
            deferred_count += 1

    if deferred_count > 0:
        print(f"   📝 Deferred {deferred_count} question(s)", file=sys.stderr)

    return deferred_count


def _get_codebase_structure(workspace: Path) -> str:
    """
    Get simplified codebase structure.

    Args:
        workspace: Workspace path

    Returns:
        Tree-like string representation
    """
    # TODO: Implement actual tree generation
    # For now, return placeholder
    return """
src/
  api/
  utils/
tests/
  unit/
  integration/
docs/
"""


def _parse_text_response(content: str) -> Dict[str, Any]:
    """
    Fallback parser for non-JSON responses.

    Args:
        content: Response content string

    Returns:
        Best-effort parsed response
    """
    # Try to extract status
    content_lower = content.lower()

    if "done" in content_lower or "complete" in content_lower:
        status = "done"
    elif "blocked" in content_lower:
        status = "blocked"
    else:
        status = "in_progress"

    return {
        "status": status,
        "steps_completed": [],
        "files_modified": [],
        "implementation_notes": content[:500]
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run autonomous execution")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--artifact", required=True, type=Path, help="Artifact path")
    parser.add_argument("--mode", required=True, choices=["review", "improve", "create"], help="Generation mode")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Run execution
    result = asyncio.run(run_autonomous_execution(
        workspace=args.workspace,
        artifact_path=args.artifact,
        mode=args.mode,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get("status") in ["complete", "skipped"] else 1)
