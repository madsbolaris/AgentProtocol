# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for Conversation"""

import pytest
from unittest.mock import AsyncMock, patch
from microsoft.agents.protocol.client import SimplifiedClient
from microsoft.agents.protocol.client.conversation import Conversation
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions


@pytest.fixture
def mock_client():
    """Creates a mock simplified client"""
    with patch("microsoft.agents.protocol.client.agent_protocol_client.aiohttp"):
        options = AgentProtocolClientOptions(base_url="http://localhost:5000")
        return SimplifiedClient(options)


@pytest.mark.asyncio
async def test_conversation_send_first_message(mock_client):
    """Test sending the first message in a conversation"""
    mock_client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Hello! How can I help?"}],
                }
            ],
        }
    )

    conversation = Conversation(mock_client, None)
    assert conversation.thread_id is None

    result = await conversation.send("Hello")

    assert result == "Hello! How can I help?"
    assert conversation.thread_id == "thread_456"


@pytest.mark.asyncio
async def test_conversation_send_subsequent_message(mock_client):
    """Test sending a message with existing thread"""
    mock_client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Response 2"}],
                }
            ],
        }
    )

    conversation = Conversation(mock_client, "thread_456")
    result = await conversation.send("Follow-up question")

    assert result == "Response 2"
    assert conversation.thread_id == "thread_456"


@pytest.mark.asyncio
async def test_conversation_send_no_output(mock_client):
    """Test sending when response has no output"""
    mock_client.runs.create_and_wait = AsyncMock(
        return_value={
            "run_id": "run_123",
            "thread_id": "thread_456",
            "status": "completed",
            "output": [],
        }
    )

    conversation = Conversation(mock_client, None)
    result = await conversation.send("Test")

    assert result == ""


@pytest.mark.asyncio
async def test_conversation_send_structured(mock_client):
    """Test sending a structured message"""
    mock_client.runs.create_and_wait = AsyncMock(
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

    conversation = Conversation(mock_client, None)
    message = {"role": "user", "contents": [{"kind": "text", "text": "Test"}]}

    result = await conversation.send_structured(message)

    assert result["role"] == "agent"
    assert result["message_id"] == "msg_789"
    assert conversation.thread_id == "thread_456"


@pytest.mark.asyncio
async def test_conversation_stream_messages(mock_client):
    """Test streaming messages from conversation"""

    async def mock_stream(request):
        events = [
            {
                "event_type": "run.started",
                "data": {"run_id": "run_123", "thread_id": "thread_456"},
            },
            {
                "event_type": "message.created",
                "data": {
                    "message_id": "msg_1",
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Hello"}],
                },
            },
            {
                "event_type": "message.delta",
                "data": {
                    "message_id": "msg_1",
                    "role": "agent",
                    "contents": [{"kind": "text", "text": "Hello world"}],
                },
            },
        ]
        for evt in events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    messages = []

    async for msg in conversation.stream_messages("Test"):
        messages.append(msg)

    assert len(messages) == 2
    assert messages[0]["message_id"] == "msg_1"
    assert messages[1]["message_id"] == "msg_1"
    assert conversation.thread_id == "thread_456"


@pytest.mark.asyncio
async def test_conversation_stream_events(mock_client):
    """Test streaming raw events from conversation"""

    async def mock_stream(request):
        events = [
            {
                "event_type": "run.started",
                "data": {"run_id": "run_123", "thread_id": "thread_456"},
            },
            {
                "event_type": "message.created",
                "data": {"message_id": "msg_1", "role": "agent"},
            },
        ]
        for evt in events:
            yield evt

    mock_client._stream_run = mock_stream

    conversation = Conversation(mock_client, None)
    events = []

    async for evt in conversation.stream_events("Test"):
        events.append(evt)

    assert len(events) == 2
    assert events[0].event_type == "run.started"
    assert events[1].event_type == "message.created"
    assert conversation.thread_id == "thread_456"


def test_conversation_thread_id_property(mock_client):
    """Test thread_id property"""
    conversation = Conversation(mock_client, "thread_123")
    assert conversation.thread_id == "thread_123"

    conversation_new = Conversation(mock_client, None)
    assert conversation_new.thread_id is None


@pytest.mark.asyncio
async def test_get_messages_with_thread_id_returns_messages(mock_client):
    """Test get_messages returns messages when thread_id exists"""
    mock_client.threads.get_messages = AsyncMock(
        return_value=[
            {"message_id": "msg-1", "role": "user", "contents": [{"kind": "text", "text": "Hello"}]},
            {"message_id": "msg-2", "role": "agent", "contents": [{"kind": "text", "text": "Hi there!"}]},
        ]
    )

    conversation = Conversation(mock_client, "thread_123")
    messages = await conversation.get_messages()

    assert messages is not None
    assert len(messages) == 2
    assert messages[0]["message_id"] == "msg-1"
    assert messages[1]["message_id"] == "msg-2"
    mock_client.threads.get_messages.assert_called_once_with(thread_id="thread_123", limit=None, after=None)


@pytest.mark.asyncio
async def test_get_messages_without_thread_id_raises_error(mock_client):
    """Test get_messages raises ValueError when no thread_id"""
    conversation = Conversation(mock_client, None)

    with pytest.raises(ValueError) as exc_info:
        await conversation.get_messages()

    assert "No thread ID available" in str(exc_info.value)
    assert "Send a message" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_messages_with_limit_parameter(mock_client):
    """Test get_messages passes limit parameter correctly"""
    mock_client.threads.get_messages = AsyncMock(return_value=[])
    conversation = Conversation(mock_client, "thread_123")

    await conversation.get_messages(limit=10)

    mock_client.threads.get_messages.assert_called_once_with(thread_id="thread_123", limit=10, after=None)


@pytest.mark.asyncio
async def test_get_messages_with_after_parameter(mock_client):
    """Test get_messages passes after parameter correctly"""
    mock_client.threads.get_messages = AsyncMock(return_value=[])
    conversation = Conversation(mock_client, "thread_123")

    await conversation.get_messages(after="msg-5")

    mock_client.threads.get_messages.assert_called_once_with(thread_id="thread_123", limit=None, after="msg-5")


@pytest.mark.asyncio
async def test_get_messages_empty_thread_returns_empty_list(mock_client):
    """Test get_messages returns empty list for empty thread"""
    mock_client.threads.get_messages = AsyncMock(return_value=[])
    conversation = Conversation(mock_client, "thread_123")

    messages = await conversation.get_messages()

    assert messages is not None
    assert len(messages) == 0
