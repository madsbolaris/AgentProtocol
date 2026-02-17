# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Recording-enabled HTTP session wrapper for aiohttp.
Intercepts HTTP requests/responses for recording and playback.
"""

import os
from typing import Any, Optional
from pathlib import Path
import aiohttp
from aiohttp import ClientResponse
from yarl import URL

from .http_recorder import HttpRecorder, HttpPlayer


class RecordingHttpSession:
    """
    Wrapper around aiohttp.ClientSession that supports HTTP recording and playback.

    When in record mode (RECORD_HTTP=true):
    - Makes real HTTP requests
    - Records request/response pairs to disk

    When in playback mode (default):
    - Loads recorded responses from disk
    - No actual HTTP requests are made
    """

    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        recordings_dir: Optional[str] = None,
        scenario_name: str = "default",
        **session_kwargs: Any
    ):
        """Initialize recording session.

        Args:
            base_url: Base URL of Agent Protocol server (used in record mode)
            recordings_dir: Directory for recordings (defaults to test-data/llm-recordings/docs)
            scenario_name: Name of the test scenario
            **session_kwargs: Additional arguments passed to aiohttp.ClientSession
        """
        # Determine recording mode from environment
        record_env = os.getenv("RECORD_HTTP", "").lower()
        self.record_mode = record_env in ("true", "1")

        # Use shared recordings directory by default (matching C# structure)
        if recordings_dir is None:
            # Navigate to repo root from client package
            repo_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
            recordings_dir = str(repo_root / "test-data" / "llm-recordings/docs" / scenario_name)

        self.recordings_dir = recordings_dir
        self.base_url = base_url

        if self.record_mode:
            # Record mode: use real session + recorder
            self.real_session = aiohttp.ClientSession(
                base_url=base_url,
                **session_kwargs
            )
            self.recorder = HttpRecorder(recordings_dir)
            self.player = None
            print(f"📹 HTTP Recording enabled: {recordings_dir}")
        else:
            # Playback mode: use player only
            self.real_session = None
            self.recorder = None
            self.player = HttpPlayer(recordings_dir)
            print(f"▶️  HTTP Playback enabled: {recordings_dir}")

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> ClientResponse:
        """Make HTTP request with recording/playback.

        Args:
            method: HTTP method
            url: Request URL (can be relative or absolute)
            **kwargs: Additional request arguments

        Returns:
            HTTP response
        """
        # Normalize URL
        if isinstance(url, str):
            if url.startswith("http://") or url.startswith("https://"):
                parsed_url = URL(url)
                path = parsed_url.path_qs
            else:
                path = url
        else:
            path = str(url)

        # Extract request body
        request_body = None
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, (str, bytes)):
                request_body = data if isinstance(data, str) else data.decode("utf-8")
        elif "json" in kwargs:
            import json
            request_body = json.dumps(kwargs["json"])

        if self.record_mode and self.real_session:
            # Record mode: make real request and save recording
            response = await self.real_session.request(method, url, **kwargs)
            status_code = response.status
            response_body = await response.text()

            await self.recorder.record_async(
                method=method,
                path=path,
                request_body=request_body,
                status_code=status_code,
                response_body=response_body
            )

            # Return a mock response with the recorded data
            return _create_mock_response(status_code, response_body)

        elif self.player:
            # Playback mode: load recorded response
            status_code, body = await self.player.replay_async(
                method=method,
                path=path,
                request_body=request_body
            )

            return _create_mock_response(status_code, body)

        else:
            raise RuntimeError("RecordingHttpSession not properly initialized")

    async def get(self, url: str, **kwargs: Any) -> ClientResponse:
        """GET request with recording/playback."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> ClientResponse:
        """POST request with recording/playback."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> ClientResponse:
        """PUT request with recording/playback."""
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> ClientResponse:
        """DELETE request with recording/playback."""
        return await self.request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs: Any) -> ClientResponse:
        """PATCH request with recording/playback."""
        return await self.request("PATCH", url, **kwargs)

    async def close(self):
        """Close the session."""
        if self.real_session:
            await self.real_session.close()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()


class _MockResponse:
    """Mock response object for playback mode."""

    def __init__(self, status: int, text: str):
        self.status = status
        self._text = text
        self._json = None

    async def text(self) -> str:
        """Get response text."""
        return self._text

    async def json(self) -> Any:
        """Get response JSON."""
        if self._json is None:
            import json
            self._json = json.loads(self._text)
        return self._json

    async def read(self) -> bytes:
        """Get response bytes."""
        return self._text.encode("utf-8")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def _create_mock_response(status: int, body: str) -> ClientResponse:
    """Create a mock response for playback mode."""
    return _MockResponse(status, body)  # type: ignore
