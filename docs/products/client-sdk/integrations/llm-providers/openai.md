# OpenAI Integration

Integrate your Agent Protocol application with OpenAI.

## Overview

Connect your agents to OpenAI to leverage its leading LLM provider. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- OpenAI account
- OpenAI API key
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client openai-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client openai-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package OpenAI.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
OPENAI_API_KEY=your-api-key-here
OPENAI_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize OpenAI client
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_openai():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize OpenAI client
    const openaiApiKey = process.env.OPENAI_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupOpenAI() {
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

    // Initialize OpenAI client
    var openaiApiKey = configuration["OPENAI_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupOpenAI()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to OpenAI from your agent:

=== "Python"

    ```python
    async def process_with_openai(message: str):
        # Process using OpenAI
        result = await openai_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this OpenAI result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithOpenAI(message: string) {
      // Process using OpenAI
      const result = await openaiClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this OpenAI result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithOpenAI(string message)
    {
        // Process using OpenAI
        var result = await openaiClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this OpenAI result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose OpenAI as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def openai_action(query: str) -> str:
        """Execute action using OpenAI."""
        # Implementation
        return result

    # Create tool
    openai_tool = Tool(
        name="openai_action",
        description="Use OpenAI to perform actions",
        function=openai_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use OpenAI to help me",
        tools=[openai_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function openaiAction(query: string): Promise<string> {
      // Execute action using OpenAI
      // Implementation
      return result;
    }

    // Create tool
    const openaiTool = new Tool({
      name: 'openai_action',
      description: 'Use OpenAI to perform actions',
      function: openaiAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use OpenAI to help me',
      { tools: [openaiTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> OpenAIAction(string query)
    {
        // Execute action using OpenAI
        // Implementation
        return result;
    }

    // Create tool
    var openaiTool = new Tool
    {
        Name = "openai_action",
        Description = "Use OpenAI to perform actions",
        Function = OpenAIAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use OpenAI to help me",
        new[] { openaiTool }
    );
    ```

---

## Error Handling

Implement robust error handling for OpenAI operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_openai_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await openai_client.call(data)
                return result
            except OpenAIError as e:
                if attempt == max_retries - 1:
                    logger.error(f"OpenAI call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeOpenAICall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await openaiClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`OpenAI call failed: ${error}`);
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
    public async Task<T?> SafeOpenAICall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await openaiClient.CallAsync(data);
                return result as T;
            }
            catch (OpenAIException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "OpenAI call failed");
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
2. **Rate Limiting** - Respect OpenAI rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your OpenAI integration:

```python
import prometheus_client as prom

openai_calls = prom.Counter(
    'openai_calls_total',
    'Total OpenAI calls',
    ['status']
)

openai_latency = prom.Histogram(
    'openai_latency_seconds',
    'OpenAI call latency'
)

@openai_latency.time()
async def monitored_openai_call():
    try:
        result = await openai_client.call()
        openai_calls.labels(status='success').inc()
        return result
    except Exception:
        openai_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/openai/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/openai/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/openai/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [OpenAI Documentation](https://openai.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
