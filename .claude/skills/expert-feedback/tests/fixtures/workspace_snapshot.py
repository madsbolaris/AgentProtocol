"""
Workspace snapshot management for test chaining.

Enables tests to save/restore complete workspace state, avoiding redundant
expert execution by reusing results from previous tests.

Usage:
    # Save snapshot
    snapshot = WorkspaceSnapshot("test_name", recordings_dir)
    snapshot.save(workspace)

    # Restore snapshot
    if snapshot.exists():
        snapshot.restore(workspace)
"""
from pathlib import Path
from typing import Optional
import shutil
import json


class WorkspaceSnapshot:
    """Manage workspace snapshots for test chaining."""

    def __init__(self, test_name: str, recordings_dir: Path):
        """
        Initialize snapshot manager.

        Args:
            test_name: Name of the test (e.g., "test_generate_iteration_1_with_questions")
            recordings_dir: Base recordings directory (tests/recordings/)
        """
        self.test_name = test_name
        self.recordings_dir = Path(recordings_dir)
        self.snapshot_dir = self.recordings_dir / test_name / "workspace"

    def exists(self) -> bool:
        """
        Check if snapshot exists and is valid.

        Returns:
            True if snapshot exists with state.json, False otherwise
        """
        return (
            self.snapshot_dir.exists() and
            self.snapshot_dir.is_dir() and
            (self.snapshot_dir / "state.json").exists()
        )

    def save(self, workspace: Path) -> None:
        """
        Save complete workspace to snapshot.

        Creates a complete copy of the workspace directory tree in
        the recordings directory alongside the LLM recordings.

        Args:
            workspace: Path to workspace directory to snapshot

        Raises:
            ValueError: If workspace missing state.json or snapshot invalid
        """
        workspace = Path(workspace)

        # Validate source workspace
        if not workspace.exists():
            raise ValueError(f"Workspace does not exist: {workspace}")

        if not (workspace / "state.json").exists():
            raise ValueError(f"Workspace missing state.json: {workspace}")

        print(f"  📸 Capturing workspace snapshot: {self.test_name}")

        # Remove existing snapshot
        if self.snapshot_dir.exists():
            shutil.rmtree(self.snapshot_dir)

        # Create snapshot directory
        self.snapshot_dir.parent.mkdir(parents=True, exist_ok=True)

        # Copy entire workspace
        shutil.copytree(workspace, self.snapshot_dir)

        # Validate snapshot
        if not (self.snapshot_dir / "state.json").exists():
            raise ValueError(f"Snapshot missing state.json after copy")

        # Count files for logging
        file_count = len(list(self.snapshot_dir.rglob("*")))
        total_size = sum(
            f.stat().st_size
            for f in self.snapshot_dir.rglob("*")
            if f.is_file()
        )
        size_mb = total_size / (1024 * 1024)

        print(f"     ✅ Saved {file_count} files ({size_mb:.2f} MB) to snapshot")

    def restore(self, workspace: Path) -> None:
        """
        Restore workspace from snapshot.

        Replaces the current workspace with a copy of the snapshot.

        Args:
            workspace: Path to workspace directory to restore into

        Raises:
            FileNotFoundError: If snapshot doesn't exist
            ValueError: If snapshot is invalid
        """
        workspace = Path(workspace)

        if not self.exists():
            raise FileNotFoundError(
                f"No snapshot found for {self.test_name}. "
                f"Expected at: {self.snapshot_dir}"
            )

        print(f"  📂 Restoring workspace from snapshot: {self.test_name}")

        # Remove existing workspace
        if workspace.exists():
            shutil.rmtree(workspace)

        # Copy snapshot to workspace
        shutil.copytree(self.snapshot_dir, workspace)

        # Validate restored workspace
        if not (workspace / "state.json").exists():
            raise ValueError(f"Restored workspace missing state.json")

        # Count files for logging
        file_count = len(list(workspace.rglob("*")))
        total_size = sum(
            f.stat().st_size
            for f in workspace.rglob("*")
            if f.is_file()
        )
        size_mb = total_size / (1024 * 1024)

        print(f"     ✅ Restored {file_count} files ({size_mb:.2f} MB) from snapshot")

    def get_state(self) -> dict:
        """
        Read state.json from snapshot without full restoration.

        Useful for checking convergence, iteration, or other state
        without copying the entire workspace.

        Returns:
            Dictionary containing state.json contents

        Raises:
            FileNotFoundError: If snapshot doesn't exist
        """
        if not self.exists():
            raise FileNotFoundError(
                f"No snapshot found for {self.test_name}"
            )

        state_file = self.snapshot_dir / "state.json"
        return json.loads(state_file.read_text())

    def get_info(self) -> Optional[dict]:
        """
        Get snapshot metadata without validation.

        Returns:
            Dict with size, file count, and state info, or None if doesn't exist
        """
        if not self.snapshot_dir.exists():
            return None

        file_count = len(list(self.snapshot_dir.rglob("*")))
        total_size = sum(
            f.stat().st_size
            for f in self.snapshot_dir.rglob("*")
            if f.is_file()
        )

        info = {
            "test_name": self.test_name,
            "path": str(self.snapshot_dir),
            "file_count": file_count,
            "size_bytes": total_size,
            "size_mb": total_size / (1024 * 1024),
            "has_state": (self.snapshot_dir / "state.json").exists()
        }

        # Try to read state if available
        if info["has_state"]:
            try:
                state = self.get_state()
                info["iteration"] = state.get("iteration")
                info["experts"] = state.get("experts", [])
                info["convergence_percent"] = state.get("convergence_percent")
            except Exception:
                pass

        return info


# Convenience functions for simpler usage


def snapshot_workspace(test_name: str, workspace: Path, recordings_dir: Path) -> None:
    """
    Save workspace snapshot.

    Args:
        test_name: Name of the test
        workspace: Workspace directory path
        recordings_dir: Base recordings directory
    """
    snapshot = WorkspaceSnapshot(test_name, recordings_dir)
    snapshot.save(workspace)


def restore_workspace(test_name: str, workspace: Path, recordings_dir: Path) -> None:
    """
    Restore workspace from snapshot.

    Args:
        test_name: Name of the test with snapshot
        workspace: Workspace directory to restore into
        recordings_dir: Base recordings directory

    Raises:
        FileNotFoundError: If snapshot doesn't exist
    """
    snapshot = WorkspaceSnapshot(test_name, recordings_dir)
    snapshot.restore(workspace)


def has_snapshot(test_name: str, recordings_dir: Path) -> bool:
    """
    Check if snapshot exists.

    Args:
        test_name: Name of the test
        recordings_dir: Base recordings directory

    Returns:
        True if valid snapshot exists
    """
    return WorkspaceSnapshot(test_name, recordings_dir).exists()


def get_snapshot_info(test_name: str, recordings_dir: Path) -> Optional[dict]:
    """
    Get snapshot metadata.

    Args:
        test_name: Name of the test
        recordings_dir: Base recordings directory

    Returns:
        Dict with snapshot info, or None if doesn't exist
    """
    return WorkspaceSnapshot(test_name, recordings_dir).get_info()
