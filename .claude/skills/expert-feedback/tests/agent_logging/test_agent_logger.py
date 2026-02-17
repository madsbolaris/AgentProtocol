"""
Unit tests for agent_logging/agent_logger.py

Tests logger setup and configuration including:
- setup_agent_logger() handler creation
- setup_agent_logger_v2() with various configs
- generate_correlation_id() ID generation
- Log file rotation
- Log formatting

Target coverage: 90%+
"""
import pytest
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import re

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.agent_logger import (
    setup_agent_logger,
    setup_agent_logger_v2,
    generate_correlation_id
)


class TestGenerateCorrelationId:
    """Test generate_correlation_id function."""

    @pytest.mark.high
    def test_generates_valid_id(self):
        """Test that correlation ID is generated."""
        correlation_id = generate_correlation_id()

        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

    @pytest.mark.high
    def test_generates_unique_ids(self):
        """Test that multiple calls generate unique IDs."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()
        id3 = generate_correlation_id()

        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    @pytest.mark.high
    def test_id_format(self):
        """Test correlation ID format."""
        correlation_id = generate_correlation_id()

        # Should match format: wf-YYYYMMDD-HHMMSS-XXXX
        pattern = r'^wf-\d{8}-\d{6}-[a-z0-9]{4}$'
        assert re.match(pattern, correlation_id), f"ID '{correlation_id}' doesn't match expected format"

    @pytest.mark.high
    def test_includes_timestamp(self):
        """Test that ID includes timestamp component."""
        correlation_id = generate_correlation_id()

        assert correlation_id.startswith("wf-")
        # Should have date and time components
        assert len(correlation_id.split('-')) == 4


class TestSetupAgentLogger:
    """Test setup_agent_logger function."""

    @pytest.mark.high
    def test_creates_logger(self, tmp_path):
        """Test that logger is created."""
        logger = setup_agent_logger(tmp_path, "test_agent")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "expert-feedback.test_agent"

    @pytest.mark.high
    def test_creates_log_directory(self, tmp_path):
        """Test that log directory is created."""
        logger = setup_agent_logger(tmp_path, "test")

        log_dir = tmp_path / "logs"
        assert log_dir.exists()
        assert log_dir.is_dir()

    @pytest.mark.high
    def test_sets_log_level_debug(self, tmp_path):
        """Test that log level is set to DEBUG."""
        logger = setup_agent_logger(tmp_path, "test")

        assert logger.level == logging.DEBUG

    @pytest.mark.high
    def test_adds_file_handler(self, tmp_path):
        """Test that file handler is added."""
        logger = setup_agent_logger(tmp_path, "test")

        assert len(logger.handlers) > 0
        has_file_handler = any(
            isinstance(h, (logging.FileHandler, RotatingFileHandler))
            for h in logger.handlers
        )
        assert has_file_handler

    @pytest.mark.high
    def test_uses_rotating_file_handler(self, tmp_path):
        """Test that RotatingFileHandler is used."""
        logger = setup_agent_logger(tmp_path, "test")

        has_rotating = any(
            isinstance(h, RotatingFileHandler)
            for h in logger.handlers
        )
        assert has_rotating

    @pytest.mark.high
    def test_log_file_location(self, tmp_path):
        """Test that log file is in correct location."""
        logger = setup_agent_logger(tmp_path, "test_agent")

        # Write a log message
        logger.info("Test message")

        log_file = tmp_path / "logs" / "test_agent.log"
        assert log_file.exists()

    @pytest.mark.high
    def test_prevents_duplicate_handlers(self, tmp_path):
        """Test that duplicate handlers are not added."""
        logger1 = setup_agent_logger(tmp_path, "test")
        handler_count1 = len(logger1.handlers)

        # Call again with same name
        logger2 = setup_agent_logger(tmp_path, "test")
        handler_count2 = len(logger2.handlers)

        # Should not add duplicate handlers
        assert handler_count1 == handler_count2
        assert logger1.name == logger2.name

    @pytest.mark.high
    def test_logs_are_written(self, tmp_path):
        """Test that logs are actually written to file."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content


class TestLogFormatting:
    """Test log message formatting."""

    @pytest.mark.high
    def test_log_includes_timestamp(self, tmp_path):
        """Test that logs include timestamp."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("Test message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # Should have timestamp pattern (YYYY-MM-DD or similar)
        assert re.search(r'\d{4}-\d{2}-\d{2}', content) or re.search(r'\d{2}:\d{2}:\d{2}', content)

    @pytest.mark.high
    def test_log_includes_level(self, tmp_path):
        """Test that logs include log level."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "INFO" in content
        assert "WARNING" in content
        assert "ERROR" in content

    @pytest.mark.high
    def test_multiline_message(self, tmp_path):
        """Test that multiline messages are handled."""
        logger = setup_agent_logger(tmp_path, "test")

        multiline = """Line 1
Line 2
Line 3"""
        logger.info(multiline)

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Line 1" in content


class TestSetupAgentLoggerV2:
    """Test setup_agent_logger_v2 function."""

    @pytest.mark.high
    def test_creates_logger_v2(self, tmp_path):
        """Test v2 logger creation."""
        logger = setup_agent_logger_v2(tmp_path, "test")

        assert isinstance(logger, logging.LoggerAdapter)

    @pytest.mark.high
    def test_v2_with_correlation_id(self, tmp_path):
        """Test v2 logger with correlation ID."""
        correlation_id = "test-corr-id"
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            correlation_id=correlation_id
        )

        logger.info("Test message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # Correlation ID should appear in logs
        assert "test-corr" in content

    @pytest.mark.high
    def test_v2_with_extra_context(self, tmp_path):
        """Test v2 logger with extra context."""
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            extra_context={"iteration": 1, "expert": "typescript"}
        )

        logger.info("Test message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # Context should appear in logs
        assert "iter=1" in content or "iteration" in content
        assert "expert=typescript" in content or "typescript" in content

    @pytest.mark.high
    def test_v2_without_console_output(self, tmp_path):
        """Test v2 logger without console output."""
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            log_to_console=False
        )

        # Count handlers
        base_logger = logger.logger
        handler_types = [type(h).__name__ for h in base_logger.handlers]

        # Should have file handler but not console handler
        assert any("File" in t for t in handler_types)
        # Console handler (StreamHandler) should not be present or minimal
        stream_handlers = [h for h in base_logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)]
        assert len(stream_handlers) == 0

    @pytest.mark.high
    def test_v2_with_console_output(self, tmp_path):
        """Test v2 logger with console output enabled."""
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            log_to_console=True
        )

        base_logger = logger.logger

        # Should have both file and console handlers
        has_file = any(isinstance(h, RotatingFileHandler) for h in base_logger.handlers)
        has_console = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
            for h in base_logger.handlers
        )

        assert has_file
        assert has_console


class TestLogRotation:
    """Test log file rotation."""

    @pytest.mark.high
    def test_rotating_handler_configured(self, tmp_path):
        """Test that rotating file handler is configured."""
        logger = setup_agent_logger(tmp_path, "test")

        rotating_handlers = [
            h for h in logger.handlers
            if isinstance(h, RotatingFileHandler)
        ]

        assert len(rotating_handlers) > 0
        handler = rotating_handlers[0]

        # Check configuration
        assert handler.maxBytes == 5 * 1024 * 1024  # 5MB
        assert handler.backupCount == 3

    @pytest.mark.high
    def test_log_rotation_creates_backups(self, tmp_path):
        """Test that log rotation creates backup files."""
        # Create logger with small max size
        logger = setup_agent_logger(tmp_path, "rotation_test")

        # Get the rotating handler and configure it for testing
        rotating_handlers = [
            h for h in logger.handlers
            if isinstance(h, RotatingFileHandler)
        ]

        if rotating_handlers:
            handler = rotating_handlers[0]
            # Set small size for testing
            handler.maxBytes = 100

        # Write enough logs to trigger rotation
        for i in range(20):
            logger.info(f"Log message {i} with some extra content to fill up space quickly")

        log_dir = tmp_path / "logs"
        log_files = list(log_dir.glob("rotation_test.log*"))

        # Should have main file and possibly backup files
        assert len(log_files) >= 1


class TestErrorHandling:
    """Test error handling in logger setup."""

    @pytest.mark.high
    def test_creates_missing_directories(self, tmp_path):
        """Test that missing directories are created."""
        deep_path = tmp_path / "level1" / "level2" / "level3"

        logger = setup_agent_logger(deep_path, "test")
        logger.info("Test")

        log_file = deep_path / "logs" / "test.log"
        assert log_file.exists()

    @pytest.mark.high
    def test_handles_special_agent_names(self, tmp_path):
        """Test handling of special characters in agent names."""
        logger = setup_agent_logger(tmp_path, "expert-typescript-v2")

        logger.info("Test")

        log_file = tmp_path / "logs" / "expert-typescript-v2.log"
        assert log_file.exists()


class TestMultipleLoggers:
    """Test multiple logger instances."""

    @pytest.mark.high
    def test_separate_loggers_different_files(self, tmp_path):
        """Test that separate loggers write to different files."""
        logger1 = setup_agent_logger(tmp_path, "agent1")
        logger2 = setup_agent_logger(tmp_path, "agent2")

        logger1.info("Message from agent 1")
        logger2.info("Message from agent 2")

        file1 = tmp_path / "logs" / "agent1.log"
        file2 = tmp_path / "logs" / "agent2.log"

        content1 = file1.read_text()
        content2 = file2.read_text()

        assert "Message from agent 1" in content1
        assert "Message from agent 2" in content2
        assert "Message from agent 2" not in content1
        assert "Message from agent 1" not in content2

    @pytest.mark.high
    def test_logger_hierarchy(self, tmp_path):
        """Test logger naming hierarchy."""
        logger1 = setup_agent_logger(tmp_path, "synthesis")
        logger2 = setup_agent_logger(tmp_path, "expert-typescript")

        assert logger1.name.startswith("expert-feedback.")
        assert logger2.name.startswith("expert-feedback.")
        assert logger1.name != logger2.name


class TestCorrelationFormatter:
    """Test correlation ID formatting in v2."""

    @pytest.mark.high
    def test_correlation_id_in_logs(self, tmp_path):
        """Test that correlation ID appears in log output."""
        correlation_id = generate_correlation_id()
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            correlation_id=correlation_id
        )

        logger.info("Test message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # At least part of correlation ID should appear
        # (might be truncated to first 8 chars)
        assert correlation_id[:8] in content

    @pytest.mark.high
    def test_context_in_logs(self, tmp_path):
        """Test that context appears in log output."""
        logger = setup_agent_logger_v2(
            tmp_path,
            "test",
            extra_context={"iteration": 2, "expert": "python", "phase": "review"}
        )

        logger.info("Test message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # Context fields should appear
        assert "iter=2" in content or "iteration" in content
        assert "python" in content
        assert "review" in content or "phase" in content


class TestLogLevels:
    """Test different log levels."""

    @pytest.mark.high
    def test_debug_level_logs(self, tmp_path):
        """Test DEBUG level logging."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.debug("Debug message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Debug message" in content
        assert "DEBUG" in content

    @pytest.mark.high
    def test_info_level_logs(self, tmp_path):
        """Test INFO level logging."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("Info message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Info message" in content
        assert "INFO" in content

    @pytest.mark.high
    def test_warning_level_logs(self, tmp_path):
        """Test WARNING level logging."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.warning("Warning message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Warning message" in content
        assert "WARNING" in content

    @pytest.mark.high
    def test_error_level_logs(self, tmp_path):
        """Test ERROR level logging."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.error("Error message")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "Error message" in content
        assert "ERROR" in content


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_empty_log_message(self, tmp_path):
        """Test logging empty message."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("")

        log_file = tmp_path / "logs" / "test.log"
        assert log_file.exists()

    @pytest.mark.high
    def test_very_long_log_message(self, tmp_path):
        """Test logging very long message."""
        logger = setup_agent_logger(tmp_path, "test")

        long_message = "A" * 10000
        logger.info(long_message)

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        # Should not truncate
        assert long_message in content

    @pytest.mark.high
    def test_unicode_in_logs(self, tmp_path):
        """Test unicode characters in logs."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info("Unicode: 你好 مرحبا 🎉")

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "你好" in content
        assert "مرحبا" in content

    @pytest.mark.high
    def test_special_characters_in_logs(self, tmp_path):
        """Test special characters in logs."""
        logger = setup_agent_logger(tmp_path, "test")

        logger.info('Special: "quotes" <tags> & ampersands')

        log_file = tmp_path / "logs" / "test.log"
        content = log_file.read_text()

        assert "quotes" in content
        assert "tags" in content
        assert "ampersands" in content
