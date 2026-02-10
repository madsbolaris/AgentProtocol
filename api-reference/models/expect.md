# Expect

Expect

<!-- GENERATED_START -->

## Expect

Expect
Evaluation expectation with judges and assertions.
Evaluated after agent response.
STRUCTURE:
1. Optional reference output (expected agent response for comparison)
2. Judges (evaluation functions that produce results)
3. Assertions (CEL expressions using judge results)
EXECUTION:
- Wait for agent response
- Run all judges in parallel
- Evaluate all assertions using judge results
- Passes if all assertions pass

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `asserts` | `Assert[]` | Yes | Assertions using CEL expressions. |
| `judges` | `Judge[]` | Yes | Judges to evaluate output. |
| `name` | `string` | No | Optional name for this expectation. |
| `referenceOutput` | `ChatMessage` | Yes | Reference output for comparison. |

---
<!-- GENERATED_END -->