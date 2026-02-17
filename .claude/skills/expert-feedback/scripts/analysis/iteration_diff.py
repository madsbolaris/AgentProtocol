"""
Generate iteration-to-iteration diffs for expert context (Context Gap Fix 1.2).

Shows what changed between iterations in:
- Expert's own review (concerns resolved, recommendations updated)
- Peer expert reviews (new concerns, changed ratings)
- User answers (questions answered)
- Convergence metrics (progress toward consensus)
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from file_io.json_ops import load_json
from state.manager import StateManager


def generate_iteration_diff(
    workspace: Path,
    expert_name: str,
    current_iteration: int,
    state_manager: Optional[StateManager] = None
) -> Dict[str, Any]:
    """
    Generate diff between current and previous iteration.

    Args:
        workspace: Workspace path
        expert_name: Name of the expert
        current_iteration: Current iteration number
        state_manager: Optional StateManager instance

    Returns:
        Dictionary with:
        - own_review_changes: Expert's own review evolution
        - peer_changes: Peer expert review updates
        - user_feedback: User answers to questions
        - convergence_change: Convergence progress
    """
    if current_iteration == 1:
        return {}  # No diff for iteration 1

    prev_iteration = current_iteration - 1

    return {
        "own_review_changes": _diff_own_review(workspace, expert_name, prev_iteration),
        "peer_changes": _diff_peer_reviews(workspace, expert_name, current_iteration),
        "user_feedback": _diff_user_answers(workspace, expert_name, prev_iteration),
        "convergence_change": _diff_convergence(workspace, prev_iteration, current_iteration, state_manager)
    }


def _diff_own_review(workspace: Path, expert: str, prev_iteration: int) -> Dict[str, Any]:
    """
    Compare expert's own review between iterations.

    Returns:
        Dict with previous and current DX rating, concerns count, recommendations count
    """
    prev_state_file = workspace / f"iteration-{prev_iteration}" / "experts" / expert / "state.json"
    current_state_file = workspace / f"iteration-{prev_iteration + 1}" / "experts" / expert / "state.json"

    if not prev_state_file.exists():
        return {}

    try:
        # Read expert state files directly (not workspace state.json)
        prev_data = json.loads(prev_state_file.read_text())

        # Try to load current iteration data if it exists
        current_data = {}
        if current_state_file.exists():
            try:
                current_data = json.loads(current_state_file.read_text())
            except Exception:
                pass  # Current iteration data may not exist yet

        prev_dx = prev_data.get("dx_rating", {}).get("stars", 0)
        current_dx = current_data.get("dx_rating", {}).get("stars", 0) if current_data else 0
        prev_concerns = len(prev_data.get("concerns", []))
        current_concerns = len(current_data.get("concerns", [])) if current_data else 0
        prev_recs = len(prev_data.get("recommendations", []))
        current_recs = len(current_data.get("recommendations", [])) if current_data else 0

        return {
            "dx_rating_previous": prev_dx,
            "dx_rating_current": current_dx,
            "dx_rating_delta": current_dx - prev_dx,
            "concerns_count_previous": prev_concerns,
            "concerns_count_current": current_concerns,
            "concerns_count_delta": current_concerns - prev_concerns,
            "recommendations_count_previous": prev_recs,
            "recommendations_count_current": current_recs,
            "recommendations_count_delta": current_recs - prev_recs,
            "top_concerns_previous": [
                c.get("title", "Unknown")
                for c in prev_data.get("concerns", [])[:3]
            ]
        }
    except Exception as e:
        return {"error": str(e)}


def _diff_peer_reviews(workspace: Path, expert: str, iteration: int) -> Dict[str, Any]:
    """
    Get peer expert reviews for the current iteration.

    Returns:
        Dict mapping peer names to their current review summaries
    """
    experts_dir = workspace / f"iteration-{iteration}" / "experts"

    if not experts_dir.exists():
        return {}

    peer_changes = {}
    try:
        # Iterate through expert subdirectories
        for expert_subdir in experts_dir.iterdir():
            if not expert_subdir.is_dir():
                continue

            peer_name = expert_subdir.name
            if peer_name == expert:
                continue  # Skip own review

            state_file = expert_subdir / "state.json"
            if not state_file.exists():
                continue

            try:
                # Read expert state file directly (not workspace state.json)
                peer_data = json.loads(state_file.read_text())
                peer_changes[peer_name] = {
                    "dx_rating": peer_data.get("dx_rating", {}).get("stars", 0),
                    "concerns_count": len(peer_data.get("concerns", [])),
                    "recommendations_count": len(peer_data.get("recommendations", [])),
                    "top_concerns": [
                        c.get("title", "Unknown")
                        for c in peer_data.get("concerns", [])[:3]
                    ] if peer_data.get("concerns") else []
                }
            except Exception:
                continue  # Skip if can't load peer data

        return peer_changes
    except Exception as e:
        return {"error": str(e)}


def _diff_user_answers(workspace: Path, expert: str, prev_iteration: int) -> Dict[str, Any]:
    """
    Count user answers to questions from previous iteration.

    Returns:
        Dict with questions_answered count and expert's questions answered
    """
    # Load questions from previous iteration
    prev_questions_file = workspace / f"iteration-{prev_iteration}" / "questions.json"

    if not prev_questions_file.exists():
        return {"questions_total": 0, "questions_answered": 0, "your_questions_answered": 0}

    try:
        questions_data = load_json(prev_questions_file)
        questions = questions_data.get("questions", [])

        # Count answered questions (questions with non-null "answer" field)
        answered_count = len([q for q in questions if q.get("answer") is not None])

        # Count expert's questions that were answered
        expert_questions_answered = len([
            q for q in questions
            if q.get("answer") is not None and expert in q.get("asked_by", [])
        ])

        return {
            "questions_total": len(questions),
            "questions_answered": answered_count,
            "your_questions_answered": expert_questions_answered
        }
    except Exception as e:
        return {"error": str(e)}


def _diff_convergence(
    workspace: Path,
    prev_iteration: int,
    current_iteration: int,
    state_manager: Optional[StateManager] = None
) -> Dict[str, Any]:
    """
    Calculate convergence change between iterations.

    Returns:
        Dict with 'from', 'to', and 'delta' convergence percentages
    """
    if not state_manager:
        state_manager = StateManager(workspace)

    try:
        state = state_manager.load()

        if not state.iteration_history:
            return {}

        # Find previous iteration summary
        prev_summary = next(
            (h for h in state.iteration_history if h["iteration"] == prev_iteration),
            None
        )

        # Find current iteration summary
        current_summary = next(
            (h for h in state.iteration_history if h["iteration"] == current_iteration),
            None
        )

        if not prev_summary or not current_summary:
            return {}

        prev_convergence = prev_summary["convergence_percent"]
        current_convergence = current_summary["convergence_percent"]

        return {
            "from": prev_convergence,
            "to": current_convergence,
            "delta": current_convergence - prev_convergence,
            "trending_up": current_convergence > prev_convergence
        }
    except Exception as e:
        return {"error": str(e)}


def format_diff_summary(diff: Dict[str, Any], expert_name: str) -> str:
    """
    Format iteration diff as human-readable summary.

    Args:
        diff: Diff dictionary from generate_iteration_diff()
        expert_name: Name of the expert

    Returns:
        Formatted string summarizing changes
    """
    if not diff:
        return "No iteration diff available (iteration 1)"

    lines = []
    lines.append(f"Iteration Diff for {expert_name}")
    lines.append("=" * 60)

    # Own review changes
    if "own_review_changes" in diff and diff["own_review_changes"]:
        own = diff["own_review_changes"]
        lines.append("\nYour Previous Review:")
        lines.append(f"  DX Rating: {own.get('dx_rating_previous', 'N/A')}/5 stars")
        lines.append(f"  Concerns Raised: {own.get('concerns_count_previous', 0)}")
        lines.append(f"  Recommendations: {own.get('recommendations_count_previous', 0)}")

    # Convergence change
    if "convergence_change" in diff and diff["convergence_change"]:
        conv = diff["convergence_change"]
        delta_sign = "+" if conv.get("delta", 0) > 0 else ""
        lines.append("\nConvergence Progress:")
        lines.append(f"  {conv.get('from', 0)}% → {conv.get('to', 0)}% ({delta_sign}{conv.get('delta', 0)}%)")
        if conv.get("trending_up"):
            lines.append("  ✅ Trending upward")
        else:
            lines.append("  ⚠️ Not improving")

    # User feedback
    if "user_feedback" in diff and diff["user_feedback"]:
        uf = diff["user_feedback"]
        lines.append("\nUser Engagement:")
        lines.append(f"  Questions Answered: {uf.get('questions_answered', 0)}/{uf.get('questions_total', 0)}")
        if uf.get("your_questions_answered", 0) > 0:
            lines.append(f"  ✅ {uf['your_questions_answered']} of YOUR questions were answered")

    # Peer changes
    if "peer_changes" in diff and diff["peer_changes"]:
        lines.append("\nPeer Expert Updates:")
        for peer_name, changes in diff["peer_changes"].items():
            lines.append(f"  {peer_name}: {changes.get('dx_rating', 0)}/5 stars ({changes.get('concerns_count', 0)} concerns)")

    return "\n".join(lines)


if __name__ == "__main__":
    """Test the iteration diff generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate iteration diff")
    parser.add_argument("--workspace", required=True, help="Workspace directory")
    parser.add_argument("--expert", required=True, help="Expert name")
    parser.add_argument("--iteration", type=int, required=True, help="Current iteration")

    args = parser.parse_args()

    workspace = Path(args.workspace)
    diff = generate_iteration_diff(workspace, args.expert, args.iteration)

    print(format_diff_summary(diff, args.expert))
