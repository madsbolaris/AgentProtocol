# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Client for Runs API operations"""

from typing import Dict, Any
import aiohttp

from .client_options import AgentProtocolClientOptions


class RunsClient:
    """
    Client for Runs API operations
    Handles creating and managing agent execution instances
    """

    def __init__(self, session: aiohttp.ClientSession, options: AgentProtocolClientOptions):
        self._session = session
        self._options = options

    async def create(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates and executes an agent run

        Args:
            run: Run configuration with input messages and agent settings

        Returns:
            The created run with status and output
        """
        async with self._session.post("/runs", json=run) as response:
            response.raise_for_status()
            return await response.json()

    async def create_and_wait(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an ephemeral run and waits for completion (blocking)

        Args:
            run: Run configuration

        Returns:
            The completed run response
        """
        async with self._session.post("/runs/wait", json=run) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, run_id: str) -> Dict[str, Any]:
        """
        Gets a specific run by ID

        Args:
            run_id: Run identifier

        Returns:
            The run details
        """
        async with self._session.get(f"/runs/{run_id}") as response:
            response.raise_for_status()
            return await response.json()

    async def wait(self, run_id: str) -> Dict[str, Any]:
        """
        Waits for an existing run to complete

        Args:
            run_id: Run identifier

        Returns:
            The completed run response
        """
        async with self._session.get(f"/runs/{run_id}/wait") as response:
            response.raise_for_status()
            return await response.json()
