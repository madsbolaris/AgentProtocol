# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Agent context implementation."""

import logging
from typing import Any, Optional

from .types import IAgentContext, IThreadState, IStateStore, CancellationToken


class ThreadState(IThreadState):
    """Thread state implementation."""

    def __init__(self, thread_id: str, state_store: IStateStore):
        self._thread_id = thread_id
        self._state_store = state_store

    async def get_async(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        value = await self._state_store.get_async(self._thread_id, key)
        return value if value is not None else default

    async def set_async(self, key: str, value: Any) -> None:
        """Set a state value."""
        await self._state_store.set_async(self._thread_id, key, value)

    async def delete_async(self, key: str) -> None:
        """Delete a state value."""
        await self._state_store.delete_async(self._thread_id, key)

    async def get_all_async(self) -> dict[str, Any]:
        """Get all state."""
        return await self._state_store.get_all_async(self._thread_id)

    async def clear_async(self) -> None:
        """Clear all state."""
        await self._state_store.clear_async(self._thread_id)


class AgentContext(IAgentContext):
    """Agent context implementation."""

    def __init__(
        self,
        run_id: str,
        thread_id: str,
        state_store: IStateStore,
        logger: logging.Logger,
        response_callback: Any = None,
    ):
        self._run_id = run_id
        self._thread_id = thread_id
        self._state = ThreadState(thread_id, state_store)
        self._logger = logger
        self._response_callback = response_callback
        self._responses: list[str] = []

    @property
    def run_id(self) -> str:
        """Gets the current run ID."""
        return self._run_id

    @property
    def thread_id(self) -> str:
        """Gets the current thread ID."""
        return self._thread_id

    @property
    def state(self) -> IThreadState:
        """Gets the state manager for this thread."""
        return self._state

    async def respond_async(
        self, content: str, cancellation_token: Optional[CancellationToken] = None
    ) -> None:
        """Send a response message to the user."""
        if cancellation_token and cancellation_token.is_cancelled():
            return

        self._responses.append(content)
        if self._response_callback:
            await self._response_callback(content)

    async def log_async(
        self,
        message: str,
        level: str = "INFO",
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """Log a message for debugging/observability."""
        if cancellation_token and cancellation_token.is_cancelled():
            return

        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.log(log_level, message, extra={"thread_id": self._thread_id, "run_id": self._run_id})

    async def pause_for_approval_async(
        self,
        summary: str,
        metadata: Optional[dict[str, Any]] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """Pause the run and wait for approval before continuing."""
        if cancellation_token and cancellation_token.is_cancelled():
            return

        # TODO: Implement pause mechanism
        await self.log_async(
            f"Pausing for approval: {summary}",
            level="INFO",
            cancellation_token=cancellation_token,
        )
