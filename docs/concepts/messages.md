# Messages

A **message** is a single contribution to a conversation in a thread. Messages are exchanged between participants (users, agents, tools, systems) and form the conversation history.

## What is a Message?

Messages are the building blocks of conversations. Each message has:
- **Role** - Who sent it (user, assistant, tool, system, developer)
- **Contents** - What was communicated (text, images, function calls, etc.)
- **Metadata** - Timestamps, IDs, sender info

## Message Roles

### User
Messages from end users:
```
"What's the weather today?"
"Can you help me with this code?"
```

### Assistant (Agent)
Responses from AI agents:
```
"The weather is sunny and 72°F"
"I can help you with that code. What's the issue?"
```

### Tool
Results from tool/function executions:
```
get_weather() → {"temp": 72, "condition": "sunny"}
```

### System
System-level instructions and context:
```
"You are a helpful assistant that answers concisely."
```

### Developer
Developer-provided instructions and guardrails:
```
"Always respond in a professional tone."
```

## Message Contents

Messages are **multimodal** - they can contain multiple types of content:

### Text
```
"Hello, how can I help you today?"
```

### Images
```
[image: user_screenshot.png]
"What's wrong with this error?"
```

### Function Calls
```
function_call: get_weather(location="Seattle")
```

### Function Results
```
function_result: {"temperature": 72, "condition": "sunny"}
```

### Files
```
[file: report.pdf]
"Please analyze this report"
```

### Mixed Content
A single message can have multiple content types:
```
Message:
  - Text: "Here's the weather data:"
  - Image: [weather_map.png]
  - Text: "And the forecast shows..."
```

## Message Properties

- **ID** - Unique identifier
- **Thread ID** - Which conversation
- **Role** - Who sent it
- **Contents** - Array of content items
- **Created timestamp** - When sent
- **Metadata** - Custom data
- **Sender info** - Participant details

## Message Flow

### Simple Conversation
```
Thread
├─ Message 1 (user): "Hello"
├─ Message 2 (assistant): "Hi! How can I help?"
├─ Message 3 (user): "What's 2+2?"
└─ Message 4 (assistant): "2+2 equals 4"
```

### Tool Usage
```
Thread
├─ Message 1 (user): "What's the weather?"
├─ Message 2 (assistant): [function_call: get_weather]
├─ Message 3 (tool): [result: 72°F, sunny]
└─ Message 4 (assistant): "It's 72°F and sunny"
```

### Multi-participant
```
Thread
├─ Message 1 (user): "I need help"
├─ Message 2 (agent_1): "I'll research that"
├─ Message 3 (agent_2): "Here's what I found"
└─ Message 4 (user): "Perfect, thanks!"
```

## Content Types

The protocol supports rich content types:

- **TextContent** - Plain text
- **ImageContent** - Images (URL or base64)
- **AudioContent** - Audio files
- **VideoContent** - Video files
- **FileContent** - Generic files
- **FunctionCallContent** - Tool invocations
- **FunctionResultContent** - Tool results
- **AdaptiveCardContent** - Rich UI cards
- **DataContent** - Structured data
- **ErrorContent** - Error information

See [Reference](../reference/abstractions/) for all content types.

## Message History

Threads maintain message history, which provides:
- **Context** - Agents see previous conversation
- **Continuity** - Multi-turn conversations work
- **Audit trail** - Track what was said
- **Debugging** - Understand agent behavior

## Related Concepts

- **[Threads](threads.md)** - Where messages live
- **[Runs](runs.md)** - How agents generate messages
- **[Tools](tools.md)** - Functions that create tool messages
- **[Content Types](../reference/abstractions/)** - All message content types

## Best Practices

✅ **Do:**
- Use appropriate roles for each message
- Include multiple content types when helpful
- Preserve message history for context
- Set meaningful metadata

❌ **Don't:**
- Mix unrelated content in one message
- Send empty messages
- Modify message history arbitrarily
- Store sensitive data in message content

## Message Events

Messages trigger lifecycle events:
- **message_created** - New message added
- **message_updated** - Message modified
- **message_completed** - Message fully processed
- **message_deleted** - Message removed

See [Events](events.md) for more.

## Next Steps

- Learn about [Threads](threads.md) to organize messages
- Understand [Runs](runs.md) to generate messages
- Explore [Content Types](../reference/abstractions/) for all options
