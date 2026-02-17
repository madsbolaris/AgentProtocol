#!/usr/bin/env python3
"""
Shared workspace analysis for all experts.

Analyzes workspace structure and organization for expert feedback sessions.

Usage:
    python3 scripts/shared/analyze_workspace.py --workspace /path/to/workspace
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def analyze_workspace(workspace: Path) -> Dict[str, Any]:
    """Analyze workspace structure and organization.

    Args:
        workspace: Path to workspace directory

    Returns:
        Dict with workspace analysis:
        - structure: Directory and file structure
        - state: Workflow state information
        - iterations: List of iterations found
        - experts: List of experts found
        - artifacts: List of artifacts found
        - issues: List of organizational issues
    """
    if not workspace.exists():
        return {"error": f"Workspace not found: {workspace}"}

    if not workspace.is_dir():
        return {"error": f"Not a directory: {workspace}"}

    issues = []
    iterations = []
    experts = set()
    artifacts = []

    # Check for state.json
    state_file = workspace / "state.json"
    state = None
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except json.JSONDecodeError as e:
            issues.append({
                "severity": "high",
                "file": "state.json",
                "issue": f"Invalid JSON: {e}"
            })

    # Check for metrics
    metrics_file = workspace / "metrics.jsonl"
    metrics_count = 0
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            metrics_count = sum(1 for line in f if line.strip())

    # Find iterations
    for item in workspace.iterdir():
        if item.is_dir() and item.name.startswith("iteration-"):
            try:
                iteration_num = int(item.name.split("-")[1])
                iterations.append(iteration_num)

                # Check iteration structure
                experts_dir = item / "experts"
                if not experts_dir.exists():
                    issues.append({
                        "severity": "medium",
                        "directory": str(item.relative_to(workspace)),
                        "issue": "Missing experts/ directory"
                    })
                else:
                    # Find experts
                    for expert_file in experts_dir.glob("*.md"):
                        experts.add(expert_file.stem)

                    # Check for orphaned files (not in subdirectories)
                    for orphan in experts_dir.glob("*"):
                        if orphan.is_file() and orphan.suffix in ['.md', '.json']:
                            # Files should be in expert subdirectories
                            issues.append({
                                "severity": "low",
                                "file": str(orphan.relative_to(workspace)),
                                "issue": "File should be in expert subdirectory"
                            })

                # Check for consolidated.md
                if not (item / "consolidated.md").exists():
                    issues.append({
                        "severity": "low",
                        "directory": str(item.relative_to(workspace)),
                        "issue": "Missing consolidated.md"
                    })

            except (ValueError, IndexError):
                issues.append({
                    "severity": "low",
                    "directory": str(item.name),
                    "issue": "Invalid iteration directory name"
                })

    # Find artifacts
    artifacts_dir = workspace / "artifacts"
    if artifacts_dir.exists():
        for artifact_file in artifacts_dir.glob("*.md"):
            artifacts.append(artifact_file.name)

    # Check for logs
    logs_dir = workspace / "logs"
    log_files = []
    if logs_dir.exists():
        log_files = [f.name for f in logs_dir.glob("*.log")]

    # Count files by type
    file_counts = {
        "markdown": len(list(workspace.rglob("*.md"))),
        "json": len(list(workspace.rglob("*.json"))),
        "python": len(list(workspace.rglob("*.py"))),
        "log": len(list(workspace.rglob("*.log")))
    }

    # Check for common issues
    # 1. Scattered review files at root
    scattered_reviews = list(workspace.glob("review-*.md"))
    if scattered_reviews:
        issues.append({
            "severity": "medium",
            "files": [f.name for f in scattered_reviews],
            "issue": "Review files should be in iteration-N/experts/ directories"
        })

    # 2. State files at root (should be in iteration dirs)
    scattered_state = list(workspace.glob("state-*.json"))
    if scattered_state:
        issues.append({
            "severity": "medium",
            "files": [f.name for f in scattered_state],
            "issue": "State files should be in iteration-N/experts/ directories"
        })

    # 3. Duplicate scripts across experts
    script_files = defaultdict(list)
    for script in workspace.rglob("*.py"):
        if "experts" in script.parts:
            script_files[script.name].append(str(script.relative_to(workspace)))

    duplicate_scripts = {
        name: locations
        for name, locations in script_files.items()
        if len(locations) > 1
    }

    if duplicate_scripts:
        issues.append({
            "severity": "high",
            "issue": "Duplicate scripts across expert directories",
            "duplicates": duplicate_scripts,
            "recommendation": "Move to shared scripts folder"
        })

    return {
        "workspace_name": workspace.name,
        "workspace_path": str(workspace),
        "state": state,
        "iterations": sorted(iterations),
        "iteration_count": len(iterations),
        "experts": sorted(list(experts)),
        "expert_count": len(experts),
        "artifacts": artifacts,
        "metrics_entries": metrics_count,
        "log_files": log_files,
        "file_counts": file_counts,
        "issues": issues,
        "issue_count": len(issues),
        "high_severity_issues": len([i for i in issues if i.get("severity") == "high"])
    }


from collections import defaultdict


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze expert feedback workspace structure"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Path to workspace directory"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (json or summary)"
    )

    args = parser.parse_args()

    result = analyze_workspace(args.workspace)

    if "error" in result:
        print(json.dumps(result))
        return 1

    if args.format == "summary":
        # Human-readable summary
        print(f"\n📂 Workspace Analysis: {result['workspace_name']}\n")
        print(f"Iterations: {result['iteration_count']} ({', '.join(map(str, result['iterations']))})")
        print(f"Experts: {result['expert_count']} ({', '.join(result['experts'])})")
        print(f"Artifacts: {len(result['artifacts'])}")
        print(f"Metrics Entries: {result['metrics_entries']}")

        print(f"\n📊 File Counts:")
        for file_type, count in result['file_counts'].items():
            print(f"  {file_type}: {count}")

        if result['issues']:
            print(f"\n⚠️ Issues Found: {result['issue_count']}")
            print(f"   High severity: {result['high_severity_issues']}")
            for issue in result['issues']:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "⚪"}.get(
                    issue.get("severity", "low"), "⚪"
                )
                print(f"\n{severity_emoji} {issue['issue']}")
                if 'file' in issue:
                    print(f"   File: {issue['file']}")
                if 'directory' in issue:
                    print(f"   Directory: {issue['directory']}")
                if 'files' in issue:
                    print(f"   Files: {', '.join(issue['files'][:5])}")
                if 'duplicates' in issue:
                    for script, locations in list(issue['duplicates'].items())[:3]:
                        print(f"   {script}: {len(locations)} copies")
        else:
            print("\n✅ No organizational issues found")
        print()
    else:
        # JSON output
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
