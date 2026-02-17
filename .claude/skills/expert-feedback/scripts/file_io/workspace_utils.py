"""
Workspace path utilities for expert-feedback skill.

Canonical workspace structure (Phase 2.4 - No backward compatibility):

workspace/
├── state.json                      # Workflow state
├── iteration-1/
│   ├── experts/
│   │   ├── review-typescript.md    # ✓ Markdown front and center
│   │   ├── review-python.md
│   │   ├── typescript/             # ✓ JSON organized in subdirs
│   │   │   ├── state.json
│   │   │   ├── questions.json
│   │   │   └── scripts/
│   │   │       └── outputs/
│   │   └── python/
│   │       ├── state.json
│   │       ├── questions.json
│   │       └── scripts/outputs/
│   ├── synthesized.md
│   ├── questions.json
│   └── qa-answers.json
├── iteration-2/
│   └── [same structure]
├── artifacts/
│   ├── draft-adr.md
│   ├── draft-plan.md
│   └── final-*.md
└── logs/
    ├── expert-typescript.log
    └── synthesis.log

See docs/workspace-structure.md for complete documentation.
"""

from pathlib import Path
from typing import Optional, Dict


class WorkspacePaths:
    """Canonical workspace path definitions.

    This is the ONLY supported structure. No backward compatibility.

    Usage:
        paths = WorkspacePaths(workspace)
        review_file = paths.expert_review_md("typescript", 1)
    """

    def __init__(self, workspace: Path):
        """Initialize workspace paths.

        Args:
            workspace: Path to workspace root directory
        """
        self.root = Path(workspace)

    # ===== State Files =====

    @property
    def state(self) -> Path:
        """state.json - workflow state and convergence"""
        return self.root / "state.json"

    # ===== Iteration Directories =====

    def iteration_dir(self, iteration: int) -> Path:
        """iteration-{N}/ directory"""
        return self.root / f"iteration-{iteration}"

    def experts_dir(self, iteration: int) -> Path:
        """iteration-{N}/experts/ directory"""
        return self.iteration_dir(iteration) / "experts"

    def expert_dir(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/{expert}/ directory"""
        return self.experts_dir(iteration) / expert

    # ===== Expert Files =====

    def expert_review_md(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/review-{expert}.md (front and center)"""
        return self.experts_dir(iteration) / f"review-{expert}.md"

    def expert_state_json(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/{expert}/state.json (auto-generated, organized in subdir)"""
        return self.expert_dir(expert, iteration) / "state.json"

    def expert_questions_json(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/{expert}/questions.json (auto-generated, organized in subdir)"""
        return self.expert_dir(expert, iteration) / "questions.json"

    def expert_scripts_dir(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/{expert}/scripts/ directory"""
        return self.expert_dir(expert, iteration) / "scripts"

    def expert_scripts_outputs_dir(self, expert: str, iteration: int) -> Path:
        """iteration-{N}/experts/{expert}/scripts/outputs/ directory"""
        return self.expert_scripts_dir(expert, iteration) / "outputs"

    # ===== Consolidation Files =====

    def synthesized_md(self, iteration: int) -> Path:
        """iteration-{N}/synthesized.md"""
        return self.iteration_dir(iteration) / "synthesized.md"

    def questions_json(self, iteration: int) -> Path:
        """iteration-{N}/questions.json"""
        return self.iteration_dir(iteration) / "questions.json"

    def qa_answers_json(self, iteration: int) -> Path:
        """iteration-{N}/qa-answers.json"""
        return self.iteration_dir(iteration) / "qa-answers.json"

    # ===== Artifacts =====

    @property
    def artifacts_dir(self) -> Path:
        """artifacts/ directory"""
        return self.root / "artifacts"

    def artifact_path(self, filename: str) -> Path:
        """artifacts/{filename}"""
        return self.artifacts_dir / filename

    # ===== Logs =====

    @property
    def logs_dir(self) -> Path:
        """logs/ directory"""
        return self.root / "logs"

    def log_path(self, name: str) -> Path:
        """logs/{name}.log"""
        return self.logs_dir / f"{name}.log"

    # ===== Helpers =====

    def ensure_structure(self, experts: list[str], iteration: int):
        """Create all necessary directories for iteration.

        Args:
            experts: List of expert names
            iteration: Iteration number
        """
        # Create iteration and expert directories
        for expert in experts:
            self.expert_dir(expert, iteration).mkdir(parents=True, exist_ok=True)
            self.expert_scripts_outputs_dir(expert, iteration).mkdir(parents=True, exist_ok=True)

        # Create artifact and log directories
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# ===== Convenience Functions =====

def load_workspace_paths(workspace: Path) -> WorkspacePaths:
    """Load workspace paths for given workspace.

    Args:
        workspace: Path to workspace directory

    Returns:
        WorkspacePaths instance
    """
    return WorkspacePaths(workspace)


def get_artifact_path(workspace: Path, mode: str = "improve") -> Path:
    """
    Get path for final artifact file.

    Args:
        workspace: Workspace root directory
        mode: Artifact mode (adr, create, improve, review)

    Returns:
        Path to artifact file in workspace root

    Example:
        >>> workspace = Path(".workspace/my-review")
        >>> artifact_path = get_artifact_path(workspace, "improve")
        >>> print(artifact_path)
        .workspace/my-review/draft-plan.md
    """
    if mode == "adr" or mode == "review":
        # ADR mode uses JSON data file
        return workspace / "adr-data.json"
    elif mode == "create":
        # Create mode uses draft-plan.md (same as improve)
        return workspace / "draft-plan.md"
    else:  # improve or default
        return workspace / "draft-plan.md"


def list_iterations(workspace: Path) -> list[int]:
    """List all iteration numbers found in the workspace.

    Args:
        workspace: Path to workspace root

    Returns:
        Sorted list of iteration numbers (1, 2, 3, ...)
    """
    iterations = []

    # Check for iteration-N directories
    for item in workspace.iterdir():
        if item.is_dir() and item.name.startswith("iteration-"):
            try:
                iteration_num = int(item.name.replace("iteration-", ""))
                iterations.append(iteration_num)
            except ValueError:
                continue

    return sorted(iterations)
