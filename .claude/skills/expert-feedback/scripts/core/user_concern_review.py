#!/usr/bin/env python3
"""
Present concerns to user and collect decisions.

This script provides an interactive CLI for users to review each concern
and decide whether to agree (address it) or disagree (skip it).
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from file_io.json_ops import load_json, save_json


def format_concern_for_user(
    concern: Dict[str, Any],
    concern_num: int,
    total_concerns: int
) -> str:
    """
    Format a concern for user display.

    Args:
        concern: Concern data dict
        concern_num: Concern number (1-indexed)
        total_concerns: Total number of concerns

    Returns:
        Formatted string for display
    """
    severity_emoji = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    emoji = severity_emoji.get(concern.get("severity", "medium"), "⚪")

    lines = []
    lines.append("=" * 70)
    lines.append(f"Concern {concern_num} of {total_concerns}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"{emoji} {concern['severity'].upper()} SEVERITY")
    lines.append(f"📝 {concern['title']}")
    lines.append("")

    experts = concern.get("experts", [])
    expert_str = ', '.join([e.capitalize() for e in experts])
    plural = 's' if len(experts) > 1 else ''
    lines.append(f"Raised by: {expert_str} ({len(experts)} expert{plural})")

    consensus = concern.get("consensus_level", "unknown")
    lines.append(f"Consensus: {consensus.capitalize()}")
    lines.append("")

    lines.append("Description:")
    lines.append(concern["description"])
    lines.append("")

    lines.append("Recommendation:")
    lines.append(concern["recommendation"])
    lines.append("")

    return "\n".join(lines)


def user_concern_review_interactive(
    workspace: Path,
    synthesized_concerns: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Interactive user concern review.

    Args:
        workspace: Workspace path
        synthesized_concerns: Synthesized concerns data

    Returns:
        Dict with user decisions:
            - concerns_reviewed: Total number of concerns
            - concerns_agreed: List of concerns user agreed with
            - concerns_disagreed: List of concerns user disagreed with
            - should_iterate: Boolean indicating if iteration is needed
    """
    concerns_by_theme = synthesized_concerns.get("concerns_by_theme", {})

    # Flatten concerns
    all_concerns = []
    for theme, concerns in concerns_by_theme.items():
        for concern in concerns:
            concern["theme"] = theme
            all_concerns.append(concern)

    if not all_concerns:
        print("✅ No concerns raised! All experts approved.", file=sys.stderr)
        result = {
            "concerns_reviewed": 0,
            "concerns_agreed": [],
            "concerns_disagreed": [],
            "should_iterate": False
        }

        # Save empty decisions file
        concern_review_dir = workspace / "artifact" / "concern-review-1"
        concern_review_dir.mkdir(parents=True, exist_ok=True)
        decision_file = concern_review_dir / "user-concern-decisions.json"
        save_json(result, decision_file)

        return result

    print("\n", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("EXPERT CONCERN REVIEW", file=sys.stderr)
    print(f"{len(all_concerns)} concern(s) raised for your review", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("\n", file=sys.stderr)

    concerns_agreed = []
    concerns_disagreed = []

    for i, concern in enumerate(all_concerns, 1):
        print(format_concern_for_user(concern, i, len(all_concerns)), file=sys.stderr)

        # Get user decision
        while True:
            decision_input = input("Do you agree with this concern? (agree/disagree): ").strip().lower()
            if decision_input in ["agree", "a", "yes", "y"]:
                decision = "agree"
                break
            elif decision_input in ["disagree", "d", "no", "n"]:
                decision = "disagree"
                break
            else:
                print("Invalid input. Please enter 'agree' or 'disagree'", file=sys.stderr)

        # Get additional context if agreed
        if decision == "agree":
            context = input("\nAdditional context (optional, press Enter to skip): ").strip()
            concerns_agreed.append({
                "concern_id": concern["concern_id"],
                "title": concern["title"],
                "theme": concern["theme"],
                "severity": concern["severity"],
                "experts": concern["experts"],
                "consensus_level": concern["consensus_level"],
                "description": concern["description"],
                "recommendation": concern["recommendation"],
                "user_context": context if context else ""
            })
            print("✅ Concern marked for addressing\n", file=sys.stderr)
        else:
            reason = input("\nReason for disagreeing (optional): ").strip()
            concerns_disagreed.append({
                "concern_id": concern["concern_id"],
                "title": concern["title"],
                "reason": reason if reason else ""
            })
            print("❌ Concern will not be addressed\n", file=sys.stderr)

    # Summary
    print("\n", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"Concerns agreed: {len(concerns_agreed)}", file=sys.stderr)
    print(f"Concerns disagreed: {len(concerns_disagreed)}", file=sys.stderr)
    print("", file=sys.stderr)

    if concerns_agreed:
        print("The following concerns will be addressed:", file=sys.stderr)
        for c in concerns_agreed:
            print(f"  - [{c['severity'].upper()}] {c['title']}", file=sys.stderr)
        print("", file=sys.stderr)

    result = {
        "concerns_reviewed": len(all_concerns),
        "concerns_agreed": concerns_agreed,
        "concerns_disagreed": concerns_disagreed,
        "should_iterate": len(concerns_agreed) > 0
    }

    # Save user decisions
    # Determine concern review directory
    concern_state = workspace / "state.json"
    if concern_state.exists():
        state_data = load_json(concern_state)
        concern_review = state_data.get("concern_review", {})
        iteration = concern_review.get("iteration", 1)
    else:
        iteration = 1

    concern_review_dir = workspace / "artifact" / f"concern-review-{iteration}"
    concern_review_dir.mkdir(parents=True, exist_ok=True)
    decision_file = concern_review_dir / "user-concern-decisions.json"
    save_json(result, decision_file)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Interactive user concern review")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--synthesized-concerns", required=True, type=Path, help="Path to synthesized concerns JSON")

    args = parser.parse_args()

    # Load synthesized concerns
    synthesized_data = load_json(args.synthesized_concerns)

    # Run interactive review
    result = user_concern_review_interactive(
        workspace=args.workspace,
        synthesized_concerns=synthesized_data
    )

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit code indicates if iteration needed
    sys.exit(0 if result["should_iterate"] else 1)
