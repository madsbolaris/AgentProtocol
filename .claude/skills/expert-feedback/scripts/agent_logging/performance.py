"""
Performance tracking for workflow phases.

Extracted from common.py to separate concerns.
"""
import json
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    import structlog
except ImportError:
    import logging as structlog


class PerformanceTracker:
    """Track performance metrics for workflow phases.

    Usage:
        tracker = PerformanceTracker(workspace)
        with tracker.track_phase("expert_spawning", expert="typescript"):
            await spawn_expert(...)
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.log = structlog.get_logger()
        self.metrics_file = workspace / "metrics.jsonl"

    @contextmanager
    def track_phase(self, phase: str, **context):
        """Context manager to track a workflow phase.

        Args:
            phase: Phase name (e.g., "expert_spawning", "synthesis")
            **context: Additional context (expert name, iteration, etc.)
        """
        start_time = time.time()
        self.log.info(f"{phase}.start", **context)

        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log.info(
                f"{phase}.end",
                duration_seconds=duration,
                **context
            )

            # Save metrics
            self._save_metric(phase, duration, context)

    def _save_metric(self, phase: str, duration: float, context: Dict):
        """Save metric to JSONL file."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase,
            "duration_seconds": duration,
            **context
        }

        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric) + '\n')

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary for all phases."""
        if not self.metrics_file.exists():
            return {}

        metrics = []
        with open(self.metrics_file, 'r') as f:
            for line in f:
                metrics.append(json.loads(line))

        # Aggregate by phase
        summary = {}
        for metric in metrics:
            phase = metric['phase']
            if phase not in summary:
                summary[phase] = {
                    "count": 0,
                    "total_duration": 0,
                    "min_duration": float('inf'),
                    "max_duration": 0
                }

            summary[phase]["count"] += 1
            summary[phase]["total_duration"] += metric["duration_seconds"]
            summary[phase]["min_duration"] = min(
                summary[phase]["min_duration"],
                metric["duration_seconds"]
            )
            summary[phase]["max_duration"] = max(
                summary[phase]["max_duration"],
                metric["duration_seconds"]
            )

        # Calculate averages
        for phase in summary:
            count = summary[phase]["count"]
            summary[phase]["avg_duration"] = summary[phase]["total_duration"] / count

        return summary
