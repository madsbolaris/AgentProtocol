#!/usr/bin/env python3
"""
Regenerate artifact incorporating concern-addressed recommendations.

After experts have addressed concerns and synthesis has consolidated the updates,
this script regenerates the artifact with the improvements.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from file_io.json_ops import load_json, save_json
from agents.conversational_session import ConversationalSession
from state.manager import StateManager as WorkspaceStateManager


async def regenerate_artifact_with_concerns(
    workspace: Path,
    mode: str,
    previous_artifact_path: Path,
    agreed_concerns: list,
    consolidated_recommendations: list,
    concern_iteration: int,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Regenerate artifact incorporating concern-addressed recommendations.

    Args:
        workspace: Workspace path
        mode: Generation mode (review/improve/create)
        previous_artifact_path: Path to previous artifact version
        agreed_concerns: List of concerns user agreed with
        consolidated_recommendations: Consolidated recommendations from synthesis
        concern_iteration: Current concern review iteration number
        correlation_id: Optional correlation ID for logging

    Returns:
        Dict with:
            - status: success/error
            - artifact_path: Path to regenerated artifact
            - artifact_version: New version number
            - error: Error message if failed
    """
    # Load state
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load()

    # Load previous artifact content
    if not previous_artifact_path.exists():
        return {
            "error": f"Previous artifact not found: {previous_artifact_path}",
            "status": "error"
        }

    previous_artifact_content = previous_artifact_path.read_text()

    # Get new artifact version
    new_version = state_manager.increment_artifact_version()

    print(f"\n🔄 Regenerating artifact (version {new_version})...", file=sys.stderr)
    print(f"   Previous: {previous_artifact_path.name}", file=sys.stderr)
    print(f"   Concerns addressed: {len(agreed_concerns)}", file=sys.stderr)
    print(f"   Recommendations: {len(consolidated_recommendations)}", file=sys.stderr)

    # Create new artifact generation session for regeneration
    # Note: We create a fresh session rather than resuming the initial generation session
    # because this is regeneration with concerns addressed (distinct from initial generation)
    session = ConversationalSession(
        agent_type="artifact-generation",
        agent_id=f"artifact-regen-v{new_version}",
        workspace=workspace
    )
    print(f"📝 Creating artifact regeneration session (version {new_version})...", file=sys.stderr)

    # Prepare context for regeneration
    context = {
        "mode": mode,
        "previous_artifact": previous_artifact_content,
        "artifact_version": new_version,
        "agreed_concerns": agreed_concerns,
        "consolidated_recommendations": consolidated_recommendations,
        "concern_iteration": concern_iteration,
        "iteration": state.iteration  # Current review iteration
    }

    # Send regeneration turn
    response = await session.send_turn(
        prompt_template="04-regenerate-with-concerns.jinja2",
        context=context,
        timeout=900  # 15 minutes for artifact generation
    )

    # Parse response
    try:
        artifact_data = json.loads(response["content"])

        # Validate response structure based on mode
        if mode == "review":
            required_fields = ["adr_markdown", "artifact_type"]
        elif mode == "improve":
            required_fields = ["plan_markdown", "artifact_type"]
        elif mode == "create":
            required_fields = ["architecture_markdown", "artifact_type"]
        else:
            required_fields = ["markdown", "artifact_type"]

        for field in required_fields:
            if field not in artifact_data and "markdown" not in artifact_data:
                raise ValueError(f"Response missing required field: {field}")

        # Extract markdown content
        if mode == "review":
            markdown_content = artifact_data.get("adr_markdown", artifact_data.get("markdown", ""))
            artifact_filename = f"draft-adr-v{new_version}.md"
            data_filename = f"adr-data-v{new_version}.json"
        elif mode == "improve":
            markdown_content = artifact_data.get("plan_markdown", artifact_data.get("markdown", ""))
            artifact_filename = f"improvement-plan-v{new_version}.md"
            data_filename = f"plan-data-v{new_version}.json"
        elif mode == "create":
            markdown_content = artifact_data.get("architecture_markdown", artifact_data.get("markdown", ""))
            artifact_filename = f"architecture-v{new_version}.md"
            data_filename = f"architecture-data-v{new_version}.json"
        else:
            markdown_content = artifact_data.get("markdown", "")
            artifact_filename = f"artifact-v{new_version}.md"
            data_filename = f"artifact-data-v{new_version}.json"

        # Save artifact markdown
        artifact_dir = workspace / "artifact"
        artifact_dir.mkdir(parents=True, exist_ok=True)

        artifact_path = artifact_dir / artifact_filename
        artifact_path.write_text(markdown_content)

        # Save artifact data JSON
        data_path = artifact_dir / data_filename
        save_json(artifact_data, data_path)

        print(f"\n✅ Artifact regenerated successfully", file=sys.stderr)
        print(f"   File: {artifact_path.name}", file=sys.stderr)
        print(f"   Version: {new_version}", file=sys.stderr)

        # Update state with new artifact info
        state_manager.update_concern_review_state(
            iteration=concern_iteration,
            status="artifact_regenerated",
            concerns_raised=len(agreed_concerns),
            concerns_agreed=len(agreed_concerns),
            concerns_disagreed=0
        )

        return {
            "status": "success",
            "artifact_path": str(artifact_path),
            "data_path": str(data_path),
            "artifact_version": new_version,
            "artifact_filename": artifact_filename
        }

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse regenerated artifact: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "error": error_msg,
            "status": "error"
        }
    except ValueError as e:
        error_msg = f"Invalid artifact response: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "error": error_msg,
            "status": "error"
        }
    except Exception as e:
        error_msg = f"Regeneration failed: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "error": error_msg,
            "status": "error"
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate artifact with concern-addressed recommendations")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--mode", required=True, choices=["review", "improve", "create"], help="Generation mode")
    parser.add_argument("--previous-artifact", required=True, type=Path, help="Path to previous artifact")
    parser.add_argument("--agreed-concerns", required=True, type=Path, help="Path to agreed concerns JSON")
    parser.add_argument("--consolidated-recommendations", required=True, type=Path, help="Path to consolidated recommendations JSON")
    parser.add_argument("--concern-iteration", required=True, type=int, help="Concern iteration number")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Load concerns and recommendations
    agreed_concerns = load_json(args.agreed_concerns)
    consolidated_recs_data = load_json(args.consolidated_recommendations)
    consolidated_recommendations = consolidated_recs_data.get("consolidated_recommendations", [])

    # Run regeneration
    result = asyncio.run(regenerate_artifact_with_concerns(
        workspace=args.workspace,
        mode=args.mode,
        previous_artifact_path=args.previous_artifact,
        agreed_concerns=agreed_concerns,
        consolidated_recommendations=consolidated_recommendations,
        concern_iteration=args.concern_iteration,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get("status") == "success" else 1)
