# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Main Agent Protocol client"""

from typing import Optional
import aiohttp

from .client_options import AgentProtocolClientOptions
from .runs_client import RunsClient
from .threads_client import ThreadsClient
from .agents_client import AgentsClient


class AgentProtocolClient:
    """
    Main client for interacting with Agent Protocol APIs
    Provides access to Agents, Runs, and Threads operations
    """

    def __init__(self, options_or_url: AgentProtocolClientOptions | str):
        """
        Creates a new instance of the Agent Protocol client

        Args:
            options_or_url: Client configuration options or base URL string
        """
        # Support passing a URL string directly for convenience (as shown in quickstart)
        if isinstance(options_or_url, str):
            self._options = AgentProtocolClientOptions(base_url=options_or_url)
        else:
            self._options = options_or_url

        self._own_session = self._options.session is None

        if self._options.session:
            self._session = self._options.session
        else:
            timeout = aiohttp.ClientTimeout(total=self._options.timeout_seconds)
            headers = {"Accept": "application/json"}

            if self._options.api_key:
                headers["Authorization"] = f"Bearer {self._options.api_key}"

            self._session = aiohttp.ClientSession(
                base_url=self._options.base_url, timeout=timeout, headers=headers
            )

        # Initialize API clients
        self.runs = RunsClient(self._session, self._options)
        self.threads = ThreadsClient(self._session, self._options)
        self.agents = AgentsClient(self._session, self._options)

    @classmethod
    def from_url(cls, base_url: str, api_key: Optional[str] = None):
        """
        Creates a new instance with just a base URL

        Args:
            base_url: Base URL for the Agent Protocol API
            api_key: Optional API key for authentication
        """
        return cls(AgentProtocolClientOptions(base_url=base_url, api_key=api_key))

    async def close(self):
        """Closes the client and releases resources"""
        if self._own_session and self._session:
            await self._session.close()

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
