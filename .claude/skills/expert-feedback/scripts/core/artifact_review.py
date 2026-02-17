#!/usr/bin/env python3
"""
Artifact Review Phase - Spawn experts to review generated artifact (ADR or Implementation Plan).

After artifact generation generates an artifact, experts get one final chance to review it
before approval. Experts can approve, request minor tweaks, or raise critical concerns with questions.

Usage:
    python3 artifact-review.py --workspace /path/to/workspace
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from file_io.json_ops import load_json, save_json
from agents.spawn import AgentSpawnConfig, spawn_agent
from prompts.templates import render_template, load_expert_info
from config import get_config
from state.manager import StateManager

# Add .claude to path
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


async def spawn_artifact_reviewer(
    expert_name: str,
    prompt: str,
    workspace: Path,
    experts_dir: Path,
    config: Any,
    timeout_seconds: int = 300  # 5 minutes for artifact review
) -> Dict[str, Any]:
    """
    Spawn an expert to review the generated artifact.

    Args:
        expert_name: Name of expert
        prompt: Artifact review prompt
        workspace: Workspace directory
        experts_dir: Experts directory for this iteration
        config: Skill configuration
        timeout_seconds: Timeout for review (default 5 minutes)

    Returns:
        Review result with decision (approve/minor_tweaks/concerns_raised)
    """
    # Create expert directory
    expert_dir = experts_dir / expert_name
    expert_dir.mkdir(parents=True, exist_ok=True)

    # Expected review files in expert's folder
    review_md = expert_dir / f"artifact-review-{expert_name}.md"
    review_json = expert_dir / f"artifact-review-{expert_name}.json"

    # Configure and spawn agent using unified function
    spawn_config = AgentSpawnConfig(
        agent_type="artifact-review",
        agent_name=f"artifact-review-{expert_name}",
        prompt=prompt,
        workspace=workspace,
        expected_files=[review_md],
        enable_file_watching=False,  # No early termination for reviews
        enable_transcript_logging=config.enable_transcript_logging,
        allowed_tools=["Read", "Grep", "Glob", "Write"],
        timeout_seconds=timeout_seconds
    )

    result = await spawn_agent(spawn_config)

    # Check if agent succeeded
    if result.status != "complete":
        return {
            "expert": expert_name,
            "status": result.status,
            "error": result.error or f"Agent failed with status: {result.status}",
            "duration_seconds": result.duration_seconds
        }

    # Check if markdown file exists
    if not review_md.exists():
        return {
            "expert": expert_name,
            "status": "error",
            "error": f"Expert did not create review file: {review_md}",
            "duration_seconds": result.duration_seconds
        }

    # Parse Markdown to JSON
    try:
        from parse_artifact_review import parse_artifact_review
        review_data = parse_artifact_review(review_md, review_json)
    except Exception as e:
        return {
            "expert": expert_name,
            "status": "error",
            "error": f"Failed to parse review markdown: {e}",
            "duration_seconds": result.duration_seconds
        }

    return {
        "expert": expert_name,
        "session_id": result.session_id,
        "status": "complete",
        "decision": review_data.get("decision"),
        "review_data": review_data,
        "tokens_used": result.tokens_used,
        "duration_seconds": result.duration_seconds
    }


def synthesize_critical_concerns(concerns_list: List[Dict[str, Any]], iteration_dir: Path) -> Dict[str, Any]:
    """
    Consolidate critical concerns into questions for user.

    Args:
        concerns_list: List of critical concern review results
        iteration_dir: Iteration directory for artifact review

    Returns:
        Consolidated concerns summary
    """
    # Extract all critical issues and questions
    all_issues = []
    all_questions = []
    experts_with_concerns = []

    for concern in concerns_list:
        review_data = concern.get("review_data", {})
        expert = concern.get("expert")
        experts_with_concerns.append(expert)

        critical_issues = review_data.get("critical_issues", [])
        questions = review_data.get("questions", [])

        all_issues.extend([{**issue, "expert": expert} for issue in critical_issues])
        all_questions.extend([{**q, "expert": expert} for q in questions])

    # Create concerns summary
    concerns_summary = {
        "total_concerns": len(concerns_list),
        "experts_with_concerns": experts_with_concerns,
        "critical_issues": all_issues,
        "questions_for_user": all_questions,
        "requires_regeneration": True
    }

    # Save concerns questions for Q&A phase in iteration folder
    concerns_questions_file = iteration_dir / "artifact-concerns-questions.json"
    save_json({"questions": all_questions}, concerns_questions_file)

    # Create markdown summary for user
    summary_md = "# Critical Concerns Summary\n\n"
    summary_md += f"**{len(concerns_list)} expert(s) raised critical concerns about the artifact:**\n\n"

    for expert in experts_with_concerns:
        summary_md += f"- {expert}\n"

    summary_md += "\n## Critical Issues\n\n"
    for i, issue in enumerate(all_issues, 1):
        summary_md += f"### {i}. {issue.get('issue', 'Unknown issue')} ({issue.get('expert')})\n\n"
        summary_md += f"**Why Critical:** {issue.get('why_critical', 'Not specified')}\n\n"
        summary_md += f"**Evidence:** {issue.get('evidence', 'Not specified')}\n\n"

    summary_md += "\n## Questions That Need Answers\n\n"
    for i, q in enumerate(all_questions, 1):
        importance = q.get('importance', 'medium')
        emoji = "🔴" if importance == "high" else "🟡" if importance == "medium" else "🔵"
        summary_md += f"### {emoji} Question {i} ({q.get('expert')})\n\n"
        summary_md += f"**Question:** {q.get('question', 'Not specified')}\n\n"
        summary_md += f"**Context:** {q.get('context', 'Not specified')}\n\n"

    # Save summary in iteration folder
    summary_file = iteration_dir / "artifact-concerns-summary.md"
    summary_file.write_text(summary_md)

    return concerns_summary


def synthesize_tweaks(minor_tweaks: List[Dict[str, Any]], iteration_dir: Path) -> Dict[str, Any]:
    """
    Consolidate minor tweaks from experts.

    Args:
        minor_tweaks: List of minor tweak review results
        iteration_dir: Iteration directory for artifact review

    Returns:
        Consolidated tweaks summary
    """
    all_tweaks = []
    experts_with_tweaks = []

    for tweak_result in minor_tweaks:
        review_data = tweak_result.get("review_data", {})
        expert = tweak_result.get("expert")
        experts_with_tweaks.append(expert)

        tweaks = review_data.get("tweaks", [])
        all_tweaks.extend([{**t, "expert": expert} for t in tweaks])

    # Create markdown summary
    summary_md = "# Suggested Minor Tweaks\n\n"
    summary_md += f"**{len(minor_tweaks)} expert(s) suggested minor improvements:**\n\n"

    for expert in experts_with_tweaks:
        summary_md += f"- {expert}\n"

    summary_md += "\n## Suggested Changes\n\n"
    for i, tweak in enumerate(all_tweaks, 1):
        summary_md += f"### {i}. {tweak.get('section', 'General')} ({tweak.get('expert')})\n\n"
        summary_md += f"**Issue:** {tweak.get('issue', 'Not specified')}\n\n"
        summary_md += f"**Suggestion:** {tweak.get('suggestion', 'Not specified')}\n\n"

    # Save summary in iteration folder
    summary_file = iteration_dir / "artifact-tweaks-summary.md"
    summary_file.write_text(summary_md)

    return {
        "total_tweaks": len(minor_tweaks),
        "experts_with_tweaks": experts_with_tweaks,
        "tweaks": all_tweaks,
        "requires_regeneration": False
    }


def create_regeneration_context(
    concerns_data: Dict[str, Any],
    expert_reviews: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create structured regeneration context from synthesized concerns.

    Extracts patterns and themes to help the generator address systemic issues
    rather than just individual concerns (Context Gap Fix 1.3).

    Args:
        concerns_data: Parsed synthesized concerns
        expert_reviews: Individual expert review data

    Returns:
        Dictionary with:
        - synthesized_concerns: Full concerns data
        - concern_patterns: Concerns grouped by theme when multiple experts mention it
        - common_themes: Themes mentioned by 2+ experts
    """
    # Extract all concerns
    all_concerns = concerns_data.get("concerns", [])

    # Group concerns by theme to identify patterns
    theme_to_concerns = {}
    for concern in all_concerns:
        theme = concern.get("theme", "Other")
        if theme not in theme_to_concerns:
            theme_to_concerns[theme] = []
        theme_to_concerns[theme].append(concern)

    # Identify concern patterns: themes with 2+ concerns or mentioned by 2+ experts
    concern_patterns = []
    for theme, concerns in theme_to_concerns.items():
        if len(concerns) >= 2:
            # Multiple concerns in this theme - likely a pattern
            expert_count = len(set(c.get("expert") for c in concerns if c.get("expert")))
            concern_patterns.append({
                "theme": theme,
                "concern_count": len(concerns),
                "expert_count": expert_count,
                "summary": f"{expert_count} expert(s) raised {len(concerns)} concern(s) about {theme}",
                "concerns": [c.get("id") or c.get("title") for c in concerns]
            })

    # Extract common themes from all concerns (themes mentioned by 2+ experts)
    expert_themes = {}
    for expert, review in expert_reviews.items():
        if review.get("decision") == "concerns_raised" and review.get("concerns"):
            for concern in review["concerns"]:
                theme = concern.get("theme", "Other")
                if theme not in expert_themes:
                    expert_themes[theme] = set()
                expert_themes[theme].add(expert)

    common_themes = [
        {
            "theme": theme,
            "expert_count": len(experts),
            "experts": list(experts)
        }
        for theme, experts in expert_themes.items()
        if len(experts) >= 2
    ]

    return {
        "synthesized_concerns": concerns_data,
        "concern_patterns": concern_patterns,
        "common_themes": common_themes,
        "total_concerns": len(all_concerns),
        "themes_count": len(theme_to_concerns)
    }


async def synthesize_artifact_concerns(
    workspace: Path,
    iteration_dir: Path,
    experts_dir: Path,
    state: Any,
    results: List[Dict[str, Any]],
    config: Any
) -> Dict[str, Any]:
    """
    Consolidate artifact review feedback from all experts.

    Deduplicates similar concerns and groups them by theme.

    Args:
        workspace: Workspace directory path
        iteration_dir: Iteration directory for artifact review
        experts_dir: Experts directory with review files
        state: Workspace state
        results: List of expert review results
        config: Skill configuration

    Returns:
        Consolidation result with total concerns
    """
    # Load all expert review JSON files from experts directories
    expert_reviews = {}
    for result in results:
        expert = result.get("expert")
        review_json_path = experts_dir / expert / f"artifact-review-{expert}.json"
        if review_json_path.exists():
            try:
                review_data = load_json(review_json_path)
                expert_reviews[expert] = review_data
            except Exception as e:
                print(f"   ⚠️  Failed to load review for {expert}: {e}", file=sys.stderr)

    if not expert_reviews:
        return {"status": "error", "error": "No expert reviews found"}

    # Count decisions
    total_experts = len(expert_reviews)
    approvals = sum(1 for r in expert_reviews.values() if r.get("decision") == "approve")
    minor_tweaks_count = sum(1 for r in expert_reviews.values() if r.get("decision") == "minor_tweaks")
    concerns_count = sum(1 for r in expert_reviews.values() if r.get("decision") == "concerns_raised")

    # Build synthesis prompt
    prompt = render_template(
        "experts/synthesize-artifact-reviews.jinja2",
        workspace=str(workspace),
        total_experts=total_experts,
        expert_reviews=expert_reviews,
        artifact_type=state.mode
    )

    # Expected output files in iteration folder
    consolidated_md = iteration_dir / "synthesized-concerns.md"
    consolidated_json = iteration_dir / "synthesized-concerns.json"

    # Spawn synthesis agent
    spawn_config = AgentSpawnConfig(
        agent_type="synthesize-concerns",
        agent_name="synthesize-artifact-concerns",
        prompt=prompt,
        workspace=workspace,
        expected_files=[consolidated_md],
        enable_file_watching=False,
        enable_transcript_logging=config.enable_transcript_logging,
        allowed_tools=["Read", "Write"],
        timeout_seconds=600  # 10 minutes for consolidation
    )

    consolidation_result = await spawn_agent(spawn_config)

    if consolidation_result.status != "complete":
        return {
            "status": "error",
            "error": f"Consolidation agent failed: {consolidation_result.error or consolidation_result.status}"
        }

    # Check if markdown file exists
    if not consolidated_md.exists():
        return {
            "status": "error",
            "error": f"Consolidation agent did not create file: {consolidated_md}"
        }

    # Parse Markdown to JSON
    try:
        from parse_synthesized_concerns import parse_synthesized_concerns
        concerns_data = parse_synthesized_concerns(consolidated_md, consolidated_json)
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to parse synthesized concerns: {e}"
        }

    # Create regeneration context for generator (Context Gap Fix 1.3)
    try:
        regeneration_context = create_regeneration_context(
            concerns_data=concerns_data,
            expert_reviews=expert_reviews
        )

        # Save regeneration context for artifact generator
        regen_context_file = iteration_dir / "regeneration-context.json"
        save_json(regeneration_context, regen_context_file)
        print(f"   📝 Created regeneration context: {regen_context_file.name}", file=sys.stderr)
    except Exception as e:
        print(f"   ⚠️  Could not create regeneration context: {e}", file=sys.stderr)

    return {
        "status": "complete",
        "total_concerns": len(concerns_data.get("concerns", [])),
        "concerns_file": str(consolidated_json)
    }


async def review_artifact(workspace: Path, config: Any) -> Dict[str, Any]:
    """
    Spawn experts to review generated artifact.

    Args:
        workspace: Workspace directory path
        config: Skill configuration

    Returns:
        Review results with status (approved/minor_tweaks/concerns_raised)
    """
    state_mgr = StateManager(workspace)
    state = state_mgr.load()

    # Artifact review happens in next iteration after artifact generation
    draft_iteration = state.draft_artifact_iteration
    review_iteration = draft_iteration + 1

    # Create iteration directory structure
    iteration_dir = workspace / f"iteration-{review_iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    # Create experts directory
    experts_dir = iteration_dir / "experts"
    experts_dir.mkdir(parents=True, exist_ok=True)

    # Update state with review iteration
    state_mgr.set_iteration(review_iteration)
    state_mgr.set_phase("reviewing_artifact")

    # Get artifact file from state (now stored in iteration folder)
    artifact_file = workspace / state.draft_artifact_path

    # Determine artifact type label
    if state.mode == "review" or state.mode == "adr":
        artifact_type_label = "ADR"
    else:
        artifact_type_label = "Implementation Plan"

    if not artifact_file.exists():
        return {
            "error": f"Artifact not found: {artifact_file}",
            "status": "error"
        }

    print(f"\n📋 Artifact Review Phase", file=sys.stderr)
    print(f"📄 Generated {artifact_type_label}: {artifact_file.name}", file=sys.stderr)
    print(f"👥 Spawning {len(state.experts)} experts to review...\n", file=sys.stderr)

    # Spawn all experts in parallel to review artifact
    tasks = []
    for expert_name in state.experts:
        expert_info = load_expert_info(expert_name)

        # Build artifact review prompt
        prompt = render_template(
            "experts/artifact-review.jinja2",
            expert_name=expert_name,
            expert_background=expert_info["background"],
            artifact_file=str(artifact_file),
            artifact_type=artifact_type_label,
            workspace=str(workspace),
            topic=state.topic,
            final_iteration=state.iteration,
            convergence=state.convergence_percent
        )

        # Spawn reviewer with 5 minute timeout
        task = spawn_artifact_reviewer(
            expert_name=expert_name,
            prompt=prompt,
            workspace=workspace,
            experts_dir=experts_dir,
            config=config,
            timeout_seconds=300
        )
        tasks.append(task)

    # Wait for all reviews to complete
    results = await asyncio.gather(*tasks)

    # Analyze results
    approvals = [r for r in results if r.get("decision") == "approve"]
    minor_tweaks = [r for r in results if r.get("decision") == "minor_tweaks"]
    concerns_raised = [r for r in results if r.get("decision") == "concerns_raised"]
    errors = [r for r in results if r.get("status") == "error" or r.get("status") == "timeout"]

    print(f"\n📊 Artifact Review Results:", file=sys.stderr)
    print(f"   ✅ Approved: {len(approvals)}", file=sys.stderr)
    print(f"   📝 Minor Tweaks: {len(minor_tweaks)}", file=sys.stderr)
    print(f"   🛑 Critical Concerns: {len(concerns_raised)}", file=sys.stderr)
    if errors:
        print(f"   ⚠️  Errors: {len(errors)}", file=sys.stderr)

    # Consolidate concerns if there are any non-approvals
    if minor_tweaks or concerns_raised:
        print(f"\n🔄 Consolidating expert feedback...", file=sys.stderr)
        consolidation_result = await synthesize_artifact_concerns(
            workspace=workspace,
            iteration_dir=iteration_dir,
            experts_dir=experts_dir,
            state=state,
            results=results,
            config=config
        )
        if consolidation_result.get("status") == "error":
            print(f"   ⚠️  Consolidation failed: {consolidation_result.get('error')}", file=sys.stderr)
        else:
            print(f"   ✅ Consolidated into {consolidation_result.get('total_concerns', 0)} concerns", file=sys.stderr)

    # Determine overall status
    if concerns_raised:
        # At least one critical concern - artifact needs regeneration
        concerns_summary = synthesize_critical_concerns(concerns_raised, iteration_dir)
        result = {
            "status": "concerns_raised",
            "concerns": concerns_summary,
            "minor_tweaks": synthesize_tweaks(minor_tweaks, iteration_dir) if minor_tweaks else None,
            "requires_regeneration": True
        }
    elif minor_tweaks:
        # Only minor tweaks - user can manually edit
        result = {
            "status": "minor_tweaks",
            "tweaks": synthesize_tweaks(minor_tweaks, iteration_dir),
            "requires_regeneration": False
        }
    else:
        # All approved
        result = {
            "status": "approved",
            "requires_regeneration": False
        }

    # Save result in iteration folder
    result_file = iteration_dir / "artifact-review-result.json"
    save_json(result, result_file)

    return result


def main():
    """Main entry point for artifact review."""
    parser = argparse.ArgumentParser(
        description="Review generated artifact with expert panel"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        required=True,
        help="Workspace directory path"
    )

    args = parser.parse_args()

    # Require authentication
    require_claude_auth()

    # Load config
    config = get_config()

    # Run artifact review
    workspace = Path(args.workspace)
    result = asyncio.run(review_artifact(workspace, config))

    # Print result
    print(json.dumps(result, indent=2))

    # Exit code based on status
    if result.get("status") == "error":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
