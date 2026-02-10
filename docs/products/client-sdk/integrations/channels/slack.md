# Slack Integration

Integrate your Agent Protocol application with Slack.

## Overview

Connect your agents to Slack to leverage its team communication platform. This guide covers setup, configuration, authentication, and best practices for production deployments.

---

## Prerequisites

- Agent Protocol Client SDK installed
- Slack account
- Slack app credentials
- Basic understanding of the Agent Protocol

---

## Installation

=== "Python"

    ```python
    # Install required packages
    pip install microsoft-agents-client slack-sdk
    ```

=== "TypeScript"

    ```typescript
    // Install required packages
    npm install @microsoft/agents-client slack-sdk
    ```

=== "C#"

    ```csharp
    // Install required packages
    dotnet add package Microsoft.Agents.Client
    dotnet add package Slack.SDK
    ```

---

## Configuration

### Environment Variables

Set up your environment variables:

```bash
# .env file
AGENT_BASE_URL=http://localhost:3978
SLACK_API_KEY=your-api-key-here
SLACK_ENDPOINT=your-endpoint-here
```

### Basic Setup

=== "Python"

    ```python
    import os
    from microsoft.agents import AgentProtocolClient

    # Initialize Slack client
    slack_api_key = os.environ.get("SLACK_API_KEY")
    
    # Initialize Agent Protocol client
    agent_client = AgentProtocolClient(
        base_url=os.environ.get("AGENT_BASE_URL")
    )

    # Configure integration
    async def setup_slack():
        # Setup code here
        pass
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { config } from 'dotenv';

    // Load environment variables
    config();

    // Initialize Slack client
    const slackApiKey = process.env.SLACK_API_KEY;

    // Initialize Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978'
    });

    // Configure integration
    async function setupSlack() {
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

    // Initialize Slack client
    var slackApiKey = configuration["SLACK_API_KEY"];

    // Initialize Agent Protocol client
    var agentClient = new AgentProtocolClient(
        configuration["AGENT_BASE_URL"] ?? "http://localhost:3978"
    );

    // Configure integration
    async Task SetupSlack()
    {
        // Setup code here
    }
    ```

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to Slack from your agent:

=== "Python"

    ```python
    async def process_with_slack(message: str):
        # Process using Slack
        result = await slack_client.process(message)
        
        # Send to agent
        response = await agent_client.send_one_off(
            f"Process this Slack result: {result}"
        )
        return response
    ```

=== "TypeScript"

    ```typescript
    async function processWithSlack(message: string) {
      // Process using Slack
      const result = await slackClient.process(message);
      
      // Send to agent
      const response = await agentClient.sendOneOff(
        `Process this Slack result: ${result}`
      );
      return response;
    }
    ```

=== "C#"

    ```csharp
    public async Task<Response> ProcessWithSlack(string message)
    {
        // Process using Slack
        var result = await slackClient.ProcessAsync(message);
        
        // Send to agent
        var response = await agentClient.SendOneOffAsync(
            $"Process this Slack result: {result}"
        );
        return response;
    }
    ```

### Pattern 2: Tool-Based Integration

Expose Slack as an agent tool:

=== "Python"

    ```python
    from microsoft.agents import Tool

    async def slack_action(query: str) -> str:
        """Execute action using Slack."""
        # Implementation
        return result

    # Create tool
    slack_tool = Tool(
        name="slack_action",
        description="Use Slack to perform actions",
        function=slack_action
    )

    # Use with agent
    response = await agent_client.send_with_tools(
        "Use Slack to help me",
        tools=[slack_tool]
    )
    ```

=== "TypeScript"

    ```typescript
    import { Tool } from '@microsoft/agents-client';

    async function slackAction(query: string): Promise<string> {
      // Execute action using Slack
      // Implementation
      return result;
    }

    // Create tool
    const slackTool = new Tool({
      name: 'slack_action',
      description: 'Use Slack to perform actions',
      function: slackAction
    });

    // Use with agent
    const response = await agentClient.sendWithTools(
      'Use Slack to help me',
      { tools: [slackTool] }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents;

    public async Task<string> SlackAction(string query)
    {
        // Execute action using Slack
        // Implementation
        return result;
    }

    // Create tool
    var slackTool = new Tool
    {
        Name = "slack_action",
        Description = "Use Slack to perform actions",
        Function = SlackAction
    };

    // Use with agent
    var response = await agentClient.SendWithToolsAsync(
        "Use Slack to help me",
        new[] { slackTool }
    );
    ```

---

## Error Handling

Implement robust error handling for Slack operations:

=== "Python"

    ```python
    from typing import Optional
    import asyncio

    async def safe_slack_call(data: dict) -> Optional[dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await slack_client.call(data)
                return result
            except SlackError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Slack call failed: {e}")
                    return None
                await asyncio.sleep(2 ** attempt)
        return None
    ```

=== "TypeScript"

    ```typescript
    async function safeSlackCall(data: any): Promise<any | null> {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          const result = await slackClient.call(data);
          return result;
        } catch (error) {
          if (attempt === maxRetries - 1) {
            logger.error(`Slack call failed: ${error}`);
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
    public async Task<T?> SafeSlackCall<T>(object data) where T : class
    {
        const int maxRetries = 3;
        for (int attempt = 0; attempt < maxRetries; attempt++)
        {
            try
            {
                var result = await slackClient.CallAsync(data);
                return result as T;
            }
            catch (SlackException ex)
            {
                if (attempt == maxRetries - 1)
                {
                    _logger.LogError(ex, "Slack call failed");
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
2. **Rate Limiting** - Respect Slack rate limits
3. **Error Handling** - Implement retry logic with exponential backoff
4. **Monitoring** - Track integration health and performance
5. **Caching** - Cache responses when appropriate
6. **Timeouts** - Set appropriate timeout values
7. **Testing** - Test integration thoroughly before production

---

## Monitoring

Monitor your Slack integration:

```python
import prometheus_client as prom

slack_calls = prom.Counter(
    'slack_calls_total',
    'Total Slack calls',
    ['status']
)

slack_latency = prom.Histogram(
    'slack_latency_seconds',
    'Slack call latency'
)

@slack_latency.time()
async def monitored_slack_call():
    try:
        result = await slack_client.call()
        slack_calls.labels(status='success').inc()
        return result
    except Exception:
        slack_calls.labels(status='error').inc()
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

- [Python Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/slack/python)
- [TypeScript Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/slack/typescript)
- [C# Example](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations/slack/csharp)

---

## See Also

- [Integrations Overview](../index.md)
- [Client SDK Guide](../../guides/README.md)
- [Slack Documentation](https://slack.com/docs)
- [Best Practices](../../guides/best-practices/index.md)
