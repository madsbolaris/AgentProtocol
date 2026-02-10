# Review

Review

<!-- GENERATED_START -->

## Review

Review
Post-run evaluation.
Evaluated after run completion to check final state.
STRUCTURE: Similar to Expect but focused on final state
- Judges evaluate final state (files, tool calls, messages)
- Assertions check run success + judge results
- No reference output (evaluates actual results only)
VARIABLES AVAILABLE:
- run.completed: Whether run finished successfully
- run.steps: Number of steps executed
- run.durationMs: Execution time
- Judge results: {judge.as}.passed, {judge.as}.score, etc.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `asserts` | `Assert[]` | Yes | Assertions using CEL expressions. |
| `judges` | `Judge[]` | Yes | Judges to evaluate final state. |

---
<!-- GENERATED_END -->