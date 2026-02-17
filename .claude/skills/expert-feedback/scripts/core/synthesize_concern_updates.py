#!/usr/bin/env python3
"""
Synthesize concern-addressed recommendations from experts.

After experts have addressed user-agreed concerns, this script consolidates
their updated recommendations into a coherent synthesis for artifact regeneration.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from file_io.json_ops import load_json, save_json
from agents.conversational_session import ConversationalSession
from state.manager import StateManager as WorkspaceStateManager


async def synthesize_concern_updates(
    workspace: Path,
    concern_iteration_dir: Path,
    experts: List[str],
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesize concern-addressed recommendations using synthesis session.

    Args:
        workspace: Workspace path
        concern_iteration_dir: Directory containing concern-addressed recommendations
        experts: List of expert IDs
        correlation_id: Optional correlation ID for logging

    Returns:
        Dict with synthesized concern updates
    """
    # Load all expert recommendations for concern addressing
    expert_recommendations = {}
    for expert_id in experts:
        rec_file = concern_iteration_dir / f"recommendations-{expert_id}.json"
        if rec_file.exists():
            expert_recommendations[expert_id] = load_json(rec_file)
        else:
            print(f"⚠️  Warning: Recommendations not found for {expert_id}", file=sys.stderr)

    if not expert_recommendations:
        return {
            "total_recommendations": 0,
            "experts_contributing": [],
            "consolidated_recommendations": [],
            "error": "No expert recommendations found"
        }

    # Load state
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load()

    # Create new synthesis session for concern updates
    # Note: We create a fresh session rather than resuming the review synthesis session
    # because this is a distinct task (synthesizing concern updates vs initial synthesis)
    session = ConversationalSession(
        agent_type="synthesis",
        agent_id="synthesis-concern-updates",
        workspace=workspace
    )
    print(f"📊 Creating synthesis session for concern updates...", file=sys.stderr)

    # Extract recommendations for synthesis
    all_recommendations = []
    experts_contributing = []

    for expert_id, rec_data in expert_recommendations.items():
        if rec_data.get("status") == "success":
            updated_recs = rec_data.get("updated_recommendations", [])
            if updated_recs:
                all_recommendations.extend(updated_recs)
                experts_contributing.append(expert_id)

    # Prepare context for synthesis
    # NOTE: This uses a generic synthesis prompt since concern-update-specific
    # prompts follow the same consolidation pattern as regular synthesis
    context = {
        "num_experts": len(experts_contributing),
        "experts_contributing": experts_contributing,
        "expert_recommendations": expert_recommendations,
        "all_recommendations": all_recommendations,
        "synthesis_type": "concern_updates"  # Signal this is addressing concerns
    }

    print(f"   Synthesizing updates from {len(experts_contributing)} expert(s)...", file=sys.stderr)

    # Send synthesis turn
    # NOTE: Using a refinement-style template since we're consolidating updates
    # This reuses the existing synthesis session for efficiency
    response = await session.send_turn(
        prompt_template="07-synthesize-concern-updates.jinja2",
        context=context,
        timeout=600  # 10 minutes
    )

    # Parse response
    try:
        synthesized_data = json.loads(response["content"])

        # Validate response structure
        required_fields = ["consolidated_recommendations", "synthesis_summary"]
        for field in required_fields:
            if field not in synthesized_data:
                raise ValueError(f"Response missing required field: {field}")

        # Save synthesized updates
        output_file = concern_iteration_dir / "consolidated-recommendations.json"
        save_json(synthesized_data, output_file)

        print(f"✅ Synthesized {len(synthesized_data.get('consolidated_recommendations', []))} recommendation(s)", file=sys.stderr)

        return {
            "status": "success",
            "total_recommendations": len(all_recommendations),
            "experts_contributing": experts_contributing,
            "consolidated_recommendations": synthesized_data["consolidated_recommendations"],
            "synthesis_summary": synthesized_data["synthesis_summary"],
            "output_file": str(output_file)
        }

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse synthesized concern updates: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "status": "error",
            "total_recommendations": len(all_recommendations),
            "experts_contributing": experts_contributing,
            "consolidated_recommendations": [],
            "error": error_msg
        }
    except ValueError as e:
        error_msg = f"Invalid synthesis response: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "status": "error",
            "total_recommendations": len(all_recommendations),
            "experts_contributing": experts_contributing,
            "consolidated_recommendations": [],
            "error": error_msg
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synthesize concern-addressed recommendations")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--concern-iteration-dir", required=True, type=Path, help="Concern iteration directory")
    parser.add_argument("--experts", nargs="+", required=True, help="Expert IDs")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Run synthesis
    result = asyncio.run(synthesize_concern_updates(
        workspace=args.workspace,
        concern_iteration_dir=args.concern_iteration_dir,
        experts=args.experts,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if "error" in result:
        sys.exit(1)
    else:
        sys.exit(0)
