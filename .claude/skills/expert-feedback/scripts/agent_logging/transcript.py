"""
Transcript logging for debugging agent activity.

Extracted from common.py to separate concerns.
"""
import time
from datetime import datetime
from pathlib import Path


class TranscriptLogger:
    """
    Simple transcript-style logger for debugging agent activity.

    Logs to {workspace}/logs/{agent}-transcript.log with format:
    [HH:MM:SS.mmm] TYPE: content

    This logger provides human-readable debug output for agent conversations,
    capturing thinking blocks, tool calls, and messages in a scannable format.

    Usage:
        transcript = TranscriptLogger(workspace, "synthesis")
        transcript.log_think("Let me analyze...")
        transcript.log_tool("Read", "scripts/common.py")
        transcript.log_message("## Analysis complete")
        transcript.log_complete(12.5, 13747)
    """

    def __init__(self, workspace: Path, agent_name: str):
        """Initialize transcript logger.

        Args:
            workspace: Workspace path
            agent_name: Agent name (e.g., "synthesis", "typescript")
        """
        self.workspace = workspace
        self.agent_name = agent_name

        # Create log file
        log_dir = workspace / "logs"
        log_dir.mkdir(exist_ok=True, parents=True)
        self.log_path = log_dir / f"{agent_name}-transcript.log"

        # Track timing
        self.start_time = time.time()

    def write(self, text: str):
        """Append text to transcript log."""
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(text)

    def log_think(self, text: str):
        """Log agent thinking/reasoning.

        Args:
            text: Thinking content
        """
        timestamp = self._timestamp()
        # Log full thinking content for debugging
        self.write(f"[{timestamp}] 🧠 THINK: {text}\n\n")

    def log_tool(self, name: str, args: str):
        """Log tool call.

        Args:
            name: Tool name (e.g., "Read", "Grep")
            args: Tool arguments (full content for debugging)
        """
        timestamp = self._timestamp()
        # Log full args for debugging
        self.write(f"[{timestamp}] 🔧 TOOL: {name} → {args}\n\n")

    def log_message(self, text: str):
        """Log final agent message.

        Args:
            text: Message content
        """
        timestamp = self._timestamp()
        # Show full message (this is the important output)
        self.write(f"[{timestamp}] 💬 MESSAGE: {text}\n\n")

    def log_complete(self, duration: float, tokens: int):
        """Log completion.

        Args:
            duration: Duration in seconds
            tokens: Total tokens used
        """
        timestamp = self._timestamp()
        self.write(f"[{timestamp}] ✅ COMPLETE (duration: {duration:.1f}s, tokens: {tokens})\n")

    def log_error(self, error: str):
        """Log error.

        Args:
            error: Error message
        """
        timestamp = self._timestamp()
        self.write(f"[{timestamp}] ❌ ERROR: {error}\n")

    def _timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
