# EvalRunResult

Evaluation Run Result

<!-- GENERATED_START -->

## EvalRunResult

Evaluation Run Result
Result from a single run of the evaluation.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `durationMs` | `int32` | Yes | Duration of this run in milliseconds |
| `error` | `string` | No | Error message if run failed |
| `expects` | `ExpectResult[]` | Yes | Results from expect blocks |
| `passed` | `boolean` | Yes | Whether this run passed |
| `review` | `ReviewResult` | No | Result from review block (if present) |
| `runNumber` | `int32` | Yes | Run number (1-based) |

---
<!-- GENERATED_END -->