# Weaviate Integration

Integrate your Agent Protocol application with Weaviate.

## Overview

Connect your agents to Weaviate to leverage its open-source vector search engine. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Weaviate account
- Weaviate instance URL
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client weaviate-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client weaviate-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Weaviate.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
WEAVIATE_API_KEY=your-api-key-here
WEAVIATE_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Weaviate client
    weaviate_api_key = os.environ.get("WEAVIATE_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_weaviate():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Weaviate client
    const weaviateApiKey = process.env.WEAVIATE_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupWeaviate() {
      // Setup code here
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;
    using Microsoft.Extensions.Configuration;

    // Load configuration
    var configuration = new ConfigurationBuilder()
        .AddEnvironmentVariables()
        .Build();

    // Initialize Weaviate client
    var weaviateApiKey = configuration["WEAVIATE_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupWeaviate()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Weaviate from your agent:

=== "Python"

    ```python
    async def process_with_weaviate(message: str):
        # Process using Weaviate
        result = await weaviate_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Weaviate result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithWeaviate(message: string) {
      // Process using Weaviate
      const result = await weaviateClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Weaviate result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithWeaviate(string message)
    {
        // Process using Weaviate
        var result = await weaviateClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Weaviate result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Weaviate as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def weaviate_action(query: str) -> str:
        """Execute action using Weaviate."""
        # Implementation
        return result

    # Create tool
    weaviate_tool = Tool(
        name="weaviate_action",
        description="Use Weaviate to perform actions",
        function=weaviate_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Weaviate to help me",
        tools=[weaviate_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function weaviateAction(query: string): Promise<string> {
      // Execute action using Weaviate
      // Implementation
      return result;
    }

    // Create tool
    const weaviateTool = new Tool({
      name: 'weaviate_action',
      description: 'Use Weaviate to perform actions',
      function: weaviateAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Weaviate to help me',
      { tools: [weaviateTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> WeaviateAction(string query)
    {
        // Execute action using Weaviate
        // Implementation
        return result;
    }

    // Create tool
    var weaviateTool = new Tool
    {
        Name = "weaviate_action",
        Description = "Use Weaviate to perform actions",
        Function = WeaviateAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Weaviate to help me",
        new[] { weaviateTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Weaviate operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_weaviate_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await weaviate_client.call(data)
                return result
            except WeaviateError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Weaviate call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeWeaviateCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await weaviateClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Weaviate call failed: ${error}`);
            return null;
          }
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
      return null;
    }
    ```

=== "C#"

    ```csharp
    public async Task<T?> SafeWeaviateCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await weaviateClient.CallAsync(data);
                return result as T;
            }
            catch (WeaviateException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Weaviate call failed");
                    return null;
                }
                await Task.Delay(TimeSpan.FromSeconds(Math.Pow(2, attempt)));
            }
        }
        return null;
    }
    ```

---

## Best Practices

1. **Secure Credentials** - Never hardcode API keys
2. **Rate Limiting** - Respect Weaviate rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Weaviate integration:

```python
import prometheus_client as prom

weaviate_calls = prom.Counter(
    'weaviate_calls_total',
    'Total Weaviate calls',
    ['status']
)

weaviate_latency = prom.Histogram(
    'weaviate_latency_seconds',
    'Weaviate call latency'
)

@weaviate_latency.time()
async def monitored_weaviate_call():
    try:
        result = await weaviate_client.call()
        weaviate_calls.labels(status='success').inc()
        return result
    except Exception:
        weaviate_calls.labels(status='error').inc()
        raise
```

---

## Troubleshooting

### Common Issues

**Authentication Failures**

- Verify API key is correct and not expired
- Check environment variable names
- Ensure proper permissions/scopes

**Rate Limiting**

- Implement exponential backoff
- Use caching to reduce API calls
- Consider upgrading service tier

**Timeout Errors**

- Increase timeout values
- Optimize request payload size
- Check network connectivity

---

## Examples

Complete working examples:

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weaviate/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weaviate/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weaviate/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Weaviate Documentation](https://weaviate.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
