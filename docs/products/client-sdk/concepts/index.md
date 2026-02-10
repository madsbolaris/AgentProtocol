# Core Concepts

Understanding the fundamental concepts of the Client SDK.

## Overview

The Client SDK provides a simple, unified API for interacting with Agent Protocol servers. It handles the complexity of runs, threads, messages, and streaming while giving you a clean, intuitive interface.

## Key Concepts

### [Data Model](data-model.md)

Understand the core primitives:

- **Runs** - A single execution of an agent
- **Threads** - Persistent conversation contexts
- **Messages** - Individual communications between you and agents
- **Participants** - Users and agents in a conversation

[Learn about the data model →](data-model.md)

### [Streaming](streaming.md)

Get real-time responses as they're generated:

- **Token-by-token streaming** for responsive UIs
- **Event-based architecture** for fine-grained control
- **Automatic reconnection** and error recovery

[Learn about streaming →](streaming.md)

### [Tools & Function Calling](tools.md)

Enable agents to call your functions:

- **Automatic tool execution** with simple callbacks
- **Type-safe tool definitions** in all languages
- **Tool result formatting** and error handling

[Learn about tools →](tools.md)

### [Error Handling](error-handling.md)

Handle failures gracefully:

- **Structured exceptions** for different error types
- **Retry strategies** for transient failures
- **Timeout management** and circuit breakers

[Learn about error handling →](error-handling.md)

---

## Next Steps

<div class="grid cards" markdown>

- **:material-rocket-launch: Quickstart**

    Get started in 5 minutes

    [:octicons-arrow-right-24: Try the Quickstart](../quickstart.md)

- **:material-book-open: How-To Guides**

    Task-focused guides

    [:octicons-arrow-right-24: Browse Guides](../guides/)

- **:material-code-braces: API Reference**

    Complete API documentation

    [:octicons-arrow-right-24: API Reference](../api-reference/)

</div>
