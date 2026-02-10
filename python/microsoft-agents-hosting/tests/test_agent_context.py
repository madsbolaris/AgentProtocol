# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Comprehensive tests for AgentContext and ThreadState."""

import pytest
import logging
from microsoft.agents.hosting.core import (
    AgentContext,
    ThreadState,
    CancellationToken,
    IThreadState,
    IAgentContext,
)
from microsoft.agents.hosting.state import MemoryStateStore


@pytest.mark.asyncio
async def test_thread_state_creation():
    """Test ThreadState creation."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)
    assert state._thread_id == "thread1"
    assert state._state_store == store


@pytest.mark.asyncio
async def test_thread_state_get_set():
    """Test ThreadState get and set operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)

    await state.set_async("key1", "value1")
    result = await state.get_async("key1")
    assert result == "value1"


@pytest.mark.asyncio
async def test_thread_state_get_with_default():
    """Test ThreadState get with default value."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)

    result = await state.get_async("nonexistent", default="default_value")
    assert result == "default_value"


@pytest.mark.asyncio
async def test_thread_state_delete():
    """Test ThreadState delete operation."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)

    await state.set_async("key1", "value1")
    await state.delete_async("key1")

    result = await state.get_async("key1")
    assert result is None


@pytest.mark.asyncio
async def test_thread_state_get_all():
    """Test ThreadState get_all operation."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)

    await state.set_async("key1", "value1")
    await state.set_async("key2", "value2")

    all_state = await state.get_all_async()
    assert all_state == {"key1": "value1", "key2": "value2"}


@pytest.mark.asyncio
async def test_thread_state_clear():
    """Test ThreadState clear operation."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)

    await state.set_async("key1", "value1")
    await state.set_async("key2", "value2")
    await state.clear_async()

    all_state = await state.get_all_async()
    assert all_state == {}


@pytest.mark.asyncio
async def test_thread_state_implements_protocol():
    """Test that ThreadState implements IThreadState protocol."""
    store = MemoryStateStore()
    await store.initialize_async()

    state = ThreadState("thread1", store)
    assert isinstance(state, IThreadState)


@pytest.mark.asyncio
async def test_agent_context_creation():
    """Test AgentContext creation."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    context = AgentContext("run1", "thread1", store, logger)
    assert context.run_id == "run1"
    assert context.thread_id == "thread1"
    assert isinstance(context.state, IThreadState)


@pytest.mark.asyncio
async def test_agent_context_properties():
    """Test AgentContext properties."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    context = AgentContext("run1", "thread1", store, logger)

    assert context.run_id == "run1"
    assert context.thread_id == "thread1"
    assert context.state is not None


@pytest.mark.asyncio
async def test_agent_context_respond_async():
    """Test AgentContext respond_async method."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")
    responses = []

    async def response_callback(content: str):
        responses.append(content)

    context = AgentContext("run1", "thread1", store, logger, response_callback)

    await context.respond_async("Hello, World!")

    assert len(context._responses) == 1
    assert context._responses[0] == "Hello, World!"
    assert len(responses) == 1
    assert responses[0] == "Hello, World!"


@pytest.mark.asyncio
async def test_agent_context_respond_multiple():
    """Test multiple responses."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")
    responses = []

    async def response_callback(content: str):
        responses.append(content)

    context = AgentContext("run1", "thread1", store, logger, response_callback)

    await context.respond_async("Message 1")
    await context.respond_async("Message 2")
    await context.respond_async("Message 3")

    assert len(context._responses) == 3
    assert len(responses) == 3
    assert responses == ["Message 1", "Message 2", "Message 3"]


@pytest.mark.asyncio
async def test_agent_context_respond_without_callback():
    """Test responding without a callback."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    context = AgentContext("run1", "thread1", store, logger, None)

    # Should not raise an exception
    await context.respond_async("Hello!")

    assert len(context._responses) == 1


@pytest.mark.asyncio
async def test_agent_context_respond_with_cancellation():
    """Test responding with cancellation token."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    context = AgentContext("run1", "thread1", store, logger)

    # Create cancelled token
    token = CancellationToken()
    token.cancel()

    # Should not add response when cancelled
    await context.respond_async("Hello!", cancellation_token=token)

    assert len(context._responses) == 0


@pytest.mark.asyncio
async def test_agent_context_log_async(caplog):
    """Test AgentContext log_async method."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    with caplog.at_level(logging.INFO):
        await context.log_async("Test log message", level="INFO")

    assert "Test log message" in caplog.text


@pytest.mark.asyncio
async def test_agent_context_log_levels(caplog):
    """Test different log levels."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")
    context = AgentContext("run1", "thread1", store, logger)

    with caplog.at_level(logging.DEBUG):
        await context.log_async("Debug message", level="DEBUG")
        await context.log_async("Info message", level="INFO")
        await context.log_async("Warning message", level="WARNING")
        await context.log_async("Error message", level="ERROR")

    log_text = caplog.text
    assert "Debug message" in log_text
    assert "Info message" in log_text
    assert "Warning message" in log_text
    assert "Error message" in log_text


@pytest.mark.asyncio
async def test_agent_context_log_with_cancellation():
    """Test logging with cancellation token."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    # Create cancelled token
    token = CancellationToken()
    token.cancel()

    # Should not log when cancelled
    await context.log_async("Should not appear", level="INFO", cancellation_token=token)


@pytest.mark.asyncio
async def test_agent_context_pause_for_approval():
    """Test pause_for_approval_async method."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    # Should not raise an exception (though not fully implemented)
    await context.pause_for_approval_async("Approve this action")


@pytest.mark.asyncio
async def test_agent_context_pause_with_metadata():
    """Test pause_for_approval_async with metadata."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    metadata = {"action": "delete", "resource": "file.txt"}

    # Should not raise an exception
    await context.pause_for_approval_async("Approve deletion", metadata=metadata)


@pytest.mark.asyncio
async def test_agent_context_pause_with_cancellation():
    """Test pause with cancellation token."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    # Create cancelled token
    token = CancellationToken()
    token.cancel()

    # Should not pause when cancelled
    await context.pause_for_approval_async(
        "Should not pause",
        cancellation_token=token
    )


@pytest.mark.asyncio
async def test_agent_context_state_integration():
    """Test AgentContext state integration with ThreadState."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)

    # Set state through context
    await context.state.set_async("counter", 0)

    # Get state
    result = await context.state.get_async("counter")
    assert result == 0

    # Update state
    await context.state.set_async("counter", 1)
    result = await context.state.get_async("counter")
    assert result == 1


@pytest.mark.asyncio
async def test_agent_context_implements_protocol():
    """Test that AgentContext implements IAgentContext protocol."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context = AgentContext("run1", "thread1", store, logger)
    assert isinstance(context, IAgentContext)


@pytest.mark.asyncio
async def test_cancellation_token():
    """Test CancellationToken functionality."""
    token = CancellationToken()

    assert not token.is_cancelled()

    token.cancel()

    assert token.is_cancelled()


@pytest.mark.asyncio
async def test_multiple_contexts_same_thread():
    """Test multiple contexts sharing the same thread state."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context1 = AgentContext("run1", "thread1", store, logger)
    context2 = AgentContext("run2", "thread1", store, logger)

    # Set state in context1
    await context1.state.set_async("shared_key", "shared_value")

    # Get state from context2 (same thread)
    result = await context2.state.get_async("shared_key")
    assert result == "shared_value"


@pytest.mark.asyncio
async def test_multiple_contexts_different_threads():
    """Test multiple contexts with different threads have isolated state."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_logger")

    context1 = AgentContext("run1", "thread1", store, logger)
    context2 = AgentContext("run2", "thread2", store, logger)

    # Set state in context1
    await context1.state.set_async("key", "value1")

    # Set different state in context2
    await context2.state.set_async("key", "value2")

    # Verify isolation
    result1 = await context1.state.get_async("key")
    result2 = await context2.state.get_async("key")

    assert result1 == "value1"
    assert result2 == "value2"
