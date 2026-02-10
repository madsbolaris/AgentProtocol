# Client SDK Best Practices

Production-tested patterns and recommendations for building robust Agent Protocol applications.

## Overview

This guide provides comprehensive best practices for developing, deploying, and maintaining applications using the Agent Protocol Client SDK across Python, TypeScript, and C#.

---

## Core Principles

### 1. Error Handling

Always implement comprehensive error handling with proper recovery strategies.

=== "Python"

    ```python
    from microsoft.agents import AgentProtocolClient, AgentError, NetworkError
    import asyncio

    async def send_with_retry(client: AgentProtocolClient, message: str, max_retries: int = 3):
        """Send message with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                return await client.send_one_off(message)
            except NetworkError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
            except AgentError as e:
                # Don't retry on validation errors
                if e.is_validation_error():
                    raise
                # Retry on transient errors
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, AgentError, NetworkError } from '@microsoft/agents-client';

    async function sendWithRetry(
      client: AgentProtocolClient,
      message: string,
      maxRetries: number = 3
    ): Promise<Response> {
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          return await client.sendOneOff(message);
        } catch (error) {
          if (error instanceof NetworkError) {
            if (attempt === maxRetries - 1) throw error;
            const waitTime = Math.pow(2, attempt) * 1000;
            await new Promise(resolve => setTimeout(resolve, waitTime));
          } else if (error instanceof AgentError) {
            // Don't retry validation errors
            if (error.isValidationError()) throw error;
            if (attempt === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          } else {
            throw error;
          }
        }
      }
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;
    using Polly;
    using Polly.Retry;

    public class ResilientAgentClient
    {
        private readonly AgentProtocolClient _client;
        private readonly AsyncRetryPolicy _retryPolicy;

        public ResilientAgentClient(AgentProtocolClient client)
        {
            _client = client;

            // Configure retry policy with exponential backoff
            _retryPolicy = Policy
                .Handle<NetworkException>()
                .Or<AgentException>(e => !e.IsValidationError())
                .WaitAndRetryAsync(
                    retryCount: 3,
                    sleepDurationProvider: retryAttempt =>
                        TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                    onRetry: (exception, timespan, retryCount, context) =>
                    {
                        Console.WriteLine($"Retry {retryCount} after {timespan.TotalSeconds}s");
                    });
        }

        public async Task<Response> SendWithRetry(string message)
        {
            return await _retryPolicy.ExecuteAsync(async () =>
                await _client.SendOneOffAsync(message));
        }
    }
    ```

### 2. Resource Management

Properly manage client lifecycle and connections.

=== "Python"

    ```python
    from microsoft.agents import AgentProtocolClient
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def create_client(base_url: str):
        """Context manager for proper client lifecycle."""
        client = AgentProtocolClient(base_url=base_url)
        try:
            await client.connect()
            yield client
        finally:
            await client.close()

    # Usage
    async def main():
        async with create_client("http://localhost:3978") as client:
            response = await client.send_one_off("Hello")
            print(response.text)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';

    export class ManagedAgentClient {
      private client: AgentProtocolClient;
      private isConnected: boolean = false;

      constructor(private baseUrl: string) {
        this.client = new AgentProtocolClient({ baseUrl });
      }

      async connect(): Promise<void> {
        if (!this.isConnected) {
          await this.client.connect();
          this.isConnected = true;
        }
      }

      async disconnect(): Promise<void> {
        if (this.isConnected) {
          await this.client.disconnect();
          this.isConnected = false;
        }
      }

      async sendMessage(message: string): Promise<Response> {
        if (!this.isConnected) {
          throw new Error('Client not connected');
        }
        return await this.client.sendOneOff(message);
      }
    }

    // Usage with proper cleanup
    const client = new ManagedAgentClient('http://localhost:3978');
    try {
      await client.connect();
      const response = await client.sendMessage('Hello');
      console.log(response.text);
    } finally {
      await client.disconnect();
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;
    using System;

    public class ManagedAgentClient : IDisposable, IAsyncDisposable
    {
        private readonly AgentProtocolClient _client;
        private bool _isConnected;
        private bool _disposed;

        public ManagedAgentClient(string baseUrl)
        {
            _client = new AgentProtocolClient(baseUrl);
        }

        public async Task ConnectAsync()
        {
            if (!_isConnected)
            {
                await _client.ConnectAsync();
                _isConnected = true;
            }
        }

        public async Task<Response> SendMessageAsync(string message)
        {
            if (!_isConnected)
            {
                throw new InvalidOperationException("Client not connected");
            }
            return await _client.SendOneOffAsync(message);
        }

        public async ValueTask DisposeAsync()
        {
            if (!_disposed)
            {
                if (_isConnected)
                {
                    await _client.DisconnectAsync();
                }
                _disposed = true;
            }
        }

        public void Dispose()
        {
            DisposeAsync().AsTask().Wait();
        }
    }

    // Usage with using statement
    await using var client = new ManagedAgentClient("http://localhost:3978");
    await client.ConnectAsync();
    var response = await client.SendMessageAsync("Hello");
    ```

### 3. Configuration Management

Use environment-specific configuration.

=== "Python"

    ```python
    from pydantic import BaseSettings
    from typing import Optional

    class AgentConfig(BaseSettings):
        """Configuration for Agent Protocol client."""
        agent_base_url: str
        agent_timeout: int = 30
        max_retries: int = 3
        api_key: Optional[str] = None
        enable_telemetry: bool = True
        log_level: str = "INFO"

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

    # Load configuration
    config = AgentConfig()

    # Create client with config
    client = AgentProtocolClient(
        base_url=config.agent_base_url,
        timeout=config.agent_timeout,
        api_key=config.api_key
    )
    ```

=== "TypeScript"

    ```typescript
    import { config as dotenvConfig } from 'dotenv';
    import { AgentProtocolClient } from '@microsoft/agents-client';

    // Load environment variables
    dotenvConfig();

    export interface AgentConfig {
      agentBaseUrl: string;
      agentTimeout: number;
      maxRetries: number;
      apiKey?: string;
      enableTelemetry: boolean;
      logLevel: string;
    }

    export function loadConfig(): AgentConfig {
      return {
        agentBaseUrl: process.env.AGENT_BASE_URL || 'http://localhost:3978',
        agentTimeout: parseInt(process.env.AGENT_TIMEOUT || '30000'),
        maxRetries: parseInt(process.env.MAX_RETRIES || '3'),
        apiKey: process.env.AGENT_API_KEY,
        enableTelemetry: process.env.ENABLE_TELEMETRY !== 'false',
        logLevel: process.env.LOG_LEVEL || 'info'
      };
    }

    // Create client with config
    const config = loadConfig();
    const client = new AgentProtocolClient({
      baseUrl: config.agentBaseUrl,
      timeout: config.agentTimeout,
      apiKey: config.apiKey
    });
    ```

=== "C#"

    ```csharp
    using Microsoft.Extensions.Configuration;
    using Microsoft.Agents.Client;

    public class AgentConfig
    {
        public string AgentBaseUrl { get; set; } = "http://localhost:3978";
        public int AgentTimeout { get; set; } = 30000;
        public int MaxRetries { get; set; } = 3;
        public string? ApiKey { get; set; }
        public bool EnableTelemetry { get; set; } = true;
        public string LogLevel { get; set; } = "Information";
    }

    public static class ConfigurationHelper
    {
        public static AgentConfig LoadConfig()
        {
            var configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false)
                .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")}.json", optional: true)
                .AddEnvironmentVariables()
                .Build();

            var config = new AgentConfig();
            configuration.GetSection("Agent").Bind(config);
            return config;
        }
    }

    // Usage
    var config = ConfigurationHelper.LoadConfig();
    var client = new AgentProtocolClient(config.AgentBaseUrl)
    {
        Timeout = TimeSpan.FromMilliseconds(config.AgentTimeout),
        ApiKey = config.ApiKey
    };
    ```

### 4. Input Validation

Always validate and sanitize user input.

=== "Python"

    ```python
    from pydantic import BaseModel, validator, constr
    from typing import Optional

    class MessageInput(BaseModel):
        """Validated message input."""
        text: constr(min_length=1, max_length=10000)
        thread_id: Optional[str] = None
        metadata: Optional[dict] = None

        @validator('text')
        def validate_text(cls, v):
            # Remove potentially harmful content
            if any(x in v.lower() for x in ['<script>', 'javascript:', 'onerror=']):
                raise ValueError('Invalid content detected')
            return v.strip()

        @validator('thread_id')
        def validate_thread_id(cls, v):
            if v and not v.startswith('thread-'):
                raise ValueError('Invalid thread ID format')
            return v

    # Usage
    try:
        validated = MessageInput(text=user_input, thread_id=thread_id)
        response = await client.send_one_off(validated.text)
    except ValidationError as e:
        logger.error(f"Invalid input: {e}")
        return {"error": "Invalid input"}
    ```

=== "TypeScript"

    ```typescript
    import { z } from 'zod';

    // Define validation schema
    const MessageInputSchema = z.object({
      text: z.string()
        .min(1, 'Message cannot be empty')
        .max(10000, 'Message too long')
        .refine(
          (val) => !['<script>', 'javascript:', 'onerror='].some(x => val.toLowerCase().includes(x)),
          'Invalid content detected'
        ),
      threadId: z.string()
        .optional()
        .refine(
          (val) => !val || val.startsWith('thread-'),
          'Invalid thread ID format'
        ),
      metadata: z.record(z.unknown()).optional()
    });

    type MessageInput = z.infer<typeof MessageInputSchema>;

    // Usage
    try {
      const validated = MessageInputSchema.parse({
        text: userInput,
        threadId: threadId
      });
      const response = await client.sendOneOff(validated.text);
    } catch (error) {
      if (error instanceof z.ZodError) {
        logger.error('Invalid input:', error.errors);
        return { error: 'Invalid input' };
      }
      throw error;
    }
    ```

=== "C#"

    ```csharp
    using System.ComponentModel.DataAnnotations;
    using FluentValidation;

    public class MessageInput
    {
        [Required]
        [StringLength(10000, MinimumLength = 1)]
        public string Text { get; set; }

        public string? ThreadId { get; set; }
        public Dictionary<string, object>? Metadata { get; set; }
    }

    public class MessageInputValidator : AbstractValidator<MessageInput>
    {
        public MessageInputValidator()
        {
            RuleFor(x => x.Text)
                .NotEmpty()
                .MaximumLength(10000)
                .Must(BeValidContent)
                .WithMessage("Invalid content detected");

            RuleFor(x => x.ThreadId)
                .Must(BeValidThreadId)
                .When(x => !string.IsNullOrEmpty(x.ThreadId))
                .WithMessage("Invalid thread ID format");
        }

        private bool BeValidContent(string text)
        {
            var forbidden = new[] { "<script>", "javascript:", "onerror=" };
            return !forbidden.Any(x => text.Contains(x, StringComparison.OrdinalIgnoreCase));
        }

        private bool BeValidThreadId(string? threadId)
        {
            return threadId == null || threadId.StartsWith("thread-");
        }
    }

    // Usage
    var validator = new MessageInputValidator();
    var input = new MessageInput { Text = userInput, ThreadId = threadId };
    var validationResult = await validator.ValidateAsync(input);

    if (!validationResult.IsValid)
    {
        _logger.LogError("Invalid input: {Errors}", validationResult.Errors);
        return BadRequest(new { error = "Invalid input" });
    }

    var response = await _client.SendOneOffAsync(input.Text);
    ```

---

## Performance Optimization

### Connection Pooling

Reuse client connections when possible.

=== "Python"

    ```python
    from microsoft.agents import AgentProtocolClient
    import asyncio

    class ClientPool:
        """Simple connection pool for Agent Protocol clients."""

        def __init__(self, base_url: str, pool_size: int = 5):
            self.base_url = base_url
            self.pool_size = pool_size
            self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
            self._initialized = False

        async def initialize(self):
            """Initialize the connection pool."""
            if not self._initialized:
                for _ in range(self.pool_size):
                    client = AgentProtocolClient(base_url=self.base_url)
                    await client.connect()
                    await self._pool.put(client)
                self._initialized = True

        async def acquire(self) -> AgentProtocolClient:
            """Acquire a client from the pool."""
            return await self._pool.get()

        async def release(self, client: AgentProtocolClient):
            """Release a client back to the pool."""
            await self._pool.put(client)

        async def close(self):
            """Close all connections in the pool."""
            while not self._pool.empty():
                client = await self._pool.get()
                await client.close()
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { EventEmitter } from 'events';

    export class ClientPool extends EventEmitter {
      private pool: AgentProtocolClient[] = [];
      private available: AgentProtocolClient[] = [];
      private initialized: boolean = false;

      constructor(
        private baseUrl: string,
        private poolSize: number = 5
      ) {
        super();
      }

      async initialize(): Promise<void> {
        if (!this.initialized) {
          for (let i = 0; i < this.poolSize; i++) {
            const client = new AgentProtocolClient({ baseUrl: this.baseUrl });
            await client.connect();
            this.pool.push(client);
            this.available.push(client);
          }
          this.initialized = true;
        }
      }

      async acquire(): Promise<AgentProtocolClient> {
        while (this.available.length === 0) {
          await new Promise(resolve => this.once('release', resolve));
        }
        return this.available.pop()!;
      }

      release(client: AgentProtocolClient): void {
        this.available.push(client);
        this.emit('release');
      }

      async close(): Promise<void> {
        await Promise.all(this.pool.map(client => client.disconnect()));
        this.pool = [];
        this.available = [];
        this.initialized = false;
      }
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;
    using System.Collections.Concurrent;

    public class ClientPool : IAsyncDisposable
    {
        private readonly ConcurrentBag<AgentProtocolClient> _pool;
        private readonly SemaphoreSlim _semaphore;
        private readonly string _baseUrl;
        private readonly int _poolSize;
        private bool _initialized;

        public ClientPool(string baseUrl, int poolSize = 5)
        {
            _baseUrl = baseUrl;
            _poolSize = poolSize;
            _pool = new ConcurrentBag<AgentProtocolClient>();
            _semaphore = new SemaphoreSlim(poolSize, poolSize);
        }

        public async Task InitializeAsync()
        {
            if (!_initialized)
            {
                for (int i = 0; i < _poolSize; i++)
                {
                    var client = new AgentProtocolClient(_baseUrl);
                    await client.ConnectAsync();
                    _pool.Add(client);
                }
                _initialized = true;
            }
        }

        public async Task<AgentProtocolClient> AcquireAsync()
        {
            await _semaphore.WaitAsync();
            if (_pool.TryTake(out var client))
            {
                return client;
            }
            throw new InvalidOperationException("Pool exhausted");
        }

        public void Release(AgentProtocolClient client)
        {
            _pool.Add(client);
            _semaphore.Release();
        }

        public async ValueTask DisposeAsync()
        {
            while (_pool.TryTake(out var client))
            {
                await client.DisconnectAsync();
            }
        }
    }
    ```

### Request Batching

Batch multiple requests when possible.

```python
# Instead of multiple individual calls
for message in messages:
    await client.send_one_off(message)

# Consider batching
responses = await client.send_batch(messages)
```

---

## Security Best Practices

### API Key Management

Never hardcode API keys.

```python
# Bad
client = AgentProtocolClient(api_key="sk-12345...")

# Good
import os
client = AgentProtocolClient(api_key=os.environ.get("AGENT_API_KEY"))
```

### Rate Limiting

Implement client-side rate limiting.

```python
from aiolimiter import AsyncLimiter

# Limit to 100 requests per minute
rate_limiter = AsyncLimiter(max_rate=100, time_period=60)

async def rate_limited_send(message: str):
    async with rate_limiter:
        return await client.send_one_off(message)
```

### Timeout Configuration

Always set appropriate timeouts.

```python
# Configure timeout to prevent hanging
client = AgentProtocolClient(
    base_url="http://localhost:3978",
    timeout=30  # 30 seconds
)
```

---

## Testing Best Practices

### Mock External Dependencies

Use mocking for unit tests.

=== "Python"

    ```python
    import pytest
    from unittest.mock import AsyncMock, patch

    @pytest.mark.asyncio
    async def test_send_message():
        with patch('microsoft.agents.AgentProtocolClient') as mock_client:
            mock_instance = mock_client.return_value
            mock_instance.send_one_off = AsyncMock(
                return_value=Response(text="Hello")
            )

            response = await mock_instance.send_one_off("Test")
            assert response.text == "Hello"
    ```

=== "TypeScript"

    ```typescript
    import { jest } from '@jest/globals';
    import { AgentProtocolClient } from '@microsoft/agents-client';

    describe('Message sending', () => {
      it('should send message successfully', async () => {
        const mockClient = {
          sendOneOff: jest.fn().mockResolvedValue({ text: 'Hello' })
        } as unknown as AgentProtocolClient;

        const response = await mockClient.sendOneOff('Test');
        expect(response.text).toBe('Hello');
      });
    });
    ```

=== "C#"

    ```csharp
    using Moq;
    using Xunit;
    using Microsoft.Agents.Client;

    public class MessageTests
    {
        [Fact]
        public async Task SendMessage_ReturnsResponse()
        {
            var mockClient = new Mock<IAgentProtocolClient>();
            mockClient
                .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
                .ReturnsAsync(new Response { Text = "Hello" });

            var response = await mockClient.Object.SendOneOffAsync("Test");
            Assert.Equal("Hello", response.Text);
        }
    }
    ```

---

## Common Pitfalls

1. **Not handling network failures** - Always implement retry logic
2. **Ignoring timeouts** - Set appropriate timeout values
3. **Leaking resources** - Always close/dispose clients properly
4. **Hardcoding configuration** - Use environment variables
5. **Insufficient logging** - Log all important events
6. **No input validation** - Always validate user input
7. **Blocking operations** - Use async/await properly

---

## See Also

- [Testing Guide](../../testing/index.md)
- [Observability Best Practices](../../observability/best-practices/index.md)
- [Deployment Guide](../../deployment/index.md)
- [Security Guide](../../security/index.md)
- [Client SDK Documentation](../../index.md)
