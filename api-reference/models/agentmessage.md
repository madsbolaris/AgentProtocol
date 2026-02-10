# AgentMessage

Example of a complex agent message with function calls.

<!-- GENERATED_START -->

## AgentMessage

Example of a complex agent message with function calls.
XML Output:
```xml
<agent
message-id="msg_456"
thread-id="thread_123"
agent-id="agent_001"
model="claude-sonnet-4.5"
created-at="2026-02-07T10:00:00Z">
<thinking exposed="false">
Need to call weather API for Seattle
</thinking>
<function-call call-id="call_001" name="get_weather">
{"location": "Seattle, WA", "units": "fahrenheit"}
</function-call>
</agent>
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | No |  |
| `completedAt` | `utcDateTime` | No |  |
| `contents` | `ContentType[]` | Yes |  |
| `createdAt` | `utcDateTime` | Yes |  |
| `messageId` | `string` | Yes |  |
| `model` | `string` | No |  |
| `threadId` | `string` | No |  |

---
<!-- GENERATED_END -->