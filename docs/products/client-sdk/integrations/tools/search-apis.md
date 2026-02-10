# Search APIs Integration

Integrate your Agent Protocol application with Search APIs.

## Overview

Connect your agents to Search APIs to leverage its web and enterprise search capabilities. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Search APIs account
- search API credentials
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client search_apis-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client search_apis-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Search.APIs.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
SEARCH_APIS_API_KEY=your-api-key-here
SEARCH_APIS_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Search APIs client
    search_apis_api_key = os.environ.get("SEARCH_APIS_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_search_apis():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Search APIs client
    const search_apisApiKey = process.env.SEARCH_APIS_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupSearchAPIs() {
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

    // Initialize Search APIs client
    var search_apisApiKey = configuration["SEARCH_APIS_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupSearchAPIs()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Search APIs from your agent:

=== "Python"

    ```python
    async def process_with_search_apis(message: str):
        # Process using Search APIs
        result = await search_apis_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Search APIs result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithSearchAPIs(message: string) {
      // Process using Search APIs
      const result = await search_apisClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Search APIs result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithSearchAPIs(string message)
    {
        // Process using Search APIs
        var result = await search_apisClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Search APIs result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Search APIs as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def search_apis_action(query: str) -> str:
        """Execute action using Search APIs."""
        # Implementation
        return result

    # Create tool
    search_apis_tool = Tool(
        name="search_apis_action",
        description="Use Search APIs to perform actions",
        function=search_apis_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Search APIs to help me",
        tools=[search_apis_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function search_apisAction(query: string): Promise<string> {
      // Execute action using Search APIs
      // Implementation
      return result;
    }

    // Create tool
    const search_apisTool = new Tool({
      name: 'search_apis_action',
      description: 'Use Search APIs to perform actions',
      function: search_apisAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Search APIs to help me',
      { tools: [search_apisTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> SearchAPIsAction(string query)
    {
        // Execute action using Search APIs
        // Implementation
        return result;
    }

    // Create tool
    var search_apisTool = new Tool
    {
        Name = "search_apis_action",
        Description = "Use Search APIs to perform actions",
        Function = SearchAPIsAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Search APIs to help me",
        new[] { search_apisTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Search APIs operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_search_apis_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await search_apis_client.call(data)
                return result
            except SearchAPIsError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Search APIs call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeSearchAPIsCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await search_apisClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Search APIs call failed: ${error}`);
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
    public async Task<T?> SafeSearchAPIsCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await search_apisClient.CallAsync(data);
                return result as T;
            }
            catch (SearchAPIsException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Search APIs call failed");
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
2. **Rate Limiting** - Respect Search APIs rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Search APIs integration:

```python
import prometheus_client as prom

search_apis_calls = prom.Counter(
    'search_apis_calls_total',
    'Total Search APIs calls',
    ['status']
)

search_apis_latency = prom.Histogram(
    'search_apis_latency_seconds',
    'Search APIs call latency'
)

@search_apis_latency.time()
async def monitored_search_apis_call():
    try:
        result = await search_apis_client.call()
        search_apis_calls.labels(status='success').inc()
        return result
    except Exception:
        search_apis_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/search_apis/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/search_apis/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/search_apis/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Search APIs Documentation](https://search-apis.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
