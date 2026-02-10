# JudgeResult

Judge Result

<!-- GENERATED_START -->

## JudgeResult

Judge Result
Result from judge evaluation.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agent` | `string` | Yes | Judge agent name |
| `as` | `string` | Yes | Variable name result was stored in |
| `details` | `Record<unknown>` | Yes | Additional judge-specific details |
| `error` | `string` | No | Error message if judge failed |
| `passed` | `boolean` | Yes | Whether judge passed |
| `score` | `float32` | Yes | Score (0.0-1.0) |

---
<!-- GENERATED_END -->