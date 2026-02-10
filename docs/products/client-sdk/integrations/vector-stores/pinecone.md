# Pinecone Integration

Integrate your Agent Protocol application with Pinecone.

## Overview

Connect your agents to Pinecone to leverage its managed vector database. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Pinecone account
- Pinecone API key
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client pinecone-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client pinecone-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Pinecone.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
PINECONE_API_KEY=your-api-key-here
PINECONE_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Pinecone client
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_pinecone():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Pinecone client
    const pineconeApiKey = process.env.PINECONE_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupPinecone() {
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

    // Initialize Pinecone client
    var pineconeApiKey = configuration["PINECONE_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupPinecone()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Pinecone from your agent:

=== "Python"

    ```python
    async def process_with_pinecone(message: str):
        # Process using Pinecone
        result = await pinecone_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Pinecone result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithPinecone(message: string) {
      // Process using Pinecone
      const result = await pineconeClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Pinecone result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithPinecone(string message)
    {
        // Process using Pinecone
        var result = await pineconeClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Pinecone result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Pinecone as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def pinecone_action(query: str) -> str:
        """Execute action using Pinecone."""
        # Implementation
        return result

    # Create tool
    pinecone_tool = Tool(
        name="pinecone_action",
        description="Use Pinecone to perform actions",
        function=pinecone_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Pinecone to help me",
        tools=[pinecone_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function pineconeAction(query: string): Promise<string> {
      // Execute action using Pinecone
      // Implementation
      return result;
    }

    // Create tool
    const pineconeTool = new Tool({
      name: 'pinecone_action',
      description: 'Use Pinecone to perform actions',
      function: pineconeAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Pinecone to help me',
      { tools: [pineconeTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> PineconeAction(string query)
    {
        // Execute action using Pinecone
        // Implementation
        return result;
    }

    // Create tool
    var pineconeTool = new Tool
    {
        Name = "pinecone_action",
        Description = "Use Pinecone to perform actions",
        Function = PineconeAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Pinecone to help me",
        new[] { pineconeTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Pinecone operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_pinecone_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await pinecone_client.call(data)
                return result
            except PineconeError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Pinecone call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safePineconeCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await pineconeClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Pinecone call failed: ${error}`);
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
    public async Task<T?> SafePineconeCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await pineconeClient.CallAsync(data);
                return result as T;
            }
            catch (PineconeException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Pinecone call failed");
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
2. **Rate Limiting** - Respect Pinecone rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Pinecone integration:

```python
import prometheus_client as prom

pinecone_calls = prom.Counter(
    'pinecone_calls_total',
    'Total Pinecone calls',
    ['status']
)

pinecone_latency = prom.Histogram(
    'pinecone_latency_seconds',
    'Pinecone call latency'
)

@pinecone_latency.time()
async def monitored_pinecone_call():
    try:
        result = await pinecone_client.call()
        pinecone_calls.labels(status='success').inc()
        return result
    except Exception:
        pinecone_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/pinecone/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/pinecone/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/pinecone/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Pinecone Documentation](https://pinecone.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
