# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""In-memory state store implementation."""

from typing import Any, Optional
import asyncio

from ..core import IStateStore


class MemoryStateStore(IStateStore):
    """In-memory state store for development and testing."""

    def __init__(self) -> None:
        """Initialize the memory state store."""
        self._data: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def initialize_async(self) -> None:
        """Initialize the state store."""
        pass

    async def get_async(self, thread_id: str, key: str) -> Optional[Any]:
        """Get a value from thread state."""
        async with self._lock:
            thread_data = self._data.get(thread_id, {})
            return thread_data.get(key)

    async def set_async(
        self, thread_id: str, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """Set a value in thread state with optional TTL in seconds."""
        async with self._lock:
            if thread_id not in self._data:
                self._data[thread_id] = {}
            self._data[thread_id][key] = value
            # TODO: Implement TTL for memory store

    async def delete_async(self, thread_id: str, key: str) -> None:
        """Delete a value from thread state."""
        async with self._lock:
            if thread_id in self._data:
                self._data[thread_id].pop(key, None)

    async def get_all_async(self, thread_id: str) -> dict[str, Any]:
        """Get all state for a thread."""
        async with self._lock:
            return self._data.get(thread_id, {}).copy()

    async def clear_async(self, thread_id: str) -> None:
        """Clear all state for a thread."""
        async with self._lock:
            self._data.pop(thread_id, None)

    async def close_async(self) -> None:
        """Close connections and clean up resources."""
        self._data.clear()
