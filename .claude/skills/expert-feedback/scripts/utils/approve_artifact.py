#!/usr/bin/env python3
"""
Move approved artifact from workspace to final location.

Usage:
    python3 approve-artifact.py --workspace /path
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from file_io.json_ops import save_json
from state.manager import StateManager


def approve_artifact(workspace: Path) -> dict:
    """Move draft artifact to final location."""
    try:
        # Load state (Phase 1.4: Use StateManager)
        state_manager = StateManager(workspace)
        state = state_manager.load().to_dict()
        mode = state.get("mode", "review")

        # Determine source and destination
        repo_root = Path(__file__).parent.parent.parent.parent.parent

        if mode == "review":
            # ADR mode
            source = workspace / "draft-adr.md"

            # Read finalization result to get final filename
            # This should have been stored when finalize.py was called
            artifact_generation_result = state.get("artifact_generation_result", {})
            final_file = artifact_generation_result.get("final_adr_file")

            if not final_file:
                return {
                    "error": "No final ADR file path found in state.artifact_generation_result",
                    "status": "error",
                    "workspace": str(workspace)
                }

            dest = repo_root / final_file
        else:
            # Improve or create mode
            source = workspace / "draft-plan.md"

            artifact_generation_result = state.get("artifact_generation_result", {})
            final_file = artifact_generation_result.get("final_plan_file")

            if not final_file:
                return {
                    "error": "No final plan file path found in state.artifact_generation_result",
                    "status": "error",
                    "workspace": str(workspace)
                }

            dest = repo_root / final_file

        # Verify source exists
        if not source.exists():
            return {
                "error": f"Draft artifact not found: {source}",
                "status": "error",
                "workspace": str(workspace)
            }

        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to final location
        shutil.copy2(source, dest)

        # Update state
        state["status"] = "complete"
        state["final_artifact"] = str(dest.relative_to(repo_root))
        save_json(state, workspace / "state.json")

        return {
            "status": "approved",
            "final_file": str(dest.relative_to(repo_root)),
            "source_file": str(source),
            "workspace": str(workspace)
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "workspace": str(workspace)
        }


def main():
    parser = argparse.ArgumentParser(description="Approve and finalize artifact")
    parser.add_argument("--workspace", required=True, help="Workspace directory path")

    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(json.dumps({
            "error": f"Workspace not found: {workspace}",
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)

    result = approve_artifact(workspace)
    print(json.dumps(result, indent=2))

    # Exit with error code if approval failed
    if result.get("status") != "approved":
        sys.exit(1)


if __name__ == "__main__":
    main()
