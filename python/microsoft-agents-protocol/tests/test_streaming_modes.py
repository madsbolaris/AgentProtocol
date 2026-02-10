# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tests for streaming modes covering all streaming-guide.md patterns.
Tests three streaming modes: Callback, Messages, and Events.
"""

import pytest
import asyncio
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
from microsoft.agents.protocol.client import SimplifiedClient
from microsoft.agents.protocol.client.conversation import Conversation
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions
from microsoft.agents.protocol.client.stream_event import StreamEvent


def create_mock_events(events: List[tuple]) -> List[Dict[str, Any]]:
    """
    Creates mock stream events for testing.

    Args:
        events: List of (event_type, data_dict) tuples

    Returns:
        List of event dicts with 'event_type' and 'data' keys
    """
    return [{"event_type": event_type, "data": data} for event_type, data in events]


def create_sse_response(events: List[tuple]) -> List[str]:
    """
    Creates a mock Server-Sent Events (SSE) response as a list of lines.
    Used for testing the runs.create_and_stream method.

    Args:
        events: List of (event_type, data_dict) tuples

    Returns:
        List of SSE formatted strings
    """
    import json

    lines = []
    for event_type, data in events:
        lines.append(f"event: {event_type}")
        json_data = json.dumps(data)
        lines.append(f"data: {json_data}")
        lines.append("")  # Empty line marks end of event

    return lines


@pytest.fixture
def mock_client():
    """Creates a mock simplified client"""
    with patch("microsoft.agents.protocol.client.agent_protocol_client.aiohttp"):
        options = AgentProtocolClientOptions(base_url="http://localhost:5000")
        return SimplifiedClient(options)


@pytest.mark.asyncio
async def test_stream_chat_callback_mode_streams_text_chunks(mock_client):
    """
    Test Mode 1: Callback (Recommended for Most Apps)
    Verifies that text chunks are streamed via callback.
    """
    # Arrange - Example from "Mode 1: Callback (Recommended for Most Apps)"
    sse_lines = create_sse_response([
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Once upon"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Once upon a time"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Once upon a time, there was"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Once upon a time, there was a curious robot named Byte..."}]
        }),
        ("message.completed", {
            "message_id": "msg_1"
        })
    ])

    async def mock_stream(request):
        for line in sse_lines:
            yield line

    mock_client.runs.create_and_stream = mock_stream

    received_chunks: List[str] = []

    # Act
    await mock_client.stream_chat(
        "Tell me a story about a robot",
        on_text_chunk=lambda text: received_chunks.append(text)
    )

    # Assert
    assert len(received_chunks) > 0
    assert any("Once upon" in chunk for chunk in received_chunks)
    assert any(" a time" in chunk for chunk in received_chunks)

    # All chunks combined should form complete text
    full_text = "".join(received_chunks)
    assert "Once upon a time, there was a curious robot named Byte..." in full_text


@pytest.mark.asyncio
async def test_stream_chat_with_cancellation_stops_streaming(mock_client):
    """
    Test Interruption Handling
    Verifies that cancellation stops streaming.
    """
    # Arrange - Example from "Interruption Handling"
    mock_events = create_mock_events([
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Starting..."}]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            await asyncio.sleep(0.1)  # Simulate delay
            yield evt

    mock_client.runs.create_and_stream = mock_stream

    # Act & Assert
    with pytest.raises((asyncio.CancelledError, asyncio.TimeoutError)):
        async with asyncio.timeout(0.01):  # Cancel almost immediately
            await mock_client.stream_chat(
                "Long story...",
                on_text_chunk=lambda text: None
            )


@pytest.mark.asyncio
async def test_stream_messages_preserves_message_boundaries(mock_client):
    """
    Test Mode 2: Messages (Advanced UI Control)
    Verifies that message boundaries are preserved during streaming.
    """
    # Arrange - Example from "Mode 2: Messages (Advanced UI Control)"
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": []
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Tell me"}]
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Tell me about Paris"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Tell me about Paris"}]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    messages: List[Dict[str, Any]] = []

    # Act
    async for message in conversation.stream_messages("Tell me about Paris"):
        messages.append(message)

    # Assert
    assert len(messages) > 0
    assert all(msg.get("message_id") == "msg_1" for msg in messages)


@pytest.mark.asyncio
async def test_stream_messages_with_multiple_messages_yields_each_message(mock_client):
    """
    Test streaming multiple messages in sequence.
    Verifies that each message is yielded separately.
    """
    # Arrange - Multiple messages in stream
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": []
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "First message"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "First message"}]
        }),
        ("message.created", {
            "message_id": "msg_2",
            "role": "agent",
            "contents": []
        }),
        ("message.updated", {
            "message_id": "msg_2",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Second message"}]
        }),
        ("message.completed", {
            "message_id": "msg_2",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Second message"}]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    message_ids: List[str] = []

    # Act
    async for message in conversation.stream_messages("Multiple messages"):
        message_id = message.get("message_id")
        if message_id:
            message_ids.append(message_id)

    # Assert
    assert "msg_1" in message_ids
    assert "msg_2" in message_ids


@pytest.mark.asyncio
async def test_stream_events_provides_raw_events(mock_client):
    """
    Test Mode 3: Raw Events (Full Control)
    Verifies that raw events are provided with all event types.
    """
    # Arrange - Example from "Mode 3: Raw Events (Full Control)"
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent"
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "metadata": {"total_tokens": 100}
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    event_types: List[str] = []

    # Act
    async for evt in conversation.stream_events("Tell me about Paris"):
        event_types.append(evt.event_type)

    # Assert
    assert "run.started" in event_types
    assert "message.created" in event_types
    assert "message.updated" in event_types
    assert "message.completed" in event_types


@pytest.mark.asyncio
async def test_stream_events_with_tool_calls_emits_requires_action_event(mock_client):
    """
    Test handling tool calls with run.requires_action event.
    """
    # Arrange - Example from "Handle tool calls" section
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("run.requires_action", {
            "run_id": "run_1",
            "required_action": {
                "type": "submit_tool_outputs",
                "tool_calls": [
                    {
                        "call_id": "call_123",
                        "name": "get_weather",
                        "arguments": '{"location":"Paris"}'
                    }
                ]
            }
        }),
        ("run.completed", {
            "run_id": "run_1",
            "status": "completed"
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    has_requires_action_event = False

    # Act
    async for evt in conversation.stream_events("What's the weather?"):
        if evt.event_type == "run.requires_action":
            has_requires_action_event = True

    # Assert
    assert has_requires_action_event


@pytest.mark.asyncio
async def test_stream_messages_with_text_accumulation_handles_incremental_text(mock_client):
    """
    Test text accumulation pattern from streaming-guide.md.
    Verifies that incremental text updates are handled correctly.
    """
    # Arrange - Test text accumulation pattern
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": []
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello"}]
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello world"}]
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello world!"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello world!"}]
        }),
        ("run.completed", {
            "run_id": "run_1",
            "status": "completed"
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    text_position = 0
    incremental_chunks: List[str] = []

    # Act - Pattern from streaming-guide.md
    async for message in conversation.stream_messages("Say hello"):
        contents = message.get("contents", [])
        for content in contents:
            if content.get("kind") == "text":
                text = content.get("text", "")
                if len(text) > text_position:
                    new_text = text[text_position:]
                    if new_text:
                        incremental_chunks.append(new_text)
                        text_position = len(text)

    # Assert
    assert len(incremental_chunks) > 0
    assert incremental_chunks[0] == "Hello"
    assert " world" in incremental_chunks
    assert "!" in incremental_chunks

    full_text = "".join(incremental_chunks)
    assert full_text == "Hello world!"


@pytest.mark.asyncio
async def test_stream_events_message_buffering_tracks_multiple_messages(mock_client):
    """
    Test message buffering pattern from streaming-guide.md "Mode 3: Raw Events".
    Verifies that multiple messages can be tracked simultaneously.
    """
    # Arrange - Pattern from streaming-guide.md
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_1",
            "thread_id": "thread_1",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent"
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "First"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent"
        }),
        ("message.created", {
            "message_id": "msg_2",
            "role": "agent"
        }),
        ("message.updated", {
            "message_id": "msg_2",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Second"}]
        }),
        ("message.completed", {
            "message_id": "msg_2",
            "role": "agent"
        }),
        ("run.completed", {
            "run_id": "run_1",
            "status": "completed"
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    message_buffers: Dict[str, List[str]] = {}

    # Act - Pattern from streaming-guide.md
    async for evt in conversation.stream_events("Multiple messages"):
        event_type = evt.event_type

        if event_type == "message.created":
            data = evt.data
            message_id = data.get("message_id")
            if message_id:
                message_buffers[message_id] = []

        elif event_type == "message.updated":
            data = evt.data
            message_id = data.get("message_id")
            if message_id and message_id in message_buffers:
                contents = data.get("contents", [])
                for content in contents:
                    if content.get("kind") == "text":
                        text = content.get("text", "")
                        # Track text length
                        current_text = "".join(message_buffers[message_id])
                        if len(text) > len(current_text):
                            new_text = text[len(current_text):]
                            message_buffers[message_id].append(new_text)

        elif event_type == "message.completed":
            data = evt.data
            message_id = data.get("message_id")
            if message_id and message_id in message_buffers:
                del message_buffers[message_id]

    # Assert
    assert len(message_buffers) == 0  # All messages should be completed and removed


@pytest.mark.asyncio
async def test_stream_event_parsing_handles_complex_data(mock_client):
    """
    Test that stream events correctly parse complex nested data structures.
    """
    # Arrange
    mock_events = create_mock_events([
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [
                {"kind": "text", "text": "Hello"},
                {"kind": "image", "url": "https://example.com/image.png"}
            ],
            "metadata": {
                "model": "gpt-4",
                "tokens": 42
            }
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    events: List[StreamEvent] = []

    # Act
    async for evt in conversation.stream_events("Test"):
        events.append(evt)

    # Assert
    assert len(events) == 1
    event = events[0]
    assert event.event_type == "message.created"
    assert event.data["message_id"] == "msg_1"
    assert len(event.data["contents"]) == 2
    assert event.data["contents"][0]["kind"] == "text"
    assert event.data["contents"][1]["kind"] == "image"
    assert event.data["metadata"]["model"] == "gpt-4"
    assert event.data["metadata"]["tokens"] == 42


@pytest.mark.asyncio
async def test_stream_error_handling_with_malformed_event(mock_client):
    """
    Test error handling when stream contains malformed events.
    """
    # Arrange - Include an event with malformed data that will be caught by JSON parsing
    # The _stream_run method catches JSON errors and creates a {"raw": data_str} object
    async def mock_stream_raw(request):
        # Yield raw SSE strings that _stream_run will parse
        yield "event: message.delta"
        yield "data: {invalid json"
        yield ""
        yield "event: message.completed"
        yield 'data: {"message_id": "msg_1"}'
        yield ""

    mock_client.runs.create_and_stream = mock_stream_raw

    conversation = Conversation(mock_client, None)
    events: List[StreamEvent] = []

    # Act - Should handle error gracefully
    async for evt in conversation.stream_events("Test"):
        events.append(evt)

    # Assert - Should get the valid event at least
    assert len(events) >= 1
    assert any(evt.event_type == "message.completed" for evt in events)


@pytest.mark.asyncio
async def test_stream_partial_message_updates_track_content_changes(mock_client):
    """
    Test that partial message updates correctly track content changes.
    """
    # Arrange
    mock_events = create_mock_events([
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": []
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "The"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "The quick"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "The quick brown"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "The quick brown fox"}]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "The quick brown fox"}]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    all_texts: List[str] = []

    # Act
    async for message in conversation.stream_messages("Test"):
        contents = message.get("contents", [])
        for content in contents:
            if content.get("kind") == "text":
                text = content.get("text", "")
                if text:
                    all_texts.append(text)

    # Assert - Each update should have progressively more text
    assert len(all_texts) > 0
    assert all_texts[0] == "The"
    assert all_texts[-1] == "The quick brown fox"
    # Verify progression
    for i in range(len(all_texts) - 1):
        assert len(all_texts[i]) <= len(all_texts[i + 1])


@pytest.mark.asyncio
async def test_stream_thread_id_extraction_from_run_started(mock_client):
    """
    Test that thread_id is correctly extracted from run.started event.
    """
    # Arrange
    mock_events = create_mock_events([
        ("run.started", {
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "in_progress"
        }),
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [{"kind": "text", "text": "Hello"}]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    assert conversation.thread_id is None

    # Act
    async for _ in conversation.stream_messages("Test"):
        pass

    # Assert
    assert conversation.thread_id == "thread_456"


@pytest.mark.asyncio
async def test_stream_callback_mode_handles_empty_chunks(mock_client):
    """
    Test that callback mode gracefully handles empty or whitespace chunks.
    """
    # Arrange
    sse_lines = create_sse_response([
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": ""}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Hello"}]
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Hello"}]  # Same text, no new content
        }),
        ("message.delta", {
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Hello World"}]
        })
    ])

    async def mock_stream(request):
        for line in sse_lines:
            yield line

    mock_client.runs.create_and_stream = mock_stream

    received_chunks: List[str] = []

    # Act
    await mock_client.stream_chat(
        "Test",
        on_text_chunk=lambda text: received_chunks.append(text)
    )

    # Assert
    # Should only get non-empty new chunks
    assert "Hello" in received_chunks
    assert " World" in received_chunks
    full_text = "".join(received_chunks)
    assert full_text == "Hello World"


@pytest.mark.asyncio
async def test_stream_events_get_data_as_with_dataclass(mock_client):
    """
    Test that StreamEvent.get_data_as works correctly in streaming context.
    """
    from dataclasses import dataclass

    @dataclass
    class MessageData:
        message_id: str
        role: str

    # Arrange
    mock_events = create_mock_events([
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent"
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)

    # Act
    async for evt in conversation.stream_events("Test"):
        if evt.event_type == "message.created":
            # Test get_data_as with dataclass
            message_data = evt.get_data_as(MessageData)

            # Assert
            assert message_data is not None
            assert message_data.message_id == "msg_1"
            assert message_data.role == "agent"


@pytest.mark.asyncio
async def test_stream_multiple_content_types_in_message(mock_client):
    """
    Test streaming messages with multiple content types (text, image, etc.).
    """
    # Arrange
    mock_events = create_mock_events([
        ("message.created", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": []
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [
                {"kind": "text", "text": "Here's an image:"}
            ]
        }),
        ("message.updated", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [
                {"kind": "text", "text": "Here's an image:"},
                {"kind": "image", "url": "https://example.com/pic.jpg"}
            ]
        }),
        ("message.completed", {
            "message_id": "msg_1",
            "role": "agent",
            "contents": [
                {"kind": "text", "text": "Here's an image:"},
                {"kind": "image", "url": "https://example.com/pic.jpg"}
            ]
        })
    ])

    async def mock_stream(request):
        for evt in mock_events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    messages: List[Dict[str, Any]] = []

    # Act
    async for message in conversation.stream_messages("Show me something"):
        messages.append(message)

    # Assert
    assert len(messages) > 0
    # Last message should have both content types
    last_message = messages[-1]
    contents = last_message.get("contents", [])
    assert len(contents) == 2
    assert contents[0]["kind"] == "text"
    assert contents[1]["kind"] == "image"
    assert contents[1]["url"] == "https://example.com/pic.jpg"
