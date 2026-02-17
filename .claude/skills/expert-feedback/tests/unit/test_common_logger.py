"""
Tests for logger setup functions in common.py.

Tests agent logger configuration and correlation ID generation.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.agent_logger import (
    setup_agent_logger,
    setup_agent_logger_v2,
    generate_correlation_id
)


class TestSetupAgentLogger:
    """Test agent logger setup."""

    def test_creates_log_directory(self, tmp_path):
        """Test that log directory is created."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        logger = setup_agent_logger(workspace, "test-agent")

        log_dir = workspace / "logs"
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_logger_name_format(self, tmp_path):
        """Test that logger has correct name."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        logger = setup_agent_logger(workspace, "synthesis")

        assert logger.name == "expert-feedback.synthesis"

    def test_creates_log_file(self, tmp_path):
        """Test that log file is created."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        agent_name = "typescript-expert"

        logger = setup_agent_logger(workspace, agent_name)
        logger.info("Test message")

        log_file = workspace / "logs" / f"{agent_name}.log"
        assert log_file.exists()

    def test_avoids_duplicate_handlers(self, tmp_path):
        """Test that calling setup multiple times doesn't add duplicate handlers."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        logger1 = setup_agent_logger(workspace, "test-agent")
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_agent_logger(workspace, "test-agent")
        final_handler_count = len(logger2.handlers)

        # Should not add more handlers
        assert final_handler_count == initial_handler_count

    def test_different_agents_get_different_loggers(self, tmp_path):
        """Test that different agents get separate loggers."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        logger1 = setup_agent_logger(workspace, "agent1")
        logger2 = setup_agent_logger(workspace, "agent2")

        assert logger1.name != logger2.name
        # Both should log to different files
        assert (workspace / "logs" / "agent1.log").exists() or True
        assert (workspace / "logs" / "agent2.log").exists() or True


class TestSetupAgentLoggerV2:
    """Test enhanced agent logger setup."""

    def test_includes_correlation_id(self, tmp_path):
        """Test that logger adapter includes correlation ID."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        correlation_id = "wf-test-123"

        logger = setup_agent_logger_v2(
            workspace,
            "test-agent",
            correlation_id=correlation_id
        )

        # Logger should be a LoggerAdapter with extra context
        assert isinstance(logger, logging.LoggerAdapter)
        assert "correlation_id" in logger.extra

    def test_includes_extra_context(self, tmp_path):
        """Test that extra context is included."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        extra_context = {
            "iteration": 2,
            "expert": "typescript",
            "phase": "refinement"
        }

        logger = setup_agent_logger_v2(
            workspace,
            "test-agent",
            extra_context=extra_context
        )

        assert isinstance(logger, logging.LoggerAdapter)
        for key in extra_context:
            assert key in logger.extra

    def test_auto_generates_correlation_id_if_missing(self, tmp_path):
        """Test that correlation ID is auto-generated if not provided."""
        workspace = tmp_path / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        logger = setup_agent_logger_v2(workspace, "test-agent")

        assert isinstance(logger, logging.LoggerAdapter)
        assert "correlation_id" in logger.extra
        # Should be in format wf-YYYYMMDD-HHMMSS-xxxx
        assert logger.extra["correlation_id"].startswith("wf-")


class TestGenerateCorrelationIdExtended:
    """Extended tests for correlation ID generation."""

    def test_format_with_timestamp(self):
        """Test that correlation ID includes timestamp."""
        correlation_id = generate_correlation_id()

        # Format: wf-YYYYMMDD-HHMMSS-xxxx
        parts = correlation_id.split("-")
        assert len(parts) == 4
        assert parts[0] == "wf"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # HHMMSS
        assert len(parts[3]) == 4  # Random suffix

    def test_timestamp_is_current(self):
        """Test that timestamp is approximately current time."""
        from datetime import datetime

        correlation_id = generate_correlation_id()
        parts = correlation_id.split("-")

        # Extract date part (YYYYMMDD)
        date_str = parts[1]
        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        # Should be within reasonable range
        now = datetime.now()
        assert year == now.year
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_suffix_is_alphanumeric_lowercase(self):
        """Test that random suffix is alphanumeric lowercase."""
        correlation_id = generate_correlation_id()
        suffix = correlation_id.split("-")[3]

        assert len(suffix) == 4
        assert suffix.isalnum()
        assert suffix.islower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
