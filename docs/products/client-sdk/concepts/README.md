# Core Concepts

Fundamental concepts for working with the Client SDK.

## Overview

Understanding these core concepts will help you build robust agent applications with the Client SDK. Each concept builds on the previous ones, creating a comprehensive mental model.

---

## Key Concepts

### [Data Model](data-model.md)

Learn about the core primitives: Threads, Runs, Messages, and Participants.

**What you'll learn:**
- How conversations are structured
- The lifecycle of threads and runs
- Message types and roles
- Managing participants

[Read more →](data-model.md)

### [Streaming](streaming.md)

Receive real-time updates as agents generate responses.

**What you'll learn:**
- When to use streaming vs. non-streaming
- Handling streaming events
- Error recovery during streams
- Performance optimization

[Read more →](streaming.md)

### [Tools & Function Calling](tools.md)

Enable agents to call your functions and access external systems.

**What you'll learn:**
- Defining tools with JSON Schema
- Handling tool calls from agents
- Validation and error handling
- Best practices for tool design

[Read more →](tools.md)

### [Error Handling](error-handling.md)

Handle failures gracefully with structured error handling.

**What you'll learn:**
- Exception hierarchy
- Retry strategies
- Circuit breakers
- Logging and debugging

[Read more →](error-handling.md)

---

## Learning Path

For the best learning experience, follow this sequence:

1. Start with **Data Model** to understand the foundation
2. Learn **Streaming** to build responsive UIs
3. Explore **Tools** to extend agent capabilities
4. Master **Error Handling** for production-ready code

---

## Quick Examples

### Basic Conversation

```python
from microsoft.agents.client import AgentProtocolClient

client = AgentProtocolClient(base_url="http://localhost:3000")
conversation = client.create_conversation()

response = await conversation.send("Hello!")
print(response.text)
```

### Streaming Response

```typescript
import { AgentProtocolClient } from '@microsoft/agents-client';

const client = new AgentProtocolClient({ baseUrl: 'http://localhost:3000' });
const conversation = client.createConversation();

for await (const event of conversation.stream('Tell me a story')) {
  if (event.type === 'text') {
    process.stdout.write(event.text);
  }
}
```

### Tool Calling

```csharp
using Microsoft.Agents.Client;
using Microsoft.Agents.Abstractions;

var client = new AgentProtocolClient("http://localhost:3000");
var tools = new ToolCollection();

tools.Add("get_weather", "Get current weather", async (location) => {
    return await WeatherService.GetWeatherAsync(location);
});

var conversation = client.CreateConversation();
var response = await conversation.SendAsync("What's the weather in Seattle?", tools);
```

---

## Advanced Topics

Once you've mastered the basics, explore:

- [Testing Strategies](../guides/testing.md)
- [Production Deployment](../docs/deployment/index.md)
- [Security Best Practices](../docs/security/index.md)
- [Observability](../observability/index.md)

---

## See Also

- [API Reference](../api-reference/index.md) - Detailed API documentation
- [Guides](../guides/index.md) - Step-by-step tutorials
- [Examples](../examples/index.md) - Complete working examples
