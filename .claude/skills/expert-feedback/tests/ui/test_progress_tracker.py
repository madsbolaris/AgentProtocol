"""
Unit tests for progress tracking (progress_tracker.py).

Tests progress display, timing, token cost calculations, and output formatting.
"""
import pytest
from pathlib import Path
import time
import tempfile
import shutil

# Add scripts directory to path
import sys
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from ui.progress_tracker import ProgressTracker


class TestProgressTracker:
    """Test ProgressTracker class."""

    def test_initialization(self, test_workspace):
        """Test ProgressTracker initialization."""
        tracker = ProgressTracker(total_experts=5, workspace=test_workspace)

        assert tracker.total_experts == 5
        assert tracker.workspace == test_workspace
        assert tracker.completed == 0
        assert tracker.failed == 0
        assert tracker.start_time is not None

    def test_session_started(self, test_workspace, capsys):
        """Test session started output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.session_started()

        output = capsys.readouterr().err
        assert "Expert Feedback Session" in output
        assert "Workspace:" in output
        assert str(test_workspace.absolute()) in output
        assert "3 experts" in output

    def test_expert_started(self, test_workspace, capsys):
        """Test expert started output."""
        tracker = ProgressTracker(total_experts=2, workspace=test_workspace)

        tracker.expert_started("typescript")

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "spawning" in output
        assert "[" in output  # Timestamp

    def test_expert_completed(self, test_workspace, capsys):
        """Test expert completed output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.expert_completed("typescript", duration=120, tokens=5000)

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "complete" in output
        assert "120s" in output
        assert "5,000 tokens" in output  # Note: comma-formatted
        assert "$" in output  # Cost
        assert "[1/3]" in output  # Progress

    def test_expert_completed_increments_counter(self, test_workspace):
        """Test that expert_completed increments completed counter."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        assert tracker.completed == 0

        tracker.expert_completed("typescript", duration=120, tokens=5000)
        assert tracker.completed == 1

        tracker.expert_completed("python", duration=130, tokens=5500)
        assert tracker.completed == 2

    def test_expert_failed(self, test_workspace, capsys):
        """Test expert failed output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.expert_failed("typescript", "Timeout")

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "failed" in output
        assert "Timeout" in output

    def test_expert_failed_increments_counter(self, test_workspace):
        """Test that expert_failed increments failed counter."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        assert tracker.failed == 0

        tracker.expert_failed("typescript", "Timeout")
        assert tracker.failed == 1

    def test_expert_timeout_warning_long(self, test_workspace, capsys):
        """Test timeout warning with > 5 minutes remaining."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_timeout_warning("typescript", minutes_elapsed=5, minutes_remaining=10)

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "10 minutes remaining until timeout" in output

    def test_expert_timeout_warning_short(self, test_workspace, capsys):
        """Test timeout warning with <= 5 minutes remaining."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_timeout_warning("typescript", minutes_elapsed=25, minutes_remaining=3)

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "remaining" in output

    def test_synthesis_started(self, test_workspace, capsys):
        """Test synthesis started output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)
        tracker.completed = 3  # Simulate 3 completed experts

        tracker.synthesis_started(iteration=1)

        output = capsys.readouterr().err
        assert "Consolidating feedback" in output or "consolidating" in output.lower()
        assert "3 experts" in output
        assert "Iteration 1" in output or "iteration 1" in output.lower()

    def test_synthesis_complete_consensus_reached(self, test_workspace, capsys):
        """Test synthesis complete with consensus."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.synthesis_complete(convergence=85, consensus=True)

        output = capsys.readouterr().err
        assert "85%" in output
        assert "Consensus" in output or "✅" in output

    def test_synthesis_complete_no_consensus(self, test_workspace, capsys):
        """Test synthesis complete without consensus."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.synthesis_complete(convergence=65, consensus=False)

        output = capsys.readouterr().err
        assert "65%" in output
        assert ("More iteration" in output or "needed" in output) or "⚠️" in output

    def test_elapsed_time_format(self, test_workspace):
        """Test elapsed time formatting."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        # Get elapsed time immediately
        elapsed = tracker._elapsed()

        # Should be in MM:SS format
        assert ":" in elapsed
        parts = elapsed.split(":")
        assert len(parts) == 2
        assert len(parts[0]) == 2  # Minutes (zero-padded)
        assert len(parts[1]) == 2  # Seconds (zero-padded)

    def test_elapsed_time_progresses(self, test_workspace):
        """Test that elapsed time increases."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        elapsed1 = tracker._elapsed_seconds()
        time.sleep(0.1)  # Sleep 100ms
        elapsed2 = tracker._elapsed_seconds()

        assert elapsed2 > elapsed1

    def test_cost_calculation(self, test_workspace, capsys):
        """Test token cost calculation."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        # Simulate expert completion with known token count
        tracker.expert_completed("typescript", duration=120, tokens=10000, accurate_cost=0.03)

        output = capsys.readouterr().err

        # Cost should be approximately $0.030
        assert "$" in output
        assert "0.03" in output

    def test_progress_format(self, test_workspace, capsys):
        """Test progress counter format."""
        tracker = ProgressTracker(total_experts=5, workspace=test_workspace)

        tracker.expert_completed("typescript", duration=120, tokens=5000, accurate_cost=0.015)

        output = capsys.readouterr().err

        # Should show [1/5] format
        assert "[1/5]" in output

    def test_multiple_expert_completions(self, test_workspace, capsys):
        """Test tracking multiple expert completions."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.expert_completed("typescript", duration=120, tokens=5000, accurate_cost=0.015)
        tracker.expert_completed("python", duration=130, tokens=5500, accurate_cost=0.017)
        tracker.expert_completed("dotnet", duration=110, tokens=4800, accurate_cost=0.014)

        output = capsys.readouterr().err

        # Should show all three experts
        assert "typescript" in output
        assert "python" in output
        assert "dotnet" in output

        # Final progress should be [3/3]
        assert "[3/3]" in output

    def test_expert_progress_activity(self, test_workspace, capsys):
        """Test logging expert activity."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_progress("typescript", "Reading files")

        # Note: expert_progress only logs if config.verbose_logging is True
        # so we just check that it doesn't error
        output = capsys.readouterr().err
        # May or may not have output depending on config

    def test_expert_cancelled(self, test_workspace, capsys):
        """Test expert cancelled output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.expert_cancelled("typescript", "User cancelled")

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "cancelled" in output
        assert "User cancelled" in output
        assert tracker.cancelled == 1

    def test_expert_timeout(self, test_workspace, capsys):
        """Test expert timeout output."""
        tracker = ProgressTracker(total_experts=2, workspace=test_workspace)

        tracker.expert_timeout("typescript")

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "TIMEOUT" in output
        assert tracker.failed == 1

    def test_expert_timeout_warning_no_remaining(self, test_workspace, capsys):
        """Test timeout warning without minutes_remaining."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_timeout_warning("typescript", minutes_elapsed=15, minutes_remaining=None)

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "15 minutes" in output

    def test_expert_timeout_warning_long_remaining(self, test_workspace, capsys):
        """Test timeout warning with > 5 minutes remaining."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_timeout_warning("typescript", minutes_elapsed=10, minutes_remaining=8)

        output = capsys.readouterr().err
        assert "typescript" in output
        assert "8 minutes" in output

    def test_cache_metrics_tracking(self, test_workspace):
        """Test cache metrics are tracked correctly."""
        tracker = ProgressTracker(total_experts=2, workspace=test_workspace)

        # First expert with cache creation
        tracker.expert_completed(
            "typescript",
            duration=120,
            tokens=10000,
            input_tokens=8000,
            output_tokens=2000,
            cache_creation_tokens=500,
            cache_read_tokens=0,
            accurate_cost=0.03
        )

        assert tracker.total_input_tokens == 8000
        assert tracker.total_output_tokens == 2000
        assert tracker.total_cache_creation_tokens == 500
        assert tracker.cache_enabled == True

        # Second expert with cache hit
        tracker.expert_completed(
            "python",
            duration=100,
            tokens=8000,
            input_tokens=6000,
            output_tokens=2000,
            cache_creation_tokens=0,
            cache_read_tokens=4000,
            accurate_cost=0.02
        )

        assert tracker.total_input_tokens == 14000
        assert tracker.total_cache_read_tokens == 4000
        assert tracker.total_cost == 0.05

    def test_finalization_started(self, test_workspace, capsys):
        """Test finalization started output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.finalization_started(mode="adr")

        output = capsys.readouterr().err
        assert "Generating" in output or "generating" in output.lower()
        assert "adr" in output.lower()

    def test_finalization_complete_with_file(self, test_workspace, capsys):
        """Test finalization complete with output file."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)
        output_file = test_workspace / "output.md"
        output_file.write_text("test")

        tracker.finalization_complete(mode="adr", output_file=output_file, tokens=5000, accurate_cost=0.015)

        output = capsys.readouterr().err
        assert "adr" in output.lower()
        assert "complete" in output.lower()
        assert str(output_file.absolute()) in output

    def test_finalization_complete_no_file(self, test_workspace, capsys):
        """Test finalization complete without output file."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.finalization_complete(mode="plan", output_file=None, tokens=4000, accurate_cost=0.012)

        output = capsys.readouterr().err
        assert "plan" in output.lower()
        assert "complete" in output.lower()

    def test_session_complete(self, test_workspace, capsys):
        """Test session complete output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)
        tracker.completed = 3
        tracker.failed = 0
        tracker.cancelled = 0
        tracker.total_tokens = 15000
        tracker.total_cost = 0.045

        tracker.session_complete()

        output = capsys.readouterr().err
        assert "session complete" in output.lower()
        assert "3 completed" in output
        assert "15,000 total" in output or "15000" in output
        assert "$0.04" in output or "$0.045" in output

    def test_session_complete_with_cache(self, test_workspace, capsys):
        """Test session complete with cache performance."""
        tracker = ProgressTracker(total_experts=2, workspace=test_workspace)
        tracker.completed = 2
        tracker.failed = 0
        tracker.cancelled = 0
        tracker.total_tokens = 20000
        tracker.total_cost = 0.05
        tracker.cache_enabled = True
        tracker.total_input_tokens = 15000
        tracker.total_cache_read_tokens = 5000
        tracker.total_cache_creation_tokens = 1000

        tracker.session_complete()

        output = capsys.readouterr().err
        assert "Cache Performance" in output or "cache" in output.lower()
        assert "Cache hit rate" in output or "hit rate" in output.lower()

    def test_iteration_complete(self, test_workspace, capsys):
        """Test iteration complete output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)
        tracker.total_tokens = 15000
        tracker.total_cost = 0.045

        tracker.iteration_complete(iteration=1, convergence=75, consensus=False)

        output = capsys.readouterr().err
        assert "Iteration 1 complete" in output
        assert "75%" in output
        assert "Consensus" in output

    def test_artifact_review_started(self, test_workspace, capsys):
        """Test artifact review started output."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.artifact_review_started()

        output = capsys.readouterr().err
        assert "Artifact" in output or "artifact" in output.lower()
        assert "review" in output.lower()

    def test_artifact_review_complete_approved(self, test_workspace, capsys):
        """Test artifact review complete with approval."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.artifact_review_complete(approval_status="approved", tokens=3000, accurate_cost=0.009)

        output = capsys.readouterr().err
        assert "review complete" in output.lower()
        assert "approved" in output.lower()

    def test_artifact_review_complete_rejected(self, test_workspace, capsys):
        """Test artifact review complete with rejection."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.artifact_review_complete(approval_status="rejected", tokens=2500, accurate_cost=0.0075)

        output = capsys.readouterr().err
        assert "review complete" in output.lower()
        assert "rejected" in output.lower()

    def test_log_info(self, test_workspace, capsys):
        """Test info logging."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.log_info("Test information message")

        output = capsys.readouterr().err
        assert "Test information message" in output
        assert "ℹ️" in output

    def test_log_warning(self, test_workspace, capsys):
        """Test warning logging."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.log_warning("Test warning message")

        output = capsys.readouterr().err
        assert "Test warning message" in output
        assert "⚠️" in output

    def test_log_error(self, test_workspace, capsys):
        """Test error logging."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.log_error("Test error message")

        output = capsys.readouterr().err
        assert "Test error message" in output
        assert "❌" in output

    def test_synthesis_complete_with_tokens(self, test_workspace, capsys):
        """Test synthesis complete with token costs."""
        tracker = ProgressTracker(total_experts=3, workspace=test_workspace)

        tracker.synthesis_complete(convergence=80, consensus=False, tokens=5000, accurate_cost=0.015)

        output = capsys.readouterr().err
        assert "80%" in output
        assert "5,000 tokens" in output or "5000 tokens" in output

    def test_expert_completed_cache_creation(self, test_workspace, capsys):
        """Test expert completed with cache creation."""
        tracker = ProgressTracker(total_experts=1, workspace=test_workspace)

        tracker.expert_completed(
            "typescript",
            duration=120,
            tokens=10000,
            input_tokens=8000,
            output_tokens=2000,
            cache_creation_tokens=500,
            cache_read_tokens=0,
            accurate_cost=0.03
        )

        output = capsys.readouterr().err
        assert "cache created: 500" in output or "cache" in output.lower()

    def test_expert_completed_cache_hit(self, test_workspace, capsys):
        """Test expert completed with cache hit."""
        tracker = ProgressTracker(total_experts=2, workspace=test_workspace)

        # First enable cache
        tracker.cache_enabled = True

        # Then use cache
        tracker.expert_completed(
            "typescript",
            duration=100,
            tokens=8000,
            input_tokens=4000,
            output_tokens=2000,
            cache_creation_tokens=0,
            cache_read_tokens=4000,
            accurate_cost=0.02
        )

        output = capsys.readouterr().err
        assert "cache hit" in output.lower() or "%" in output


class TestProgressTrackerEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Create temporary workspace."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.temp_dir)

    def test_zero_experts(self):
        """Test initialization with zero experts."""
        tracker = ProgressTracker(total_experts=0, workspace=self.workspace)

        assert tracker.total_experts == 0
        assert tracker.completed == 0

    def test_single_expert(self):
        """Test progress tracking with single expert."""
        tracker = ProgressTracker(total_experts=1, workspace=self.workspace)

        tracker.expert_completed("typescript", duration=120, tokens=5000)

        assert tracker.completed == 1

    def test_large_expert_count(self):
        """Test progress tracking with many experts."""
        tracker = ProgressTracker(total_experts=20, workspace=self.workspace)

        for i in range(20):
            tracker.expert_completed(f"expert-{i}", duration=120, tokens=5000)

        assert tracker.completed == 20

    def test_mixed_success_and_failure(self):
        """Test tracking mix of successful and failed experts."""
        tracker = ProgressTracker(total_experts=5, workspace=self.workspace)

        tracker.expert_completed("typescript", duration=120, tokens=5000)
        tracker.expert_failed("python", "Timeout")
        tracker.expert_completed("dotnet", duration=130, tokens=5500)
        tracker.expert_failed("dx", "Error")
        tracker.expert_completed("openai-sdk", duration=110, tokens=4800)

        assert tracker.completed == 3
        assert tracker.failed == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
