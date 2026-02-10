# Client SDK Guides

Comprehensive guides for building applications with the Agent Protocol Client SDK.

## Overview

This section provides practical guides for implementing common patterns, integrating with external services, and following best practices when building Agent Protocol applications.

---

## Getting Started

New to the Client SDK? Start here:

- [Quickstart](../quickstart.md) - Get up and running in 5 minutes
- [Installation](installation.md) - Detailed installation instructions
- [Basic Concepts](../concepts/index.md) - Core concepts and terminology
- [First Application](tutorials/first-app.md) - Build your first agent

---

## Implementation Guides

### Core Features

- **[Multimodal Support](multimodal.md)** - Working with text, images, audio, and video
- **[Tool Integration](tools.md)** - Adding custom tools and function calling
- **[Batch Processing](batch-processing.md)** - Processing multiple requests efficiently
- **[Testing Strategies](testing.md)** - Unit, integration, and end-to-end testing

### Best Practices

- **[Best Practices Overview](best-practices/index.md)** - Production-ready patterns
- **[Error Handling](best-practices/error-handling.md)** - Robust error management
- **[Performance Optimization](best-practices/performance.md)** - Optimize for speed and efficiency
- **[Security](best-practices/security.md)** - Secure your applications

---

## Tutorials

Step-by-step tutorials for common use cases:

- **[Building a Chatbot](tutorials/chatbot.md)** - Create an interactive conversational agent
- **[RAG Implementation](tutorials/rag.md)** - Build a retrieval-augmented generation system
- **[Multi-Agent System](tutorials/multi-agent.md)** - Coordinate multiple agents
- **[Custom Tool Development](tutorials/custom-tools.md)** - Create and integrate custom tools

---

## Language-Specific Guides

### Python

=== "Python"

    ```python
    from microsoft.agents import AgentProtocolClient

    # Create client
    client = AgentProtocolClient(base_url="http://localhost:3978")

    # Send message
    async def main():
        response = await client.send_one_off("Hello, agent!")
        print(response.text)
    ```

**Python Resources:**

- [Python API Reference](../api-reference/python/index.md)
- [Python Best Practices](best-practices/python.md)
- [Python Deployment](../deployment/python.md)

### TypeScript

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';

    // Create client
    const client = new AgentProtocolClient({
      baseUrl: 'http://localhost:3978'
    });

    // Send message
    async function main() {
      const response = await client.sendOneOff('Hello, agent!');
      console.log(response.text);
    }
    ```

**TypeScript Resources:**

- [TypeScript API Reference](../api-reference/typescript/index.md)
- [TypeScript Best Practices](best-practices/typescript.md)
- [TypeScript Deployment](../deployment/typescript.md)

### C#

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;

    // Create client
    var client = new AgentProtocolClient("http://localhost:3978");

    // Send message
    var response = await client.SendOneOffAsync("Hello, agent!");
    Console.WriteLine(response.Text);
    ```

**C# Resources:**

- [C# API Reference](../api-reference/csharp/index.md)
- [C# Best Practices](best-practices/csharp.md)
- [C# Deployment](../deployment/csharp.md)

---

## Integration Guides

Connect with popular platforms and services:

### LLM Providers

- [OpenAI](../integrations/llm-providers/openai.md)
- [Azure OpenAI](../integrations/llm-providers/azure-openai.md)
- [Anthropic](../integrations/llm-providers/anthropic.md)

### Communication Channels

- [Microsoft Teams](../integrations/channels/teams.md)
- [Slack](../integrations/channels/slack.md)
- [Discord](../integrations/channels/discord.md)

### Vector Stores

- [Pinecone](../integrations/vector-stores/pinecone.md)
- [Weaviate](../integrations/vector-stores/weaviate.md)
- [Chroma](../integrations/vector-stores/chroma.md)

### Tools and APIs

- [Weather APIs](../integrations/tools/weather-api.md)
- [Database Tools](../integrations/tools/database.md)
- [Search APIs](../integrations/tools/search-apis.md)

---

## Patterns and Use Cases

Learn common architectural patterns:

- **[Chatbot Pattern](../use-cases/chatbot/index.md)** - Interactive conversation management
- **[Function Calling Pattern](../use-cases/function-calling/index.md)** - Tool use and execution
- **[RAG Pattern](../use-cases/rag/index.md)** - Knowledge retrieval and generation
- **[Multi-Agent Pattern](../use-cases/multi-agent/index.md)** - Agent coordination and orchestration
- **[Production Deployment](../use-cases/production/index.md)** - Production-ready deployments

---

## Advanced Topics

### Performance and Scalability

- **[Connection Pooling](advanced/connection-pooling.md)** - Efficient connection management
- **[Caching Strategies](advanced/caching.md)** - Response and data caching
- **[Load Balancing](advanced/load-balancing.md)** - Distribute requests effectively
- **[Rate Limiting](advanced/rate-limiting.md)** - Control request rates

### Observability

- **[Logging](../observability/logging/index.md)** - Structured logging patterns
- **[Metrics](../observability/metrics/index.md)** - Performance monitoring
- **[Tracing](../observability/tracing/index.md)** - Distributed tracing
- **[Observability Integrations](../observability/integrations/index.md)** - Platform integrations

### Testing

- **[Unit Testing](../testing/unit-testing/index.md)** - Test individual components
- **[Integration Testing](../testing/integration-testing/index.md)** - Test component interactions
- **[Security Testing](../testing/security-testing/index.md)** - Security validation
- **[Compliance Testing](../testing/compliance-testing/index.md)** - Compliance verification

---

## Troubleshooting

Common issues and solutions:

- **[Connection Issues](../troubleshooting/connection.md)** - Resolve connectivity problems
- **[Authentication Errors](../troubleshooting/authentication.md)** - Fix auth issues
- **[Performance Problems](../troubleshooting/performance.md)** - Diagnose slowness
- **[Error Messages](../troubleshooting/errors.md)** - Understanding error codes

---

## Migration Guides

Upgrading or migrating? Check these guides:

- **[Migration from v1 to v2](../docs/migration/v1-to-v2.md)** - Breaking changes and upgrade path
- **[Legacy System Migration](../docs/migration/legacy.md)** - Migrate from older systems
- **[Platform Migration](../docs/migration/platforms.md)** - Move between platforms

---

## Contributing

Help improve the Client SDK:

- [Contributing Guidelines](../../community/contributing.md)
- [Code of Conduct](../../community/code-of-conduct.md)
- [Development Setup](../../community/development.md)

---

## Quick Reference

### Common Operations

=== "Python"

    ```python
    # Send one-off message
    response = await client.send_one_off("Hello")

    # Create thread
    thread = await client.create_thread()

    # Send to thread
    response = await client.send_to_thread(thread.id, "Hello")

    # Stream response
    async for chunk in client.stream("Tell me a story"):
        print(chunk.text)

    # Use tools
    response = await client.send_with_tools(
        "What's the weather?",
        tools=[weather_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    // Send one-off message
    const response = await client.sendOneOff('Hello');

    // Create thread
    const thread = await client.createThread();

    // Send to thread
    const response = await client.sendToThread(thread.id, 'Hello');

    // Stream response
    for await (const chunk of client.stream('Tell me a story')) {
      console.log(chunk.text);
    }

    // Use tools
    const response = await client.sendWithTools(
      'What\'s the weather?',
      { tools: [weatherTool] }
    );
    ```

=== "C#"

    ```csharp
    // Send one-off message
    var response = await client.SendOneOffAsync("Hello");

    // Create thread
    var thread = await client.CreateThreadAsync();

    // Send to thread
    var response = await client.SendToThreadAsync(thread.Id, "Hello");

    // Stream response
    await foreach (var chunk in client.StreamAsync("Tell me a story"))
    {
        Console.WriteLine(chunk.Text);
    }

    // Use tools
    var response = await client.SendWithToolsAsync(
        "What's the weather?",
        new[] { weatherTool }
    );
    ```

---

## See Also

- [Client SDK Overview](../index.md)
- [API Reference](../api-reference/index.md)
- [Concepts](../concepts/index.md)
- [Examples Repository](https://github.com/microsoft/agent-protocol/tree/main/examples)
