# Database Tools Integration

Integrate your Agent Protocol application with Database tools.

## Overview

Connect your agents to Database tools to leverage its data persistence and retrieval. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Database tools account
- database connection string
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client database_tools-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client database_tools-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Database.tools.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
DATABASE_TOOLS_API_KEY=your-api-key-here
DATABASE_TOOLS_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Database tools client
    database_tools_api_key = os.environ.get("DATABASE_TOOLS_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_database_tools():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Database tools client
    const database_toolsApiKey = process.env.DATABASE_TOOLS_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupDatabasetools() {
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

    // Initialize Database tools client
    var database_toolsApiKey = configuration["DATABASE_TOOLS_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupDatabasetools()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Database tools from your agent:

=== "Python"

    ```python
    async def process_with_database_tools(message: str):
        # Process using Database tools
        result = await database_tools_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Database tools result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithDatabasetools(message: string) {
      // Process using Database tools
      const result = await database_toolsClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Database tools result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithDatabasetools(string message)
    {
        // Process using Database tools
        var result = await database_toolsClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Database tools result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Database tools as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def database_tools_action(query: str) -> str:
        """Execute action using Database tools."""
        # Implementation
        return result

    # Create tool
    database_tools_tool = Tool(
        name="database_tools_action",
        description="Use Database tools to perform actions",
        function=database_tools_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Database tools to help me",
        tools=[database_tools_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function database_toolsAction(query: string): Promise<string> {
      // Execute action using Database tools
      // Implementation
      return result;
    }

    // Create tool
    const database_toolsTool = new Tool({
      name: 'database_tools_action',
      description: 'Use Database tools to perform actions',
      function: database_toolsAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Database tools to help me',
      { tools: [database_toolsTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> DatabasetoolsAction(string query)
    {
        // Execute action using Database tools
        // Implementation
        return result;
    }

    // Create tool
    var database_toolsTool = new Tool
    {
        Name = "database_tools_action",
        Description = "Use Database tools to perform actions",
        Function = DatabasetoolsAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Database tools to help me",
        new[] { database_toolsTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Database tools operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_database_tools_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await database_tools_client.call(data)
                return result
            except DatabasetoolsError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Database tools call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeDatabasetoolsCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await database_toolsClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Database tools call failed: ${error}`);
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
    public async Task<T?> SafeDatabasetoolsCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await database_toolsClient.CallAsync(data);
                return result as T;
            }
            catch (DatabasetoolsException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Database tools call failed");
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
2. **Rate Limiting** - Respect Database tools rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Database tools integration:

```python
import prometheus_client as prom

database_tools_calls = prom.Counter(
    'database_tools_calls_total',
    'Total Database tools calls',
    ['status']
)

database_tools_latency = prom.Histogram(
    'database_tools_latency_seconds',
    'Database tools call latency'
)

@database_tools_latency.time()
async def monitored_database_tools_call():
    try:
        result = await database_tools_client.call()
        database_tools_calls.labels(status='success').inc()
        return result
    except Exception:
        database_tools_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/database_tools/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/database_tools/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/database_tools/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Database tools Documentation](https://database-tools.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
