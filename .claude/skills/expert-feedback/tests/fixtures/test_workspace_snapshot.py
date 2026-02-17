"""
Unit tests for workspace snapshot functionality.

Tests the WorkspaceSnapshot class that enables test chaining by
saving/restoring complete workspace state.
"""
import sys
from pathlib import Path

# Add tests directory to path so we can import fixtures
_tests_dir = Path(__file__).parent.parent
sys.path.insert(0, str(_tests_dir))

import pytest
import json
import shutil
from fixtures.workspace_snapshot import (
    WorkspaceSnapshot,
    snapshot_workspace,
    restore_workspace,
    has_snapshot,
    get_snapshot_info
)


class TestWorkspaceSnapshot:
    """Test WorkspaceSnapshot class."""

    @pytest.fixture
    def test_workspace(self, tmp_path):
        """Create a test workspace with state.json."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create state.json
        state_data = {
            "iteration": 1,
            "experts": ["typescript", "python"],
            "convergence_percent": 45,
            "phase": "expert-review"
        }
        (workspace / "state.json").write_text(json.dumps(state_data, indent=2))

        # Create some dummy files
        (workspace / "file1.txt").write_text("content1")
        subdir = workspace / "subdir"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("content2")

        return workspace

    @pytest.fixture
    def recordings_dir(self, tmp_path):
        """Create a recordings directory."""
        recordings = tmp_path / "recordings"
        recordings.mkdir()
        return recordings

    def test_save_workspace_snapshot(self, test_workspace, recordings_dir):
        """Test saving a workspace snapshot."""
        snapshot = WorkspaceSnapshot("test_example", recordings_dir)

        # Save snapshot
        snapshot.save(test_workspace)

        # Verify snapshot directory created
        assert snapshot.snapshot_dir.exists()
        assert snapshot.snapshot_dir.is_dir()

        # Verify state.json copied
        assert (snapshot.snapshot_dir / "state.json").exists()

        # Verify other files copied
        assert (snapshot.snapshot_dir / "file1.txt").exists()
        assert (snapshot.snapshot_dir / "subdir" / "file2.txt").exists()

        # Verify content preserved
        assert (snapshot.snapshot_dir / "file1.txt").read_text() == "content1"
        assert (snapshot.snapshot_dir / "subdir" / "file2.txt").read_text() == "content2"

    def test_restore_workspace_snapshot(self, test_workspace, recordings_dir):
        """Test restoring a workspace from snapshot."""
        snapshot = WorkspaceSnapshot("test_example", recordings_dir)

        # Save snapshot
        snapshot.save(test_workspace)

        # Modify original workspace
        (test_workspace / "file1.txt").write_text("modified")
        (test_workspace / "new_file.txt").write_text("new")

        # Create new workspace location
        restore_location = test_workspace.parent / "restored"

        # Restore snapshot
        snapshot.restore(restore_location)

        # Verify restored files
        assert (restore_location / "state.json").exists()
        assert (restore_location / "file1.txt").exists()
        assert (restore_location / "subdir" / "file2.txt").exists()

        # Verify original content restored (not modified version)
        assert (restore_location / "file1.txt").read_text() == "content1"

        # Verify new file not in snapshot
        assert not (restore_location / "new_file.txt").exists()

    def test_snapshot_validation(self, test_workspace, recordings_dir):
        """Test that snapshot requires state.json."""
        workspace_no_state = test_workspace.parent / "no_state"
        workspace_no_state.mkdir()
        (workspace_no_state / "file1.txt").write_text("content")

        snapshot = WorkspaceSnapshot("test_validation", recordings_dir)

        # Should fail: no state.json
        with pytest.raises(ValueError, match="missing state.json"):
            snapshot.save(workspace_no_state)

    def test_snapshot_exists_check(self, test_workspace, recordings_dir):
        """Test exists() logic."""
        snapshot = WorkspaceSnapshot("test_exists", recordings_dir)

        # Should not exist initially
        assert not snapshot.exists()

        # Save snapshot
        snapshot.save(test_workspace)

        # Should exist now
        assert snapshot.exists()

        # Remove state.json from snapshot
        (snapshot.snapshot_dir / "state.json").unlink()

        # Should not exist (state.json missing)
        assert not snapshot.exists()

    def test_nonexistent_snapshot_restore(self, test_workspace, recordings_dir):
        """Test error handling when restoring non-existent snapshot."""
        snapshot = WorkspaceSnapshot("test_nonexistent", recordings_dir)

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="No snapshot found"):
            snapshot.restore(test_workspace.parent / "restore_target")

    def test_get_state(self, test_workspace, recordings_dir):
        """Test reading state.json without full restore."""
        snapshot = WorkspaceSnapshot("test_state", recordings_dir)

        # Save snapshot
        snapshot.save(test_workspace)

        # Get state
        state = snapshot.get_state()

        # Verify state contents
        assert state["iteration"] == 1
        assert state["experts"] == ["typescript", "python"]
        assert state["convergence_percent"] == 45
        assert state["phase"] == "expert-review"

    def test_get_info(self, test_workspace, recordings_dir):
        """Test getting snapshot metadata."""
        snapshot = WorkspaceSnapshot("test_info", recordings_dir)

        # No snapshot yet
        assert snapshot.get_info() is None

        # Save snapshot
        snapshot.save(test_workspace)

        # Get info
        info = snapshot.get_info()

        # Verify metadata
        assert info is not None
        assert info["test_name"] == "test_info"
        assert info["file_count"] > 0
        assert info["size_bytes"] > 0
        assert info["size_mb"] > 0
        assert info["has_state"] is True
        assert info["iteration"] == 1
        assert info["experts"] == ["typescript", "python"]
        assert info["convergence_percent"] == 45

    def test_overwrite_existing_snapshot(self, test_workspace, recordings_dir):
        """Test that saving overwrites existing snapshot."""
        snapshot = WorkspaceSnapshot("test_overwrite", recordings_dir)

        # Save initial snapshot
        snapshot.save(test_workspace)
        initial_count = len(list(snapshot.snapshot_dir.rglob("*")))

        # Modify workspace
        (test_workspace / "new_file.txt").write_text("new content")

        # Save again (should overwrite)
        snapshot.save(test_workspace)

        # Verify new file in snapshot
        assert (snapshot.snapshot_dir / "new_file.txt").exists()

        # Verify file count increased
        new_count = len(list(snapshot.snapshot_dir.rglob("*")))
        assert new_count > initial_count


class TestConvenienceFunctions:
    """Test convenience functions for simpler API."""

    @pytest.fixture
    def test_workspace(self, tmp_path):
        """Create a test workspace with state.json."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        state_data = {
            "iteration": 1,
            "experts": ["typescript"],
            "convergence_percent": 50
        }
        (workspace / "state.json").write_text(json.dumps(state_data, indent=2))
        (workspace / "file.txt").write_text("test")

        return workspace

    @pytest.fixture
    def recordings_dir(self, tmp_path):
        """Create a recordings directory."""
        recordings = tmp_path / "recordings"
        recordings.mkdir()
        return recordings

    def test_snapshot_workspace_function(self, test_workspace, recordings_dir):
        """Test snapshot_workspace() convenience function."""
        snapshot_workspace("test_func", test_workspace, recordings_dir)

        # Verify snapshot created
        snapshot_dir = recordings_dir / "test_func" / "workspace"
        assert snapshot_dir.exists()
        assert (snapshot_dir / "state.json").exists()

    def test_restore_workspace_function(self, test_workspace, recordings_dir):
        """Test restore_workspace() convenience function."""
        # Save snapshot
        snapshot_workspace("test_restore_func", test_workspace, recordings_dir)

        # Restore to new location
        restore_location = test_workspace.parent / "restored"
        restore_workspace("test_restore_func", restore_location, recordings_dir)

        # Verify restored
        assert restore_location.exists()
        assert (restore_location / "state.json").exists()

    def test_has_snapshot_function(self, test_workspace, recordings_dir):
        """Test has_snapshot() convenience function."""
        # Should not exist
        assert not has_snapshot("test_has", recordings_dir)

        # Create snapshot
        snapshot_workspace("test_has", test_workspace, recordings_dir)

        # Should exist now
        assert has_snapshot("test_has", recordings_dir)

    def test_get_snapshot_info_function(self, test_workspace, recordings_dir):
        """Test get_snapshot_info() convenience function."""
        # No snapshot
        assert get_snapshot_info("test_info_func", recordings_dir) is None

        # Create snapshot
        snapshot_workspace("test_info_func", test_workspace, recordings_dir)

        # Get info
        info = get_snapshot_info("test_info_func", recordings_dir)

        # Verify
        assert info is not None
        assert info["test_name"] == "test_info_func"
        assert info["has_state"] is True
        assert info["iteration"] == 1
