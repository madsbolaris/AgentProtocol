"""
Unit tests for agent_logging/transcript.py

Tests conversation transcript logging including:
- TranscriptLogger initialization
- Message logging methods
- Timestamp formatting
- File operations

Target coverage: 90%+
"""
import pytest
import time
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.transcript import TranscriptLogger


class TestTranscriptLoggerInit:
    """Test TranscriptLogger initialization."""

    @pytest.mark.high
    def test_init_with_workspace_and_agent(self, tmp_path):
        """Test TranscriptLogger initialization."""
        logger = TranscriptLogger(
            workspace=tmp_path,
            agent_name="test_agent"
        )

        assert logger.workspace == tmp_path
        assert logger.agent_name == "test_agent"
        assert logger.log_path == tmp_path / "logs" / "test_agent-transcript.log"

    @pytest.mark.high
    def test_creates_log_directory(self, tmp_path):
        """Test that log directory is created."""
        logger = TranscriptLogger(
            workspace=tmp_path,
            agent_name="test"
        )

        log_dir = tmp_path / "logs"
        assert log_dir.exists()
        assert log_dir.is_dir()

    @pytest.mark.high
    def test_tracks_start_time(self, tmp_path):
        """Test that start time is tracked."""
        start = time.time()
        logger = TranscriptLogger(tmp_path, "test")

        assert hasattr(logger, 'start_time')
        assert logger.start_time >= start


class TestLogThink:
    """Test log_think method."""

    @pytest.mark.high
    def test_log_think_writes_to_file(self, tmp_path):
        """Test that think logging writes to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("Analyzing the problem...")

        assert logger.log_path.exists()
        content = logger.log_path.read_text()
        assert "THINK" in content
        assert "Analyzing the problem" in content

    @pytest.mark.high
    def test_log_think_includes_timestamp(self, tmp_path):
        """Test that think logs include timestamp."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("Test thinking")

        content = logger.log_path.read_text()
        # Should have timestamp format [HH:MM:SS.mmm]
        assert "[" in content
        assert "]" in content
        assert ":" in content

    @pytest.mark.high
    def test_log_think_includes_emoji(self, tmp_path):
        """Test that think logs include emoji."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("Test")

        content = logger.log_path.read_text()
        assert "🧠" in content

    @pytest.mark.high
    def test_log_think_multiple_entries(self, tmp_path):
        """Test logging multiple think entries."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("First thought")
        logger.log_think("Second thought")

        content = logger.log_path.read_text()
        assert "First thought" in content
        assert "Second thought" in content


class TestLogTool:
    """Test log_tool method."""

    @pytest.mark.high
    def test_log_tool_writes_to_file(self, tmp_path):
        """Test that tool logging writes to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_tool("Read", "scripts/common.py")

        assert logger.log_path.exists()
        content = logger.log_path.read_text()
        assert "TOOL" in content
        assert "Read" in content
        assert "scripts/common.py" in content

    @pytest.mark.high
    def test_log_tool_includes_timestamp(self, tmp_path):
        """Test that tool logs include timestamp."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_tool("Grep", "pattern")

        content = logger.log_path.read_text()
        assert "[" in content
        assert "]" in content

    @pytest.mark.high
    def test_log_tool_includes_emoji(self, tmp_path):
        """Test that tool logs include emoji."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_tool("Read", "file.py")

        content = logger.log_path.read_text()
        assert "🔧" in content

    @pytest.mark.high
    def test_log_tool_with_complex_args(self, tmp_path):
        """Test logging tool with complex arguments."""
        logger = TranscriptLogger(tmp_path, "test")

        complex_args = "{'pattern': 'test', 'glob': '**/*.py', 'context': 3}"
        logger.log_tool("Grep", complex_args)

        content = logger.log_path.read_text()
        assert complex_args in content


class TestLogMessage:
    """Test log_message method."""

    @pytest.mark.high
    def test_log_message_writes_to_file(self, tmp_path):
        """Test that message logging writes to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_message("## Analysis complete")

        assert logger.log_path.exists()
        content = logger.log_path.read_text()
        assert "MESSAGE" in content
        assert "Analysis complete" in content

    @pytest.mark.high
    def test_log_message_includes_timestamp(self, tmp_path):
        """Test that message logs include timestamp."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_message("Test message")

        content = logger.log_path.read_text()
        assert "[" in content
        assert "]" in content

    @pytest.mark.high
    def test_log_message_includes_emoji(self, tmp_path):
        """Test that message logs include emoji."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_message("Test")

        content = logger.log_path.read_text()
        assert "💬" in content

    @pytest.mark.high
    def test_log_message_preserves_formatting(self, tmp_path):
        """Test that message formatting is preserved."""
        logger = TranscriptLogger(tmp_path, "test")

        formatted_message = """## Results

- Item 1
- Item 2"""
        logger.log_message(formatted_message)

        content = logger.log_path.read_text()
        assert "## Results" in content
        assert "- Item 1" in content


class TestLogComplete:
    """Test log_complete method."""

    @pytest.mark.high
    def test_log_complete_writes_to_file(self, tmp_path):
        """Test that complete logging writes to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_complete(12.5, 13747)

        assert logger.log_path.exists()
        content = logger.log_path.read_text()
        assert "COMPLETE" in content
        assert "12.5s" in content
        assert "13747" in content

    @pytest.mark.high
    def test_log_complete_includes_timestamp(self, tmp_path):
        """Test that complete logs include timestamp."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_complete(10.0, 1000)

        content = logger.log_path.read_text()
        assert "[" in content
        assert "]" in content

    @pytest.mark.high
    def test_log_complete_includes_emoji(self, tmp_path):
        """Test that complete logs include emoji."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_complete(5.0, 500)

        content = logger.log_path.read_text()
        assert "✅" in content

    @pytest.mark.high
    def test_log_complete_formats_duration(self, tmp_path):
        """Test that duration is formatted correctly."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_complete(123.456, 10000)

        content = logger.log_path.read_text()
        assert "123.5s" in content or "123.4s" in content


class TestLogError:
    """Test log_error method."""

    @pytest.mark.high
    def test_log_error_writes_to_file(self, tmp_path):
        """Test that error logging writes to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_error("Connection timeout")

        assert logger.log_path.exists()
        content = logger.log_path.read_text()
        assert "ERROR" in content
        assert "Connection timeout" in content

    @pytest.mark.high
    def test_log_error_includes_timestamp(self, tmp_path):
        """Test that error logs include timestamp."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_error("Test error")

        content = logger.log_path.read_text()
        assert "[" in content
        assert "]" in content

    @pytest.mark.high
    def test_log_error_includes_emoji(self, tmp_path):
        """Test that error logs include emoji."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_error("Test error")

        content = logger.log_path.read_text()
        assert "❌" in content


class TestTimestamp:
    """Test _timestamp method."""

    @pytest.mark.high
    def test_timestamp_format(self, tmp_path):
        """Test timestamp format."""
        logger = TranscriptLogger(tmp_path, "test")

        timestamp = logger._timestamp()

        # Format: HH:MM:SS.mmm
        parts = timestamp.split(":")
        assert len(parts) == 3
        # Last part should have milliseconds
        assert "." in parts[2]

    @pytest.mark.high
    def test_timestamp_changes_over_time(self, tmp_path):
        """Test that timestamp changes over time."""
        logger = TranscriptLogger(tmp_path, "test")

        ts1 = logger._timestamp()
        time.sleep(0.01)
        ts2 = logger._timestamp()

        # Timestamps should be different (at least milliseconds)
        assert ts1 != ts2


class TestWriteMethod:
    """Test write method."""

    @pytest.mark.high
    def test_write_appends_to_file(self, tmp_path):
        """Test that write appends to file."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.write("First line\n")
        logger.write("Second line\n")

        content = logger.log_path.read_text()
        assert "First line" in content
        assert "Second line" in content

    @pytest.mark.high
    def test_write_creates_file_if_missing(self, tmp_path):
        """Test that write creates file if it doesn't exist."""
        logger = TranscriptLogger(tmp_path, "test")

        # Delete file if it exists
        if logger.log_path.exists():
            logger.log_path.unlink()

        logger.write("Test content\n")

        assert logger.log_path.exists()

    @pytest.mark.high
    def test_write_handles_unicode(self, tmp_path):
        """Test that write handles unicode characters."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.write("Unicode: 你好 مرحبا\n")

        content = logger.log_path.read_text()
        assert "你好" in content
        assert "مرحبا" in content


class TestCompleteWorkflow:
    """Test complete transcript workflow."""

    @pytest.mark.high
    def test_typical_agent_workflow(self, tmp_path):
        """Test typical agent workflow logging."""
        logger = TranscriptLogger(tmp_path, "typescript-expert")

        logger.log_think("Analyzing the TypeScript code...")
        logger.log_tool("Read", "/path/to/file.ts")
        logger.log_tool("Grep", "interface")
        logger.log_message("## Analysis\n\nThe code looks good.")
        logger.log_complete(15.3, 8500)

        content = logger.log_path.read_text()

        # Verify all entries are present
        assert "Analyzing the TypeScript code" in content
        assert "Read" in content
        assert "Grep" in content
        assert "Analysis" in content
        assert "COMPLETE" in content

    @pytest.mark.high
    def test_error_workflow(self, tmp_path):
        """Test workflow with error."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("Starting analysis...")
        logger.log_tool("Read", "file.py")
        logger.log_error("File not found: file.py")

        content = logger.log_path.read_text()

        assert "Starting analysis" in content
        assert "ERROR" in content
        assert "File not found" in content


class TestMultipleAgents:
    """Test multiple transcript loggers."""

    @pytest.mark.high
    def test_separate_logs_per_agent(self, tmp_path):
        """Test that different agents have separate log files."""
        logger1 = TranscriptLogger(tmp_path, "agent1")
        logger2 = TranscriptLogger(tmp_path, "agent2")

        logger1.log_message("Message from agent 1")
        logger2.log_message("Message from agent 2")

        content1 = logger1.log_path.read_text()
        content2 = logger2.log_path.read_text()

        assert "Message from agent 1" in content1
        assert "Message from agent 2" in content2
        assert "Message from agent 2" not in content1
        assert "Message from agent 1" not in content2

    @pytest.mark.high
    def test_log_files_in_same_directory(self, tmp_path):
        """Test that log files are in same directory."""
        logger1 = TranscriptLogger(tmp_path, "agent1")
        logger2 = TranscriptLogger(tmp_path, "agent2")

        logger1.log_message("Test")
        logger2.log_message("Test")

        assert logger1.log_path.parent == logger2.log_path.parent
        assert logger1.log_path != logger2.log_path


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_empty_messages(self, tmp_path):
        """Test logging empty messages."""
        logger = TranscriptLogger(tmp_path, "test")

        logger.log_think("")
        logger.log_message("")

        # Should not crash
        assert logger.log_path.exists()

    @pytest.mark.high
    def test_very_long_message(self, tmp_path):
        """Test logging very long message."""
        logger = TranscriptLogger(tmp_path, "test")

        long_message = "A" * 100000  # 100K characters
        logger.log_message(long_message)

        content = logger.log_path.read_text()
        assert long_message in content

    @pytest.mark.high
    def test_special_characters_in_messages(self, tmp_path):
        """Test special characters in messages."""
        logger = TranscriptLogger(tmp_path, "test")

        special = 'Test with "quotes", newlines\n\nand\ttabs'
        logger.log_message(special)

        content = logger.log_path.read_text()
        assert "quotes" in content
        assert "tabs" in content

    @pytest.mark.high
    def test_agent_name_with_special_chars(self, tmp_path):
        """Test agent name with special characters."""
        logger = TranscriptLogger(tmp_path, "expert-typescript-v2")

        logger.log_message("Test")

        assert logger.log_path.exists()
        assert "expert-typescript-v2-transcript.log" in str(logger.log_path)
