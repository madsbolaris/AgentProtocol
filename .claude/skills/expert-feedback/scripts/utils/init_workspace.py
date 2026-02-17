#!/usr/bin/env python3
"""
Initialize deterministic workspace structure for expert-feedback.

Creates organized folder structure:
.workspace/YYYY/MM/DD/expert-feedback-{slug}/
├── state.json
├── iteration-1/
│   ├── experts/
│   │   └── scripts/
│   │       └── outputs/
│   └── consolidated.md
└── logs/

Usage:
    python3 scripts/init_workspace.py --topic "My Topic" --experts typescript python dx --mode review
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List


def slugify(text: str) -> str:
    """Convert text to slug."""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    return text[:50]


def find_repo_root() -> Path:
    """Find git repository root by looking for .git directory."""
    current = Path.cwd().resolve()

    # Walk up the directory tree looking for .git
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent

    # Fallback to current directory if no .git found
    return current


def create_workspace(
    topic: str,
    experts: List[str],
    mode: str = "review",
    base_dir: Path = None
) -> Path:
    """Create deterministic workspace structure."""

    # Use .workspace at repository root by default
    if base_dir is None:
        repo_root = find_repo_root()
        base_dir = repo_root / ".workspace"

    # Create dated folder: .workspace/YYYY/MM/DD/
    now = datetime.now()
    date_dir = base_dir / f"{now.year:04d}" / f"{now.month:02d}" / f"{now.day:02d}"

    # Create topic slug
    slug = slugify(topic)
    workspace = date_dir / f"expert-feedback-{slug}"

    # Create directories
    workspace.mkdir(parents=True, exist_ok=True)

    # Create iteration-1 structure
    iteration_dir = workspace / "iteration-1"
    iteration_dir.mkdir(exist_ok=True)

    # Create experts directory with subfolders for each expert
    experts_dir = iteration_dir / "experts"
    experts_dir.mkdir(exist_ok=True)

    for expert in experts:
        expert_dir = experts_dir / expert
        expert_dir.mkdir(exist_ok=True)

        # Create scripts and outputs folders
        (expert_dir / "scripts").mkdir(exist_ok=True)
        (expert_dir / "scripts" / "outputs").mkdir(exist_ok=True)

    # Create logs directory
    logs_dir = workspace / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create initial state.json
    state = {
        "topic": topic,
        "mode": mode,
        "experts": experts,
        "iteration": 1,
        "convergence_percent": 0.0,
        "consensus_reached": False,
        "phase": "spawning_experts",  # Initial phase for web UI
        "expert_results": {},
        "created_at": datetime.now().astimezone().isoformat(),
        "convergence_target": 80
    }

    state_file = workspace / "state.json"
    state_file.write_text(json.dumps(state, indent=2))

    # Create README
    readme = f"""# Expert Feedback Session: {topic}

**Mode:** {mode}
**Experts:** {', '.join(experts)}
**Created:** {now.strftime('%Y-%m-%d %H:%M:%S')}

## Workspace Structure

- `state.json` - Master state file
- `qa-answers.json` - User Q&A responses (created during session)
- `approvals.json` - Recommendation approvals (created during session)
- `iteration-N/` - Each iteration's data
  - `experts/` - Expert reviews
    - `review-{expert}.md` - Expert review (source of truth, front and center)
    - `{expert}/` - Per-expert folder (for auto-generated files)
      - `state.json` - Parsed from markdown
      - `questions.json` - Parsed from markdown
      - `scripts/` - Scripts created by expert
      - `scripts/outputs/` - Script outputs
  - `consolidated.md` - Consolidated feedback (source of truth)
  - `state.json` - Iteration state (parsed from consolidated.md)
  - `questions.json` - Consolidated questions
- `logs/` - Execution logs
- `draft-{mode}.md` - Final draft artifact

## Web UI

Access the session UI at: http://localhost:8765

## Progress

Track expert progress in real-time through the web UI.
"""

    readme_file = workspace / "README.md"
    readme_file.write_text(readme)

    print(f"✅ Workspace created: {workspace}")
    print(f"📁 Structure:")
    print(f"   - State: {state_file}")
    print(f"   - Iteration: {iteration_dir}")
    print(f"   - Experts: {experts_dir}")
    print(f"   - Logs: {logs_dir}")

    return workspace


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Initialize expert-feedback workspace")
    parser.add_argument("--topic", type=str, required=True, help="Topic for feedback")
    parser.add_argument("--experts", nargs="+", required=True, help="Expert names")
    parser.add_argument("--mode", type=str, default="review", choices=["review", "improve", "create"], help="Feedback mode")
    parser.add_argument("--base-dir", type=Path, help="Base directory (default: .workspace)")

    args = parser.parse_args()

    workspace = create_workspace(
        topic=args.topic,
        experts=args.experts,
        mode=args.mode,
        base_dir=args.base_dir
    )

    # Print workspace path for scripts to capture
    print(f"\nWORKSPACE={workspace}")

    return 0


if __name__ == "__main__":
    exit(main())
