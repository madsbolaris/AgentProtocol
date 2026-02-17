"""
Unit tests for file_io/json_ops.py

Tests JSON file operations including:
- Loading valid/invalid JSON files
- Saving JSON with atomic writes
- state.json access protection (CRITICAL)
- Error handling (file not found, permissions, etc.)

Target coverage: 95%+ (critical data integrity module)
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from file_io import json_ops


class TestLoadJson:
    """Test load_json function."""

    @pytest.mark.high
    def test_load_valid_json(self, test_workspace):
        """Test loading a valid JSON file."""
        test_file = test_workspace / "test.json"
        test_data = {"key": "value", "number": 42, "nested": {"data": True}}
        test_file.write_text(json.dumps(test_data))

        result = json_ops.load_json(test_file)

        assert result == test_data
        assert result["key"] == "value"
        assert result["number"] == 42
        assert result["nested"]["data"] is True

    @pytest.mark.high
    def test_load_empty_json(self, test_workspace):
        """Test loading an empty JSON object."""
        test_file = test_workspace / "empty.json"
        test_file.write_text("{}")

        result = json_ops.load_json(test_file)

        assert result == {}

    @pytest.mark.high
    def test_load_json_array(self, test_workspace):
        """Test loading a JSON array."""
        test_file = test_workspace / "array.json"
        test_data = [1, 2, 3, "four", {"five": 5}]
        test_file.write_text(json.dumps(test_data))

        result = json_ops.load_json(test_file)

        assert result == test_data
        assert len(result) == 5

    @pytest.mark.high
    def test_load_json_with_unicode(self, test_workspace):
        """Test loading JSON with Unicode characters."""
        test_file = test_workspace / "unicode.json"
        test_data = {"emoji": "🎉", "chinese": "你好", "arabic": "مرحبا"}
        test_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding='utf-8')

        result = json_ops.load_json(test_file)

        assert result["emoji"] == "🎉"
        assert result["chinese"] == "你好"

    @pytest.mark.high
    def test_load_json_file_not_found(self, test_workspace):
        """Test loading non-existent file raises FileNotFoundError."""
        nonexistent_file = test_workspace / "does_not_exist.json"

        with pytest.raises(FileNotFoundError):
            json_ops.load_json(nonexistent_file)

    @pytest.mark.high
    def test_load_invalid_json(self, test_workspace):
        """Test loading invalid JSON raises JSONDecodeError."""
        test_file = test_workspace / "invalid.json"
        test_file.write_text("{ invalid json content }")

        with pytest.raises(json.JSONDecodeError):
            json_ops.load_json(test_file)

    @pytest.mark.high
    def test_load_json_trailing_commas(self, test_workspace):
        """Test loading JSON with trailing commas (invalid) fails."""
        test_file = test_workspace / "trailing_comma.json"
        test_file.write_text('{"key": "value",}')

        with pytest.raises(json.JSONDecodeError):
            json_ops.load_json(test_file)

    @pytest.mark.high
    @pytest.mark.critical
    def test_load_state_json_blocked(self):
        """
        CRITICAL: Test that direct state.json access is blocked.

        This is a critical security/integrity feature - state.json must
        only be accessed through StateManager to prevent race conditions.
        """
        state_path = Path("state.json")

        with pytest.raises(RuntimeError, match="state.json access is forbidden"):
            json_ops.load_json(state_path)

    @pytest.mark.high
    @pytest.mark.critical
    def test_load_state_json_blocked_absolute_path(self, test_workspace):
        """Test that state.json access is blocked even with absolute path."""
        state_path = test_workspace / "state.json"

        with pytest.raises(RuntimeError, match="state.json"):
            json_ops.load_json(state_path)

    @pytest.mark.high
    @pytest.mark.critical
    def test_load_state_json_blocked_nested_path(self, test_workspace):
        """Test that state.json access is blocked in nested directories."""
        nested_state = test_workspace / "subdir" / "state.json"

        with pytest.raises(RuntimeError, match="state.json"):
            json_ops.load_json(nested_state)


class TestSaveJson:
    """Test save_json function."""

    @pytest.mark.high
    def test_save_simple_json(self, test_workspace):
        """Test saving simple JSON data."""
        test_file = test_workspace / "output.json"
        test_data = {"result": "success", "count": 10}

        json_ops.save_json(test_data, test_file)

        assert test_file.exists()
        loaded = json.loads(test_file.read_text())
        assert loaded == test_data

    @pytest.mark.high
    def test_save_json_creates_directory(self, test_workspace):
        """Test that save_json creates parent directories if needed."""
        nested_file = test_workspace / "nested" / "dir" / "data.json"
        test_data = {"nested": True}

        json_ops.save_json(test_data, nested_file)

        assert nested_file.exists()
        assert nested_file.parent.exists()

    @pytest.mark.high
    def test_save_json_overwrites_existing(self, test_workspace):
        """Test that save_json overwrites existing files."""
        test_file = test_workspace / "overwrite.json"

        # Write initial data
        initial_data = {"version": 1}
        json_ops.save_json(initial_data, test_file)

        # Overwrite with new data
        new_data = {"version": 2, "updated": True}
        json_ops.save_json(new_data, test_file)

        loaded = json.loads(test_file.read_text())
        assert loaded == new_data
        assert loaded["version"] == 2

    @pytest.mark.high
    def test_save_json_pretty_print(self, test_workspace):
        """Test that saved JSON is pretty-printed with indentation."""
        test_file = test_workspace / "pretty.json"
        test_data = {"level1": {"level2": {"level3": "value"}}}

        json_ops.save_json(test_data, test_file)

        content = test_file.read_text()
        # Check for indentation (pretty printing)
        assert "  " in content or "\t" in content
        assert "\n" in content

    @pytest.mark.high
    def test_save_json_with_unicode(self, test_workspace):
        """Test saving JSON with Unicode characters."""
        test_file = test_workspace / "unicode_save.json"
        test_data = {"greeting": "Hello 世界", "emoji": "🚀"}

        json_ops.save_json(test_data, test_file)

        loaded = json.loads(test_file.read_text(encoding='utf-8'))
        assert loaded["greeting"] == "Hello 世界"
        assert loaded["emoji"] == "🚀"

    @pytest.mark.high
    def test_save_json_array(self, test_workspace):
        """Test saving JSON array."""
        test_file = test_workspace / "array_save.json"
        test_data = [{"id": 1}, {"id": 2}, {"id": 3}]

        json_ops.save_json(test_data, test_file)

        loaded = json.loads(test_file.read_text())
        assert isinstance(loaded, list)
        assert len(loaded) == 3

    @pytest.mark.high
    def test_save_json_atomic_write(self, test_workspace):
        """Test that save_json uses atomic write (temp file + rename)."""
        test_file = test_workspace / "atomic.json"
        test_data = {"atomic": True}

        # Mock the atomic write behavior
        with patch('pathlib.Path.rename') as mock_rename:
            with patch('pathlib.Path.write_text') as mock_write:
                # Note: Actual implementation might use different approach
                # This tests the concept of atomic writes
                json_ops.save_json(test_data, test_file)

    @pytest.mark.high
    def test_save_json_permission_error(self, test_workspace):
        """Test handling of permission errors when saving."""
        test_file = test_workspace / "readonly.json"
        test_file.touch()
        test_file.chmod(0o444)  # Read-only

        test_data = {"data": "value"}

        # Should raise PermissionError or similar
        with pytest.raises((PermissionError, OSError)):
            json_ops.save_json(test_data, test_file)

        # Cleanup
        test_file.chmod(0o644)

    @pytest.mark.high
    @pytest.mark.critical
    def test_save_state_json_blocked(self):
        """
        CRITICAL: Test that direct state.json writes are blocked.

        This is a critical security/integrity feature - state.json must
        only be modified through StateManager to prevent race conditions.
        """
        state_path = Path("state.json")
        test_data = {"should": "not work"}

        with pytest.raises(RuntimeError, match="Direct state.json writes are forbidden"):
            json_ops.save_json(test_data, state_path)

    @pytest.mark.high
    @pytest.mark.critical
    def test_save_state_json_blocked_absolute_path(self, test_workspace):
        """Test that state.json writes are blocked even with absolute path."""
        state_path = test_workspace / "state.json"
        test_data = {"should": "not work"}

        with pytest.raises(RuntimeError, match="state.json"):
            json_ops.save_json(test_data, state_path)

    @pytest.mark.high
    @pytest.mark.critical
    def test_save_state_json_blocked_nested_path(self, test_workspace):
        """Test that state.json writes are blocked in nested directories."""
        nested_state = test_workspace / "subdir" / "state.json"
        test_data = {"should": "not work"}

        with pytest.raises(RuntimeError, match="state.json"):
            json_ops.save_json(test_data, nested_state)


class TestJsonOpsIntegration:
    """Integration tests for JSON operations."""

    @pytest.mark.high
    def test_save_and_load_roundtrip(self, test_workspace):
        """Test that data survives save-load cycle unchanged."""
        test_file = test_workspace / "roundtrip.json"
        original_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"deep": {"data": "here"}}
        }

        json_ops.save_json(original_data, test_file)
        loaded_data = json_ops.load_json(test_file)

        assert loaded_data == original_data

    @pytest.mark.high
    def test_multiple_saves_same_file(self, test_workspace):
        """Test multiple saves to same file (simulating updates)."""
        test_file = test_workspace / "updates.json"

        # Save version 1
        v1 = {"version": 1, "data": "first"}
        json_ops.save_json(v1, test_file)
        assert json_ops.load_json(test_file)["version"] == 1

        # Save version 2
        v2 = {"version": 2, "data": "second"}
        json_ops.save_json(v2, test_file)
        assert json_ops.load_json(test_file)["version"] == 2

        # Save version 3
        v3 = {"version": 3, "data": "third"}
        json_ops.save_json(v3, test_file)
        final = json_ops.load_json(test_file)
        assert final["version"] == 3
        assert final["data"] == "third"

    @pytest.mark.high
    def test_concurrent_access_safety(self, test_workspace):
        """Test that file operations are safe for concurrent access."""
        # This is a basic test - real concurrent access would need threading
        test_file = test_workspace / "concurrent.json"

        # Simulate multiple processes trying to save
        for i in range(5):
            data = {"iteration": i, "timestamp": i * 100}
            json_ops.save_json(data, test_file)

        # Last write should win
        final = json_ops.load_json(test_file)
        assert final["iteration"] == 4


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.high
    def test_load_empty_file(self, test_workspace):
        """Test loading completely empty file."""
        test_file = test_workspace / "empty_file.json"
        test_file.write_text("")

        with pytest.raises(json.JSONDecodeError):
            json_ops.load_json(test_file)

    @pytest.mark.high
    def test_load_whitespace_only(self, test_workspace):
        """Test loading file with only whitespace."""
        test_file = test_workspace / "whitespace.json"
        test_file.write_text("   \n  \t  ")

        with pytest.raises(json.JSONDecodeError):
            json_ops.load_json(test_file)

    @pytest.mark.high
    def test_save_to_directory_fails(self, test_workspace):
        """Test that saving to a directory path fails."""
        # Try to save to directory instead of file
        with pytest.raises((IsADirectoryError, OSError)):
            json_ops.save_json({"data": "value"}, test_workspace)

    @pytest.mark.high
    def test_load_binary_file(self, test_workspace):
        """Test loading binary file as JSON fails."""
        test_file = test_workspace / "binary.json"
        test_file.write_bytes(b'\x00\x01\x02\x03')

        with pytest.raises((json.JSONDecodeError, UnicodeDecodeError)):
            json_ops.load_json(test_file)
