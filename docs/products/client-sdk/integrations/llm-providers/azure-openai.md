# Azure OpenAI Integration

Integrate your Agent Protocol application with Azure OpenAI.

## Overview

Connect your agents to Azure OpenAI to leverage its enterprise-grade LLM service. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Azure OpenAI account
- Azure credentials
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client azure_openai-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client azure_openai-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Azure.OpenAI.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Azure OpenAI client
    azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_azure_openai():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Azure OpenAI client
    const azure_openaiApiKey = process.env.AZURE_OPENAI_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupAzureOpenAI() {
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

    // Initialize Azure OpenAI client
    var azure_openaiApiKey = configuration["AZURE_OPENAI_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupAzureOpenAI()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Azure OpenAI from your agent:

=== "Python"

    ```python
    async def process_with_azure_openai(message: str):
        # Process using Azure OpenAI
        result = await azure_openai_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Azure OpenAI result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithAzureOpenAI(message: string) {
      // Process using Azure OpenAI
      const result = await azure_openaiClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Azure OpenAI result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithAzureOpenAI(string message)
    {
        // Process using Azure OpenAI
        var result = await azure_openaiClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Azure OpenAI result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Azure OpenAI as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def azure_openai_action(query: str) -> str:
        """Execute action using Azure OpenAI."""
        # Implementation
        return result

    # Create tool
    azure_openai_tool = Tool(
        name="azure_openai_action",
        description="Use Azure OpenAI to perform actions",
        function=azure_openai_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Azure OpenAI to help me",
        tools=[azure_openai_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function azure_openaiAction(query: string): Promise<string> {
      // Execute action using Azure OpenAI
      // Implementation
      return result;
    }

    // Create tool
    const azure_openaiTool = new Tool({
      name: 'azure_openai_action',
      description: 'Use Azure OpenAI to perform actions',
      function: azure_openaiAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Azure OpenAI to help me',
      { tools: [azure_openaiTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> AzureOpenAIAction(string query)
    {
        // Execute action using Azure OpenAI
        // Implementation
        return result;
    }

    // Create tool
    var azure_openaiTool = new Tool
    {
        Name = "azure_openai_action",
        Description = "Use Azure OpenAI to perform actions",
        Function = AzureOpenAIAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Azure OpenAI to help me",
        new[] { azure_openaiTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Azure OpenAI operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_azure_openai_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await azure_openai_client.call(data)
                return result
            except AzureOpenAIError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Azure OpenAI call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeAzureOpenAICall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await azure_openaiClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Azure OpenAI call failed: ${error}`);
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
    public async Task<T?> SafeAzureOpenAICall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await azure_openaiClient.CallAsync(data);
                return result as T;
            }
            catch (AzureOpenAIException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Azure OpenAI call failed");
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
2. **Rate Limiting** - Respect Azure OpenAI rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Azure OpenAI integration:

```python
import prometheus_client as prom

azure_openai_calls = prom.Counter(
    'azure_openai_calls_total',
    'Total Azure OpenAI calls',
    ['status']
)

azure_openai_latency = prom.Histogram(
    'azure_openai_latency_seconds',
    'Azure OpenAI call latency'
)

@azure_openai_latency.time()
async def monitored_azure_openai_call():
    try:
        result = await azure_openai_client.call()
        azure_openai_calls.labels(status='success').inc()
        return result
    except Exception:
        azure_openai_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/azure_openai/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/azure_openai/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/azure_openai/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Azure OpenAI Documentation](https://azure-openai.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
