# AssertResult

Assert Result

<!-- GENERATED_START -->

## AssertResult

Assert Result
Result from assertion evaluation.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `error` | `string` | No | Error message if evaluation failed |
| `expression` | `string` | Yes | CEL expression that was evaluated |
| `minPassRate` | `float32` | No | Required minimum pass rate |
| `passRate` | `float32` | No | Pass rate for repeated evaluations (0.0-1.0) |
| `passed` | `boolean` | Yes | Whether assertion passed |
| `passes` | `int32` | No | Number of passes (for repeated evaluations) |
| `runs` | `int32` | No | Total number of runs (for repeated evaluations) |
| `value` | `boolean` | Yes | Boolean result of expression |

---
<!-- GENERATED_END -->