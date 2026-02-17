#!/usr/bin/env python3
"""
Synthesize expert concerns into user-reviewable format.

This script consolidates concerns from all experts, groups them by theme,
calculates consensus, and prepares them for user review.
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


async def synthesize_concerns(
    workspace: Path,
    concern_review_dir: Path,
    experts: List[str],
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesize expert concerns using synthesis session.

    Args:
        workspace: Workspace path
        concern_review_dir: Directory containing concern reviews
        experts: List of expert IDs
        correlation_id: Optional correlation ID for logging

    Returns:
        Dict with synthesized concerns data
    """
    # Load all expert concerns
    expert_concerns = {}
    for expert_id in experts:
        concern_file = concern_review_dir / f"concerns-{expert_id}.json"
        if concern_file.exists():
            expert_concerns[expert_id] = load_json(concern_file)
        else:
            print(f"⚠️  Warning: Concern review not found for {expert_id}", file=sys.stderr)

    if not expert_concerns:
        return {
            "total_concerns": 0,
            "experts_approving": [],
            "experts_with_concerns": [],
            "concerns_by_theme": {},
            "error": "No expert concerns found"
        }

    # Categorize experts
    experts_approving = [
        e for e, c in expert_concerns.items()
        if c.get("decision") == "approve"
    ]
    experts_with_concerns = [
        e for e, c in expert_concerns.items()
        if c.get("decision") == "concern"
    ]

    # If no concerns, return early
    if not experts_with_concerns:
        synthesized_data = {
            "total_concerns": 0,
            "experts_approving": experts_approving,
            "experts_with_concerns": [],
            "concerns_by_theme": {}
        }

        # Save synthesized concerns
        output_file = concern_review_dir / "synthesized-concerns.json"
        save_json(synthesized_data, output_file)

        print("✅ No concerns raised - all experts approved!", file=sys.stderr)
        return synthesized_data

    # Load or create synthesis session
    state_manager = WorkspaceStateManager(workspace, correlation_id=correlation_id)
    state = state_manager.load()

    session_id = state.synthesis_session_id
    if session_id:
        session = ConversationalSession.load(
            agent_id="synthesis",
            workspace=workspace
        )
        print(f"📊 Resuming synthesis session (turn {session.turn_count + 1})...", file=sys.stderr)
    else:
        session = ConversationalSession(
            agent_type="synthesis",
            agent_id="synthesis",
            workspace=workspace
        )
        print("📊 Creating new synthesis session...", file=sys.stderr)

    # Prepare context for synthesis
    context = {
        "num_experts": len(experts),
        "experts_approving": experts_approving,
        "experts_with_concerns": experts_with_concerns,
        "expert_concerns": expert_concerns
    }

    print(f"   Synthesizing concerns from {len(experts_with_concerns)} expert(s)...", file=sys.stderr)

    # Send synthesis turn
    response = await session.send_turn(
        prompt_template="04-synthesize-concerns.jinja2",
        context=context,
        timeout=600  # 10 minutes
    )

    # Parse response
    try:
        synthesized_data = json.loads(response["content"])

        # Validate response structure
        required_fields = ["total_concerns", "experts_approving", "experts_with_concerns", "concerns_by_theme"]
        for field in required_fields:
            if field not in synthesized_data:
                raise ValueError(f"Response missing required field: {field}")

        # Save synthesized concerns
        output_file = concern_review_dir / "synthesized-concerns.json"
        save_json(synthesized_data, output_file)

        print(f"✅ Synthesized {synthesized_data.get('total_concerns', 0)} concern(s)", file=sys.stderr)

        # Print summary by theme
        concerns_by_theme = synthesized_data.get("concerns_by_theme", {})
        if concerns_by_theme:
            print("\n📋 Concerns by theme:", file=sys.stderr)
            for theme, concerns in concerns_by_theme.items():
                print(f"   - {theme}: {len(concerns)} concern(s)", file=sys.stderr)

        return synthesized_data

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse synthesized concerns: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "total_concerns": 0,
            "experts_approving": experts_approving,
            "experts_with_concerns": experts_with_concerns,
            "concerns_by_theme": {},
            "error": error_msg
        }
    except ValueError as e:
        error_msg = f"Invalid synthesis response: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {
            "total_concerns": 0,
            "experts_approving": experts_approving,
            "experts_with_concerns": experts_with_concerns,
            "concerns_by_theme": {},
            "error": error_msg
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synthesize expert concerns")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--concern-review-dir", required=True, type=Path, help="Concern review directory")
    parser.add_argument("--experts", nargs="+", required=True, help="Expert IDs")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Run synthesis
    result = asyncio.run(synthesize_concerns(
        workspace=args.workspace,
        concern_review_dir=args.concern_review_dir,
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
