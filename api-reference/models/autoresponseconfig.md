# AutoResponseConfig

Auto Response Configuration

<!-- GENERATED_START -->

## AutoResponseConfig

Auto Response Configuration
Key Capabilities:
- Condition-based participation (always, roles, content, mentions)
- Loop prevention via maxConsecutiveRuns
- Thread cleanup strategy (keep or delete)

### Usage

Configuration for automatic agent participation in threads.
Determines when and how agents should respond to thread activity.
Prevents infinite loops with maxConsecutiveRuns limit.

Key Capabilities:
- Condition-based participation (always, roles, content, mentions)
- Loop prevention via maxConsecutiveRuns
- Thread cleanup strategy (keep or delete)

Use Cases:
- Support agents: Respond to all user messages
- Specialized agents: Respond only when mentioned
- Monitoring agents: React to specific content types (video, files)
- Multi-agent conversations: Limit consecutive runs to prevent loops

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `maxConsecutiveRuns` | `int32 = 1` | No | Maximum consecutive runs before requiring user message. |
| `runCondition` | `RunCondition` | No | Condition for when agent should participate. |
| `threadCleanup` | `ThreadCleanup` | No | Thread cleanup after participation. |

### Examples

#### Always respond to user messages

```json
{
"runCondition": {
"kind": "roles",
"roles": ["user"]
},
"maxConsecutiveRuns": 1,
"threadCleanup": "keep"
}
```

#### Respond only when mentioned

```json
{
"runCondition": {
"kind": "mention",
"requireExplicitMention": true
},
"maxConsecutiveRuns": 1,
"threadCleanup": "keep"
}
```

#### Multi-agent with loop prevention

```json
{
"runCondition": {
"kind": "roles",
"roles": ["user", "assistant"]
},
"maxConsecutiveRuns": 2,
"threadCleanup": "keep"
}
```

#### React to video content

```json
{
"runCondition": {
"kind": "content",
"contentTypes": ["video"]
},
"maxConsecutiveRuns": 1,
"threadCleanup": "keep"
}
```

---
<!-- GENERATED_END -->