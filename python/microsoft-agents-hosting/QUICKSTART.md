# Quick Start Guide

Get started with the Microsoft Agents Protocol Hosting SDK in 5 minutes.

## Installation

```bash
pip install microsoft-agents-hosting
```

## Your First Agent (30 seconds)

Create `my_agent.py`:

```python
from microsoft.agents.hosting import AgentHostBuilder
from datetime import datetime

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

if __name__ == "__main__":
    agent_host.run()
```

Run it:
```bash
python my_agent.py
```

## Add Custom Commands (2 minutes)

```python
from microsoft.agents.hosting import AgentHostBuilder, TurnResult

async def on_user_message(message, context, cancellation_token):
    if message.text == "/help":
        await context.respond_async("Available commands: /help, /about")
        return TurnResult.REPLIED
    return TurnResult.CONTINUE

agent_host = (
    AgentHostBuilder()
    .add_default_agent(lambda agent: agent
        .use_llm("gpt-4", "You are helpful.")
        .on_user_message(on_user_message)
    )
    .build()
)
```

## Add State Management (2 minutes)

```python
async def on_user_message(message, context, cancellation_token):
    # Get state
    count = await context.state.get_async("count", default=0)

    # Update state
    await context.state.set_async("count", count + 1)

    # Use state
    await context.respond_async(f"Message #{count + 1}")
    return TurnResult.REPLIED
```

## Production Ready (1 line!)

```python
agent_host = (
    AgentHostBuilder()
    .use_production_defaults()  # ✨ Magic!
    .add_default_agent(...)
    .build()
)
```

This enables:
- ✅ Retries with exponential backoff
- ✅ Structured logging
- ✅ Circuit breakers
- ✅ Function sandboxing
- ✅ Error handling
- ✅ State management
- ✅ Observability

## What's Next?

- Read the [full README](README.md) for detailed docs
- Check out [examples/](examples/) for complete examples
- See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture

## Common Patterns

### Multiple Functions

```python
.add_functions(lambda f: f
    .add("get_time@v1", "Gets time", get_time)
    .add("search@v1", "Search database", search)
    .add("calculate@v1", "Do math", calculate)
)
```

### Async Functions

```python
async def fetch_url(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

.add_functions(lambda f: f
    .add("fetch@v1", "Fetch URL", fetch_url, timeout=10.0)
)
```

### Require Approval

```python
.add_functions(lambda f: f
    .add("delete_data@v1", "Delete data", delete_data,
         require_approval=True)
)
```

### Error Handling

```python
async def on_error(error, context, cancellation_token):
    if isinstance(error, RateLimitError):
        await context.respond_async("Rate limited. Try again later.")
        return ErrorHandlingResult.HANDLED
    return ErrorHandlingResult.UNHANDLED

.add_default_agent(lambda agent: agent
    .use_llm("gpt-4", "You are helpful.")
    .on_error(on_error)
)
```

### Out-of-Band Messages

```python
# Get publisher
publisher = agent_host.get_publisher()

# Send from background task
async def send_reminder():
    await publisher.send_to_thread_async(
        "thread_123",
        "Your reminder!"
    )
```

## Need Help?

- Check the [README](README.md)
- Browse [examples/](examples/)
- Read the [specification](.workspace/python-hosting-sdk/)
- File an [issue](https://github.com/microsoft/agent-protocol/issues)

## License

MIT License - See [LICENSE](LICENSE)
