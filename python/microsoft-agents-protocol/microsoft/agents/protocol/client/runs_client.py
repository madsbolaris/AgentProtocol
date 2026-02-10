# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Client for Runs API operations"""

from typing import Dict, Any, List, Optional
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

    async def list(
        self,
        agent_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Lists runs with optional filtering and pagination

        Args:
            agent_id: Filter by agent ID
            thread_id: Filter by thread ID
            status: Filter by run status (e.g., 'completed', 'in_progress', 'failed')
            limit: Maximum number of runs to return
            offset: Number of runs to skip for pagination

        Returns:
            List of runs matching the filters
        """
        params = {}
        if agent_id:
            params["agentId"] = agent_id
        if thread_id:
            params["threadId"] = thread_id
        if status:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        url = "/runs"
        if params:
            # Build query string
            query_parts = [f"{k}={v}" for k, v in params.items()]
            url = f"{url}?{'&'.join(query_parts)}"

        async with self._session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def cancel(
        self,
        run_id: str,
        action: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cancels a running execution

        Args:
            run_id: Run identifier
            action: Cancel action - 'interrupt' preserves state, 'rollback' cleans up
            reason: Optional reason for cancellation

        Returns:
            The cancelled run details
        """
        payload = {}
        if action:
            payload["action"] = action
        if reason:
            payload["reason"] = reason

        async with self._session.post(
            f"/runs/{run_id}/cancel", json=payload if payload else None
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def submit_tool_outputs(
        self, run_id: str, tool_outputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Submits tool outputs for a run requiring action (HITL)

        Args:
            run_id: Run identifier
            tool_outputs: List of tool outputs with tool_call_id and output

        Returns:
            Updated run details
        """
        payload = {"tool_outputs": tool_outputs}
        async with self._session.post(
            f"/runs/{run_id}/submit_tool_outputs", json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def submit_input(self, run_id: str, input_text: str) -> Dict[str, Any]:
        """
        Submits user input for a run requiring input

        Args:
            run_id: Run identifier
            input_text: User input text

        Returns:
            Updated run details
        """
        payload = {"input": input_text}
        async with self._session.post(
            f"/runs/{run_id}/submit_input", json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def submit_auth(
        self, run_id: str, token: str, token_type: str = "Bearer"
    ) -> Dict[str, Any]:
        """
        Submits authentication credentials for a run requiring auth

        Args:
            run_id: Run identifier
            token: Authentication token
            token_type: Token type (default: "Bearer")

        Returns:
            Updated run details
        """
        payload = {"token": token, "token_type": token_type}
        async with self._session.post(
            f"/runs/{run_id}/submit_auth", json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def create_and_stream(self, run: Dict[str, Any]):
        """
        Creates a run and streams results via Server-Sent Events

        Args:
            run: Run configuration

        Yields:
            SSE lines (without "data: " prefix)
        """
        async with self._session.post("/runs/stream", json=run) as response:
            response.raise_for_status()

            # Read SSE stream line by line
            async for line_bytes in response.content:
                line = line_bytes.decode("utf-8").strip()
                if line:
                    yield line
