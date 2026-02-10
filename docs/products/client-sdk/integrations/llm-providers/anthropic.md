# Anthropic Integration

Integrate your Agent Protocol application with Anthropic.

## Overview

Connect your agents to Anthropic to leverage its Claude AI provider. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Anthropic account
- Anthropic API key
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client anthropic-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client anthropic-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Anthropic.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Anthropic client
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_anthropic():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Anthropic client
    const anthropicApiKey = process.env.ANTHROPIC_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupAnthropic() {
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

    // Initialize Anthropic client
    var anthropicApiKey = configuration["ANTHROPIC_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupAnthropic()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Anthropic from your agent:

=== "Python"

    ```python
    async def process_with_anthropic(message: str):
        # Process using Anthropic
        result = await anthropic_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Anthropic result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithAnthropic(message: string) {
      // Process using Anthropic
      const result = await anthropicClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Anthropic result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithAnthropic(string message)
    {
        // Process using Anthropic
        var result = await anthropicClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Anthropic result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Anthropic as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def anthropic_action(query: str) -> str:
        """Execute action using Anthropic."""
        # Implementation
        return result

    # Create tool
    anthropic_tool = Tool(
        name="anthropic_action",
        description="Use Anthropic to perform actions",
        function=anthropic_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Anthropic to help me",
        tools=[anthropic_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function anthropicAction(query: string): Promise<string> {
      // Execute action using Anthropic
      // Implementation
      return result;
    }

    // Create tool
    const anthropicTool = new Tool({
      name: 'anthropic_action',
      description: 'Use Anthropic to perform actions',
      function: anthropicAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Anthropic to help me',
      { tools: [anthropicTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> AnthropicAction(string query)
    {
        // Execute action using Anthropic
        // Implementation
        return result;
    }

    // Create tool
    var anthropicTool = new Tool
    {
        Name = "anthropic_action",
        Description = "Use Anthropic to perform actions",
        Function = AnthropicAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Anthropic to help me",
        new[] { anthropicTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Anthropic operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_anthropic_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await anthropic_client.call(data)
                return result
            except AnthropicError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Anthropic call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeAnthropicCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await anthropicClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Anthropic call failed: ${error}`);
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
    public async Task<T?> SafeAnthropicCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await anthropicClient.CallAsync(data);
                return result as T;
            }
            catch (AnthropicException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Anthropic call failed");
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
2. **Rate Limiting** - Respect Anthropic rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Anthropic integration:

```python
import prometheus_client as prom

anthropic_calls = prom.Counter(
    'anthropic_calls_total',
    'Total Anthropic calls',
    ['status']
)

anthropic_latency = prom.Histogram(
    'anthropic_latency_seconds',
    'Anthropic call latency'
)

@anthropic_latency.time()
async def monitored_anthropic_call():
    try:
        result = await anthropic_client.call()
        anthropic_calls.labels(status='success').inc()
        return result
    except Exception:
        anthropic_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/anthropic/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/anthropic/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/anthropic/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Anthropic Documentation](https://anthropic.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
