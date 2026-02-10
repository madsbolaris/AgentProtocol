# Weather API Integration

Integrate your Agent Protocol application with Weather APIs.

## Overview

Connect your agents to Weather APIs to leverage its real-time weather data. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Weather APIs account
- weather API key
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client weather_apis-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client weather_apis-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Weather.APIs.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
WEATHER_APIS_API_KEY=your-api-key-here
WEATHER_APIS_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Weather APIs client
    weather_apis_api_key = os.environ.get("WEATHER_APIS_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_weather_apis():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Weather APIs client
    const weather_apisApiKey = process.env.WEATHER_APIS_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupWeatherAPIs() {
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

    // Initialize Weather APIs client
    var weather_apisApiKey = configuration["WEATHER_APIS_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupWeatherAPIs()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Weather APIs from your agent:

=== "Python"

    ```python
    async def process_with_weather_apis(message: str):
        # Process using Weather APIs
        result = await weather_apis_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Weather APIs result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithWeatherAPIs(message: string) {
      // Process using Weather APIs
      const result = await weather_apisClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Weather APIs result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithWeatherAPIs(string message)
    {
        // Process using Weather APIs
        var result = await weather_apisClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Weather APIs result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Weather APIs as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def weather_apis_action(query: str) -> str:
        """Execute action using Weather APIs."""
        # Implementation
        return result

    # Create tool
    weather_apis_tool = Tool(
        name="weather_apis_action",
        description="Use Weather APIs to perform actions",
        function=weather_apis_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Weather APIs to help me",
        tools=[weather_apis_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function weather_apisAction(query: string): Promise<string> {
      // Execute action using Weather APIs
      // Implementation
      return result;
    }

    // Create tool
    const weather_apisTool = new Tool({
      name: 'weather_apis_action',
      description: 'Use Weather APIs to perform actions',
      function: weather_apisAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Weather APIs to help me',
      { tools: [weather_apisTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> WeatherAPIsAction(string query)
    {
        // Execute action using Weather APIs
        // Implementation
        return result;
    }

    // Create tool
    var weather_apisTool = new Tool
    {
        Name = "weather_apis_action",
        Description = "Use Weather APIs to perform actions",
        Function = WeatherAPIsAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Weather APIs to help me",
        new[] { weather_apisTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Weather APIs operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_weather_apis_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await weather_apis_client.call(data)
                return result
            except WeatherAPIsError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Weather APIs call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeWeatherAPIsCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await weather_apisClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Weather APIs call failed: ${error}`);
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
    public async Task<T?> SafeWeatherAPIsCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await weather_apisClient.CallAsync(data);
                return result as T;
            }
            catch (WeatherAPIsException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Weather APIs call failed");
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
2. **Rate Limiting** - Respect Weather APIs rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Weather APIs integration:

```python
import prometheus_client as prom

weather_apis_calls = prom.Counter(
    'weather_apis_calls_total',
    'Total Weather APIs calls',
    ['status']
)

weather_apis_latency = prom.Histogram(
    'weather_apis_latency_seconds',
    'Weather APIs call latency'
)

@weather_apis_latency.time()
async def monitored_weather_apis_call():
    try:
        result = await weather_apis_client.call()
        weather_apis_calls.labels(status='success').inc()
        return result
    except Exception:
        weather_apis_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weather_apis/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weather_apis/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/weather_apis/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Weather APIs Documentation](https://weather-apis.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
