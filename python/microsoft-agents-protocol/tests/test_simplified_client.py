# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for the simplified client API"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from microsoft.agents.protocol.client import (
    SimplifiedClient,
    ChatOptions,
    ToolCollection,
    create_simplified_client,
)
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions
from test_helpers.doc_markers import doc_example


@pytest.fixture
def mock_options():
    """Creates mock client options"""
    return AgentProtocolClientOptions(base_url="http://localhost:5000")


@pytest.fixture
def client(mock_options):
    """Creates a simplified client with mocked HTTP"""
    with patch("microsoft.agents.protocol.client.agent_protocol_client.aiohttp"):
        return SimplifiedClient(mock_options)


@pytest.mark.asyncio
@doc_example("client-simple-completion", "Simple Chat Completion")
async def test_complete_chat_basic(client):
    """Test basic complete_chat functionality"""
    # Mock the runs.create_and_wait method
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "I can help you with analysis, writing, coding, research, and problem-solving tasks."}],
                }
            ],
        }
    )

    # doc-example-start
    # Send message and get response
    response = await client.complete_chat("What can you help me with?")
    print(response)
    # doc-example-end

    assert response == "I can help you with analysis, writing, coding, research, and problem-solving tasks."
    assert client.runs.create_and_wait.called


@pytest.mark.asyncio
async def test_complete_chat_with_options(client):
    """Test complete_chat with ChatOptions"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Response text"}],
                }
            ],
        }
    )

    options = ChatOptions(
        agent_id="agent_1", metadata={"key": "value"}
    )
    result = await client.complete_chat("Test message", options)

    assert result == "Response text"
    call_args = client.runs.create_and_wait.call_args[0][0]
    assert call_args["agent_id"] == "agent_1"
    assert call_args["metadata"] == {"key": "value"}


@pytest.mark.asyncio
@doc_example("client-tools", "Tools with Lambda Functions")
async def test_complete_chat_with_tools(client):
    """Test complete_chat with tools"""
    # Mock the underlying create_and_wait to return a simple response
    async def mock_create_and_wait(request):
        return {
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "The weather in Seattle is sunny and 72°F"}],
                }
            ],
        }

    client.runs.create_and_wait = mock_create_and_wait

    # doc-example-start
    # Define tools using lambda functions
    tools = ToolCollection()
    tools.add("get_weather", lambda location: f"The weather in {location} is sunny and 72°F")
    tools.add("get_time", lambda timezone: "2024-01-15 14:30:00")

    # Use tools in chat
    options = ChatOptions(tools=tools)
    response = await client.complete_chat("What's the weather in Seattle?", options)
    print(response)
    # doc-example-end

    # Verify tools were added
    assert len(tools) == 2
    assert tools.get("get_weather") is not None


@pytest.mark.asyncio
async def test_complete_chat_structured(client):
    """Test complete_chat_structured"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "message_id": "msg_789",
                    "contents": [{"kind": "text", "text": "Structured response"}],
                }
            ],
        }
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
    }

    result = await client.complete_chat_structured(message)

    assert result["role"] == "agent"
    assert result["message_id"] == "msg_789"
    assert result["contents"][0]["text"] == "Structured response"


@pytest.mark.asyncio
@doc_example("client-streaming", "Streaming with Callback")
async def test_stream_chat(client):
    """Test stream_chat functionality"""
    # Mock SSE stream
    async def mock_stream(request):
        events = [
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Hello"}]}\n',
            "\n",
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Hello world"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    # doc-example-start
    # Stream the response with a callback
    def on_chunk(text):
        print(text, end="")

    await client.stream_chat("Tell me a story about a robot", on_chunk)
    print()
    # doc-example-end

    # Also verify streaming works (for test)
    chunks = []
    def capture_chunk(text):
        chunks.append(text)
    await client.stream_chat("Test", capture_chunk)
    assert len(chunks) > 0


def test_create_conversation(client):
    """Test creating a new conversation"""
    conversation = client.create_conversation()

    assert conversation is not None
    assert conversation.thread_id is None


@doc_example("client-resume-conversation", "Resume Conversation")
def test_resume_conversation(client):
    """Test resuming an existing conversation"""
    thread_id = "thread_123"

    # doc-example-start
    # Resume a previous conversation by thread ID
    conversation = client.resume_conversation(thread_id)
    # doc-example-end

    assert conversation is not None
    assert conversation.thread_id == thread_id


@pytest.mark.asyncio
@doc_example("client-conversation", "Persistent Conversation")
async def test_conversation_send(client):
    """Test conversation send method"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Conversation response"}],
                }
            ],
        }
    )

    # doc-example-start
    # Create a persistent conversation
    conversation = client.create_conversation()

    # Send messages that maintain context
    response1 = await conversation.send("My name is Alice")
    print(response1)

    response2 = await conversation.send("What's my name?")
    print(response2)
    # doc-example-end

    result = await conversation.send("Hello")
    assert result == "Conversation response"
    assert conversation.thread_id == "thread_456"


def test_tool_collection_add():
    """Test adding tools to collection"""
    tools = ToolCollection()

    def my_tool(x: int, y: int) -> str:
        return str(x + y)

    tools.add("add", my_tool, "Adds two numbers")

    tool = tools.get("add")
    assert tool is not None
    assert tool.name == "add"
    assert tool.description == "Adds two numbers"


@pytest.mark.asyncio
async def test_tool_collection_execute():
    """Test executing a tool"""
    tools = ToolCollection()

    def add_numbers(x: int, y: int) -> str:
        return str(x + y)

    tools.add("add", add_numbers)

    result = await tools.execute("add", '{"x": 5, "y": 3}')
    assert result == "8"


@pytest.mark.asyncio
async def test_tool_collection_execute_async():
    """Test executing an async tool"""
    tools = ToolCollection()

    async def async_tool(message: str) -> str:
        return f"Processed: {message}"

    tools.add("process", async_tool)

    result = await tools.execute("process", '{"message": "test"}')
    assert result == "Processed: test"


def test_create_simplified_client():
    """Test the create_simplified_client convenience function"""
    with patch("microsoft.agents.protocol.client.agent_protocol_client.aiohttp"):
        client = create_simplified_client(
            "http://localhost:5000", api_key="test_key"
        )

        assert client is not None
        assert isinstance(client, SimplifiedClient)


@pytest.mark.asyncio
async def test_complete_chat_structured_with_no_output(client):
    """Test complete_chat_structured when response has no output"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [],
        }
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
    }

    result = await client.complete_chat_structured(message)

    assert result["role"] == "agent"
    assert result["contents"] == []


@pytest.mark.asyncio
async def test_complete_chat_structured_with_no_agent_message(client):
    """Test complete_chat_structured when output has no agent message"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": "User message"}],
                }
            ],
        }
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
    }

    result = await client.complete_chat_structured(message)

    # Should return default agent message when no agent message found
    assert result["role"] == "agent"
    assert result["contents"] == []


@pytest.mark.asyncio
async def test_complete_chat_structured_with_options(client):
    """Test complete_chat_structured with options"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Response"}],
                }
            ],
        }
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
    }

    options = ChatOptions(agent_id="agent_123", metadata={"session": "abc"})

    result = await client.complete_chat_structured(message, options)

    assert result["role"] == "agent"
    call_args = client.runs.create_and_wait.call_args[0][0]
    assert call_args["agent_id"] == "agent_123"
    assert call_args["metadata"] == {"session": "abc"}


@pytest.mark.asyncio
async def test_complete_chat_with_no_output(client):
    """Test complete_chat when response has no output"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [],
        }
    )

    result = await client.complete_chat("Test message")

    assert result == ""


@pytest.mark.asyncio
async def test_complete_chat_with_no_agent_message(client):
    """Test complete_chat when output has no agent message"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": "User message"}],
                }
            ],
        }
    )

    result = await client.complete_chat("Test message")

    assert result == ""


@pytest.mark.asyncio
async def test_complete_chat_with_no_text_content(client):
    """Test complete_chat when agent message has no text content"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "image", "url": "http://example.com/img.png"}],
                }
            ],
        }
    )

    result = await client.complete_chat("Test message")

    assert result == ""


@pytest.mark.asyncio
async def test_complete_chat_with_empty_contents(client):
    """Test complete_chat when agent message has empty contents"""
    client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [],
                }
            ],
        }
    )

    result = await client.complete_chat("Test message")

    assert result == ""


@pytest.mark.asyncio
async def test_stream_chat_with_message_updated_event(client):
    """Test stream_chat with message.updated event type"""
    # Mock SSE stream
    async def mock_stream(request):
        events = [
            "event: message.updated\n",
            'data: {"contents": [{"kind": "text", "text": "Updated text"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    chunks = []
    def capture_chunk(text):
        chunks.append(text)

    await client.stream_chat("Test", capture_chunk)

    assert len(chunks) > 0
    assert "Updated text" in "".join(chunks)


@pytest.mark.asyncio
async def test_stream_chat_with_non_text_content(client):
    """Test stream_chat ignores non-text content"""
    # Mock SSE stream
    async def mock_stream(request):
        events = [
            "event: message.delta\n",
            'data: {"contents": [{"kind": "image", "url": "test.png"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    chunks = []
    def capture_chunk(text):
        chunks.append(text)

    await client.stream_chat("Test", capture_chunk)

    # Should not capture any chunks since content is not text
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_stream_chat_with_text_replacement(client):
    """Test stream_chat handles full text replacement"""
    # Mock SSE stream with text that doesn't start with accumulated text
    async def mock_stream(request):
        events = [
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "First"}]}\n',
            "\n",
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Completely different"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    chunks = []
    def capture_chunk(text):
        chunks.append(text)

    await client.stream_chat("Test", capture_chunk)

    assert len(chunks) == 2
    assert chunks[0] == "First"
    assert chunks[1] == "Completely different"


@pytest.mark.asyncio
async def test_stream_chat_with_empty_new_text(client):
    """Test stream_chat doesn't call callback for empty new text"""
    # Mock SSE stream with same text twice
    async def mock_stream(request):
        events = [
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Same"}]}\n',
            "\n",
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Same"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    chunks = []
    def capture_chunk(text):
        chunks.append(text)

    await client.stream_chat("Test", capture_chunk)

    # Should only have one chunk since second event has no new text
    assert len(chunks) == 1


@pytest.mark.asyncio
async def test_stream_run_internal_method(client):
    """Test _stream_run internal method"""
    # Mock SSE stream
    async def mock_stream(request):
        events = [
            "event: message.start\n",
            'data: {"message_id": "msg_1"}\n',
            "\n",
            "event: message.delta\n",
            'data: {"text": "Hello"}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    request = {"input": [{"role": "user", "contents": [{"kind": "text", "text": "Hi"}]}]}

    events = []
    async for event in client._stream_run(request):
        events.append(event)

    assert len(events) == 2
    assert events[0]["event_type"] == "message.start"
    assert events[1]["event_type"] == "message.delta"


@pytest.mark.asyncio
async def test_stream_run_with_invalid_json(client):
    """Test _stream_run handles invalid JSON gracefully"""
    # Mock SSE stream with invalid JSON
    async def mock_stream(request):
        events = [
            "event: test\n",
            'data: {invalid json}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    request = {"input": [{"role": "user", "contents": [{"kind": "text", "text": "Hi"}]}]}

    events = []
    async for event in client._stream_run(request):
        events.append(event)

    # Should still yield event with raw data
    assert len(events) == 1
    assert events[0]["event_type"] == "test"
    assert "raw" in events[0]["data"]


@pytest.mark.asyncio
async def test_stream_run_yields_final_event(client):
    """Test _stream_run yields final event without trailing empty line"""
    # Mock SSE stream without final empty line
    async def mock_stream(request):
        events = [
            "event: final\n",
            'data: {"status": "done"}\n',
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    request = {"input": [{"role": "user", "contents": [{"kind": "text", "text": "Hi"}]}]}

    events = []
    async for event in client._stream_run(request):
        events.append(event)

    # Should yield the final event even without trailing empty line
    assert len(events) == 1
    assert events[0]["event_type"] == "final"


@pytest.mark.asyncio
async def test_complete_chat_with_tools_triggers_stream_run(client):
    """Test _complete_chat_with_tools method"""
    # Mock SSE stream
    async def mock_stream(request):
        events = [
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Result"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    request = {"input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}]}
    options = ChatOptions(tools=ToolCollection())

    result = await client._complete_chat_with_tools(request, options)

    assert result == "Result"


@pytest.mark.asyncio
async def test_complete_chat_with_tools_run_requires_action(client):
    """Test _complete_chat_with_tools with run.requires_action event"""
    # Mock SSE stream with requires_action event
    async def mock_stream(request):
        events = [
            "event: run.requires_action\n",
            'data: {"tool_calls": [{"id": "call_1", "function": "test"}]}\n',
            "\n",
            "event: message.delta\n",
            'data: {"contents": [{"kind": "text", "text": "Done"}]}\n',
            "\n",
        ]
        for event in events:
            yield event.strip()

    client.runs.create_and_stream = mock_stream

    request = {"input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}]}
    options = ChatOptions(tools=ToolCollection())

    result = await client._complete_chat_with_tools(request, options)

    # The run.requires_action event is currently a no-op (TODO in code)
    assert result == "Done"


@pytest.mark.asyncio
async def test_extract_text_from_response_with_multiple_messages(client):
    """Test _extract_text_from_response finds first agent message"""
    response = {
        "output": [
            {
                "role": "user",
                "contents": [{"kind": "text", "text": "User message"}],
            },
            {
                "role": "agent",
                "contents": [{"kind": "text", "text": "Agent message 1"}],
            },
            {
                "role": "agent",
                "contents": [{"kind": "text", "text": "Agent message 2"}],
            },
        ]
    }

    result = client._extract_text_from_response(response)

    # Should return first agent message
    assert result == "Agent message 1"


@pytest.mark.asyncio
async def test_extract_text_from_response_with_no_text_content(client):
    """Test _extract_text_from_response with no text content"""
    response = {
        "output": [
            {
                "role": "agent",
                "contents": [{"kind": "image", "url": "test.png"}],
            }
        ]
    }

    result = client._extract_text_from_response(response)

    assert result == ""
