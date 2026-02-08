# Agent Protocol Documentation

Welcome to the Agent Protocol documentation! This protocol provides a unified, standardized way to build AI agents that work across multiple platforms and frameworks.

## What is Agent Protocol?

The Agent Protocol is a comprehensive specification for building production-ready AI agents. It defines:

- **REST API Structure** - Endpoints for runs, threads, messages, and agent management
- **Multi-Modal Content** - Support for text, images, audio, video, files, and structured data
- **Tool Execution** - Standardized function calling with streaming support
- **State Management** - Run lifecycle, conversation history, and persistence
- **Security & Compliance** - OAuth2, encryption, PII handling, HIPAA patterns
- **Real-Time Communication** - SSE streaming, webhooks, bidirectional audio/video

!!! tip "👋 New to Agent Protocol?"

    **Start here!** Our [5-Minute Quickstart](getting-started/index.md) will help you:

    1. ✅ Send your first agent message
    2. ✅ Receive a streaming response
    3. ✅ Execute a tool with function calling

    ⏱️ Takes 5 minutes | 📋 No complex setup required

## Quick Navigation

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    New to Agent Protocol? Start here with quickstart guides and basic examples.

    [:octicons-arrow-right-24: Get Started](getting-started/index.md)

-   :material-book-open-variant:{ .lg .middle } **API Reference**

    ---

    Complete API documentation with all endpoints, models, and content types.

    [:octicons-arrow-right-24: API Reference](api-reference/index.md)

-   :material-cog:{ .lg .middle } **Specifications**

    ---

    Behavioral specifications, state machines, validation rules, and requirements.

    [:octicons-arrow-right-24: Specifications](specifications/index.md)

-   :material-compass:{ .lg .middle } **Integration Guides**

    ---

    Patterns for security, webhooks, multi-agent systems, voice integration, and more.

    [:octicons-arrow-right-24: Guides](guides/index.md)

</div>

## Quick Start Example

Send a message and get an agent response in one API call:

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    client = AgentProtocolClient(AgentProtocolClientOptions(
        base_url="https://agents.example.com/v1",
        api_key="your-api-key"
    ))

    async with client:
        result = await client.runs.create({
            "agentId": "my-agent",
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Hello! What can you help me with?"}]
            }]
        })
        print(result["output"][0]["contents"][0]["text"])
    ```

=== "JavaScript/TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient({
        baseUrl: "https://agents.example.com/v1",
        apiKey: "your-api-key"
    });

    const result = await client.runs.create({
        agentId: "my-agent",
        input: [{
            role: "user",
            contents: [{ kind: "text", text: "Hello! What can you help me with?" }]
        }]
    });

    console.log(result.output[0].contents[0].text);
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    var client = new AgentProtocolClient(new AgentProtocolClientOptions
    {
        BaseUrl = "https://agents.example.com/v1",
        ApiKey = "your-api-key"
    });

    var result = await client.Runs.CreateAsync(new
    {
        agentId = "my-agent",
        input = new[]
        {
            new
            {
                role = "user",
                contents = new[] { new { kind = "text", text = "Hello! What can you help me with?" } }
            }
        }
    });

    Console.WriteLine(result.Output[0].Contents[0].Text);
    ```

**Response:**

```json
{
  "runId": "run_abc123",
  "status": "completed",
  "output": [{
    "role": "assistant",
    "contents": [{
      "kind": "text",
      "text": "Hello! I'm an AI assistant. I can help you with questions, tasks, and more. What would you like assistance with today?"
    }]
  }],
  "usage": {
    "inputTokens": 12,
    "outputTokens": 25,
    "totalTokens": 37
  }
}
```

That's it! You just made your first agent call. [:octicons-arrow-right-24: See full tutorial](getting-started/index.md)

## Key Features

### :material-palette: Multi-Modal Content

Support for 29 content types including text, images, audio, video, files, function calls, search results, and more.

```json
{
  "role": "assistant",
  "contents": [
    {"kind": "text", "text": "Here's the analysis:"},
    {"kind": "image", "uri": "https://example.com/chart.png"},
    {"kind": "file", "filename": "report.pdf", "dataUri": "data:..."}
  ]
}
```

[:octicons-arrow-right-24: Content Types](api-reference/content-types.md)

### :material-hammer-wrench: Tool Execution

Standardized function calling with support for streaming large inputs/outputs.

```json
{
  "kind": "functionCall",
  "callId": "call_abc",
  "name": "search_database",
  "arguments": {
    "query": "customers in California",
    "limit": 100
  }
}
```

[:octicons-arrow-right-24: Tool Execution](specifications/tool-execution.md)

### :material-shield-lock: Security & Compliance

Built-in patterns for OAuth2, content encryption, PII redaction, and HIPAA compliance.

```json
{
  "kind": "text",
  "text": "Patient has diabetes",
  "encryption": "aes-256-gcm:key-hipaa-001",
  "audience": "healthcare-providers"
}
```

[:octicons-arrow-right-24: Security Guide](guides/security-compliance.md)

### :material-sync: Real-Time Streaming

Server-Sent Events for streaming responses, tool results, and bidirectional audio/video.

```http
GET /runs/{runId}/stream HTTP/1.1
Accept: text/event-stream

event: message.delta
data: {"delta": {"contents": [{"kind": "text", "text": "Hello"}]}}

event: message.completed
data: {"message": {...}}
```

[:octicons-arrow-right-24: Streaming Guide](specifications/streaming.md)

### :material-robot: Multi-Agent Orchestration

Agent handoffs, delegation patterns, and human-in-the-loop workflows.

```json
{
  "kind": "text",
  "text": "Transferring to billing specialist...",
  "audience": "user"
},
{
  "kind": "action",
  "action": "transfer",
  "targetAgent": "billing-agent"
}
```

[:octicons-arrow-right-24: Multi-Agent Guide](guides/multi-agent.md)

## Documentation Structure

### :material-run-fast: [Getting Started](getting-started/index.md)
Quickstart guides, installation instructions, and basic examples to get you up and running quickly.

### :material-api: [API Reference](api-reference/index.md)
Complete API documentation including all endpoints, models, content types, and operation details.

### :material-file-document: [Specifications](specifications/index.md)
Behavioral specifications defining state machines, validation rules, error semantics, and requirements.

### :material-compass: [Guides](guides/index.md)
Integration patterns for common scenarios including security, webhooks, testing, deployment, and more.

### :material-code-braces: [TypeSpec](typespec/index.md)
TypeSpec schema definitions that serve as the single source of truth for the API structure.

### :material-handshake: [Contributing](contributing.md)
Guidelines for contributing to the protocol, documentation standards, and validation workflows.

## TypeSpec Foundation

The Agent Protocol is defined using [TypeSpec](https://typespec.io/), providing:

- **Type-Safe Contracts** - Validated schemas for all API operations
- **OpenAPI Generation** - Automatic OpenAPI 3.0 specification generation
- **SDK Generation** - Client library generation for multiple languages
- **Documentation Sync** - Single source of truth that keeps docs and code in sync

```typescript
// typespec/messages.tsp
model ChatMessage {
  messageId: string;
  role: "user" | "assistant" | "system";
  contents: AIContent[];
  timestamp?: utcDateTime;
}

union AIContent {
  TextContent,
  ImageContent,
  AudioContent,
  VideoContent,
  FunctionCallContent,
  FunctionResultContent,
  // ... 23 more types
}
```

[:octicons-arrow-right-24: Explore TypeSpec Definitions](typespec/index.md)

## Framework Alignment

This protocol aligns with and extends patterns from:

| Framework | Alignment |
|-----------|-----------|
| **Microsoft Agent Framework (MAF)** | ChatMessage, Run, Thread models |
| **OpenAI Agents SDK** | Tool system, streaming, function calling |
| **Azure Agent API** | Multi-modal content types (audio, video, file) |
| **Google A2A Protocol** | Agent cards, discovery, task lifecycle |
| **LangGraph** | State management, checkpointing, HITL patterns |

## Use Cases

The Agent Protocol supports a wide range of AI agent scenarios:

- **Customer Support** - Chatbots with tool calling and escalation
- **Enterprise Assistants** - Multi-agent systems with security/compliance
- **Voice Applications** - Bidirectional audio streaming and transcription
- **Data Analysis** - Agents that query databases and generate reports
- **Workflow Automation** - Agents that orchestrate multi-step processes
- **Healthcare** - HIPAA-compliant agents with PII handling
- **Developer Tools** - Code generation, testing, and deployment agents

## Implementation Status

**Specification Status:** `v2.0` - Stable

**Implementations:**
- :material-language-csharp: C# (agent-xml) - Reference implementation with XML serialization
- :material-language-python: Python - Community implementation (link TBD)
- :material-language-typescript: TypeScript - Community implementation (link TBD)

## Community & Support

- **GitHub Repository** - [View source](https://github.com/madsbolaris/AgentProtocol)
- **Issue Tracker** - [Report bugs](https://github.com/madsbolaris/AgentProtocol/issues)
- **Discussions** - [Ask questions](https://github.com/madsbolaris/AgentProtocol/discussions)
- **Contributing** - [Contribution guidelines](contributing.md)

## Next Steps

<div class="grid cards" markdown>

-   :material-run-fast: **New to Agent Protocol?**

    Start with the [Getting Started Guide](getting-started/index.md) for a step-by-step introduction.

-   :material-book-open: **Building an Integration?**

    Check out the [Integration Guides](guides/index.md) for common patterns and best practices.

-   :material-code-tags: **Implementing a Server?**

    Read the [Specifications](specifications/index.md) to understand required behaviors.

-   :material-api: **Looking for API Details?**

    Browse the [API Reference](api-reference/index.md) for complete endpoint documentation.

</div>

---

**Questions?** Check the [Contributing Guide](contributing.md) or [open an issue](https://github.com/madsbolaris/AgentProtocol/issues).
