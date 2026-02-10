# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Client for Agents API operations"""

from typing import Dict, Any
import aiohttp

from .client_options import AgentProtocolClientOptions


class AgentsClient:
    """
    Client for Agents API operations
    Handles agent discovery and metadata retrieval
    """

    def __init__(self, session: aiohttp.ClientSession, options: AgentProtocolClientOptions):
        self._session = session
        self._options = options

    async def get_card(self, agent_id: str) -> Dict[str, Any]:
        """
        Gets an agent's capability card

        Args:
            agent_id: Agent identifier

        Returns:
            The agent card with capabilities and tools
        """
        async with self._session.get(f"/agents/{agent_id}/card") as response:
            response.raise_for_status()
            return await response.json()

    async def inspect(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects an agent's capabilities with optional context

        Args:
            payload: Inspection request with optional context

        Returns:
            Detailed agent capabilities
        """
        async with self._session.post("/agents/inspect", json=payload) as response:
            response.raise_for_status()
            return await response.json()
