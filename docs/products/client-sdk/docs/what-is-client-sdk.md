# What is the Client SDK?

The Agent Protocol Client SDK is a multi-language library that simplifies building applications that interact with AI agents. It provides a consistent, developer-friendly API across Python, TypeScript, and C# for common agent operations.

## Overview

The Client SDK abstracts the complexity of the Agent Protocol HTTP API, providing:

- **Simple Completions**: One-line API calls for basic agent interactions
- **Streaming Responses**: Real-time token-by-token responses
- **Conversation Management**: Persistent multi-turn conversations with automatic thread handling
- **Tool Execution**: Function calling with type-safe parameter validation
- **Multimodal Support**: Images, audio, video, and file attachments
- **Error Handling**: Structured exceptions with detailed error information

## When to Use the Client SDK

### ✅ Use the Client SDK When:

- **Building Agent Applications**: You're creating chatbots, assistants, or automation tools
- **Multi-Language Projects**: You need consistent APIs across Python, TypeScript, and C#
- **Production Deployments**: You need error handling, retry logic, and production-ready patterns
- **Rapid Prototyping**: You want to test agent capabilities quickly

### ❌ Don't Use the Client SDK When:

- **Direct HTTP Control**: You need fine-grained control over HTTP requests
- **Custom Protocol**: You're implementing a non-standard agent protocol
- **Unsupported Language**: Your language isn't Python, TypeScript, or C#

## Architecture

```
┌─────────────────────────────────────┐
│   Your Application                  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Client SDK                  │ │
│  │  - AgentProtocolClient        │ │
│  │  - IConversation              │ │
│  │  - ToolCollection             │ │
│  └───────────────────────────────┘ │
│             │                       │
│             │ HTTP/HTTPS            │
│             ▼                       │
│  ┌───────────────────────────────┐ │
│  │   Agent Protocol Server       │ │
│  │  - Threads API                │ │
│  │  - Runs API                   │ │
│  │  - Messages API               │ │
│  └───────────────────────────────┘ │
│             │                       │
│             │                       │
│             ▼                       │
│  ┌───────────────────────────────┐ │
│  │   AI Agent Implementation     │ │
│  │  - LLM Integration            │ │
│  │  - Tool Handlers              │ │
│  │  - Custom Logic               │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Abstraction Levels

The SDK provides three levels of abstraction to match your needs:

### Level 1: Simple Completions (Easiest)

Perfect for quick prototypes and simple use cases:

```python
client = AgentProtocolClient("http://localhost:3978")
response = await client.complete_chat("Hello!")
```

### Level 2: Conversations (Recommended)

For multi-turn conversations with automatic thread management:

```python
conversation = client.create_conversation()
response1 = await conversation.add_user_message("What's the weather?")
response2 = await conversation.add_user_message("How about tomorrow?")
```

### Level 3: Raw Protocol (Advanced)

For fine-grained control over threads and runs:

```python
thread = await client.threads.create()
run = await client.runs.create(thread_id=thread.id, message="Hello")
```

## Key Concepts

### Threads

A **thread** is a conversation session that maintains message history. Each thread has a unique ID and contains an ordered list of messages.

### Runs

A **run** is a single execution of the agent within a thread. When you send a message, a run is created to process it and generate a response.

### Messages

**Messages** are the content exchanged in a thread. They can be:
- **User messages**: Input from your application
- **Agent messages**: Responses from the AI agent
- **Tool messages**: Results from function executions

### Tools

**Tools** are functions the agent can call to take actions or retrieve information. The SDK handles tool registration, parameter validation, and result formatting.

## Supported Languages

### Python

- **Minimum Version**: Python 3.8+
- **Package**: `microsoft-agents-protocol`
- **Install**: `pip install microsoft-agents-protocol`
- **Async Support**: Full `asyncio` integration with type hints

### TypeScript

- **Minimum Version**: Node.js 16+
- **Package**: `@microsoft/agents-protocol`
- **Install**: `npm install @microsoft/agents-protocol`
- **Type Safety**: Full TypeScript definitions included

### C#

- **Minimum Version**: .NET 6.0+
- **Package**: `Microsoft.Agents.Protocol.Client`
- **Install**: `dotnet add package Microsoft.Agents.Protocol.Client`
- **Async Support**: Modern `async/await` with `IAsyncEnumerable` for streaming

## Features

### Production-Ready

- **Error Handling**: Structured exceptions with retry guidance
- **Timeout Configuration**: Configurable request timeouts
- **Connection Pooling**: Efficient HTTP client management
- **Resource Cleanup**: Proper disposal patterns (`IDisposable`, context managers)

### Security

- **HTTPS Support**: Secure communication with agent servers
- **API Key Authentication**: Built-in support for API key auth
- **Input Validation**: Parameter sanitization and validation helpers
- **Secrets Management**: Environment variable integration

### Developer Experience

- **IntelliSense**: Full IDE autocomplete support
- **Type Safety**: Strong typing in all three languages
- **Clear Errors**: Descriptive error messages with resolution hints
- **Examples**: Comprehensive code samples for common scenarios

## Next Steps

- **[Quickstart](../quickstart.md)**: Get started in 30 minutes
- **[Core Concepts](concepts/runs-threads-messages.md)**: Deep dive into threads, runs, and messages
- **[API Reference](../api-reference/index.md)**: Complete API documentation
- **[Security](security/index.md)**: Security best practices

## Related Documentation

- **[Hosting SDK](../../hosting-sdk/index.md)**: For building agent servers
- **[XML Protocol](../../xml/index.md)**: For working with XML message formats
- **[Operations SDK](../../operations-sdk/index.md)**: For managing agent deployments
