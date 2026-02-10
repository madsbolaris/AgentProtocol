# Microsoft Teams Integration

Integrate your Agent Protocol application with Microsoft Teams.

## Overview

Connect your agents to Microsoft Teams to leverage its enterprise collaboration platform. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Microsoft Teams account
- Bot Framework credentials
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client microsoft_teams-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client microsoft_teams-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Microsoft.Teams.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
MICROSOFT_TEAMS_API_KEY=your-api-key-here
MICROSOFT_TEAMS_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Microsoft Teams client
    microsoft_teams_api_key = os.environ.get("MICROSOFT_TEAMS_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_microsoft_teams():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Microsoft Teams client
    const microsoft_teamsApiKey = process.env.MICROSOFT_TEAMS_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupMicrosoftTeams() {
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

    // Initialize Microsoft Teams client
    var microsoft_teamsApiKey = configuration["MICROSOFT_TEAMS_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupMicrosoftTeams()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Microsoft Teams from your agent:

=== "Python"

    ```python
    async def process_with_microsoft_teams(message: str):
        # Process using Microsoft Teams
        result = await microsoft_teams_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Microsoft Teams result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithMicrosoftTeams(message: string) {
      // Process using Microsoft Teams
      const result = await microsoft_teamsClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Microsoft Teams result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithMicrosoftTeams(string message)
    {
        // Process using Microsoft Teams
        var result = await microsoft_teamsClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Microsoft Teams result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Microsoft Teams as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def microsoft_teams_action(query: str) -> str:
        """Execute action using Microsoft Teams."""
        # Implementation
        return result

    # Create tool
    microsoft_teams_tool = Tool(
        name="microsoft_teams_action",
        description="Use Microsoft Teams to perform actions",
        function=microsoft_teams_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Microsoft Teams to help me",
        tools=[microsoft_teams_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function microsoft_teamsAction(query: string): Promise<string> {
      // Execute action using Microsoft Teams
      // Implementation
      return result;
    }

    // Create tool
    const microsoft_teamsTool = new Tool({
      name: 'microsoft_teams_action',
      description: 'Use Microsoft Teams to perform actions',
      function: microsoft_teamsAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Microsoft Teams to help me',
      { tools: [microsoft_teamsTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> MicrosoftTeamsAction(string query)
    {
        // Execute action using Microsoft Teams
        // Implementation
        return result;
    }

    // Create tool
    var microsoft_teamsTool = new Tool
    {
        Name = "microsoft_teams_action",
        Description = "Use Microsoft Teams to perform actions",
        Function = MicrosoftTeamsAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Microsoft Teams to help me",
        new[] { microsoft_teamsTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Microsoft Teams operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_microsoft_teams_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await microsoft_teams_client.call(data)
                return result
            except MicrosoftTeamsError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Microsoft Teams call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeMicrosoftTeamsCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await microsoft_teamsClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Microsoft Teams call failed: ${error}`);
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
    public async Task<T?> SafeMicrosoftTeamsCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await microsoft_teamsClient.CallAsync(data);
                return result as T;
            }
            catch (MicrosoftTeamsException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Microsoft Teams call failed");
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
2. **Rate Limiting** - Respect Microsoft Teams rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Microsoft Teams integration:

```python
import prometheus_client as prom

microsoft_teams_calls = prom.Counter(
    'microsoft_teams_calls_total',
    'Total Microsoft Teams calls',
    ['status']
)

microsoft_teams_latency = prom.Histogram(
    'microsoft_teams_latency_seconds',
    'Microsoft Teams call latency'
)

@microsoft_teams_latency.time()
async def monitored_microsoft_teams_call():
    try:
        result = await microsoft_teams_client.call()
        microsoft_teams_calls.labels(status='success').inc()
        return result
    except Exception:
        microsoft_teams_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/microsoft_teams/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/microsoft_teams/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/microsoft_teams/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Microsoft Teams Documentation](https://microsoft-teams.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
