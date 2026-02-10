# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Client for Threads API operations"""

from typing import Dict, Any, List, Optional
import aiohttp

from .client_options import AgentProtocolClientOptions


class ThreadsClient:
    """
    Client for Threads API operations
    Handles conversation thread management
    """

    def __init__(self, session: aiohttp.ClientSession, options: AgentProtocolClientOptions):
        self._session = session
        self._options = options

    async def create(self, thread: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Creates a new conversation thread

        Args:
            thread: Optional thread configuration with metadata

        Returns:
            The created thread
        """
        async with self._session.post("/threads", json=thread or {}) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, thread_id: str) -> Dict[str, Any]:
        """
        Gets a specific thread by ID

        Args:
            thread_id: Thread identifier

        Returns:
            The thread details
        """
        async with self._session.get(f"/threads/{thread_id}") as response:
            response.raise_for_status()
            return await response.json()

    async def add_message(self, thread_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a message to a thread

        Args:
            thread_id: Thread identifier
            message: Message to add

        Returns:
            The added message
        """
        async with self._session.post(
            f"/threads/{thread_id}/messages", json=message
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_messages(
        self, thread_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Gets messages from a thread

        Args:
            thread_id: Thread identifier
            limit: Optional limit on number of messages to return

        Returns:
            List of messages
        """
        params = {"limit": limit} if limit else {}
        async with self._session.get(
            f"/threads/{thread_id}/messages", params=params
        ) as response:
            response.raise_for_status()
            return await response.json()
