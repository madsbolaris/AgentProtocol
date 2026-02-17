#!/usr/bin/env python3
"""
Handle user rejection of draft artifact.

Creates rejection notice for experts and prepares for next iteration.

Usage:
    python3 handle-rejection.py --workspace /path --reason "rejection reason"
"""
import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from file_io.json_ops import save_json
from prompts.templates import render_template
from agents.spawn import AgentSpawnConfig, spawn_agent
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


async def handle_rejection(workspace: Path, reason: str) -> dict:
    """Create rejection notice for experts."""
    # Load config
    config = get_config()

    try:
        # Load state (Phase 1.4: Use StateManager)
        state_manager = StateManager(workspace)
        state = state_manager.load().to_dict()
        iteration = state.get("iteration", 1)
        experts = state.get("experts", [])
        mode = state.get("mode", "review")

        # Determine artifact type and path
        if mode == "review":
            artifact_type = "ADR"
            artifact_path = workspace / "draft-adr.md"
        else:
            artifact_type = "Implementation Plan"
            artifact_path = workspace / "draft-plan.md"

        # Verify artifact exists
        if not artifact_path.exists():
            return {
                "error": f"Draft artifact not found: {artifact_path}",
                "status": "error",
                "workspace": str(workspace)
            }

        # Create rejection record
        rejection = {
            "iteration": iteration,
            "artifact_type": artifact_type,
            "artifact_path": str(artifact_path),
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

        # Save rejection.json
        rejection_file = workspace / "rejection.json"
        with open(rejection_file, 'w') as f:
            json.dump(rejection, f, indent=2)

        # Build rejection notice prompt
        prompt = render_template(
            "rejection-handler/rejection-notice.jinja2",
            workspace=str(workspace),
            artifact_type=artifact_type,
            artifact_path=str(artifact_path),
            iteration=iteration,
            experts=experts,
            rejection_reason=reason,
            date=datetime.now().strftime("%Y-%m-%d"),
            timestamp=rejection["timestamp"]
        )

        # Spawn rejection notice agent using unified function
        rejection_notice_file = workspace / f"rejection-notice-{iteration}.md"
        spawn_config = AgentSpawnConfig(
            agent_type="rejection",
            agent_name="rejection-handler",
            prompt=prompt,
            workspace=workspace,
            expected_files=[rejection_notice_file],
            enable_file_watching=False,  # No early termination needed
            enable_transcript_logging=config.enable_transcript_logging,
            allowed_tools=["Read", "Write"],
            timeout_seconds=300  # 5 minutes for rejection notice
        )

        result = await spawn_agent(spawn_config)

        # Check if agent succeeded
        if result.status != "complete":
            return {
                "error": result.error or "Agent failed to create rejection notice",
                "status": "error",
                "workspace": str(workspace),
                "rejection_file": str(rejection_file),
                "duration_seconds": result.duration_seconds
            }

        # Verify rejection notice was created
        if not rejection_notice_file.exists():
            return {
                "error": "Agent did not create rejection notice",
                "status": "error",
                "workspace": str(workspace),
                "rejection_file": str(rejection_file),
                "duration_seconds": result.duration_seconds
            }

        # Update state
        state["last_rejection"] = rejection
        state["status"] = "awaiting_refinement"
        save_json(state, workspace / "state.json")

        return {
            "status": "rejection_processed",
            "rejection_file": str(rejection_file),
            "rejection_notice": str(rejection_notice_file),
            "workspace": str(workspace),
            "duration_seconds": result.duration_seconds
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "workspace": str(workspace)
        }


def main():
    # Setup authentication first
    require_claude_auth()

    parser = argparse.ArgumentParser(description="Handle artifact rejection")
    parser.add_argument("--workspace", required=True, help="Workspace directory path")
    parser.add_argument("--reason", required=True, help="Rejection reason from user")

    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(json.dumps({
            "error": f"Workspace not found: {workspace}",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    # Run async function
    result = asyncio.run(handle_rejection(workspace, args.reason))

    # Output JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with error code if rejection handling failed
    if result.get("status") != "rejection_processed":
        sys.exit(1)


if __name__ == "__main__":
    main()
