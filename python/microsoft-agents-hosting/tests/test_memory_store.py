# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Comprehensive tests for MemoryStateStore."""

import pytest
from microsoft.agents.hosting.state import MemoryStateStore


@pytest.mark.asyncio
async def test_memory_store_initialization():
    """Test MemoryStateStore initialization."""
    store = MemoryStateStore()
    await store.initialize_async()
    assert store._data == {}


@pytest.mark.asyncio
async def test_memory_store_get_nonexistent():
    """Test getting a non-existent key."""
    store = MemoryStateStore()
    await store.initialize_async()

    result = await store.get_async("thread1", "key1")
    assert result is None


@pytest.mark.asyncio
async def test_memory_store_set_and_get():
    """Test setting and getting a value."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    result = await store.get_async("thread1", "key1")
    assert result == "value1"


@pytest.mark.asyncio
async def test_memory_store_set_multiple_keys():
    """Test setting multiple keys in the same thread."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread1", "key2", "value2")

    assert await store.get_async("thread1", "key1") == "value1"
    assert await store.get_async("thread1", "key2") == "value2"


@pytest.mark.asyncio
async def test_memory_store_multiple_threads():
    """Test storing data across multiple threads."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread2", "key1", "value2")

    assert await store.get_async("thread1", "key1") == "value1"
    assert await store.get_async("thread2", "key1") == "value2"


@pytest.mark.asyncio
async def test_memory_store_overwrite_value():
    """Test overwriting an existing value."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread1", "key1", "value2")

    result = await store.get_async("thread1", "key1")
    assert result == "value2"


@pytest.mark.asyncio
async def test_memory_store_delete():
    """Test deleting a value."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.delete_async("thread1", "key1")

    result = await store.get_async("thread1", "key1")
    assert result is None


@pytest.mark.asyncio
async def test_memory_store_delete_nonexistent():
    """Test deleting a non-existent key doesn't raise an error."""
    store = MemoryStateStore()
    await store.initialize_async()

    # Should not raise an exception
    await store.delete_async("thread1", "key1")


@pytest.mark.asyncio
async def test_memory_store_get_all_empty():
    """Test getting all state from an empty thread."""
    store = MemoryStateStore()
    await store.initialize_async()

    result = await store.get_all_async("thread1")
    assert result == {}


@pytest.mark.asyncio
async def test_memory_store_get_all():
    """Test getting all state from a thread."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread1", "key2", "value2")
    await store.set_async("thread1", "key3", "value3")

    result = await store.get_all_async("thread1")
    assert result == {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }


@pytest.mark.asyncio
async def test_memory_store_get_all_isolation():
    """Test that get_all returns a copy, not the internal dict."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")

    result1 = await store.get_all_async("thread1")
    result1["key2"] = "value2"  # Modify returned dict

    result2 = await store.get_all_async("thread1")
    assert "key2" not in result2


@pytest.mark.asyncio
async def test_memory_store_clear():
    """Test clearing all state for a thread."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread1", "key2", "value2")

    await store.clear_async("thread1")

    result = await store.get_all_async("thread1")
    assert result == {}


@pytest.mark.asyncio
async def test_memory_store_clear_nonexistent():
    """Test clearing a non-existent thread doesn't raise an error."""
    store = MemoryStateStore()
    await store.initialize_async()

    # Should not raise an exception
    await store.clear_async("thread1")


@pytest.mark.asyncio
async def test_memory_store_clear_isolation():
    """Test that clearing one thread doesn't affect others."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.set_async("thread2", "key1", "value2")

    await store.clear_async("thread1")

    assert await store.get_async("thread1", "key1") is None
    assert await store.get_async("thread2", "key1") == "value2"


@pytest.mark.asyncio
async def test_memory_store_close():
    """Test closing the store."""
    store = MemoryStateStore()
    await store.initialize_async()

    await store.set_async("thread1", "key1", "value1")
    await store.close_async()

    # After close, data should be cleared
    assert store._data == {}


@pytest.mark.asyncio
async def test_memory_store_various_types():
    """Test storing various Python types."""
    store = MemoryStateStore()
    await store.initialize_async()

    test_values = {
        "string": "test",
        "int": 42,
        "float": 3.14,
        "bool": True,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "none": None,
    }

    for key, value in test_values.items():
        await store.set_async("thread1", key, value)

    for key, expected_value in test_values.items():
        result = await store.get_async("thread1", key)
        assert result == expected_value


@pytest.mark.asyncio
async def test_memory_store_thread_safety():
    """Test concurrent access to the store."""
    import asyncio

    store = MemoryStateStore()
    await store.initialize_async()

    # Create multiple concurrent set operations
    async def set_values(thread_id: str, count: int):
        for i in range(count):
            await store.set_async(thread_id, f"key{i}", f"value{i}")

    # Run multiple threads concurrently
    await asyncio.gather(
        set_values("thread1", 10),
        set_values("thread2", 10),
        set_values("thread3", 10),
    )

    # Verify all values were set correctly
    for thread_num in range(1, 4):
        thread_id = f"thread{thread_num}"
        for i in range(10):
            result = await store.get_async(thread_id, f"key{i}")
            assert result == f"value{i}"


@pytest.mark.asyncio
async def test_memory_store_set_with_ttl():
    """Test set with TTL parameter (even though not implemented)."""
    store = MemoryStateStore()
    await store.initialize_async()

    # TTL is accepted but not implemented in memory store
    await store.set_async("thread1", "key1", "value1", ttl=60)

    result = await store.get_async("thread1", "key1")
    assert result == "value1"
