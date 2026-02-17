"""
Unit tests for agent_logging/performance.py

Tests performance timing and tracking including:
- PerformanceTracker context manager
- Phase timing
- Metrics persistence
- Summary generation

Target coverage: 90%+
"""
import pytest
import time
import json
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.performance import PerformanceTracker


class TestPerformanceTrackerInit:
    """Test PerformanceTracker initialization."""

    @pytest.mark.high
    def test_init_with_workspace(self, tmp_path):
        """Test PerformanceTracker initialization with workspace."""
        tracker = PerformanceTracker(tmp_path)

        assert tracker.workspace == tmp_path
        assert tracker.metrics_file == tmp_path / "metrics.jsonl"

    @pytest.mark.high
    def test_creates_metrics_file_on_first_write(self, tmp_path):
        """Test that metrics file is created on first metric write."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("test_phase"):
            time.sleep(0.01)

        assert tracker.metrics_file.exists()


class TestPhaseTracking:
    """Test phase timing functionality."""

    @pytest.mark.high
    def test_track_single_phase(self, tmp_path):
        """Test tracking a single phase."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("test_phase"):
            time.sleep(0.02)

        # Verify metrics file contains the phase
        assert tracker.metrics_file.exists()
        with open(tracker.metrics_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            metric = json.loads(lines[0])
            assert metric["phase"] == "test_phase"
            assert metric["duration_seconds"] >= 0.02

    @pytest.mark.high
    def test_track_multiple_phases(self, tmp_path):
        """Test tracking multiple phases."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("phase1"):
            time.sleep(0.01)

        with tracker.track_phase("phase2"):
            time.sleep(0.02)

        # Verify both phases recorded
        with open(tracker.metrics_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            metrics = [json.loads(line) for line in lines]
            assert metrics[0]["phase"] == "phase1"
            assert metrics[1]["phase"] == "phase2"

    @pytest.mark.high
    def test_phase_context_manager(self, tmp_path):
        """Test phase as context manager."""
        tracker = PerformanceTracker(tmp_path)

        start_time = time.time()
        with tracker.track_phase("context_test"):
            time.sleep(0.015)
        end_time = time.time()

        elapsed = end_time - start_time

        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())
            phase_duration = metric["duration_seconds"]

        # Phase duration should be close to actual elapsed time
        assert abs(phase_duration - elapsed) < 0.01  # Within 10ms tolerance

    @pytest.mark.high
    def test_phase_with_context(self, tmp_path):
        """Test phase tracking with additional context."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("expert_phase", expert="typescript", iteration=1):
            time.sleep(0.01)

        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())
            assert metric["phase"] == "expert_phase"
            assert metric["expert"] == "typescript"
            assert metric["iteration"] == 1


class TestPhaseExceptions:
    """Test exception handling in phases."""

    @pytest.mark.high
    def test_phase_with_exception(self, tmp_path):
        """Test that phase timing works even with exceptions."""
        tracker = PerformanceTracker(tmp_path)

        try:
            with tracker.track_phase("error_phase"):
                time.sleep(0.01)
                raise ValueError("Test error")
        except ValueError:
            pass

        # Phase should still be recorded
        assert tracker.metrics_file.exists()
        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())
            assert metric["phase"] == "error_phase"
            assert metric["duration_seconds"] >= 0.01

    @pytest.mark.high
    def test_phase_exception_propagates(self, tmp_path):
        """Test that exceptions propagate correctly."""
        tracker = PerformanceTracker(tmp_path)

        with pytest.raises(RuntimeError):
            with tracker.track_phase("failing_phase"):
                raise RuntimeError("Expected error")


class TestSummaryGeneration:
    """Test summary generation and formatting."""

    @pytest.mark.high
    def test_generate_summary_empty(self, tmp_path):
        """Test generating summary with no metrics."""
        tracker = PerformanceTracker(tmp_path)

        summary = tracker.get_summary()

        assert isinstance(summary, dict)
        assert len(summary) == 0

    @pytest.mark.high
    def test_generate_summary_single_phase(self, tmp_path):
        """Test generating performance summary for single phase."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("phase1"):
            time.sleep(0.01)

        summary = tracker.get_summary()

        assert "phase1" in summary
        assert summary["phase1"]["count"] == 1
        assert summary["phase1"]["total_duration"] >= 0.01
        assert summary["phase1"]["avg_duration"] >= 0.01
        assert summary["phase1"]["min_duration"] >= 0.01
        assert summary["phase1"]["max_duration"] >= 0.01

    @pytest.mark.high
    def test_summary_includes_all_phases(self, tmp_path):
        """Test that summary includes all tracked phases."""
        tracker = PerformanceTracker(tmp_path)

        phases = ["init", "process", "finalize"]
        for phase in phases:
            with tracker.track_phase(phase):
                time.sleep(0.005)

        summary = tracker.get_summary()

        for phase in phases:
            assert phase in summary
            assert summary[phase]["count"] == 1

    @pytest.mark.high
    def test_summary_aggregates_repeated_phases(self, tmp_path):
        """Test that summary aggregates repeated phases."""
        tracker = PerformanceTracker(tmp_path)

        # Run same phase multiple times
        for i in range(3):
            with tracker.track_phase("repeated"):
                time.sleep(0.01)

        summary = tracker.get_summary()

        assert summary["repeated"]["count"] == 3
        assert summary["repeated"]["total_duration"] >= 0.03
        assert summary["repeated"]["avg_duration"] >= 0.01

    @pytest.mark.high
    def test_summary_calculates_min_max(self, tmp_path):
        """Test that summary calculates min/max durations."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("test"):
            time.sleep(0.01)

        with tracker.track_phase("test"):
            time.sleep(0.02)

        with tracker.track_phase("test"):
            time.sleep(0.015)

        summary = tracker.get_summary()

        assert summary["test"]["min_duration"] >= 0.01
        assert summary["test"]["max_duration"] >= 0.02
        assert summary["test"]["min_duration"] < summary["test"]["max_duration"]


class TestMetricsPersistence:
    """Test metrics file persistence."""

    @pytest.mark.high
    def test_metrics_file_jsonl_format(self, tmp_path):
        """Test that metrics are saved in JSONL format."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("test"):
            pass

        # Read and verify JSONL format
        content = tracker.metrics_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) == 1

        metric = json.loads(lines[0])
        assert isinstance(metric, dict)

    @pytest.mark.high
    def test_metrics_have_timestamps(self, tmp_path):
        """Test that metrics include timestamps."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("test"):
            pass

        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())

        assert "timestamp" in metric
        assert isinstance(metric["timestamp"], str)

    @pytest.mark.high
    def test_metrics_append_not_overwrite(self, tmp_path):
        """Test that metrics append to file, not overwrite."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("phase1"):
            pass

        with tracker.track_phase("phase2"):
            pass

        with open(tracker.metrics_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) == 2


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.high
    def test_zero_duration_phase(self, tmp_path):
        """Test phase with effectively zero duration."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("instant"):
            pass  # No sleep

        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())

        # Duration might be very small but not negative
        assert metric["duration_seconds"] >= 0

    @pytest.mark.high
    def test_very_long_phase(self, tmp_path):
        """Test tracking a longer phase."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("long"):
            time.sleep(0.1)  # 100ms

        with open(tracker.metrics_file, 'r') as f:
            metric = json.loads(f.readline())

        assert metric["duration_seconds"] >= 0.1

    @pytest.mark.high
    def test_duplicate_phase_names(self, tmp_path):
        """Test handling duplicate phase names."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("duplicate"):
            time.sleep(0.01)

        with tracker.track_phase("duplicate"):
            time.sleep(0.02)

        summary = tracker.get_summary()

        # Should aggregate both phases
        assert summary["duplicate"]["count"] == 2


class TestPerformanceMetrics:
    """Test various performance metrics."""

    @pytest.mark.high
    def test_average_phase_duration(self, tmp_path):
        """Test calculating average phase duration."""
        tracker = PerformanceTracker(tmp_path)

        for i in range(5):
            with tracker.track_phase("phase"):
                time.sleep(0.01)

        summary = tracker.get_summary()

        assert summary["phase"]["count"] == 5
        assert summary["phase"]["avg_duration"] >= 0.01

    @pytest.mark.high
    def test_total_duration_calculation(self, tmp_path):
        """Test total duration calculation."""
        tracker = PerformanceTracker(tmp_path)

        with tracker.track_phase("phase"):
            time.sleep(0.01)

        with tracker.track_phase("phase"):
            time.sleep(0.01)

        summary = tracker.get_summary()

        assert summary["phase"]["total_duration"] >= 0.02
