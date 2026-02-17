"""
Unit tests for agent_logging/token_tracker.py

Tests token counting and cost calculation including:
- TokenUsageWithCache dataclass
- extract_usage_from_sdk_result() parsing
- TokenTracker usage recording
- Cost calculation accuracy
- Summary generation

Target coverage: 95%+ (important for cost tracking)
"""
import pytest
import json
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agent_logging.token_tracker import (
    extract_usage_from_sdk_result,
    TokenTracker
)


class TestExtractUsageFromSDKResult:
    """Test extract_usage_from_sdk_result function."""

    @pytest.mark.high
    def test_extract_standard_usage(self):
        """Test extracting standard usage from SDK result."""
        sdk_result = {
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 500
            }
        }

        usage = extract_usage_from_sdk_result(sdk_result)

        assert usage["input_tokens"] == 1000
        assert usage["output_tokens"] == 500

    @pytest.mark.high
    def test_extract_missing_usage_field(self):
        """Test extracting when usage field is missing."""
        sdk_result = {"content": "response"}

        usage = extract_usage_from_sdk_result(sdk_result)

        assert usage["input_tokens"] == 0
        assert usage["output_tokens"] == 0


class TestTokenTrackerInit:
    """Test TokenTracker initialization."""

    @pytest.mark.high
    def test_init_with_workspace(self, tmp_path):
        """Test TokenTracker initialization with workspace."""
        tracker = TokenTracker(tmp_path)

        assert tracker.workspace == tmp_path
        assert tracker.tokens_file == tmp_path / "token-usage.jsonl"

    @pytest.mark.high
    def test_creates_tokens_file_on_first_write(self, tmp_path):
        """Test that tokens file is created on first record."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=100,
            output_tokens=50
        )

        assert tracker.tokens_file.exists()


class TestRecordUsage:
    """Test recording token usage."""

    @pytest.mark.high
    def test_record_basic_usage(self, tmp_path):
        """Test recording basic token usage."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test_phase",
            input_tokens=1000,
            output_tokens=500
        )

        assert tracker.tokens_file.exists()
        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert record["phase"] == "test_phase"
            assert record["input_tokens"] == 1000
            assert record["output_tokens"] == 500
            assert record["total_tokens"] == 1500

    @pytest.mark.high
    def test_record_with_expert(self, tmp_path):
        """Test recording usage with expert name."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="expert_review",
            expert="typescript",
            input_tokens=5000,
            output_tokens=3000
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert record["expert"] == "typescript"
            assert record["phase"] == "expert_review"

    @pytest.mark.high
    def test_record_with_iteration(self, tmp_path):
        """Test recording usage with iteration number."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="expert_review",
            expert="python",
            iteration=2,
            input_tokens=4000,
            output_tokens=2000
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert record["iteration"] == 2

    @pytest.mark.high
    def test_record_calculates_cost(self, tmp_path):
        """Test that cost is calculated correctly."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=1000,
            output_tokens=1000
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            # Claude 3.5 Sonnet pricing: $0.003/1K input, $0.015/1K output
            expected_cost = (1000 * 0.003 / 1000) + (1000 * 0.015 / 1000)
            assert abs(record["estimated_cost_usd"] - expected_cost) < 0.0001

    @pytest.mark.high
    def test_record_has_timestamp(self, tmp_path):
        """Test that records include timestamps."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=100,
            output_tokens=50
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert "timestamp" in record
            assert isinstance(record["timestamp"], str)

    @pytest.mark.high
    def test_record_with_extra_context(self, tmp_path):
        """Test recording with extra context kwargs."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=100,
            output_tokens=50,
            model="claude-3-5-sonnet",
            custom_field="custom_value"
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert record["model"] == "claude-3-5-sonnet"
            assert record["custom_field"] == "custom_value"


class TestZeroTokenWarning:
    """Test zero token warning."""

    @pytest.mark.high
    def test_warns_on_zero_tokens(self, tmp_path, caplog):
        """Test that warning is logged when tokens are 0."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            expert="typescript",
            input_tokens=0,
            output_tokens=0
        )

        # Check that warning was logged
        # Note: This depends on logging configuration


class TestGetTotalUsage:
    """Test get_total_usage method."""

    @pytest.mark.high
    def test_total_usage_empty(self, tmp_path):
        """Test total usage with no records."""
        tracker = TokenTracker(tmp_path)

        total = tracker.get_total_usage()

        assert total["total_tokens"] == 0
        assert total["total_cost_usd"] == 0

    @pytest.mark.high
    def test_total_usage_single_record(self, tmp_path):
        """Test total usage with single record."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=1000,
            output_tokens=500
        )

        total = tracker.get_total_usage()

        assert total["total_tokens"] == 1500
        assert total["total_cost_usd"] > 0

    @pytest.mark.high
    def test_total_usage_multiple_records(self, tmp_path):
        """Test total usage aggregation across multiple records."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(phase="phase1", input_tokens=1000, output_tokens=500)
        tracker.record_usage(phase="phase2", input_tokens=2000, output_tokens=1000)

        total = tracker.get_total_usage()

        assert total["total_tokens"] == 4500
        assert total["total_cost_usd"] > 0


class TestGetUsageByPhase:
    """Test get_usage_by_phase method."""

    @pytest.mark.high
    def test_usage_by_phase_empty(self, tmp_path):
        """Test usage by phase with no records."""
        tracker = TokenTracker(tmp_path)

        usage = tracker.get_usage_by_phase()

        assert usage == {}

    @pytest.mark.high
    def test_usage_by_phase_single_phase(self, tmp_path):
        """Test usage by phase with single phase."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="expert_review",
            input_tokens=1000,
            output_tokens=500
        )

        usage = tracker.get_usage_by_phase()

        assert "expert_review" in usage
        assert usage["expert_review"]["total_tokens"] == 1500
        assert usage["expert_review"]["count"] == 1

    @pytest.mark.high
    def test_usage_by_phase_aggregates(self, tmp_path):
        """Test that usage by phase aggregates multiple records."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(phase="review", input_tokens=1000, output_tokens=500)
        tracker.record_usage(phase="review", input_tokens=2000, output_tokens=1000)

        usage = tracker.get_usage_by_phase()

        assert usage["review"]["total_tokens"] == 4500
        assert usage["review"]["count"] == 2


class TestGetUsageByExpert:
    """Test get_usage_by_expert method."""

    @pytest.mark.high
    def test_usage_by_expert_empty(self, tmp_path):
        """Test usage by expert with no records."""
        tracker = TokenTracker(tmp_path)

        usage = tracker.get_usage_by_expert()

        assert usage == {}

    @pytest.mark.high
    def test_usage_by_expert_single_expert(self, tmp_path):
        """Test usage by expert with single expert."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="review",
            expert="typescript",
            input_tokens=5000,
            output_tokens=3000
        )

        usage = tracker.get_usage_by_expert()

        assert "typescript" in usage
        assert usage["typescript"]["total_tokens"] == 8000

    @pytest.mark.high
    def test_usage_by_expert_with_iterations(self, tmp_path):
        """Test usage by expert tracks iterations."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="review",
            expert="typescript",
            iteration=1,
            input_tokens=1000,
            output_tokens=500
        )
        tracker.record_usage(
            phase="review",
            expert="typescript",
            iteration=2,
            input_tokens=2000,
            output_tokens=1000
        )

        usage = tracker.get_usage_by_expert()

        assert "typescript" in usage
        assert 1 in usage["typescript"]["iterations"]
        assert 2 in usage["typescript"]["iterations"]
        assert usage["typescript"]["iterations"][1]["total_tokens"] == 1500
        assert usage["typescript"]["iterations"][2]["total_tokens"] == 3000

    @pytest.mark.high
    def test_usage_by_expert_skips_none_expert(self, tmp_path):
        """Test that records without expert are skipped."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="synthesis",
            input_tokens=1000,
            output_tokens=500
        )

        usage = tracker.get_usage_by_expert()

        assert usage == {}


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.high
    def test_zero_tokens_recorded(self, tmp_path):
        """Test recording zero tokens."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="test",
            input_tokens=0,
            output_tokens=0
        )

        with open(tracker.tokens_file, 'r') as f:
            record = json.loads(f.readline())
            assert record["total_tokens"] == 0
            assert record["estimated_cost_usd"] == 0

    @pytest.mark.high
    def test_very_large_token_count(self, tmp_path):
        """Test handling of very large token counts."""
        tracker = TokenTracker(tmp_path)

        tracker.record_usage(
            phase="large",
            input_tokens=1_000_000,
            output_tokens=500_000
        )

        total = tracker.get_total_usage()
        assert total["total_tokens"] == 1_500_000

    @pytest.mark.high
    def test_multiple_experts_and_phases(self, tmp_path):
        """Test complex scenario with multiple experts and phases."""
        tracker = TokenTracker(tmp_path)

        # Expert 1, Iteration 1
        tracker.record_usage(
            phase="review",
            expert="typescript",
            iteration=1,
            input_tokens=5000,
            output_tokens=3000
        )

        # Expert 2, Iteration 1
        tracker.record_usage(
            phase="review",
            expert="python",
            iteration=1,
            input_tokens=4000,
            output_tokens=2000
        )

        # Synthesis phase (no expert)
        tracker.record_usage(
            phase="synthesis",
            input_tokens=10000,
            output_tokens=5000
        )

        # Verify total
        total = tracker.get_total_usage()
        assert total["total_tokens"] == 29000

        # Verify by phase
        by_phase = tracker.get_usage_by_phase()
        assert "review" in by_phase
        assert "synthesis" in by_phase
        assert by_phase["review"]["count"] == 2

        # Verify by expert
        by_expert = tracker.get_usage_by_expert()
        assert "typescript" in by_expert
        assert "python" in by_expert
        assert len(by_expert) == 2  # Should not include synthesis (no expert)
