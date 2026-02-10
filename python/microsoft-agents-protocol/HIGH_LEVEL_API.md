# High-Level Python Client SDK API

This document describes the high-level convenience API for the Microsoft Agents Protocol Python client, which matches the .NET implementation.

## Overview

The high-level API provides simplified methods for common operations:

- **Simple text chat**: Send text, get text back
- **Structured messages**: Full control over message objects
- **Streaming**: Real-time response chunks
- **Conversations**: Stateful multi-turn interactions
- **Tool execution**: Register and execute functions

## Installation

```bash
pip install microsoft-agents-protocol
```

## Quick Start

### Simple Chat

```python
from microsoft.agents.protocol.client import create_simplified_client

# Create client
client = create_simplified_client("http://localhost:5000")

async with client:
    # Simple text in, text out
    response = await client.complete_chat("Hello, how are you?")
    print(response)
```

### With Options

```python
from microsoft.agents.protocol.client import SimplifiedClient, ChatOptions, AgentProtocolClientOptions

# Create client with full options
options = AgentProtocolClientOptions(
    base_url="https://agents.example.com/v1",
    api_key="your-api-key"
)
client = SimplifiedClient(options)

# Chat with options
async with client:
    chat_options = ChatOptions(
        agent_id="my-agent",
        metadata={"session": "123"}
    )
    response = await client.complete_chat("Tell me a joke", chat_options)
    print(response)
```

## Conversations

Maintain state across multiple messages:

```python
from microsoft.agents.protocol.client import create_simplified_client

client = create_simplified_client("http://localhost:5000")

async with client:
    # Create a new conversation
    conversation = client.create_conversation()

    # Send multiple messages
    response1 = await conversation.send("My name is Alice")
    print(response1)  # "Nice to meet you, Alice!"

    response2 = await conversation.send("What's my name?")
    print(response2)  # "Your name is Alice"

    # Thread ID is automatically tracked
    print(f"Thread ID: {conversation.thread_id}")
```

### Resume Existing Conversation

```python
# Resume from a saved thread ID
conversation = client.resume_conversation("thread_abc123")
response = await conversation.send("Continue our discussion")
```

## Structured Messages

Work with full message objects:

```python
# Send structured message
message = {
    "role": "user",
    "contents": [
        {"kind": "text", "text": "Hello"},
        {"kind": "image", "data": "base64..."}
    ]
}

response = await client.complete_chat_structured(message)
print(response["role"])  # "agent"
print(response["contents"])
```

## Streaming

### Text Chunks

```python
def handle_chunk(text: str):
    print(text, end="", flush=True)

await client.stream_chat("Tell me a long story", handle_chunk)
print()  # New line after streaming
```

### Stream Messages

```python
conversation = client.create_conversation()

async for message in conversation.stream_messages("Generate a report"):
    # Each message is a dict with full structure
    contents = message.get("contents", [])
    for content in contents:
        if content.get("kind") == "text":
            print(content.get("text"))
```

### Stream Events (Low-Level)

```python
async for event in conversation.stream_events("Process this"):
    print(f"Event: {event.event_type}")
    print(f"Data: {event.data}")

    # Or deserialize to specific type
    if event.event_type == "message.delta":
        # event.get_data_as(SomeDataClass)
        pass
```

## Tools

Register and execute functions that the agent can call:

```python
from microsoft.agents.protocol.client import ToolCollection, ChatOptions

# Create tool collection
tools = ToolCollection()

# Add synchronous tool
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny"

tools.add("get_weather", get_weather, "Gets the current weather")

# Add async tool
async def search_database(query: str) -> str:
    # Simulate async database search
    return f"Results for: {query}"

tools.add("search", search_database, "Searches the database")

# Use tools in chat
options = ChatOptions(tools=tools)
response = await client.complete_chat(
    "What's the weather in Seattle?",
    options
)
```

### Tool Schema Generation

Schemas are automatically generated from function signatures:

```python
def calculate(x: int, y: int, operation: str = "add") -> str:
    if operation == "add":
        return str(x + y)
    elif operation == "multiply":
        return str(x * y)
    return str(x)

tools.add("calculate", calculate)

# Generated schema:
# {
#     "type": "object",
#     "properties": {
#         "x": {"type": "integer", "description": "Parameter x"},
#         "y": {"type": "integer", "description": "Parameter y"},
#         "operation": {"type": "string", "description": "Parameter operation"}
#     },
#     "required": ["x", "y"]  # "operation" is optional
# }
```

### Manual Tool Execution

```python
tools = ToolCollection()
tools.add("add", lambda x, y: str(x + y))

# Execute directly
result = await tools.execute("add", '{"x": 5, "y": 3}')
print(result)  # "8"
```

## API Reference

### SimplifiedClient

Main high-level client class.

**Methods:**

- `complete_chat(message: str, options: Optional[ChatOptions] = None) -> str`
  - Simple text-in, text-out chat

- `complete_chat_structured(message: Dict[str, Any], options: Optional[ChatOptions] = None) -> Dict[str, Any]`
  - Send and receive structured messages

- `stream_chat(message: str, on_text_chunk: Callable[[str], None]) -> None`
  - Stream response with text chunk callback

- `create_conversation() -> IConversation`
  - Create new stateful conversation

- `resume_conversation(thread_id: str) -> IConversation`
  - Resume existing conversation

### IConversation

Interface for stateful conversations.

**Properties:**

- `thread_id: Optional[str]` - Thread ID (None until first message)

**Methods:**

- `send(message: str) -> str` - Send text, get text back
- `send_structured(message: Dict[str, Any]) -> Dict[str, Any]` - Send structured message
- `stream_messages(message: str) -> AsyncIterator[Dict[str, Any]]` - Stream messages
- `stream_events(message: str) -> AsyncIterator[StreamEvent]` - Stream raw events

### ChatOptions

Configuration for chat requests.

**Fields:**

- `agent_id: Optional[str]` - Specific agent to use
- `tools: Optional[ToolCollection]` - Available tools
- `metadata: Optional[Dict[str, Any]]` - Custom metadata
- `on_tool_call_started: Optional[Callable]` - Tool call start callback
- `on_tool_call_completed: Optional[Callable]` - Tool call completion callback
- `on_tool_call_failed: Optional[Callable]` - Tool call failure callback

### ToolCollection

Collection of callable functions.

**Methods:**

- `add(name: str, handler: Callable, description: Optional[str] = None)` - Add tool
- `get(name: str) -> Optional[ToolDefinition]` - Get tool by name
- `get_all() -> List[ToolDefinition]` - Get all tools
- `execute(tool_name: str, arguments_json: str) -> Any` - Execute tool

### StreamEvent

Represents a server-sent event.

**Fields:**

- `event_type: str` - Event type (e.g., "message.delta")
- `data: Dict[str, Any]` - Event data

**Methods:**

- `get_data_as(cls: Type[T]) -> Optional[T]` - Deserialize to type

## Complete Example

```python
import asyncio
from microsoft.agents.protocol.client import (
    create_simplified_client,
    ChatOptions,
    ToolCollection
)

async def main():
    # Setup
    client = create_simplified_client("http://localhost:5000")

    # Create tools
    tools = ToolCollection()

    def add(x: int, y: int) -> str:
        return str(x + y)

    async def search(query: str) -> str:
        return f"Found: {query}"

    tools.add("add", add, "Adds two numbers")
    tools.add("search", search, "Searches for information")

    # Use client
    async with client:
        # Simple chat
        response = await client.complete_chat("Hello!")
        print(response)

        # Chat with tools
        options = ChatOptions(tools=tools)
        response = await client.complete_chat(
            "What is 5 + 3?",
            options
        )
        print(response)

        # Conversation
        conversation = client.create_conversation()
        r1 = await conversation.send("My favorite color is blue")
        r2 = await conversation.send("What's my favorite color?")
        print(r2)

        # Streaming
        print("Streaming: ", end="")
        await client.stream_chat(
            "Count to 5",
            lambda chunk: print(chunk, end="", flush=True)
        )
        print()

if __name__ == "__main__":
    asyncio.run(main())
```

## Type Hints

All public APIs include full type hints for IDE support:

```python
from typing import Optional, Callable, AsyncIterator, Dict, Any

async def complete_chat(
    message: str,
    options: Optional[ChatOptions] = None
) -> str:
    ...
```

## Error Handling

```python
try:
    response = await client.complete_chat("Hello")
except Exception as e:
    print(f"Error: {e}")
```

## Comparison with .NET

The Python API closely matches the .NET implementation:

| .NET | Python |
|------|--------|
| `CompleteChatAsync(message)` | `await complete_chat(message)` |
| `CompleteChatAsync(message, options)` | `await complete_chat(message, options)` |
| `StreamChatAsync(message, onTextChunk)` | `await stream_chat(message, on_text_chunk)` |
| `CreateConversation()` | `create_conversation()` |
| `ResumeConversation(threadId)` | `resume_conversation(thread_id)` |
| `IConversation.SendAsync(message)` | `await conversation.send(message)` |
| `IConversation.StreamMessagesAsync(message)` | `conversation.stream_messages(message)` |
| `ToolCollection.Add(name, handler)` | `tools.add(name, handler)` |

## Testing

The package includes comprehensive tests. To run them:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/test_simplified_client.py -v
pytest tests/test_tool_collection.py -v
pytest tests/test_conversation.py -v
pytest tests/test_stream_event.py -v
```

## License

MIT License - Copyright (c) Microsoft Corporation
