# EvalResult

Evaluation Result

<!-- GENERATED_START -->

## EvalResult

Evaluation Result
Complete result from running evaluation thread.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `avgDurationMs` | `float32` | Yes |  |
| `description` | `string` | No | Evaluation description |
| `failedAsserts` | `int32` | Yes |  |
| `failedRuns` | `int32` | Yes |  |
| `passed` | `boolean` | Yes | Overall pass/fail |
| `passedAsserts` | `int32` | Yes |  |
| `passedRuns` | `int32` | Yes |  |
| `runs` | `EvalRunResult[]` | Yes | Results from each run (if repeated) |
| `threadId` | `string` | Yes | Thread ID that was evaluated |
| `timestamp` | `utcDateTime` | Yes | Timestamp when evaluation completed |
| `totalAsserts` | `int32` | Yes |  |
| `totalDurationMs` | `int32` | Yes | Total duration across all runs |
| `totalRuns` | `int32` | Yes | Aggregate summary statistics |

---
<!-- GENERATED_END -->