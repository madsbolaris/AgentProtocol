#!/usr/bin/env python3
"""
Spawn experts to review artifact and voice concerns.

This script spawns all experts in parallel to review the generated artifact
and determine if they approve it or have concerns that should be addressed.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_io.json_ops import load_json, save_json
from agents.conversational_session import ConversationalSession
from state.manager import StateManager as WorkspaceStateManager
from prompts.templates import load_expert_info
from agents.spawn import AgentSpawnConfig, spawn_agent
from config import get_config
from core.test_control import inject_test_control


async def spawn_expert_concern_review(
    expert_id: str,
    workspace: Path,
    artifact_content: str,
    expert_previous_recommendations: Dict[str, Any],
    synthesis_summary: str,
    review_context: str,
    expert_role: str,
    correlation_id: Optional[str] = None,
    test_control: Optional[Dict[str, Any]] = None  # Test control for deterministic recordings
) -> Dict[str, Any]:
    """
    Spawn single expert to review artifact and voice concerns.

    Args:
        expert_id: Expert identifier (typescript, python, csharp, etc.)
        workspace: Workspace path
        artifact_content: Generated artifact markdown content
        expert_previous_recommendations: Expert's recommendations from previous iterations
        synthesis_summary: Consolidated synthesis feedback
        review_context: Original review context/topic
        expert_role: Expert role description (e.g., "TypeScript/JavaScript")
        correlation_id: Optional correlation ID for logging

    Returns:
        Dict with expert_id and concern_review data
    """
    # Load existing expert session (turn N+1)
    session = ConversationalSession.load(
        agent_id=expert_id,
        workspace=workspace
    )

    # Prepare context for concern review prompt
    context = {
        "expert_role": expert_role,
        "iteration": session.turn_count,
        "review_context": review_context,
        "artifact_content": artifact_content,
        "expert_previous_recommendations": expert_previous_recommendations,
        "synthesis_summary": synthesis_summary
    }

    # Send concern review turn using the concern review prompt
    response = await session.send_turn(
        prompt_template="05-artifact-concern-review.jinja2",
        context=context,
        timeout=600  # 10 minutes
    )

    # Parse response
    try:
        # DEBUG: Log what we're trying to parse
        content = response.get("content", "")
        print(f"[DEBUG concern_review] expert_id={expert_id}, response keys={list(response.keys())}", file=sys.stderr)
        print(f"[DEBUG concern_review] content type={type(content)}, length={len(content)}, first 100 chars: {content[:100]}", file=sys.stderr)

        concern_data = json.loads(content)

        # Validate response structure
        if "decision" not in concern_data:
            raise ValueError("Response missing 'decision' field")

        if concern_data["decision"] not in ["approve", "concern"]:
            raise ValueError(f"Invalid decision: {concern_data['decision']}")

        if concern_data["decision"] == "concern" and "concerns" not in concern_data:
            raise ValueError("Concern decision must include 'concerns' array")

        return {
            "expert_id": expert_id,
            "concern_review": concern_data,
            "status": "success"
        }

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse concern review from {expert_id}: {e}", file=sys.stderr)
        return {
            "expert_id": expert_id,
            "concern_review": {
                "decision": "error",
                "error": f"Failed to parse JSON response: {str(e)}"
            },
            "status": "error"
        }
    except ValueError as e:
        print(f"❌ Invalid concern review from {expert_id}: {e}", file=sys.stderr)
        return {
            "expert_id": expert_id,
            "concern_review": {
                "decision": "error",
                "error": f"Invalid response structure: {str(e)}"
            },
            "status": "error"
        }


async def artifact_concern_review(
    workspace: Path,
    experts: List[str],
    artifact_path: Path,
    review_context: str,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to coordinate artifact concern review across all experts.

    Args:
        workspace: Workspace path
        experts: List of expert IDs (e.g., ["typescript", "python", "csharp"])
        artifact_path: Path to generated artifact
        review_context: Original review context/topic
        correlation_id: Optional correlation ID for logging

    Returns:
        Dict with:
            - all_concerns: Dict mapping expert_id to concern_review data
            - experts_approving: List of experts who approved
            - experts_with_concerns: List of experts with concerns
            - concern_review_dir: Path to directory where concerns saved
            - status: Overall status (success/partial/error)
    """
    # Load state
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load()

    # Load artifact content
    if not artifact_path.exists():
        return {
            "error": f"Artifact not found: {artifact_path}",
            "status": "error"
        }

    artifact_content = artifact_path.read_text()

    # Determine concern review iteration
    concern_state = state_manager.get_concern_review_state()
    concern_iteration = concern_state.get("iteration", 0) + 1

    # Load synthesis summary (from last iteration)
    last_iteration = state.iteration
    synthesis_path = workspace / f"iteration-{last_iteration}" / "synthesis.json"

    if synthesis_path.exists():
        synthesis_data = load_json(synthesis_path)
        synthesis_summary = synthesis_data.get("consolidated_feedback", "")
    else:
        synthesis_summary = "No synthesis available"

    # Load expert roles
    expert_roles = {
        "typescript": "TypeScript/JavaScript",
        "python": "Python",
        "csharp": "C#/.NET",
        "dx": "Developer Experience",
        "security": "Security",
        "performance": "Performance",
        "accessibility": "Accessibility",
        "cost-optimization": "Cost Optimization",
        "claude-code-sdk": "Claude Code SDK"
    }

    # Create concern review directory
    concern_review_dir = workspace / "artifact" / f"concern-review-{concern_iteration}"
    concern_review_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🔍 Starting concern review (iteration {concern_iteration})...", file=sys.stderr)
    print(f"   Experts: {', '.join(experts)}", file=sys.stderr)
    print(f"   Artifact: {artifact_path.name}", file=sys.stderr)

    # Spawn all experts in parallel
    tasks = []
    for expert_id in experts:
        # Load expert's previous recommendations
        recommendations_path = workspace / f"iteration-{last_iteration}" / "experts" / expert_id / "review.json"

        if recommendations_path.exists():
            expert_recs = load_json(recommendations_path)
            # Format recommendations as string for prompt
            recs_summary = json.dumps(expert_recs.get("recommendations", []), indent=2)
        else:
            recs_summary = "No previous recommendations available"

        expert_role = expert_roles.get(expert_id, expert_id.title())

        task = spawn_expert_concern_review(
            expert_id=expert_id,
            workspace=workspace,
            artifact_content=artifact_content,
            expert_previous_recommendations=recs_summary,
            synthesis_summary=synthesis_summary,
            review_context=review_context,
            expert_role=expert_role,
            correlation_id=correlation_id
        )
        tasks.append(task)

    # Await all experts
    print(f"   Waiting for {len(experts)} experts to review artifact...", file=sys.stderr)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    all_concerns = {}
    experts_approving = []
    experts_with_concerns = []
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue

        expert_id = result["expert_id"]
        concern_review = result["concern_review"]

        # Save individual concern review
        concern_file = concern_review_dir / f"concerns-{expert_id}.json"
        save_json(concern_review, concern_file)

        all_concerns[expert_id] = concern_review

        # Categorize experts
        if result.get("status") == "error":
            errors.append(f"{expert_id}: {concern_review.get('error', 'Unknown error')}")
        elif concern_review.get("decision") == "approve":
            experts_approving.append(expert_id)
        elif concern_review.get("decision") == "concern":
            experts_with_concerns.append(expert_id)

    # Determine overall status
    if len(errors) == len(experts):
        status = "error"
    elif errors:
        status = "partial"
    else:
        status = "success"

    # Print summary
    print(f"\n✅ Concern review complete:", file=sys.stderr)
    print(f"   - Approving: {len(experts_approving)}/{len(experts)}", file=sys.stderr)
    print(f"   - With concerns: {len(experts_with_concerns)}/{len(experts)}", file=sys.stderr)

    if errors:
        print(f"   - Errors: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"     • {error}", file=sys.stderr)

    return {
        "all_concerns": all_concerns,
        "experts_approving": experts_approving,
        "experts_with_concerns": experts_with_concerns,
        "concern_review_dir": str(concern_review_dir),
        "concern_iteration": concern_iteration,
        "status": status,
        "errors": errors if errors else None
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Spawn experts to review artifact and voice concerns")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--experts", nargs="+", required=True, help="Expert IDs to spawn")
    parser.add_argument("--artifact-path", required=True, type=Path, help="Path to artifact")
    parser.add_argument("--review-context", required=True, help="Review context/topic")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Run concern review
    result = asyncio.run(artifact_concern_review(
        workspace=args.workspace,
        experts=args.experts,
        artifact_path=args.artifact_path,
        review_context=args.review_context,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if result["status"] == "error":
        sys.exit(1)
    elif result["status"] == "partial":
        sys.exit(2)
    else:
        sys.exit(0)
