"""
Progress tracking and structured logging for expert-feedback skill.

This module provides real-time progress visibility during expert execution,
addressing the "silent execution" problem with timestamps, links, and metrics.
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import get_config


class ProgressTracker:
    """
    Track and display progress during expert execution.

    Features:
    - Real-time progress updates with timestamps
    - Clickable workspace links (User Issue 2)
    - Token usage and cost tracking
    - Timeout warnings (User Issue 1)
    - Expert completion metrics
    - Consolidation progress

    Example:
        tracker = ProgressTracker(3, workspace_path)
        tracker.session_started()

        tracker.expert_started("typescript")
        # ... expert executes ...
        tracker.expert_completed("typescript", duration=120, tokens=50000)

        tracker.synthesis_started(iteration=1)
        tracker.synthesis_complete(convergence=75, consensus=False)
    """

    def __init__(self, total_experts: int, workspace: Path):
        """
        Initialize progress tracker.

        Args:
            total_experts: Total number of experts to spawn
            workspace: Workspace directory path
        """
        self.total_experts = total_experts
        self.workspace = Path(workspace)
        self.completed = 0
        self.failed = 0
        self.cancelled = 0
        self.start_time = datetime.now()
        self.config = get_config()

        # Cumulative metrics
        self.total_tokens = 0
        self.total_cost = 0.0

        # Token metrics
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def session_started(self) -> None:
        """Log session start with workspace link (User Issue 2)."""
        if not self.config.show_workspace_link:
            return

        print(f"\n🎯 Expert Feedback Session", file=sys.stderr)
        print(f"📁 Workspace: file://{self.workspace.absolute()}", file=sys.stderr)
        print(f"👥 Spawning {self.total_experts} experts in parallel...\n", file=sys.stderr)

    def expert_started(self, expert: str) -> None:
        """
        Log expert starting.

        Args:
            expert: Expert name
        """
        elapsed = self._elapsed()
        print(f"🤖 [{elapsed}] {expert} - spawning...", file=sys.stderr)

    def expert_progress(self, expert: str, activity: str) -> None:
        """
        Log expert activity (e.g., 'Reading files', 'Running analysis').

        This provides visibility into what the expert is doing during
        the potentially long execution time.

        Args:
            expert: Expert name
            activity: Description of current activity
        """
        if not self.config.verbose_logging:
            return

        elapsed = self._elapsed()
        print(f"   [{elapsed}] {expert} - {activity}", file=sys.stderr)

    def expert_completed(
        self,
        expert: str,
        duration: int,
        tokens: int,
        input_tokens: int = 0,
        output_tokens: int = 0,
        accurate_cost: Optional[float] = None
    ) -> None:
        """
        Log expert completion with metrics.

        Args:
            expert: Expert name
            duration: Duration in seconds
            tokens: Total tokens used
            input_tokens: Input tokens
            output_tokens: Output tokens
            accurate_cost: Accurate cost in USD
        """
        self.completed += 1
        self.total_tokens += tokens

        # Track detailed metrics
        if input_tokens > 0 or output_tokens > 0:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

        # Use accurate cost if provided, otherwise assume 0 (cost tracking disabled)
        cost = accurate_cost if accurate_cost is not None else 0.0
        self.total_cost += cost

        elapsed = self._elapsed()
        progress = f"{self.completed}/{self.total_experts}"

        if self.config.show_token_costs:
            print(
                f"✅ [{elapsed}] {expert} - complete ({duration}s, {tokens:,} tokens, ${cost:.3f}) [{progress}]",
                file=sys.stderr
            )
        else:
            print(
                f"✅ [{elapsed}] {expert} - complete ({duration}s) [{progress}]",
                file=sys.stderr
            )

    def expert_failed(self, expert: str, error: str) -> None:
        """
        Log expert failure.

        Args:
            expert: Expert name
            error: Error message
        """
        self.failed += 1
        elapsed = self._elapsed()
        print(f"❌ [{elapsed}] {expert} - failed: {error}", file=sys.stderr)

    def expert_cancelled(self, expert: str, reason: str) -> None:
        """
        Log expert cancellation.

        Args:
            expert: Expert name
            reason: Cancellation reason
        """
        self.cancelled += 1
        elapsed = self._elapsed()
        print(f"⚠️  [{elapsed}] {expert} - cancelled: {reason}", file=sys.stderr)

    def expert_timeout_warning(
        self,
        expert: str,
        minutes_elapsed: int,
        minutes_remaining: Optional[int] = None
    ) -> None:
        """
        Log timeout warning (User Issue 1).

        Shows progressive warnings as expert approaches timeout.

        Args:
            expert: Expert name
            minutes_elapsed: Minutes since expert started
            minutes_remaining: Minutes until timeout (optional)
        """
        elapsed = self._elapsed()

        if minutes_remaining is None:
            # First warning - no specific countdown yet
            print(
                f"⏰ [{elapsed}] {expert} - running for {minutes_elapsed} minutes, please wrap up soon",
                file=sys.stderr
            )
        elif minutes_remaining > 5:
            # Mid-range warning
            print(
                f"⏰ [{elapsed}] {expert} - {minutes_remaining} minutes remaining until timeout",
                file=sys.stderr
            )
        else:
            # Final countdown
            print(
                f"⏱️  [{elapsed}] {expert} - ⚠️  {minutes_remaining} minute{'s' if minutes_remaining != 1 else ''} remaining!",
                file=sys.stderr
            )

    def expert_timeout(self, expert: str) -> None:
        """
        Log expert timeout.

        Args:
            expert: Expert name
        """
        self.failed += 1
        elapsed = self._elapsed()
        print(
            f"⏱️  [{elapsed}] {expert} - TIMEOUT after {self.config.expert_timeout_seconds // 60} minutes",
            file=sys.stderr
        )

    def synthesis_started(self, iteration: int, expert_count: int) -> None:
        """
        Log synthesis starting with link.

        Args:
            iteration: Current iteration number
            expert_count: Number of experts being synthesized
        """
        elapsed = self._elapsed()
        print(
            f"\n📈 [{elapsed}] Consolidating feedback from {expert_count} experts...",
            file=sys.stderr
        )
        print(f"📊 Iteration {iteration} analysis in progress...", file=sys.stderr)

    def synthesis_complete(
        self,
        convergence: int,
        consensus: bool,
        tokens: int = 0,
        accurate_cost: Optional[float] = None
    ) -> None:
        """
        Log synthesis completion.

        Args:
            convergence: Convergence percentage
            consensus: Whether consensus was reached
            tokens: Tokens used in synthesis
            accurate_cost: Accurate cost in USD
        """
        self.total_tokens += tokens
        cost = accurate_cost if accurate_cost is not None else 0.0
        self.total_cost += cost

        elapsed = self._elapsed()
        status = "✅ Consensus reached!" if consensus else "⚠️  More iteration needed"

        if self.config.show_token_costs and tokens > 0:
            print(
                f"📊 [{elapsed}] Convergence: {convergence}% - {status} ({tokens:,} tokens, ${cost:.3f})\n",
                file=sys.stderr
            )
        else:
            print(
                f"📊 [{elapsed}] Convergence: {convergence}% - {status}\n",
                file=sys.stderr
            )

    def finalization_started(self, mode: str) -> None:
        """
        Log finalization starting.

        Args:
            mode: Finalization mode (adr, create, improve, review)
        """
        elapsed = self._elapsed()
        print(f"\n📝 [{elapsed}] Generating final {mode} output...", file=sys.stderr)

    def finalization_complete(
        self,
        mode: str,
        output_file: Optional[Path] = None,
        tokens: int = 0,
        accurate_cost: Optional[float] = None
    ) -> None:
        """
        Log finalization completion.

        Args:
            mode: Finalization mode
            output_file: Output file path (if applicable)
            tokens: Tokens used in finalization
            accurate_cost: Accurate cost in USD
        """
        self.total_tokens += tokens
        cost = accurate_cost if accurate_cost is not None else 0.0
        self.total_cost += cost

        elapsed = self._elapsed()

        if output_file:
            print(
                f"✅ [{elapsed}] {mode.capitalize()} complete: file://{output_file.absolute()}",
                file=sys.stderr
            )
        else:
            print(f"✅ [{elapsed}] {mode.capitalize()} complete", file=sys.stderr)

        if self.config.show_token_costs and tokens > 0:
            print(f"   Tokens: {tokens:,}, Cost: ${cost:.3f}", file=sys.stderr)

    def session_complete(self) -> None:
        """Log session completion with final metrics."""
        elapsed = self._elapsed()
        duration_minutes = self._elapsed_seconds() / 60

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"✅ Expert feedback session complete [{elapsed}]", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        print(f"\n📊 Summary:", file=sys.stderr)
        print(f"   Duration: {duration_minutes:.1f} minutes", file=sys.stderr)
        print(f"   Experts: {self.completed} completed, {self.failed} failed, {self.cancelled} cancelled", file=sys.stderr)

        if self.config.show_token_costs:
            print(f"   Tokens: {self.total_tokens:,} total", file=sys.stderr)
            print(f"   Cost: ${self.total_cost:.2f}", file=sys.stderr)

        print(f"\n📁 Results: file://{self.workspace.absolute()}\n", file=sys.stderr)

    def iteration_complete(
        self,
        iteration: int,
        convergence: int,
        consensus: bool
    ) -> None:
        """
        Log iteration completion.

        Args:
            iteration: Iteration number
            convergence: Convergence percentage
            consensus: Whether consensus was reached
        """
        elapsed = self._elapsed()
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Iteration {iteration} complete [{elapsed}]", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"Convergence: {convergence}%", file=sys.stderr)
        print(f"Consensus: {'✅ Yes' if consensus else '❌ No'}", file=sys.stderr)

        if self.config.show_token_costs:
            print(f"Tokens (this iteration): {self.total_tokens:,}", file=sys.stderr)
            print(f"Cost (this iteration): ${self.total_cost:.2f}", file=sys.stderr)

        print(f"{'='*60}\n", file=sys.stderr)

    def artifact_review_started(self) -> None:
        """Log artifact review starting."""
        elapsed = self._elapsed()
        print(f"\n🔍 [{elapsed}] Artifact generated - starting expert review...", file=sys.stderr)

    def artifact_review_complete(
        self,
        approval_status: str,
        tokens: int = 0,
        accurate_cost: Optional[float] = None
    ) -> None:
        """
        Log artifact review completion.

        Args:
            approval_status: "approved", "minor_tweaks", or "rejected"
            tokens: Tokens used in review
            accurate_cost: Accurate cost in USD
        """
        self.total_tokens += tokens
        cost = accurate_cost if accurate_cost is not None else 0.0
        self.total_cost += cost

        elapsed = self._elapsed()

        status_emoji = {
            "approved": "✅",
            "minor_tweaks": "📝",
            "rejected": "🛑"
        }.get(approval_status, "❓")

        print(f"{status_emoji} [{elapsed}] Artifact review complete: {approval_status}", file=sys.stderr)

        if self.config.show_token_costs and tokens > 0:
            print(f"   Tokens: {tokens:,}, Cost: ${cost:.3f}", file=sys.stderr)

    def _elapsed(self) -> str:
        """Get elapsed time as MM:SS."""
        if not self.config.show_progress_timestamps:
            return ""

        seconds = self._elapsed_seconds()
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"

    def _elapsed_seconds(self) -> float:
        """Get elapsed seconds as float."""
        return (datetime.now() - self.start_time).total_seconds()

    def log_info(self, message: str) -> None:
        """
        Log informational message.

        Args:
            message: Message to log
        """
        elapsed = self._elapsed()
        if elapsed:
            print(f"ℹ️  [{elapsed}] {message}", file=sys.stderr)
        else:
            print(f"ℹ️  {message}", file=sys.stderr)

    def log_warning(self, message: str) -> None:
        """
        Log warning message.

        Args:
            message: Warning message
        """
        elapsed = self._elapsed()
        if elapsed:
            print(f"⚠️  [{elapsed}] {message}", file=sys.stderr)
        else:
            print(f"⚠️  {message}", file=sys.stderr)

    def log_error(self, message: str) -> None:
        """
        Log error message.

        Args:
            message: Error message
        """
        elapsed = self._elapsed()
        if elapsed:
            print(f"❌ [{elapsed}] {message}", file=sys.stderr)
        else:
            print(f"❌ {message}", file=sys.stderr)
