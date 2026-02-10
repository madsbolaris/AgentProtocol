# Discord Integration

Integrate your Agent Protocol application with Discord.

## Overview

Connect your agents to Discord to leverage its messaging platform. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Discord account
- Discord bot token
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client discord-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client discord-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Discord.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
DISCORD_API_KEY=your-api-key-here
DISCORD_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Discord client
    discord_api_key = os.environ.get("DISCORD_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_discord():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Discord client
    const discordApiKey = process.env.DISCORD_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupDiscord() {
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

    // Initialize Discord client
    var discordApiKey = configuration["DISCORD_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupDiscord()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Discord from your agent:

=== "Python"

    ```python
    async def process_with_discord(message: str):
        # Process using Discord
        result = await discord_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Discord result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithDiscord(message: string) {
      // Process using Discord
      const result = await discordClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Discord result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithDiscord(string message)
    {
        // Process using Discord
        var result = await discordClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Discord result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Discord as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def discord_action(query: str) -> str:
        """Execute action using Discord."""
        # Implementation
        return result

    # Create tool
    discord_tool = Tool(
        name="discord_action",
        description="Use Discord to perform actions",
        function=discord_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Discord to help me",
        tools=[discord_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function discordAction(query: string): Promise<string> {
      // Execute action using Discord
      // Implementation
      return result;
    }

    // Create tool
    const discordTool = new Tool({
      name: 'discord_action',
      description: 'Use Discord to perform actions',
      function: discordAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Discord to help me',
      { tools: [discordTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> DiscordAction(string query)
    {
        // Execute action using Discord
        // Implementation
        return result;
    }

    // Create tool
    var discordTool = new Tool
    {
        Name = "discord_action",
        Description = "Use Discord to perform actions",
        Function = DiscordAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Discord to help me",
        new[] { discordTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Discord operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_discord_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await discord_client.call(data)
                return result
            except DiscordError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Discord call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeDiscordCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await discordClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Discord call failed: ${error}`);
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
    public async Task<T?> SafeDiscordCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await discordClient.CallAsync(data);
                return result as T;
            }
            catch (DiscordException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Discord call failed");
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
2. **Rate Limiting** - Respect Discord rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Discord integration:

```python
import prometheus_client as prom

discord_calls = prom.Counter(
    'discord_calls_total',
    'Total Discord calls',
    ['status']
)

discord_latency = prom.Histogram(
    'discord_latency_seconds',
    'Discord call latency'
)

@discord_latency.time()
async def monitored_discord_call():
    try:
        result = await discord_client.call()
        discord_calls.labels(status='success').inc()
        return result
    except Exception:
        discord_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/discord/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/discord/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/discord/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Discord Documentation](https://discord.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
