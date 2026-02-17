# Structured Logging and Performance Metrics

## Overview

Phase 2.3 added structured logging and performance tracking utilities to improve observability and enable data-driven optimization.

## Features

1. **Structured Logging** - JSON-formatted logs with timestamps and context
2. **Performance Tracking** - Measure execution time for each workflow phase
3. **Token Usage Tracking** - Track token consumption and costs
4. **Aggregate Metrics** - Summarize performance and costs across phases/experts

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `structlog` - Structured logging library
- Other dependencies (jinja2, aiofiles, etc.)

### Initialize Logging

```python
from pathlib import Path
from scripts.common import setup_logging, PerformanceTracker, TokenTracker

workspace = Path(".workspace/2026/02/15/my-review")

# Setup structured logging
log = setup_logging(workspace, log_level="INFO")

# Initialize trackers
perf = PerformanceTracker(workspace)
tokens = TokenTracker(workspace)
```

## Usage Examples

### Performance Tracking

Track execution time for workflow phases:

```python
async def spawn_experts(experts: List[str], iteration: int):
    """Spawn all expert agents."""

    # Track the entire spawn phase
    with perf.track_phase("spawn_all_experts", iteration=iteration, expert_count=len(experts)):
        results = []

        for expert in experts:
            # Track individual expert spawning
            with perf.track_phase("spawn_expert", expert=expert, iteration=iteration):
                result = await spawn_expert(expert, iteration)
                results.append(result)

        return results
```

**Output:**
```
2026-02-15T10:30:00.123Z [info] spawn_all_experts.start iteration=1 expert_count=5
2026-02-15T10:30:00.456Z [info] spawn_expert.start expert=typescript iteration=1
2026-02-15T10:30:45.789Z [info] spawn_expert.end expert=typescript iteration=1 duration_seconds=45.333
...
2026-02-15T10:35:12.345Z [info] spawn_all_experts.end iteration=1 expert_count=5 duration_seconds=312.222
```

### Token Usage Tracking

Track token consumption and costs:

```python
async def spawn_expert(expert: str, iteration: int):
    """Spawn expert and track token usage."""

    result = await claude_sdk.send_message(session_id, prompt)

    # Extract token usage from response
    usage = result.usage if hasattr(result, 'usage') else None
    if usage:
        tokens.record_usage(
            phase="expert_review",
            expert=expert,
            iteration=iteration,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens
        )
    else:
        log.warning(f"No token usage in response for {expert}")

    return result
```

**Output:**
```
2026-02-15T10:30:45.789Z [info] token_usage phase=expert_review expert=typescript tokens=8543 cost=$0.1281
```

### Get Performance Summary

Retrieve aggregate performance metrics:

```python
# At end of workflow
summary = perf.get_summary()

print("Performance Summary:")
for phase, stats in summary.items():
    print(f"  {phase}:")
    print(f"    Count: {stats['count']}")
    print(f"    Total: {stats['total_duration']:.2f}s")
    print(f"    Avg: {stats['avg_duration']:.2f}s")
    print(f"    Min: {stats['min_duration']:.2f}s")
    print(f"    Max: {stats['max_duration']:.2f}s")
```

**Example Output:**
```
Performance Summary:
  spawn_expert:
    Count: 5
    Total: 312.22s
    Avg: 62.44s
    Min: 45.33s
    Max: 89.12s
  consolidation:
    Count: 1
    Total: 23.45s
    Avg: 23.45s
    Min: 23.45s
    Max: 23.45s
```

### Get Token Usage Summary

Retrieve aggregate token usage:

```python
# Total usage
total = tokens.get_total_usage()
print(f"Total tokens: {total['total_tokens']:,}")
print(f"Total cost: ${total['total_cost_usd']:.2f}")

# Usage by phase
by_phase = tokens.get_usage_by_phase()
for phase, stats in by_phase.items():
    print(f"{phase}: {stats['total_tokens']:,} tokens (${stats['total_cost_usd']:.4f})")

# Usage by expert
by_expert = tokens.get_usage_by_expert()
for expert, stats in by_expert.items():
    print(f"{expert}: {stats['total_tokens']:,} tokens (${stats['total_cost_usd']:.4f})")
    for iteration, iter_stats in stats['iterations'].items():
        print(f"  Iteration {iteration}: {iter_stats['total_tokens']:,} tokens")
```

**Example Output:**
```
Total tokens: 125,543
Total cost: $1.88

Phase Breakdown:
expert_review: 98,234 tokens ($1.4735)
consolidation: 15,432 tokens ($0.2315)
artifact generation: 11,877 tokens ($0.1781)

Expert Breakdown:
typescript: 22,456 tokens ($0.3368)
  Iteration 1: 18,234 tokens
  Iteration 2: 4,222 tokens
python: 19,823 tokens ($0.2973)
  Iteration 1: 16,543 tokens
  Iteration 2: 3,280 tokens
```

## Output Files

### metrics.jsonl

Performance metrics in JSON Lines format:

```json
{"timestamp": "2026-02-15T10:30:45.789Z", "phase": "spawn_expert", "duration_seconds": 45.333, "expert": "typescript", "iteration": 1}
{"timestamp": "2026-02-15T10:31:23.456Z", "phase": "spawn_expert", "duration_seconds": 52.112, "expert": "python", "iteration": 1}
```

### token-usage.jsonl

Token usage in JSON Lines format:

```json
{"timestamp": "2026-02-15T10:30:45.789Z", "phase": "expert_review", "expert": "typescript", "iteration": 1, "input_tokens": 5234, "output_tokens": 3309, "total_tokens": 8543, "estimated_cost_usd": 0.1281}
{"timestamp": "2026-02-15T10:31:23.456Z", "phase": "expert_review", "expert": "python", "iteration": 1, "input_tokens": 4823, "output_tokens": 2987, "total_tokens": 7810, "estimated_cost_usd": 0.1172}
```

## Benefits

1. **Visibility** - See exactly where time and tokens are spent
2. **Optimization** - Identify bottlenecks and high-cost phases
3. **Cost Tracking** - Monitor token usage and estimated costs
4. **Debugging** - Structured logs easier to search and analyze
5. **Data-Driven** - Make optimization decisions based on metrics

## Integration with Workflow Scripts

All major workflow scripts should use these utilities:

- `spawn-all-experts.py` - Track expert spawning and token usage
- `consolidate-feedback.py` - Track consolidation performance
- `generate_artifact.py` - Track artifact generation performance
- `run_workflow.py` - Track overall workflow execution

## Token Cost Calculation

Current pricing (Claude 3.5 Sonnet, as of 2026):
- **Input tokens:** $0.003 / 1K tokens
- **Output tokens:** $0.015 / 1K tokens

The `TokenTracker` automatically calculates estimated costs based on these rates.

**Note:** Update pricing in `common.py` if Claude pricing changes.

## Zero Token Warning

The `TokenTracker` includes validation to detect broken token tracking:

```python
if input_tokens == 0 and output_tokens == 0:
    log.warning(
        f"⚠️ Token usage is 0 for {phase} (expert={expert}). "
        "Token tracking may be broken. Check Claude SDK response."
    )
```

This helps identify cases where token usage isn't being captured from the Claude SDK response.

## Future Enhancements

- **Dashboard:** Web-based metrics dashboard
- **Alerts:** Notify when costs exceed thresholds
- **Comparisons:** Compare token usage across different workflows
- **Export:** Export metrics to CSV/Excel for analysis
- **Grafana Integration:** Send metrics to Grafana for visualization
