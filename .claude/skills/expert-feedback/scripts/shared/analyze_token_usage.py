#!/usr/bin/env python3
"""
Shared token usage analysis for all experts.

Analyzes token usage across all iterations and phases in a workspace.

Usage:
    python3 scripts/shared/analyze_token_usage.py --workspace /path/to/workspace
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any


def analyze_token_usage(workspace: Path) -> Dict[str, Any]:
    """Analyze token usage across all iterations.

    Args:
        workspace: Path to workspace directory

    Returns:
        Dict with token usage analysis:
        - total_tokens: Total tokens used
        - total_cost_usd: Estimated cost in USD
        - by_phase: Token usage by phase
        - by_expert: Token usage by expert
        - by_iteration: Token usage by iteration
        - entries: List of all token usage entries
    """
    metrics_file = workspace / "metrics.jsonl"

    if not metrics_file.exists():
        return {
            "error": f"No metrics.jsonl found at {metrics_file}",
            "total_tokens": 0,
            "total_cost_usd": 0.0
        }

    entries = []
    with metrics_file.open("r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    # Calculate totals
    total_tokens = sum(e.get("total_tokens", 0) for e in entries)
    total_cost = sum(e.get("estimated_cost_usd", 0.0) for e in entries)

    # Aggregate by phase
    by_phase = {}
    for entry in entries:
        phase = entry.get("phase", "unknown")
        if phase not in by_phase:
            by_phase[phase] = {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "count": 0,
                "cost_usd": 0.0
            }
        by_phase[phase]["total_tokens"] += entry.get("total_tokens", 0)
        by_phase[phase]["input_tokens"] += entry.get("input_tokens", 0)
        by_phase[phase]["output_tokens"] += entry.get("output_tokens", 0)
        by_phase[phase]["count"] += 1
        by_phase[phase]["cost_usd"] += entry.get("estimated_cost_usd", 0.0)

    # Aggregate by expert
    by_expert = {}
    for entry in entries:
        expert = entry.get("expert")
        if not expert:
            continue
        if expert not in by_expert:
            by_expert[expert] = {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "count": 0,
                "cost_usd": 0.0
            }
        by_expert[expert]["total_tokens"] += entry.get("total_tokens", 0)
        by_expert[expert]["input_tokens"] += entry.get("input_tokens", 0)
        by_expert[expert]["output_tokens"] += entry.get("output_tokens", 0)
        by_expert[expert]["count"] += 1
        by_expert[expert]["cost_usd"] += entry.get("estimated_cost_usd", 0.0)

    # Aggregate by iteration
    by_iteration = {}
    for entry in entries:
        iteration = entry.get("iteration")
        if iteration is None:
            continue
        if iteration not in by_iteration:
            by_iteration[iteration] = {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "count": 0,
                "cost_usd": 0.0
            }
        by_iteration[iteration]["total_tokens"] += entry.get("total_tokens", 0)
        by_iteration[iteration]["input_tokens"] += entry.get("input_tokens", 0)
        by_iteration[iteration]["output_tokens"] += entry.get("output_tokens", 0)
        by_iteration[iteration]["count"] += 1
        by_iteration[iteration]["cost_usd"] += entry.get("estimated_cost_usd", 0.0)

    # Calculate duration total
    total_duration = sum(e.get("duration_seconds", 0) for e in entries)

    return {
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "total_duration_seconds": round(total_duration, 2),
        "entry_count": len(entries),
        "by_phase": by_phase,
        "by_expert": by_expert,
        "by_iteration": by_iteration,
        "entries": entries
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze token usage in expert feedback workspace"
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

    if not args.workspace.exists():
        print(json.dumps({"error": f"Workspace not found: {args.workspace}"}))
        return 1

    result = analyze_token_usage(args.workspace)

    if args.format == "summary":
        # Human-readable summary
        print(f"\n📊 Token Usage Analysis: {args.workspace.name}\n")
        print(f"Total Tokens: {result['total_tokens']:,}")
        print(f"Total Cost: ${result['total_cost_usd']:.4f}")
        print(f"Total Duration: {result['total_duration_seconds']:.1f}s")
        print(f"Entries: {result['entry_count']}")

        print("\n📈 By Phase:")
        for phase, data in result['by_phase'].items():
            print(f"  {phase}: {data['total_tokens']:,} tokens (${data['cost_usd']:.4f})")

        if result['by_expert']:
            print("\n👤 By Expert:")
            for expert, data in result['by_expert'].items():
                print(f"  {expert}: {data['total_tokens']:,} tokens (${data['cost_usd']:.4f})")

        if result['by_iteration']:
            print("\n🔄 By Iteration:")
            for iteration, data in sorted(result['by_iteration'].items()):
                print(f"  Iteration {iteration}: {data['total_tokens']:,} tokens (${data['cost_usd']:.4f})")
        print()
    else:
        # JSON output
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
