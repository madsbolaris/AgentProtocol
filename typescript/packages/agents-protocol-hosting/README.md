# Microsoft Agents Hosting SDK for TypeScript

The official hosting SDK for building agent applications with the Microsoft Agents Protocol.

## Features

- **Type-Safe Builders**: Fluent API with full TypeScript type inference
- **LLM Integration**: Built-in support for OpenAI, Anthropic, and other LLM providers
- **Function/Tool Support**: Register functions that LLMs can call with full type safety
- **State Management**: Persistent conversation state across turns
- **Event Handlers**: Intercept and process user messages, reactions, and more
- **Production-Ready**: Built-in retry policies, rate limiting, logging, and health checks
- **Scalable**: Supports distributed deployments with PostgreSQL and Redis
- **Secure**: Sandboxed function execution for untrusted code
- **Testable**: Mock implementations for deterministic testing

## Installation

```bash
npm install @microsoft/agents-hosting
```

## Quick Start

Create a simple agent that responds to messages and can tell the time:

```typescript
import { AgentHostBuilder } from '@microsoft/agents-hosting';

const agentHost = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM('gpt-4', 'You are a helpful assistant.')
    .addFunctions(f => f
      .add('getTime@v1', 'Gets the current UTC time',
        {},  // No parameters
        (): string => new Date().toISOString(),
        { trustLevel: 'trusted' }
      )
    )
  )
  .build();

await agentHost.start(3000);
console.log('Agent running on http://localhost:3000');
```

## Adding Functions

Functions allow the LLM to call your code. You must provide explicit JSON schemas for parameters:

```typescript
.addFunctions(f => f
  .add('sum@v1', 'Adds two numbers',
    {
      type: 'object',
      properties: {
        a: { type: 'number', description: 'First number' },
        b: { type: 'number', description: 'Second number' }
      },
      required: ['a', 'b']
    },
    ({ a, b }: { a: number; b: number }): string => (a + b).toString(),
    { trustLevel: 'trusted' }
  )
)
```

### Security: Trust Levels

**CRITICAL**: Every function must specify a `trustLevel`:

- **'trusted'**: For functions you control. Runs without sandboxing.
- **'untrusted'**: For user-provided code or external functions. Runs in sandbox with resource limits.

```typescript
// Trusted function (your code)
.add('getWeather@v1', 'Gets weather data', schema, implementation,
  { trustLevel: 'trusted' })

// Untrusted function (user code)
.add('runUserCode@v1', 'Executes user code', schema, implementation,
  {
    trustLevel: 'untrusted',
    timeoutMs: 5000,
    maxMemoryBytes: 100 * 1024 * 1024,
    allowNetwork: false,
    allowFilesystem: false
  })
```

## Handling User Messages

Intercept messages before they reach the LLM:

```typescript
import { TurnResult, UserMessageHandler, IAgentContext, ChatMessage } from '@microsoft/agents-hosting';

const onUserMessage: UserMessageHandler = async (
  message: ChatMessage,
  context: IAgentContext,
  cancellationToken?: AbortSignal
): Promise<TurnResult> => {
  // Log the message
  await context.logAsync(`User said: ${message.text}`);

  // Handle special commands
  if (message.text === '/help') {
    await context.respondAsync('Available commands: /help, /about');
    return TurnResult.Replied;  // We handled it, don't send to LLM
  }

  return TurnResult.Continue;  // Let the LLM handle it
};

const agentHost = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM('gpt-4', 'You are helpful.')
    .onUserMessage(onUserMessage)
  )
  .build();
```

### TurnResult Values

Control message flow with three options:

- **`TurnResult.Continue`**: Pass to next handler or LLM
- **`TurnResult.Consumed`**: Stop processing, no response needed
- **`TurnResult.Replied`**: Stop processing, already sent response

## Managing State

Store data across conversation turns:

```typescript
const onUserMessage: UserMessageHandler = async (
  message: ChatMessage,
  context: IAgentContext
): Promise<TurnResult> => {
  // Get message count
  const count = await context.getStateAsync<number>('message_count') || 0;

  // Increment and store
  await context.setStateAsync('message_count', count + 1);

  // Use in response
  await context.respondAsync(`This is message ${count + 1} in our conversation.`);

  return TurnResult.Replied;
};
```

## Production Configuration

Configure storage, queues, and operational features for production:

```typescript
import { AgentHostBuilder } from '@microsoft/agents-hosting';
import { PostgresStorage } from '@microsoft/agents-hosting/storage';
import { RedisQueue } from '@microsoft/agents-hosting/queue';

const agentHost = new AgentHostBuilder()
  .useStorage(new PostgresStorage({
    connectionString: process.env.DATABASE_URL,
    pool: { min: 2, max: 10 }
  }))
  .useQueue(new RedisQueue({
    host: process.env.REDIS_HOST,
    port: 6379
  }))
  .useRetryPolicy({
    maxAttempts: 3,
    backoff: 'exponential',
    initialDelayMs: 1000,
    maxDelayMs: 10000
  })
  .useRateLimiting({
    global: { windowMs: 60_000, maxRequests: 1000 },
    perThread: { windowMs: 60_000, maxRequests: 100 }
  })
  .useLogging({
    level: 'info',
    format: 'json',
    destination: 'console',
    includeStackTraces: true,
    redactSecrets: true
  })
  .addDefaultAgent(agent => agent
    .useLLM('gpt-4', 'You are a helpful assistant.')
  )
  .build();
```

## Multiple Agents with Routing

Route requests to different specialized agents:

```typescript
const agentHost = new AgentHostBuilder()
  .addAgent('sales', agent => agent
    .useLLM('gpt-4', 'You are a sales assistant.')
  )
  .addAgent('support', agent => agent
    .useLLM('gpt-4', 'You are a support assistant.')
  )
  .useRouting(routing => routing
    .byHeader('X-Agent-Type')  // Route based on header
    .withFallback('sales')      // Default agent
  )
  .build();
```

## Streaming Responses

Enable token-by-token streaming for real-time UX:

```typescript
.addDefaultAgent(agent => agent
  .useLLM('gpt-4', 'You are helpful.', {
    streaming: true,
    onToken: async (token: string, ctx: IAgentContext) => {
      await ctx.streamAsync(token);
    }
  })
)
```

## Testing

Use mock implementations to test without real API calls:

```typescript
import { MockLLM, MockAgentContext } from '@microsoft/agents-hosting/testing';

const mockLLM = new MockLLM()
  .on('Hello!', 'Hi there!')
  .on('What time is it?', (functions) => {
    const result = functions.call('getTime@v1');
    return `The current time is ${result}`;
  });

const host = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM(mockLLM)
    .addFunctions(f => f
      .add('getTime@v1', 'Gets time', {}, (): string => '2024-01-01T00:00:00Z',
           { trustLevel: 'trusted' })
    )
  )
  .build();

const response = await host.processMessage('Hello!');
expect(response.text).toBe('Hi there!');
```

## Health Checks

Built-in health checks for Kubernetes and other orchestration platforms:

```typescript
const health = await agentHost.checkHealth();

if (health.status === 'healthy') {
  console.log('All systems operational');
} else {
  console.error('Health check failed:', health.checks);
}
```

## Graceful Shutdown

Handle shutdown signals properly:

```typescript
process.on('SIGTERM', async () => {
  await agentHost.stop({
    gracePeriodMs: 30000,
    finishQueued: true
  });
  process.exit(0);
});
```

## Out-of-Band Messages

Send messages from background jobs, webhooks, or scheduled tasks:

```typescript
const publisher = agentHost.getPublisher();

// From a scheduled task
setInterval(async () => {
  await publisher.sendToThreadAsync(
    'thread-123',
    'Your daily reminder!',
    undefined,
    `reminder-${new Date().toISOString()}`
  );
}, 24 * 60 * 60 * 1000);
```

## API Reference

For complete API documentation, see:
- [Getting Started Guide](../../.workspace/typescript-hosting-sdk/09-final-getting-started.md)
- [Technical Specification](../../.workspace/typescript-hosting-sdk/10-final-technical-specification.md)

## Examples

See the `examples/` directory for complete working examples:
- Basic agent with functions
- Multi-agent routing
- Production configuration
- Custom storage and queue implementations

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

## Support

- GitHub Issues: https://github.com/microsoft/agents-protocol/issues
- Documentation: https://docs.microsoft.com/agents-protocol
- Discord: https://discord.gg/microsoft-agents
