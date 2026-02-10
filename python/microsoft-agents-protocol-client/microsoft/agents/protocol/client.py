# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Agent Protocol Client

Provides a high-level client for interacting with Agent Protocol APIs.
"""

from typing import Any, Dict, List, Optional
import httpx
from dataclasses import dataclass


@dataclass
class AgentProtocolClientOptions:
    """Configuration options for the Agent Protocol client."""

    base_url: str
    """Base URL for the Agent Protocol API"""

    api_key: Optional[str] = None
    """Optional API key for authentication"""

    timeout: float = 30.0
    """Request timeout in seconds"""

    http_client: Optional[httpx.AsyncClient] = None
    """Optional custom HTTP client"""


class RunsClient:
    """Client for Run operations."""

    def __init__(self, http_client: httpx.AsyncClient, options: AgentProtocolClientOptions):
        self._http = http_client
        self._options = options

    async def create(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and execute a new run.

        Args:
            run_data: Run configuration including agent, input messages, and options

        Returns:
            Run response with runId, status, and output
        """
        response = await self._http.post("/runs", json=run_data)
        response.raise_for_status()
        return response.json()

    async def create_and_wait(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a run and wait for completion.

        Args:
            run_data: Run configuration

        Returns:
            Completed run response
        """
        response = await self._http.post("/runs/wait", json=run_data)
        response.raise_for_status()
        return response.json()

    async def create_and_stream(self, run_data: Dict[str, Any]):
        """
        Create a run and stream results via Server-Sent Events.

        Args:
            run_data: Run configuration

        Yields:
            Server-Sent Events as they arrive
        """
        async with self._http.stream("POST", "/runs/stream", json=run_data) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]  # Remove "data: " prefix

    async def get(self, run_id: str) -> Dict[str, Any]:
        """
        Get run status and details.

        Args:
            run_id: Run identifier

        Returns:
            Run details
        """
        response = await self._http.get(f"/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    async def stream(self, run_id: str):
        """
        Stream an existing run's results.

        Args:
            run_id: Run identifier

        Yields:
            Server-Sent Events
        """
        async with self._http.stream("GET", f"/runs/{run_id}/stream") as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]


class ThreadsClient:
    """Client for Thread operations."""

    def __init__(self, http_client: httpx.AsyncClient, options: AgentProtocolClientOptions):
        self._http = http_client
        self._options = options

    async def create(self, thread_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new conversation thread.

        Args:
            thread_data: Optional thread configuration

        Returns:
            Thread response with threadId
        """
        response = await self._http.post("/threads", json=thread_data or {})
        response.raise_for_status()
        return response.json()

    async def get(self, thread_id: str) -> Dict[str, Any]:
        """
        Get thread details.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread details
        """
        response = await self._http.get(f"/threads/{thread_id}")
        response.raise_for_status()
        return response.json()

    async def delete(self, thread_id: str) -> None:
        """
        Delete a thread.

        Args:
            thread_id: Thread identifier
        """
        response = await self._http.delete(f"/threads/{thread_id}")
        response.raise_for_status()

    async def create_run(self, thread_id: str, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a run within an existing thread.

        Args:
            thread_id: Thread identifier
            run_data: Run configuration

        Returns:
            Run response
        """
        response = await self._http.post(f"/threads/{thread_id}/runs", json=run_data)
        response.raise_for_status()
        return response.json()


class MessagesClient:
    """Client for Message operations."""

    def __init__(self, http_client: httpx.AsyncClient, options: AgentProtocolClientOptions):
        self._http = http_client
        self._options = options

    async def list(self, thread_id: str, limit: int = 20, before: Optional[str] = None) -> Dict[str, Any]:
        """
        List messages in a thread.

        Args:
            thread_id: Thread identifier
            limit: Maximum number of messages to return
            before: Message ID to paginate before

        Returns:
            List of messages
        """
        params = {"limit": limit}
        if before:
            params["before"] = before

        response = await self._http.get(f"/threads/{thread_id}/messages", params=params)
        response.raise_for_status()
        return response.json()

    async def create(self, thread_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a message to a thread.

        Args:
            thread_id: Thread identifier
            message: Message to add

        Returns:
            Created message
        """
        response = await self._http.post(f"/threads/{thread_id}/messages", json=message)
        response.raise_for_status()
        return response.json()

    async def get(self, thread_id: str, message_id: str) -> Dict[str, Any]:
        """
        Get a specific message.

        Args:
            thread_id: Thread identifier
            message_id: Message identifier

        Returns:
            Message details
        """
        response = await self._http.get(f"/threads/{thread_id}/messages/{message_id}")
        response.raise_for_status()
        return response.json()


class AgentProtocolClient:
    """
    Main client for interacting with Agent Protocol APIs.

    Provides access to Runs, Threads, and Messages operations.

    Example:
        ```python
        from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

        # Create client
        client = AgentProtocolClient(AgentProtocolClientOptions(
            base_url="https://agents.example.com/v1",
            api_key="your-api-key"
        ))

        # Create a run
        async with client:
            result = await client.runs.create({
                "agent": {
                    "name": "MyAgent",
                    "kind": "prompt",
                    "model": "gpt-4o"
                },
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": "Hello!"}]
                }]
            })
            print(result)
        ```
    """

    def __init__(self, options: AgentProtocolClientOptions):
        """
        Initialize the Agent Protocol client.

        Args:
            options: Client configuration options
        """
        self._options = options
        self._owns_http_client = options.http_client is None

        # Create or use provided HTTP client
        if options.http_client:
            self._http = options.http_client
        else:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            if options.api_key:
                headers["Authorization"] = f"Bearer {options.api_key}"

            self._http = httpx.AsyncClient(
                base_url=options.base_url,
                headers=headers,
                timeout=options.timeout
            )

        # Initialize resource clients
        self.runs = RunsClient(self._http, options)
        self.threads = ThreadsClient(self._http, options)
        self.messages = MessagesClient(self._http, options)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client if owned by this instance."""
        if self._owns_http_client:
            await self._http.aclose()


# Convenience function for simple use cases
def create_client(base_url: str, api_key: Optional[str] = None) -> AgentProtocolClient:
    """
    Create an Agent Protocol client with simplified configuration.

    Args:
        base_url: Base URL for the Agent Protocol API
        api_key: Optional API key for authentication

    Returns:
        Configured Agent Protocol client
    """
    return AgentProtocolClient(AgentProtocolClientOptions(
        base_url=base_url,
        api_key=api_key
    ))
