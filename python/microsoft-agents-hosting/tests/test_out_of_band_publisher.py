# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for OutOfBandPublisher."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, Mock
from microsoft.agents.hosting.hosting.out_of_band_publisher import OutOfBandPublisher
from microsoft.agents.hosting.core import IQueueAdapter


class MockQueueAdapter(IQueueAdapter):
    """Mock queue adapter for testing."""

    def __init__(self):
        self.messages = []

    async def initialize_async(self) -> None:
        """Initialize the adapter."""
        pass

    async def enqueue_async(self, message: Any) -> None:
        """Enqueue a message."""
        self.messages.append(message)

    async def dequeue_async(self) -> Any:
        """Dequeue a message."""
        if self.messages:
            return self.messages.pop(0)
        return None

    async def close_async(self) -> None:
        """Close connections."""
        pass


def test_out_of_band_publisher_creation():
    """Test creating an OutOfBandPublisher."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)
    assert publisher is not None


def test_out_of_band_publisher_creation_without_adapter():
    """Test creating an OutOfBandPublisher without adapter."""
    publisher = OutOfBandPublisher(None)
    assert publisher is not None


@pytest.mark.asyncio
async def test_send_to_thread_async():
    """Test sending a message to a thread."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    await publisher.send_to_thread_async("thread_123", "Hello, World!")

    assert len(adapter.messages) == 1
    message = adapter.messages[0]
    assert message["thread_id"] == "thread_123"
    assert message["content"] == "Hello, World!"
    assert message["type"] == "out_of_band"
    assert message["metadata"] == {}


@pytest.mark.asyncio
async def test_send_to_thread_async_with_metadata():
    """Test sending a message with metadata."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    metadata = {"source": "test", "priority": "high"}
    await publisher.send_to_thread_async(
        "thread_456", "Important message", metadata=metadata
    )

    assert len(adapter.messages) == 1
    message = adapter.messages[0]
    assert message["thread_id"] == "thread_456"
    assert message["content"] == "Important message"
    assert message["metadata"] == metadata


@pytest.mark.asyncio
async def test_send_to_thread_async_without_adapter():
    """Test sending a message without queue adapter (should log warning)."""
    publisher = OutOfBandPublisher(None)

    # Should not raise an error, just log a warning
    await publisher.send_to_thread_async("thread_789", "Test message")

    # No exception should be raised
    assert True


@pytest.mark.asyncio
async def test_send_to_thread_async_without_adapter_with_metadata():
    """Test sending a message with metadata but no adapter."""
    publisher = OutOfBandPublisher(None)

    metadata = {"test": "data"}
    await publisher.send_to_thread_async(
        "thread_abc", "Test message", metadata=metadata
    )

    # Should complete without error
    assert True


@pytest.mark.asyncio
async def test_send_to_multiple_threads_async():
    """Test sending a message to multiple threads."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    thread_ids = ["thread_1", "thread_2", "thread_3"]
    await publisher.send_to_multiple_threads_async(thread_ids, "Broadcast message")

    assert len(adapter.messages) == 3
    for i, thread_id in enumerate(thread_ids):
        assert adapter.messages[i]["thread_id"] == thread_id
        assert adapter.messages[i]["content"] == "Broadcast message"


@pytest.mark.asyncio
async def test_send_to_multiple_threads_async_with_metadata():
    """Test sending a message to multiple threads with metadata."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    thread_ids = ["thread_a", "thread_b"]
    metadata = {"category": "notification"}
    await publisher.send_to_multiple_threads_async(
        thread_ids, "System alert", metadata=metadata
    )

    assert len(adapter.messages) == 2
    for message in adapter.messages:
        assert message["content"] == "System alert"
        assert message["metadata"] == metadata


@pytest.mark.asyncio
async def test_send_to_multiple_threads_async_empty_list():
    """Test sending to an empty list of threads."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    await publisher.send_to_multiple_threads_async([], "Message")

    assert len(adapter.messages) == 0


@pytest.mark.asyncio
async def test_send_to_multiple_threads_async_without_adapter():
    """Test sending to multiple threads without adapter."""
    publisher = OutOfBandPublisher(None)

    thread_ids = ["thread_1", "thread_2"]
    await publisher.send_to_multiple_threads_async(thread_ids, "Test message")

    # Should complete without error
    assert True


@pytest.mark.asyncio
async def test_multiple_sends_accumulate():
    """Test that multiple sends accumulate in the queue."""
    adapter = MockQueueAdapter()
    publisher = OutOfBandPublisher(adapter)

    await publisher.send_to_thread_async("thread_1", "Message 1")
    await publisher.send_to_thread_async("thread_2", "Message 2")
    await publisher.send_to_thread_async("thread_3", "Message 3")

    assert len(adapter.messages) == 3
    assert adapter.messages[0]["content"] == "Message 1"
    assert adapter.messages[1]["content"] == "Message 2"
    assert adapter.messages[2]["content"] == "Message 3"
