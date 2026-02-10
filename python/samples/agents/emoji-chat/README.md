# Emoji Chat Bot

A sample agent demonstrating the Microsoft Agents Protocol Hosting SDK with emoji functionality.

## Features

- **Tool Calling**: Two functions that the LLM can call:
  - `add_emoji_to_message`: Add emoji reactions to specific messages
  - `suggest_emoji`: Suggest appropriate emojis based on message sentiment

- **Event Handling**:
  - User joined/left events
  - Emoji reaction events

- **State Management**:
  - Track message count
  - Remember last emoji used

- **Fluent Builder API**: Uses the `AgentHostBuilder` for clean configuration

## Project Structure

```
emoji-chat-bot/
├── README.md
├── pyproject.toml
└── src/
    ├── __init__.py
    ├── emoji_chat_bot.py    # Main entry point with AgentHostBuilder
    └── types.py             # Result types (AddEmojiResult, EmojiSuggestion)
```

## Installation

1. Install the package in development mode:

```bash
cd python/samples/agents/emoji-chat-bot
pip install -e .
```

Or install with the parent hosting SDK:

```bash
cd python/microsoft-agents-hosting
pip install -e .
cd ../../samples/agents/emoji-chat-bot
pip install -e .
```

## Running the Agent

### Method 1: Using the installed script

```bash
emoji-chat-bot
```

### Method 2: Running the module directly

```bash
python -m src.emoji_chat_bot
```

### Method 3: Running the Python file

```bash
python src/emoji_chat_bot.py
```

## Usage

Once running, the agent will:

1. Listen for incoming messages
2. Process emoji-related requests using the LLM and available functions
3. Handle system events like users joining/leaving
4. Track conversation state

### Commands

- `/stats` - Show conversation statistics (message count, last emoji used)

### Example Interactions

**Adding Emoji Reactions:**
```
User: "Add a thumbs up to message 123"
Bot: [Calls add_emoji_to_message function] "Added 👍 reaction to message 123"
```

**Suggesting Emojis:**
```
User: "What emoji should I use for 'Great job!'"
Bot: [Calls suggest_emoji function] "For 'Great job!' I suggest: 😊 🎉 👍"
```

**Reacting with Emojis:**
```
User: [Adds 👍 reaction]
Bot: "I see you reacted with 👍! That's a great choice! 😊"
```

## Architecture

This sample demonstrates the **Hosting SDK** pattern:

### AgentHostBuilder API

```python
agent_host = (
    AgentHostBuilder()
    .add_default_agent(lambda agent: agent
        .use_llm("gpt-4", "You are an emoji bot...")
        .add_functions(lambda f: f
            .add("add_emoji_to_message@v1", "...", add_emoji_to_message)
            .add("suggest_emoji@v1", "...", suggest_emoji)
        )
        .on_user_message(on_user_message)
        .on_reaction(handle_emoji_reaction)
    )
    .build()
)
```

### Function Registration

Functions are registered with the fluent builder API and automatically exposed to the LLM as tools:

```python
async def add_emoji_to_message(message_id: str, emoji: str) -> AddEmojiResult:
    """Add an emoji reaction to a specific message."""
    return AddEmojiResult(
        success=True,
        message_id=message_id,
        emoji=emoji,
        message=f"Added {emoji} reaction to message {message_id}"
    )
```

### Event Handlers

Event handlers process specific events and can:
- Return `TurnResult.CONTINUE` to let the LLM handle it
- Return `TurnResult.REPLIED` to indicate the handler already responded
- Return `TurnResult.CONSUMED` to stop processing without responding

```python
async def handle_emoji_reaction(reaction, context, cancellation_token):
    """Handle emoji reactions."""
    emoji = getattr(reaction, 'emoji', '?')
    await context.state.set_async("last_emoji_used", emoji)
    await context.respond_async(f"I see you reacted with {emoji}!")
    return TurnResult.REPLIED
```

### State Management

The agent tracks state across messages using the context's state API:

```python
# Get state
count = await context.state.get_async("message_count", default=0)

# Set state
await context.state.set_async("message_count", count + 1)

# Clear all state
await context.state.clear_async()
```

## Comparison with .NET Version

This Python implementation mirrors the .NET version at `dotnet/samples/agents/EmojiChatBot/` but uses:

- **Python naming conventions**: `snake_case` instead of `PascalCase`
- **Dataclasses**: Instead of C# classes for result types
- **Async/await**: Python's native async syntax
- **Fluent builder API**: Lambdas with the builder pattern
- **Type hints**: Python's typing system instead of C# generics

## Dependencies

- `microsoft-agents-hosting>=0.1.0` - Microsoft Agents Protocol Hosting SDK

## License

MIT License - Copyright (c) Microsoft Corporation
