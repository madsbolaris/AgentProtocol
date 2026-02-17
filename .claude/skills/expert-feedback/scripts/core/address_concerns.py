#!/usr/bin/env python3
"""
Spawn experts to address user-agreed concerns.

This script spawns all experts in parallel to provide updated recommendations
that address the concerns the user agreed should be resolved.
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


async def spawn_expert_address_concerns(
    expert_id: str,
    workspace: Path,
    concerns_to_address: List[Dict[str, Any]],
    artifact_content: str,
    expert_role: str,
    iteration: int,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Spawn single expert to address concerns.

    Args:
        expert_id: Expert identifier
        workspace: Workspace path
        concerns_to_address: List of concerns this expert should address
        artifact_content: Current artifact content
        expert_role: Expert role description
        iteration: Current iteration number
        correlation_id: Optional correlation ID

    Returns:
        Dict with expert_id and updated recommendations
    """
    # If expert has no concerns to address, skip
    if not concerns_to_address:
        return {
            "expert_id": expert_id,
            "updated_recommendations": [],
            "status": "skipped",
            "message": "No concerns to address"
        }

    # Create new session for addressing concerns
    # Note: We create a fresh session rather than resuming the review session
    # because this is a distinct task (addressing concerns vs initial review)
    session = ConversationalSession(
        agent_type="expert",
        agent_id=expert_id,
        workspace=workspace
    )

    # Prepare context
    context = {
        "expert_role": expert_role,
        "concerns_to_address": concerns_to_address,
        "artifact_content": artifact_content,
        "iteration": iteration
    }

    # Send address concerns turn
    response = await session.send_turn(
        prompt_template="06-address-concerns.jinja2",
        context=context,
        timeout=600  # 10 minutes
    )

    # Parse response
    try:
        recommendations_data = json.loads(response["content"])

        # Validate response structure
        if "updated_recommendations" not in recommendations_data:
            raise ValueError("Response missing 'updated_recommendations' field")

        return {
            "expert_id": expert_id,
            "updated_recommendations": recommendations_data["updated_recommendations"],
            "additional_notes": recommendations_data.get("additional_notes", ""),
            "status": "success"
        }

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse recommendations from {expert_id}: {e}", file=sys.stderr)
        return {
            "expert_id": expert_id,
            "updated_recommendations": [],
            "status": "error",
            "error": f"Failed to parse JSON response: {str(e)}"
        }
    except ValueError as e:
        print(f"❌ Invalid recommendations from {expert_id}: {e}", file=sys.stderr)
        return {
            "expert_id": expert_id,
            "updated_recommendations": [],
            "status": "error",
            "error": f"Invalid response structure: {str(e)}"
        }


async def address_concerns_iteration(
    workspace: Path,
    experts: List[str],
    agreed_concerns: List[Dict[str, Any]],
    artifact_path: Path,
    concern_iteration: int,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Coordinate experts to address user-agreed concerns.

    Args:
        workspace: Workspace path
        experts: List of expert IDs
        agreed_concerns: List of concerns user agreed with
        artifact_path: Path to current artifact
        concern_iteration: Concern review iteration number
        correlation_id: Optional correlation ID

    Returns:
        Dict with results from all experts
    """
    # Load artifact content
    if not artifact_path.exists():
        return {
            "error": f"Artifact not found: {artifact_path}",
            "status": "error"
        }

    artifact_content = artifact_path.read_text()

    # Load state
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load()

    # Create concern iteration directory
    concern_iter_dir = workspace / "artifact" / f"concern-iteration-{concern_iteration}"
    concern_iter_dir.mkdir(parents=True, exist_ok=True)

    # Expert roles
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

    # Organize concerns by expert
    concerns_by_expert = {}
    for concern in agreed_concerns:
        for expert_id in concern.get("experts", []):
            if expert_id not in concerns_by_expert:
                concerns_by_expert[expert_id] = []
            concerns_by_expert[expert_id].append(concern)

    print(f"\n🔧 Addressing concerns (iteration {concern_iteration})...", file=sys.stderr)
    print(f"   Total concerns: {len(agreed_concerns)}", file=sys.stderr)
    print(f"   Experts involved: {len(concerns_by_expert)}", file=sys.stderr)

    # Spawn experts in parallel
    tasks = []
    for expert_id in experts:
        concerns_for_expert = concerns_by_expert.get(expert_id, [])
        expert_role = expert_roles.get(expert_id, expert_id.title())

        task = spawn_expert_address_concerns(
            expert_id=expert_id,
            workspace=workspace,
            concerns_to_address=concerns_for_expert,
            artifact_content=artifact_content,
            expert_role=expert_role,
            iteration=state.iteration,
            correlation_id=correlation_id
        )
        tasks.append(task)

    # Await all experts
    print(f"   Waiting for {len(experts)} experts to address concerns...", file=sys.stderr)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    all_recommendations = {}
    skipped = []
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue

        expert_id = result["expert_id"]

        # Save individual recommendations
        if result["status"] == "success":
            rec_file = concern_iter_dir / f"recommendations-{expert_id}.json"
            save_json(result, rec_file)
            all_recommendations[expert_id] = result
        elif result["status"] == "skipped":
            skipped.append(expert_id)
        elif result["status"] == "error":
            errors.append(f"{expert_id}: {result.get('error', 'Unknown error')}")

    # Print summary
    print(f"\n✅ Concern addressing complete:", file=sys.stderr)
    print(f"   - Provided recommendations: {len(all_recommendations)}", file=sys.stderr)
    print(f"   - Skipped (no concerns): {len(skipped)}", file=sys.stderr)

    if errors:
        print(f"   - Errors: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"     • {error}", file=sys.stderr)

    return {
        "all_recommendations": all_recommendations,
        "skipped": skipped,
        "errors": errors if errors else None,
        "concern_iteration_dir": str(concern_iter_dir),
        "status": "error" if len(errors) == len(experts) else "success"
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Spawn experts to address concerns")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--experts", nargs="+", required=True, help="Expert IDs")
    parser.add_argument("--agreed-concerns", required=True, type=Path, help="Path to agreed concerns JSON")
    parser.add_argument("--artifact-path", required=True, type=Path, help="Path to artifact")
    parser.add_argument("--concern-iteration", required=True, type=int, help="Concern iteration number")
    parser.add_argument("--correlation-id", help="Optional correlation ID")

    args = parser.parse_args()

    # Load agreed concerns
    agreed_concerns = load_json(args.agreed_concerns)

    # Run address concerns
    result = asyncio.run(address_concerns_iteration(
        workspace=args.workspace,
        experts=args.experts,
        agreed_concerns=agreed_concerns,
        artifact_path=args.artifact_path,
        concern_iteration=args.concern_iteration,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "success" else 1)
