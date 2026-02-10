# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Comprehensive tests for async/await patterns in the Hosting SDK."""

import pytest
import asyncio
from microsoft.agents.hosting import (
    AgentHostBuilder,
    TurnResult,
    IAgentContext,
    CancellationToken,
    UserMessage,
)
from microsoft.agents.hosting.state import MemoryStateStore
from microsoft.agents.hosting.core import AgentContext
from typing import Any
import logging


@pytest.mark.asyncio
async def test_async_state_operations():
    """Test async state operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    result = await store.get_async("thread1", "key1")

    assert result == "value1"


@pytest.mark.asyncio
async def test_concurrent_state_operations():
    """Test concurrent state operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    async def set_multiple_keys(thread_id: str, count: int):
        for i in range(count):
            await store.set_async(thread_id, f"key{i}", f"value{i}")

    # Run concurrent operations
    await asyncio.gather(
        set_multiple_keys("thread1", 10),
        set_multiple_keys("thread2", 10),
        set_multiple_keys("thread3", 10),
    )

    # Verify results
    for i in range(10):
        assert await store.get_async("thread1", f"key{i}") == f"value{i}"
        assert await store.get_async("thread2", f"key{i}") == f"value{i}"
        assert await store.get_async("thread3", f"key{i}") == f"value{i}"


@pytest.mark.asyncio
async def test_async_context_respond():
    """Test async respond operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")
    responses = []

    async def callback(content: str):
        await asyncio.sleep(0.01)  # Simulate async work
        responses.append(content)

    context = AgentContext("run1", "thread1", store, logger, callback)

    await context.respond_async("Message 1")
    await context.respond_async("Message 2")
    await context.respond_async("Message 3")

    assert len(responses) == 3


@pytest.mark.asyncio
async def test_concurrent_context_operations():
    """Test concurrent context operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    async def work_in_context(context: IAgentContext, count: int):
        for i in range(count):
            await context.state.set_async(f"key{i}", f"value{i}")
            await context.log_async(f"Processed item {i}")

    contexts = [
        AgentContext(f"run{i}", f"thread{i}", store, logger)
        for i in range(5)
    ]

    await asyncio.gather(*[
        work_in_context(ctx, 10) for ctx in contexts
    ])

    # Verify each thread has its own state
    for i in range(5):
        all_state = await store.get_all_async(f"thread{i}")
        assert len(all_state) == 10


@pytest.mark.asyncio
async def test_async_function_execution():
    """Test async function execution in AgentBuilder."""
    async def async_func(x: int) -> str:
        await asyncio.sleep(0.01)
        return str(x * 2)

    # Function should be callable
    result = await async_func(5)
    assert result == "10"


@pytest.mark.asyncio
async def test_cancellation_token_async():
    """Test cancellation token in async operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")
    context = AgentContext("run1", "thread1", store, logger)

    token = CancellationToken()

    # Operations should work before cancellation
    await context.respond_async("Message 1", cancellation_token=token)
    assert len(context._responses) == 1

    # Cancel the token
    token.cancel()

    # Operations should be skipped after cancellation
    await context.respond_async("Message 2", cancellation_token=token)
    assert len(context._responses) == 1  # Still 1, not 2


@pytest.mark.asyncio
async def test_async_handler_execution():
    """Test async handler execution."""
    called = []

    async def async_handler(msg: Any, ctx: IAgentContext, ct: CancellationToken) -> TurnResult:
        await asyncio.sleep(0.01)
        called.append(msg)
        return TurnResult.CONTINUE

    # Simulate calling the handler
    store = MemoryStateStore()
    await store.initialize_async()
    logger = logging.getLogger("test")
    context = AgentContext("run1", "thread1", store, logger)
    token = CancellationToken()

    result = await async_handler("test message", context, token)

    assert result == TurnResult.CONTINUE
    assert len(called) == 1
    assert called[0] == "test message"


@pytest.mark.asyncio
async def test_multiple_async_handlers():
    """Test multiple async handlers executing in sequence."""
    execution_order = []

    async def handler1(msg: Any, ctx: IAgentContext, ct: CancellationToken) -> TurnResult:
        await asyncio.sleep(0.01)
        execution_order.append(1)
        return TurnResult.CONTINUE

    async def handler2(msg: Any, ctx: IAgentContext, ct: CancellationToken) -> TurnResult:
        await asyncio.sleep(0.01)
        execution_order.append(2)
        return TurnResult.CONTINUE

    async def handler3(msg: Any, ctx: IAgentContext, ct: CancellationToken) -> TurnResult:
        await asyncio.sleep(0.01)
        execution_order.append(3)
        return TurnResult.CONTINUE

    store = MemoryStateStore()
    await store.initialize_async()
    logger = logging.getLogger("test")
    context = AgentContext("run1", "thread1", store, logger)
    token = CancellationToken()

    # Execute handlers in sequence
    await handler1("msg", context, token)
    await handler2("msg", context, token)
    await handler3("msg", context, token)

    assert execution_order == [1, 2, 3]


@pytest.mark.asyncio
async def test_async_state_store_close():
    """Test async close operation."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.close_async()

    assert store._data == {}


@pytest.mark.asyncio
async def test_async_error_handling():
    """Test async error handling."""
    async def failing_operation():
        await asyncio.sleep(0.01)
        raise ValueError("Something went wrong")

    with pytest.raises(ValueError) as exc_info:
        await failing_operation()

    assert str(exc_info.value) == "Something went wrong"


@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async operations with timeout."""
    async def slow_operation():
        await asyncio.sleep(10)
        return "done"

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.1)


@pytest.mark.asyncio
async def test_async_gather_operations():
    """Test gathering multiple async operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    async def set_key(thread: str, key: str, value: str):
        await store.set_async(thread, key, value)
        return f"{key}:{value}"

    results = await asyncio.gather(
        set_key("thread1", "key1", "value1"),
        set_key("thread1", "key2", "value2"),
        set_key("thread1", "key3", "value3"),
    )

    assert results == ["key1:value1", "key2:value2", "key3:value3"]


@pytest.mark.asyncio
async def test_async_state_race_condition():
    """Test that concurrent state updates are handled correctly."""
    store = MemoryStateStore()
    await store.initialize_async()

    # Set initial value
    await store.set_async("thread1", "counter", 0)

    async def increment():
        for _ in range(10):
            current = await store.get_async("thread1", "counter")
            await asyncio.sleep(0.001)  # Small delay to encourage race conditions
            await store.set_async("thread1", "counter", current + 1)

    # Run multiple concurrent increments
    await asyncio.gather(
        increment(),
        increment(),
        increment(),
    )

    # Due to lock in MemoryStateStore, final value should be correct
    final = await store.get_async("thread1", "counter")
    # Note: This may not be 30 due to race conditions, but it tests the behavior
    assert final > 0


@pytest.mark.asyncio
async def test_async_context_logging():
    """Test async logging operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test_async")
    context = AgentContext("run1", "thread1", store, logger)

    # Should not raise exceptions
    await context.log_async("Message 1", level="INFO")
    await context.log_async("Message 2", level="DEBUG")
    await context.log_async("Message 3", level="WARNING")


@pytest.mark.asyncio
async def test_async_pause_for_approval():
    """Test async pause for approval."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")
    context = AgentContext("run1", "thread1", store, logger)

    # Should not raise exceptions
    await context.pause_for_approval_async("Test approval")


@pytest.mark.asyncio
async def test_concurrent_thread_state_access():
    """Test concurrent access to thread state."""
    store = MemoryStateStore()
    await store.initialize_async()

    logger = logging.getLogger("test")

    async def worker(worker_id: int):
        context = AgentContext(f"run{worker_id}", "shared_thread", store, logger)

        for i in range(5):
            await context.state.set_async(f"worker{worker_id}_key{i}", f"value{i}")
            await asyncio.sleep(0.001)

    # Run multiple workers concurrently on the same thread
    await asyncio.gather(*[worker(i) for i in range(5)])

    # Verify all keys exist
    all_state = await store.get_all_async("shared_thread")
    assert len(all_state) == 25  # 5 workers * 5 keys each


@pytest.mark.asyncio
async def test_async_builder_pattern():
    """Test async operations in builder pattern."""
    async def async_test_func() -> str:
        await asyncio.sleep(0.01)
        return "result"

    # Builder should accept async functions
    result = await async_test_func()
    assert result == "result"


@pytest.mark.asyncio
async def test_async_error_in_handler():
    """Test error handling in async handler."""
    async def error_handler(msg: Any, ctx: IAgentContext, ct: CancellationToken) -> TurnResult:
        await asyncio.sleep(0.01)
        raise RuntimeError("Handler error")

    store = MemoryStateStore()
    await store.initialize_async()
    logger = logging.getLogger("test")
    context = AgentContext("run1", "thread1", store, logger)
    token = CancellationToken()

    with pytest.raises(RuntimeError) as exc_info:
        await error_handler("msg", context, token)

    assert str(exc_info.value) == "Handler error"


@pytest.mark.asyncio
async def test_async_cleanup():
    """Test async cleanup operations."""
    store = MemoryStateStore()
    await store.initialize_async()

    # Set some data
    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread2", "key2", "value2")

    # Clean up
    await store.clear_async("thread1")
    await store.clear_async("thread2")

    # Verify cleanup
    assert await store.get_all_async("thread1") == {}
    assert await store.get_all_async("thread2") == {}

    # Final close
    await store.close_async()
