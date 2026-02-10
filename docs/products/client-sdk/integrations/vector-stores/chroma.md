# Chroma Integration

Integrate your Agent Protocol application with Chroma.

## Overview

Connect your agents to Chroma to leverage its embedded vector database. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Chroma account
- Chroma client configuration
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client chroma-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client chroma-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Chroma.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
CHROMA_API_KEY=your-api-key-here
CHROMA_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Chroma client
    chroma_api_key = os.environ.get("CHROMA_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_chroma():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Chroma client
    const chromaApiKey = process.env.CHROMA_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupChroma() {
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

    // Initialize Chroma client
    var chromaApiKey = configuration["CHROMA_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupChroma()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Chroma from your agent:

=== "Python"

    ```python
    async def process_with_chroma(message: str):
        # Process using Chroma
        result = await chroma_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Chroma result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithChroma(message: string) {
      // Process using Chroma
      const result = await chromaClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Chroma result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithChroma(string message)
    {
        // Process using Chroma
        var result = await chromaClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Chroma result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Chroma as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def chroma_action(query: str) -> str:
        """Execute action using Chroma."""
        # Implementation
        return result

    # Create tool
    chroma_tool = Tool(
        name="chroma_action",
        description="Use Chroma to perform actions",
        function=chroma_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Chroma to help me",
        tools=[chroma_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function chromaAction(query: string): Promise<string> {
      // Execute action using Chroma
      // Implementation
      return result;
    }

    // Create tool
    const chromaTool = new Tool({
      name: 'chroma_action',
      description: 'Use Chroma to perform actions',
      function: chromaAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Chroma to help me',
      { tools: [chromaTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> ChromaAction(string query)
    {
        // Execute action using Chroma
        // Implementation
        return result;
    }

    // Create tool
    var chromaTool = new Tool
    {
        Name = "chroma_action",
        Description = "Use Chroma to perform actions",
        Function = ChromaAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Chroma to help me",
        new[] { chromaTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Chroma operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_chroma_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await chroma_client.call(data)
                return result
            except ChromaError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Chroma call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeChromaCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await chromaClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Chroma call failed: ${error}`);
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
    public async Task<T?> SafeChromaCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await chromaClient.CallAsync(data);
                return result as T;
            }
            catch (ChromaException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Chroma call failed");
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
2. **Rate Limiting** - Respect Chroma rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Chroma integration:

```python
import prometheus_client as prom

chroma_calls = prom.Counter(
    'chroma_calls_total',
    'Total Chroma calls',
    ['status']
)

chroma_latency = prom.Histogram(
    'chroma_latency_seconds',
    'Chroma call latency'
)

@chroma_latency.time()
async def monitored_chroma_call():
    try:
        result = await chroma_client.call()
        chroma_calls.labels(status='success').inc()
        return result
    except Exception:
        chroma_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/chroma/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/chroma/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/chroma/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Chroma Documentation](https://chroma.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
