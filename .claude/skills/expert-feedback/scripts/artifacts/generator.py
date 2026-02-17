#!/usr/bin/env python3
"""
Generate artifact from expert feedback using Claude Agent SDK.

Creates ADR (review mode) or Implementation Plan (improve/create modes) from expert recommendations.

Supports three modes:
- review: Generate ADR (Architecture Decision Record)
- improve: Generate Implementation Plan for improvements
- create: Generate Architecture & Implementation Plan (greenfield)

Usage:
    python3 generate_artifact.py --workspace /path --review-context "..." --mode review
    python3 generate_artifact.py --workspace /path --review-context "..." --mode improve
    python3 generate_artifact.py --workspace /path --review-context "..." --mode create
"""
import argparse
import asyncio
import json
import logging
import re
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent_logging.agent_logger import setup_agent_logger
from prompts.templates import render_template
from agents.spawn import AgentSpawnConfig, spawn_agent
# Note: load_json now blocks state.json access (Phase 1.4)
# Use StateManager instead for all state operations
from config import get_config
from state.manager import StateManager as WorkspaceStateManager
from core.test_control import inject_test_control
from file_io.json_ops import load_json
from file_io.workspace_utils import (
    get_artifact_path,
    WorkspacePaths,
    list_iterations
)

# Add .claude to path
claude_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(claude_dir))
from sdk_auth import require_claude_auth

try:
    from claude_agent_sdk import query, ClaudeAgentOptions
    import jinja2
except ImportError as e:
    print(json.dumps({
        "error": f"Missing dependency: {e}",
        "message": "Please run: pip3 install claude-agent-sdk jinja2",
        "status": "error"
    }), file=sys.stderr)
    sys.exit(1)


def merge_iterations(workspace: Path, expert: str, total_iterations: int) -> Dict:
    """Merge all iterations into complete review.

    For delta-based refinements, this reconstructs the full review by:
    1. Loading the base review from iteration 1
    2. Applying each delta from iterations 2+ in sequence
    3. Tracking iteration history for transparency

    Args:
        workspace: Workspace path
        expert: Expert name
        total_iterations: Total number of iterations

    Returns:
        Complete expert review with full context from iteration 1
        plus all accumulated changes from iterations 2+
    """
    # Load base review (iteration 1)
    base_path = workspace / "iteration-1" / "experts" / expert / "state.json"

    if not base_path.exists():
        raise FileNotFoundError(f"Base review not found for expert {expert}: {base_path}")

    with open(base_path, 'r') as f:
        base = json.load(f)

    # Initialize iteration history
    if "iteration_history" not in base:
        base["iteration_history"] = []

    # Apply each delta
    for iteration in range(2, total_iterations + 1):
        delta_path = workspace / f"iteration-{iteration}" / "experts" / f"delta-{expert}.json"

        if not delta_path.exists():
            # No delta for this iteration, skip
            continue

        with open(delta_path, 'r') as f:
            delta_data = json.load(f)

        base = apply_delta(base, delta_data, iteration)

    return base


def apply_delta(base: Dict, delta: Dict, iteration: int) -> Dict:
    """Apply a delta to base review.

    Args:
        base: Base review dict
        delta: Delta changes dict
        iteration: Iteration number

    Returns:
        Updated base review
    """
    # Track iteration history
    if "iteration_history" not in base:
        base["iteration_history"] = []

    base["iteration_history"].append({
        "iteration": iteration,
        "what_changed": delta.get("what_changed", "")
    })

    # Update recommendations
    updated_recs = delta.get("updated_recommendations", {})
    for rec_id, changes in updated_recs.items():
        # Find recommendation by ID
        for rec in base.get("recommendations", []):
            if rec.get("id") == rec_id:
                rec.update(changes)
                rec["updated_in_iteration"] = iteration
                break

    # Add new recommendations
    for new_rec in delta.get("new_recommendations", []):
        new_rec["added_in_iteration"] = iteration
        base.setdefault("recommendations", []).append(new_rec)

    # Add new concerns
    for new_concern in delta.get("new_concerns", []):
        new_concern["added_in_iteration"] = iteration
        base.setdefault("concerns", []).append(new_concern)

    # Remove resolved concerns
    resolved_ids = delta.get("resolved_concerns", [])
    if resolved_ids:
        base["concerns"] = [
            c for c in base.get("concerns", [])
            if c.get("id") not in resolved_ids
        ]

    # Update assessment if changed
    updated_assessment = delta.get("updated_assessment")
    if updated_assessment:
        base.setdefault("assessment", {}).update(updated_assessment)
        base["assessment"]["updated_in_iteration"] = iteration

    # Add new questions
    for new_question in delta.get("new_questions", []):
        new_question["added_in_iteration"] = iteration
        base.setdefault("questions", []).append(new_question)

    # Update DX rating if changed
    if updated_assessment and "new_rating" in updated_assessment:
        base["dx_rating"]["stars"] = updated_assessment["new_rating"]
        base["dx_rating"]["updated_in_iteration"] = iteration

    return base


def build_artifact_generation_prompt(
    workspace: Path,
    topic: str,
    mode: str = "review",
    turn: int = 1,
    regeneration_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build artifact generation prompt based on mode and turn (Session-Preserved Architecture).

    Args:
        workspace: Workspace directory path
        topic: Original topic/design question
        mode: Operation mode (review, improve, or create)
        turn: Conversation turn (1=initial, 2=regenerate with concerns, 3=apply tweaks)
        regeneration_context: Context for regeneration (concerns, tweaks, etc.)

    Returns:
        Rendered prompt string
    """
    # Load state (Phase 1.4: Use StateManager)
    state_manager = WorkspaceStateManager(workspace)
    state = state_manager.load().to_dict()
    final_iteration = state.get("iteration", 1)
    convergence_percent = state.get("convergence_percent", 0)
    consensus_reached = state.get("consensus_reached", False)
    experts = state.get("experts", [])

    # Find consolidation files from all iterations
    synthesis_files = []
    paths = WorkspacePaths(workspace)
    for iteration in list_iterations(workspace):
        synthesized_file = paths.synthesized_md(iteration)
        if synthesized_file.exists():
            synthesis_files.append(synthesized_file)

    # Load questions from latest iteration
    questions = []
    if final_iteration > 0:
        paths = WorkspacePaths(workspace)
        questions_file = paths.questions_json(final_iteration)
        if questions_file.exists():
            questions_data = load_json(questions_file)
            questions = questions_data.get("questions", [])

    # Load Q&A answers
    qa_answers = []
    paths = WorkspacePaths(workspace)
    qa_file = paths.qa_answers_json(final_iteration)
    if qa_file.exists():
        qa_data = load_json(qa_file)
        qa_answers = qa_data.get("questions", [])

    # Select appropriate template based on turn and mode (Session-Preserved Architecture)
    if turn == 1:
        # Turn 1: Initial artifact generation
        if mode == "review":
            template_name = "artifact-generator/01-generate-adr.jinja2"
        elif mode == "improve":
            template_name = "artifact-generator/01-generate-plan.jinja2"
        else:  # create
            template_name = "artifact-generator/01-generate-architecture.jinja2"
    elif turn == 2:
        # Turn 2: Regenerate with critical concerns feedback
        template_name = "finalization/02-regenerate-with-concerns.jinja2"
    elif turn == 3:
        # Turn 3: Apply minor tweaks
        template_name = "finalization/03-apply-tweaks.jinja2"
    else:
        # Fallback to legacy templates
        if mode == "review":
            template_name = "artifact-generator/adr.jinja2"
        elif mode == "improve":
            template_name = "artifact-generator/improve.jinja2"
        else:
            template_name = "artifact-generator/create.jinja2"

    # Build template variables
    template_vars = {
        "workspace": str(workspace),
        "topic": topic,
        "final_iteration": final_iteration,
        "convergence_percent": convergence_percent,
        "consensus_reached": consensus_reached,
        "synthesis_files": [str(f.name) for f in synthesis_files],
        "experts": experts,
        "questions": questions,
        "qa_answers": qa_answers,
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    # Add regeneration context if provided (turn 2 or 3)
    if regeneration_context:
        if turn == 2:
            # Critical concerns regeneration context
            concerns_raised = regeneration_context.get("concerns_raised", {})
            template_vars.update({
                "concerns_feedback": format_concerns_feedback(concerns_raised),
                "concerns": {expert: concerns for expert, concerns in
                          zip(concerns_raised.get("experts_with_concerns", []),
                              [issue.get("issue", "") for issue in concerns_raised.get("critical_issues", [])])},
                "concern_questions": format_concerns_questions(concerns_raised.get("questions_for_user", []))
            })
        elif turn == 3:
            # Tweak application context
            tweaks = regeneration_context.get("tweaks", {})
            template_vars.update({
                "tweak_suggestions": format_tweak_suggestions(tweaks),
                "expert_tweaks": group_tweaks_by_expert(tweaks.get("tweaks", []))
            })

    # Render template
    prompt = render_template(template_name, **template_vars)

    return prompt


def format_concerns_feedback(concerns_raised: Dict[str, Any]) -> str:
    """Format critical concerns feedback for prompt."""
    experts = concerns_raised.get("experts_with_concerns", [])
    issues = concerns_raised.get("critical_issues", [])

    feedback = f"{len(experts)} expert(s) raised critical concerns:\n\n"
    for issue in issues:
        feedback += f"- **{issue.get('expert')}**: {issue.get('issue')}\n"
        feedback += f"  Why critical: {issue.get('why_critical')}\n"
        if issue.get('evidence'):
            feedback += f"  Evidence: {issue.get('evidence')}\n"
        feedback += "\n"

    return feedback


def format_concerns_questions(questions: List[Dict[str, Any]]) -> str:
    """Format critical concern questions for prompt."""
    if not questions:
        return "No specific questions raised."

    formatted = ""
    for i, q in enumerate(questions, 1):
        formatted += f"{i}. **{q.get('expert')}** asks: {q.get('question')}\n"
        if q.get('context'):
            formatted += f"   Context: {q.get('context')}\n"
        formatted += "\n"

    return formatted


def format_tweak_suggestions(tweaks: Dict[str, Any]) -> str:
    """Format tweak suggestions for prompt."""
    all_tweaks = tweaks.get("tweaks", [])
    if not all_tweaks:
        return "No specific tweaks suggested."

    formatted = ""
    for i, t in enumerate(all_tweaks, 1):
        formatted += f"{i}. **{t.get('section', 'General')}**: {t.get('suggestion')}\n"
        if t.get('issue'):
            formatted += f"   Issue: {t.get('issue')}\n"
        formatted += "\n"

    return formatted


def group_tweaks_by_expert(tweaks: List[Dict[str, Any]]) -> Dict[str, str]:
    """Group tweaks by expert for template."""
    grouped = {}
    for tweak in tweaks:
        expert = tweak.get("expert", "unknown")
        suggestion = tweak.get("suggestion", "")
        if expert not in grouped:
            grouped[expert] = []
        grouped[expert].append(suggestion)

    # Convert lists to strings
    return {expert: "; ".join(suggestions) for expert, suggestions in grouped.items()}


def get_next_adr_number(docs_decisions: Path) -> int:
    """Get next ADR number by scanning existing ADRs."""
    existing_adrs = list(docs_decisions.glob("*.md"))
    if not existing_adrs:
        return 1

    numbers = []
    for adr_file in existing_adrs:
        match = re.match(r'^(\d+)-', adr_file.stem)
        if match:
            numbers.append(int(match.group(1)))

    return max(numbers) + 1 if numbers else 1


async def generate_adr(
    workspace: Path,
    topic: str,
    correlation_id: Optional[str] = None,
    regenerate: bool = False,
    regeneration_attempt: int = 1,
    regeneration_context: Optional[Dict[str, Any]] = None,
    test_control: Optional[Dict[str, Any]] = None  # Test control for deterministic recordings
) -> Dict[str, Any]:
    """Generate ADR artifact from expert feedback (review mode) with session reuse and regeneration support."""
    start_time = time.time()

    # Setup logger
    logger = setup_agent_logger(workspace, "artifact-generation-adr")
    if regenerate:
        logger.info(f"Regenerating ADR (attempt {regeneration_attempt}) for topic: {topic}")
    else:
        logger.info(f"Starting ADR generation for topic: {topic}")

    transcript = None  # Initialize for exception handler
    try:
        # Check for existing artifact generation session (User Issue 9)
        config = get_config()
        state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)

        # Update phase for web UI
        state_manager.set_phase("generating_artifact")

        session_id = None

        # Always try to reuse session for regeneration (turn 2+)
        if config.reuse_artifact_generation_session or regenerate:
            try:
                workspace_state = state_manager.load()
                session_id = workspace_state.artifact_generation_session_id
                if session_id:
                    print(f"📝 Resuming artifact generation session: {session_id[:8]}...", file=sys.stderr)
            except Exception:
                pass  # No existing session

        # Determine conversation turn (Session-Preserved Architecture)
        turn = regeneration_attempt + 1 if regenerate else 1  # Turn 1=initial, 2=concerns regen, 3=tweaks

        # Build artifact generation prompt with turn and regeneration context
        prompt = build_artifact_generation_prompt(
            workspace,
            topic,
            mode="review",
            turn=turn,
            regeneration_context=regeneration_context
        )

        # Inject test controls if in recording mode
        prompt = inject_test_control(prompt, test_control)
        logger.info(f"Context size: {len(prompt)} characters")
        logger.info(f"Turn: {turn} (regenerate={regenerate}, attempt={regeneration_attempt})")

        # Get current iteration from state
        current_state = state_manager.load()
        current_iteration = current_state.iteration

        # Create iteration directory for draft artifact
        iteration_dir = workspace / f"iteration-{current_iteration}"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        # Calculate expected output file for file watcher - save to iteration folder
        expected_file = iteration_dir / "adr-data.json"

        # Spawn ADR generation agent using unified function
        spawn_config = AgentSpawnConfig(
            agent_type="artifact-generation",
            agent_name="artifact-generation-adr",
            prompt=prompt,
            workspace=workspace,
            session_id=session_id if config.reuse_artifact_generation_session else None,
            enable_session_reuse=config.reuse_artifact_generation_session,
            expected_files=[expected_file],
            enable_file_watching=True,
            enable_transcript_logging=config.enable_transcript_logging,
            allowed_tools=["Read", "Write", "Glob", "Grep"],
            timeout_seconds=config.expert_timeout_seconds,
            logger=logger  # Pass workspace-specific logger for prompt logging
        )

        result = await spawn_agent(spawn_config)

        # Save session ID for reuse if captured (User Issue 9)
        if result.session_id and config.reuse_artifact_generation_session:
            try:
                state_manager.set_artifact_generation_session(result.session_id)
                print(f"💾 Saved artifact generation session: {result.session_id[:8]}...", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Could not save artifact generation session ID: {e}", file=sys.stderr)

        # Check if agent succeeded
        if result.status != "complete":
            return {
                "error": result.error or f"Agent failed with status: {result.status}",
                "status": "error",
                "workspace": str(workspace),
                "duration_seconds": result.duration_seconds
            }

        tokens_used = result.tokens_used

        # After agent completes, look for adr-data.json in iteration folder
        adr_json_file = iteration_dir / "adr-data.json"

        # Also check workspace root (agent sometimes creates files there despite absolute path in prompt)
        adr_json_file_alt = workspace / "adr-data.json"

        if adr_json_file.exists():
            # File in correct location
            pass
        elif adr_json_file_alt.exists():
            # File created in workspace root, move it to iteration folder
            import shutil
            shutil.move(str(adr_json_file_alt), str(adr_json_file))
            logger.info(f"Moved adr-data.json from workspace root to {iteration_dir}")
        else:
            return {
                "error": "Agent did not create adr-data.json",
                "status": "error",
                "workspace": str(workspace)
            }

        # Load ADR JSON
        with open(adr_json_file) as f:
            adr_data = json.load(f)

        # Get next ADR number
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        docs_decisions = repo_root / "docs" / "decisions"
        docs_decisions.mkdir(parents=True, exist_ok=True)

        next_number = get_next_adr_number(docs_decisions)
        adr_number = f"{next_number:04d}"

        # Create slug from title
        slug = adr_data["title"].lower().replace(" ", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        adr_filename = f"{adr_number}-{slug}.md"
        adr_path = docs_decisions / adr_filename

        # Add metadata (Phase 1.4: Use StateManager)
        state_manager_local = WorkspaceStateManager(workspace)
        state = state_manager_local.load().to_dict()
        adr_data["workspace"] = str(workspace)
        adr_data["convergence_percent"] = state.get("convergence_percent", 0)
        adr_data["experts"] = state.get("experts", [])

        # Render ADR from template
        template_path = Path(__file__).parent.parent.parent / "prompts" / "output-templates" / "adr.md.jinja2"
        with open(template_path) as f:
            template = jinja2.Template(f.read())

        adr_content = template.render(**adr_data)

        # Write ADR to iteration folder (temporary location for approval)
        temp_adr_path = iteration_dir / "draft-adr.md"
        with open(temp_adr_path, 'w') as f:
            f.write(adr_content)

        # Update state with artifact location and review flag (Phase 4.1)
        try:
            state_manager.update({
                "draft_artifact_path": str(temp_adr_path.relative_to(workspace)),
                "draft_artifact_iteration": current_iteration,
                "artifact_review_needed": True
            })
        except Exception as e:
            print(f"⚠️ Could not set artifact_review_needed flag: {e}", file=sys.stderr)

        duration_seconds = int(time.time() - start_time)

        logger.info(f"ADR generation completed in {duration_seconds}s")
        logger.info(f"Total tokens used: {tokens_used}")
        logger.info(f"ADR created: {adr_filename}")
        logger.info(f"Temporary file: {temp_adr_path}")

        # Log completion
        if transcript:
            transcript.log_complete(duration_seconds, tokens_used)

        return {
            "status": "awaiting_approval",
            "temp_adr_file": str(temp_adr_path),
            "final_adr_file": f"docs/decisions/{adr_filename}",
            "adr_number": adr_number,
            "title": adr_data["title"],
            "workspace": str(workspace),
            "duration_seconds": duration_seconds,
            "artifact_review_needed": True,
            "tokens_used": tokens_used
        }

    except Exception as e:
        duration_seconds = int(time.time() - start_time)
        logger.error(f"ADR generation failed after {duration_seconds}s: {e}", exc_info=True)

        if transcript:
            transcript.log_error(str(e))
        return {
            "error": str(e),
            "status": "error",
            "workspace": str(workspace),
            "duration_seconds": duration_seconds
        }


async def generate_plan(
    workspace: Path,
    topic: str,
    mode: str = "improve",
    correlation_id: Optional[str] = None,
    regenerate: bool = False,
    regeneration_attempt: int = 1,
    regeneration_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate implementation plan artifact from expert feedback (improve or create mode) with session reuse and regeneration support."""
    start_time = time.time()

    # Setup logger
    logger = setup_agent_logger(workspace, f"finalization-{mode}")
    if regenerate:
        logger.info(f"Regenerating plan (attempt {regeneration_attempt}) for topic: {topic}")

    transcript = None  # Initialize for exception handler
    try:
        # Check for existing artifact generation session (User Issue 9)
        config = get_config()
        state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)

        # Update phase for web UI
        state_manager.set_phase("generating_artifact")

        session_id = None

        # Always try to reuse session for regeneration (turn 2+)
        if config.reuse_artifact_generation_session or regenerate:
            try:
                workspace_state = state_manager.load()
                session_id = workspace_state.artifact_generation_session_id
                if session_id:
                    print(f"📝 Resuming artifact generation session: {session_id[:8]}...", file=sys.stderr)
            except Exception:
                pass  # No existing session

        # Determine conversation turn (Session-Preserved Architecture)
        turn = regeneration_attempt + 1 if regenerate else 1  # Turn 1=initial, 2=concerns regen, 3=tweaks

        # Build artifact generation prompt with turn and regeneration context
        prompt = build_artifact_generation_prompt(
            workspace,
            topic,
            mode=mode,
            turn=turn,
            regeneration_context=regeneration_context
        )

        # Get current iteration from state
        current_state = state_manager.load()
        current_iteration = current_state.iteration

        # Create iteration directory for draft artifact
        iteration_dir = workspace / f"iteration-{current_iteration}"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        # Calculate expected output file for file watcher - save to iteration folder
        expected_file = iteration_dir / "draft-plan.md"

        # Spawn plan generation agent using unified function
        spawn_config = AgentSpawnConfig(
            agent_type="finalization",
            agent_name=f"finalization-{mode}",
            prompt=prompt,
            workspace=workspace,
            session_id=session_id if config.reuse_artifact_generation_session else None,
            enable_session_reuse=config.reuse_artifact_generation_session,
            expected_files=[expected_file],
            enable_file_watching=True,
            enable_transcript_logging=config.enable_transcript_logging,
            allowed_tools=["Read", "Write", "Glob", "Grep"],
            timeout_seconds=config.expert_timeout_seconds,
            logger=logger  # Pass workspace-specific logger for prompt logging
        )

        result = await spawn_agent(spawn_config)

        # Save session ID for reuse if captured (User Issue 9)
        if result.session_id and config.reuse_artifact_generation_session:
            try:
                state_manager.set_artifact_generation_session(result.session_id)
                print(f"💾 Saved artifact generation session: {result.session_id[:8]}...", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Could not save artifact generation session ID: {e}", file=sys.stderr)

        # Check if agent succeeded
        if result.status != "complete":
            return {
                "error": result.error or f"Agent failed with status: {result.status}",
                "status": "error",
                "workspace": str(workspace),
                "duration_seconds": result.duration_seconds
            }

        # After agent completes, look for draft plan in iteration folder
        # (Agent should create it in iteration folder, not in final plans/ directory)
        temp_plan_path = iteration_dir / "draft-plan.md"

        if not temp_plan_path.exists():
                return {
                    "error": "No plan file created",
                    "status": "error",
                    "workspace": str(workspace)
                }

        # Extract title from plan
        plan_content = temp_plan_path.read_text()
        title = "Unknown"
        for line in plan_content.split("\n"):
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                break

        # Generate final filename
        slug = title.lower().replace(" ", "-")
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        date_str = datetime.now().strftime("%Y-%m-%d")
        final_filename = f"{date_str}-{slug}.md"

        # Update state with artifact location and review flag (Phase 4.1)
        try:
            state_manager.update({
                "draft_artifact_path": str(temp_plan_path.relative_to(workspace)),
                "draft_artifact_iteration": current_iteration,
                "artifact_review_needed": True
            })
        except Exception as e:
            print(f"⚠️ Could not set artifact_review_needed flag: {e}", file=sys.stderr)

        duration_seconds = int(time.time() - start_time)

        # Log completion (plan mode doesn't track tokens)
        if transcript:
            transcript.log_complete(duration_seconds, 0)

        return {
            "status": "awaiting_approval",
            "temp_plan_file": str(temp_plan_path),
            "final_plan_file": f"plans/{final_filename}",
            "title": title,
            "mode": mode,
            "workspace": str(workspace),
            "duration_seconds": duration_seconds,
            "artifact_review_needed": True
        }

    except Exception as e:
        duration_seconds = int(time.time() - start_time)

        if transcript:
            transcript.log_error(str(e))

        return {
            "error": str(e),
            "status": "error",
            "workspace": str(workspace),
            "duration_seconds": duration_seconds
        }


def main():
    # Setup authentication first
    require_claude_auth()

    parser = argparse.ArgumentParser(description="Generate artifact from expert feedback")
    parser.add_argument("--workspace", required=True, help="Workspace directory path")
    parser.add_argument("--review-context", dest="review_context", required=True,
                       help="Review context/topic")
    parser.add_argument("--mode", choices=["review", "improve", "create"], default="review",
                       help="Operation mode (default: review)")
    parser.add_argument("--correlation-id", dest="correlation_id", default=None,
                       help="Correlation ID for end-to-end workflow tracing")
    parser.add_argument("--regenerate", action="store_true",
                       help="Regenerate artifact with critical concerns feedback (turn 2+)")
    parser.add_argument("--regeneration-attempt", type=int, default=1,
                       help="Regeneration attempt number (1-indexed)")

    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(json.dumps({
            "error": f"Workspace not found: {workspace}",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    # Load state to get mode (state takes precedence) - Phase 1.4: Use StateManager
    state_manager = WorkspaceStateManager(workspace, correlation_id=args.correlation_id)
    if state_manager.exists():
        state = state_manager.load().to_dict()
        mode = state.get("mode", args.mode)
    else:
        mode = args.mode

    # Load regeneration context if regenerating
    regeneration_context = None
    if args.regenerate:
        # Load concerns/tweak feedback from artifact review iteration
        review_iteration = state.get("iteration", 1) + 1
        iteration_dir = workspace / f"iteration-{review_iteration}"
        review_result_file = iteration_dir / "artifact-review-result.json"

        if review_result_file.exists():
            from file_io.json_ops import load_json
            review_result = load_json(review_result_file)
            regeneration_context = {
                "concerns_raised": review_result.get("concerns_raised"),
                "tweaks": review_result.get("tweaks")
            }

            # Load regeneration context with synthesized concerns (Context Gap Fix 1.3)
            regen_context_file = iteration_dir / "regeneration-context.json"
            if regen_context_file.exists():
                try:
                    regen_data = load_json(regen_context_file)
                    regeneration_context.update({
                        "synthesized_concerns": regen_data.get("synthesized_concerns"),
                        "concern_patterns": regen_data.get("concern_patterns", []),
                        "common_themes": regen_data.get("common_themes", []),
                        "total_concerns": regen_data.get("total_concerns", 0)
                    })
                    print(f"✅ Loaded regeneration context: {len(regen_data.get('concern_patterns', []))} patterns, {len(regen_data.get('common_themes', []))} themes", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️  Could not load regeneration context: {e}", file=sys.stderr)

            # Load user concern feedback (Context Gap Fix 2.2)
            concerns_feedback_file = iteration_dir / "concerns-feedback.json"
            if concerns_feedback_file.exists():
                try:
                    concerns_feedback = load_json(concerns_feedback_file)
                    user_approved_concerns = []

                    # Extract concern IDs that user approved despite expert objections
                    feedback_items = concerns_feedback.get("feedback", {})
                    for concern_id, feedback in feedback_items.items():
                        decision = feedback.get("decision")
                        if decision == "approve_anyway" or decision == "approve":
                            user_approved_concerns.append(concern_id)

                    if user_approved_concerns:
                        regeneration_context["user_approved_concerns"] = user_approved_concerns
                        print(f"✅ User approved {len(user_approved_concerns)} concerns anyway", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️  Could not load concern feedback: {e}", file=sys.stderr)
        else:
            print(json.dumps({
                "error": f"Cannot regenerate: No review result found at {review_result_file}",
                "status": "error"
            }), file=sys.stderr)
            sys.exit(1)

    # Run appropriate artifact generation based on mode
    if mode == "review":
        result = asyncio.run(generate_adr(
            workspace,
            args.review_context,
            correlation_id=args.correlation_id,
            regenerate=args.regenerate,
            regeneration_attempt=args.regeneration_attempt,
            regeneration_context=regeneration_context
        ))
    else:  # improve or create
        result = asyncio.run(generate_plan(
            workspace,
            args.review_context,
            mode=mode,
            correlation_id=args.correlation_id,
            regenerate=args.regenerate,
            regeneration_attempt=args.regeneration_attempt,
            regeneration_context=regeneration_context
        ))

    # Output JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
