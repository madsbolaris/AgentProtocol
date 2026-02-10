# AutoResponseConfig

Auto Response Configuration

<!-- GENERATED_START -->

## AutoResponseConfig

Auto Response Configuration

### Usage

Use Cases:
- Support agents: Respond to user messages in support threads
- Specialized agents: Respond only when mentioned or when specific content appears
- Monitoring agents: React to video, files, or other content types

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `maxConsecutiveRuns` | `int32 = 1` | No | Maximum consecutive runs before requiring user message. |
| `runCondition` | `RunCondition` | No | Condition for when agent should participate. |
| `threadCleanup` | `ThreadCleanup` | No | Thread cleanup after participation. |

---
<!-- GENERATED_END -->