"""
Token usage tracking and cost estimation.

Extracted from common.py to separate concerns.
"""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import structlog
except ImportError:
    import logging as structlog


def extract_usage_from_sdk_result(result: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract token usage from Claude Agent SDK response.

    The SDK returns usage data in the ResultMessage.usage field with structure:
    {
        "input_tokens": 1000,
        "output_tokens": 500
    }

    Args:
        result: Result dictionary from Claude Agent SDK

    Returns:
        Dictionary with token usage metrics

    Example:
        async for message in query(prompt, options):
            if isinstance(message, ResultMessage):
                usage = extract_usage_from_sdk_result({"usage": message.usage})
                print(f"Total tokens: {usage['input_tokens'] + usage['output_tokens']}")
    """
    usage_data = result.get("usage", {})

    return {
        "input_tokens": usage_data.get("input_tokens", 0),
        "output_tokens": usage_data.get("output_tokens", 0)
    }


class TokenTracker:
    """Track token usage across workflow.

    Usage:
        tracker = TokenTracker(workspace)
        tracker.record_usage(
            phase="expert_review",
            expert="typescript",
            iteration=1,
            input_tokens=5000,
            output_tokens=3000
        )
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.log = structlog.get_logger()
        self.tokens_file = workspace / "token-usage.jsonl"

    def record_usage(
        self,
        phase: str,
        expert: Optional[str] = None,
        iteration: Optional[int] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        **context
    ):
        """Record token usage for a phase.

        Args:
            phase: Phase name
            expert: Expert name (if applicable)
            iteration: Iteration number (if applicable)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            **context: Additional context
        """
        total = input_tokens + output_tokens
        # Claude 3.5 Sonnet pricing (as of 2026)
        cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase,
            "expert": expert,
            "iteration": iteration,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total,
            "estimated_cost_usd": cost,
            **context
        }

        with open(self.tokens_file, 'a') as f:
            f.write(json.dumps(record) + '\n')

        self.log.info(
            "token_usage",
            phase=phase,
            expert=expert,
            tokens=total,
            cost=f"${cost:.4f}"
        )

        # VALIDATION: Warn if tokens are 0 (likely broken tracking)
        if input_tokens == 0 and output_tokens == 0:
            self.log.warning(
                f"⚠️ Token usage is 0 for {phase} (expert={expert}). "
                "Token tracking may be broken. Check Claude SDK response."
            )

    def get_total_usage(self) -> Dict[str, Any]:
        """Get total token usage for workflow."""
        if not self.tokens_file.exists():
            return {"total_tokens": 0, "total_cost_usd": 0}

        total_tokens = 0
        total_cost = 0

        with open(self.tokens_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                total_tokens += record["total_tokens"]
                total_cost += record["estimated_cost_usd"]

        return {
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost
        }

    def get_usage_by_phase(self) -> Dict[str, Dict[str, Any]]:
        """Get token usage broken down by phase."""
        if not self.tokens_file.exists():
            return {}

        phase_usage = {}

        with open(self.tokens_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                phase = record["phase"]

                if phase not in phase_usage:
                    phase_usage[phase] = {
                        "total_tokens": 0,
                        "total_cost_usd": 0,
                        "count": 0
                    }

                phase_usage[phase]["total_tokens"] += record["total_tokens"]
                phase_usage[phase]["total_cost_usd"] += record["estimated_cost_usd"]
                phase_usage[phase]["count"] += 1

        return phase_usage

    def get_usage_by_expert(self) -> Dict[str, Dict[str, Any]]:
        """Get token usage broken down by expert."""
        if not self.tokens_file.exists():
            return {}

        expert_usage = {}

        with open(self.tokens_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                expert = record.get("expert")
                if not expert:
                    continue

                if expert not in expert_usage:
                    expert_usage[expert] = {
                        "total_tokens": 0,
                        "total_cost_usd": 0,
                        "iterations": {}
                    }

                expert_usage[expert]["total_tokens"] += record["total_tokens"]
                expert_usage[expert]["total_cost_usd"] += record["estimated_cost_usd"]

                # Track by iteration
                iteration = record.get("iteration", 0)
                if iteration not in expert_usage[expert]["iterations"]:
                    expert_usage[expert]["iterations"][iteration] = {
                        "total_tokens": 0,
                        "total_cost_usd": 0
                    }

                expert_usage[expert]["iterations"][iteration]["total_tokens"] += record["total_tokens"]
                expert_usage[expert]["iterations"][iteration]["total_cost_usd"] += record["estimated_cost_usd"]

        return expert_usage
