"""
Agent logger setup and configuration.

Extracted from common.py to separate concerns.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, Optional


def setup_agent_logger(workspace: Path, agent_name: str) -> logging.Logger:
    """
    Setup workspace-specific logger with rotating file handler.

    Logs are stored in {workspace}/logs/{agent_name}.log

    Args:
        workspace: Workspace directory path
        agent_name: Name for the log file (e.g., "synthesis", "expert-typescript")

    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_dir = workspace / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(f"expert-feedback.{agent_name}")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Rotating file handler (max 5MB, keep 3 backups)
    log_file = log_dir / f"{agent_name}.log"
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    handler.setLevel(logging.DEBUG)

    # Format: timestamp - level - message
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for workflow tracing.

    Format: wf-YYYYMMDD-HHMMSS-XXXX
    Where XXXX is a random 4-character suffix for uniqueness

    Returns:
        Correlation ID string

    Example:
        "wf-20260215-143022-a3f9"
    """
    import random
    import string
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"wf-{timestamp}-{suffix}"


def setup_agent_logger_v2(
    workspace: Path,
    agent_name: str,
    correlation_id: Optional[str] = None,
    extra_context: Optional[Dict[str, Any]] = None,
    log_to_console: Optional[bool] = None
) -> logging.LoggerAdapter:
    """
    Enhanced workspace-specific logger with correlation IDs and structured context.

    Improvements over setup_agent_logger():
    - Correlation IDs for cross-process tracing
    - Structured extra context (iteration, expert, phase)
    - Optional console logging (stderr only)
    - Environment variable control

    Logs are stored in {workspace}/logs/{agent_name}.log

    Args:
        workspace: Workspace directory path
        agent_name: Name for the log file (e.g., "synthesis", "expert-typescript")
        correlation_id: Optional correlation ID to track workflow across processes
        extra_context: Optional structured context (iteration, expert, phase, etc.)
        log_to_console: Whether to also log to stderr (None = read from config)

    Returns:
        LoggerAdapter instance with correlation ID injection

    Example:
        logger = setup_agent_logger_v2(
            workspace,
            "expert-typescript",
            correlation_id="wf-20260215-143022-a3f9",
            extra_context={"iteration": 1, "expert": "typescript"}
        )
        logger.info("Starting analysis")  # Includes correlation_id in output
    """
    # Determine console logging
    if log_to_console is None:
        try:
            from config import get_config
            config = get_config()
            log_to_console = config.verbose_logging
        except Exception:
            log_to_console = False

    # Create logs directory
    log_dir = workspace / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger with hierarchical name
    logger_name = f"expert-feedback.{agent_name}"
    if correlation_id:
        logger_name = f"{logger_name}.{correlation_id[:8]}"

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        # Return existing logger as adapter
        class CorrelatedLoggerAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                extra = kwargs.get('extra', {})
                if correlation_id:
                    extra['correlation_id'] = correlation_id
                if extra_context:
                    extra['extra_context'] = extra_context
                kwargs['extra'] = extra
                return msg, kwargs

        return CorrelatedLoggerAdapter(logger, {})

    # Custom formatter with correlation ID
    class CorrelationFormatter(logging.Formatter):
        def format(self, record):
            # Add correlation ID if available
            if hasattr(record, 'correlation_id'):
                record.correlation_id_display = f"[{record.correlation_id}]"
            else:
                record.correlation_id_display = ""

            # Add extra context if available
            if hasattr(record, 'extra_context'):
                ctx = record.extra_context
                parts = []
                if 'iteration' in ctx:
                    parts.append(f"iter={ctx['iteration']}")
                if 'expert' in ctx:
                    parts.append(f"expert={ctx['expert']}")
                if 'phase' in ctx:
                    parts.append(f"phase={ctx['phase']}")
                record.context_display = f"[{','.join(parts)}]" if parts else ""
            else:
                record.context_display = ""

            return super().format(record)

    # Format: timestamp - level - [correlation_id] [context] - message
    formatter = CorrelationFormatter(
        '%(asctime)s - %(levelname)s - %(correlation_id_display)s%(context_display)s - %(message)s'
    )

    # Rotating file handler (max 5MB, keep 3 backups)
    log_file = log_dir / f"{agent_name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional console handler (stderr only - never stdout!)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)  # Less verbose on console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Create LoggerAdapter to automatically inject correlation_id and context
    class CorrelatedLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            # Inject correlation_id and extra_context into all log records
            extra = kwargs.get('extra', {})
            if correlation_id:
                extra['correlation_id'] = correlation_id
            if extra_context:
                extra['extra_context'] = extra_context
            kwargs['extra'] = extra
            return msg, kwargs

    adapter = CorrelatedLoggerAdapter(logger, {})
    return adapter
