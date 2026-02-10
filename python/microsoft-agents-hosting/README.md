# Microsoft Agents Protocol Hosting SDK for Python

Build production-ready AI agents with LLM function calling, state management, and operational best practices built-in.

## Features

- **Simple API**: Build agents in just a few lines of code with a fluent builder pattern
- **LLM Integration**: Built-in support for OpenAI, Anthropic, and other LLM providers
- **Function Calling**: Automatic schema generation and type-safe function execution
- **State Management**: Persistent conversation state with pluggable storage backends
- **Production Ready**: Retries, circuit breakers, observability, and sandboxing built-in
- **Async First**: Fully async/await throughout for high performance
- **Type Safe**: Complete type hints for IDE autocomplete and type checking

## Installation

```bash
pip install microsoft-agents-hosting
```

### Optional dependencies

```bash
# SQL state storage
pip install microsoft-agents-hosting[sql]

# Redis queue and caching
pip install microsoft-agents-hosting[redis]

# OpenTelemetry observability
pip install microsoft-agents-hosting[observability]

# Install everything
pip install microsoft-agents-hosting[all]
```

## Quick Start

```python
from microsoft.agents.hosting import AgentHostBuilder, TurnResult
from datetime import datetime

# Create and configure your agent
agent_host = (
    AgentHostBuilder()
    .add_default_agent(lambda agent: agent
        .use_llm("gpt-4", "You are a helpful assistant.")
        .add_functions(lambda f: f
            .add("get_time@v1", "Gets the current time",
                 lambda: datetime.utcnow().isoformat())
        )
    )
    .build()
)

# Run the agent
if __name__ == "__main__":
    agent_host.run()
```

## Core Concepts

### TurnResult

Control message processing flow with explicit result types:

- `TurnResult.CONTINUE` - Pass to next handler or LLM
- `TurnResult.CONSUMED` - Stop processing, no response needed
- `TurnResult.REPLIED` - Response already sent, stop processing

### Agent Context

Every handler receives an `IAgentContext` with:

```python
async def my_handler(message, context, cancellation_token):
    # Send responses
    await context.respond_async("Hello!")

    # Log messages
    await context.log_async("Processing...")

    # Access state
    count = await context.state.get_async("count", default=0)
    await context.state.set_async("count", count + 1)

    # Get IDs
    thread_id = context.thread_id
    run_id = context.run_id

    return TurnResult.CONTINUE
```

## Adding Functions

Functions are automatically registered with type inference:

```python
from typing import Annotated

agent.add_functions(lambda f: f
    # No parameters
    .add("get_time@v1", "Gets current time",
         lambda: datetime.utcnow().isoformat())

    # With parameters (types inferred)
    .add("sum@v1", "Add two numbers",
         lambda a: int, b: int: str(a + b))

    # Async function
    .add("fetch@v1", "Fetch URL", fetch_url, timeout=10.0)

    # Require approval
    .add("delete@v1", "Delete data", delete_data, require_approval=True)
)
```

## Message Handlers

Intercept and process messages before the LLM:

```python
from microsoft.agents.hosting import TurnResult

async def on_user_message(message, context, cancellation_token):
    # Log all messages
    await context.log_async(f"User said: {message.text}")

    # Handle commands
    if message.text.lower() == "/help":
        await context.respond_async("Available commands: /help, /about")
        return TurnResult.REPLIED

    # Let LLM handle normal messages
    return TurnResult.CONTINUE

agent.on_user_message(on_user_message)
```

## State Management

Store conversation state across turns:

```python
async def on_user_message(message, context, cancellation_token):
    # Get state
    count = await context.state.get_async("message_count", default=0)

    # Update state
    await context.state.set_async("message_count", count + 1)
    await context.state.set_async("last_message", message.text)

    # Use state
    await context.respond_async(f"Message #{count + 1} in this conversation")
    return TurnResult.REPLIED
```

### Storage Backends

```python
from microsoft.agents.hosting import AgentHostBuilder
from microsoft.agents.hosting.state import MemoryStateStore

# In-memory (default, for development)
builder = AgentHostBuilder()  # Uses MemoryStateStore by default

# SQL (production)
from microsoft.agents.hosting.state import SqlStateStore
store = SqlStateStore("postgresql://user:pass@localhost/agentdb")
builder = builder.use_state_store(store)

# Redis (production, fast)
from microsoft.agents.hosting.state import RedisStateStore
store = RedisStateStore("redis://localhost:6379")
builder = builder.use_state_store(store)
```

## Production Configuration

Enable production defaults with one line:

```python
agent_host = (
    AgentHostBuilder()
    .use_production_defaults()  # ✨ Adds retries, logging, queuing, etc.
    .add_default_agent(lambda agent: agent
        .use_llm("gpt-4", "You are helpful.")
    )
    .build()
)
```

This configures:

- ✅ SQL state storage (configurable)
- ✅ Redis message queue (configurable)
- ✅ Structured JSON logging
- ✅ Retry logic with exponential backoff
- ✅ Circuit breakers for failing services
- ✅ OpenTelemetry observability
- ✅ Function sandboxing
- ✅ Dead letter queue for failed messages

### Fine-Tuned Configuration

```python
agent_host = (
    AgentHostBuilder()
    .configure_concurrency(
        max_concurrent_requests=200,
        request_timeout=60.0
    )
    .configure_retries(
        max_attempts=5,
        backoff_base=1.5
    )
    .configure_sandbox(
        max_memory_mb=256,
        allow_network=True,  # For API functions
        allowed_modules=["requests", "json"]
    )
    .configure_logging(
        level="INFO",
        format="json",
        mask_secrets=True
    )
    .add_default_agent(...)
    .build()
)
```

## Out-of-Band Messages

Send messages from background tasks or webhooks:

```python
# Get the publisher
publisher = agent_host.get_publisher()

# In a background task
async def send_reminder():
    await publisher.send_to_thread_async(
        "thread_abc123",
        "This is your daily reminder!"
    )
```

## Testing

Use built-in mocks for testing:

```python
import pytest
from microsoft.agents.hosting import AgentHostBuilder, TurnResult
from microsoft.agents.hosting.testing import MockLLM

@pytest.mark.asyncio
async def test_agent_command():
    async def on_user_message(msg, ctx, ct):
        if msg.text == "/help":
            await ctx.respond_async("Help text")
            return TurnResult.REPLIED
        return TurnResult.CONTINUE

    agent_host = (
        AgentHostBuilder()
        .add_default_agent(lambda a: a
            .use_llm("gpt-4", "You are helpful.")
            .on_user_message(on_user_message)
        )
        .build()
    )

    response = await agent_host.process_message("/help")
    assert response.text == "Help text"
```

## Error Handling

Custom error handlers:

```python
from microsoft.agents.hosting import RateLimitError

async def error_handler(error, context, cancellation_token):
    if isinstance(error, RateLimitError):
        await context.respond_async("Too many requests. Please try again later.")
        return ErrorHandlingResult.HANDLED

    return ErrorHandlingResult.UNHANDLED

agent.on_error(error_handler)
```

## Security

Sandboxing is **enabled by default**:

```python
# Default sandbox (safe)
agent_host = AgentHostBuilder().add_default_agent(...)  # ✅ Safe defaults

# Custom sandbox (be careful!)
agent_host = (
    AgentHostBuilder()
    .configure_sandbox(
        max_memory_mb=512,
        max_cpu_percent=50.0,
        allow_network=False,  # ✅ Network disabled by default
        allow_filesystem_write=False,  # ✅ Writes disabled by default
        allowed_modules=["json", "datetime"]  # ✅ Only safe modules
    )
    .add_default_agent(...)
)
```

## Documentation

For complete documentation, see:

- [Getting Started Guide](https://github.com/microsoft/agent-protocol/docs/python-hosting-sdk/getting-started.md)
- [Technical Specification](https://github.com/microsoft/agent-protocol/docs/python-hosting-sdk/technical-specification.md)
- [API Reference](https://github.com/microsoft/agent-protocol/docs/python-hosting-sdk/api-reference.md)
- [Example Repository](https://github.com/microsoft/agent-protocol/tree/main/python/examples)

## Requirements

- Python 3.10+
- An LLM API key (OpenAI, Anthropic, etc.)

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- [GitHub Issues](https://github.com/microsoft/agent-protocol/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/microsoft-agents)
- [Community Forum](https://github.com/microsoft/agent-protocol/discussions)
