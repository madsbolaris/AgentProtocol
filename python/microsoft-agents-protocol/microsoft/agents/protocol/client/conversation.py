# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Conversation interface and implementation"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from .simplified_client import SimplifiedClient
    from .stream_event import StreamEvent


class IConversation(ABC):
    """
    Represents a conversation with state maintained across multiple messages.
    """

    @property
    @abstractmethod
    def thread_id(self) -> Optional[str]:
        """Gets the thread ID for this conversation (None until first message sent)"""
        ...

    @property
    @abstractmethod
    def messages(self) -> List[Dict[str, Any]]:
        """
        Gets all messages in this conversation (cached locally).
        Messages are automatically added as the conversation progresses.
        """
        ...

    @abstractmethod
    async def send(self, message: str) -> str:
        """
        Sends a message and returns the complete response as text.

        Args:
            message: The message to send

        Returns:
            The agent's text response
        """
        ...

    @abstractmethod
    async def send_structured(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a structured message and returns the complete response.

        Args:
            message: The message to send (as dict representation of ChatMessage)

        Returns:
            The agent's response message (as dict)
        """
        ...

    @abstractmethod
    def stream_messages(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Streams message responses as structured messages (Mode 2: Messages).

        Args:
            message: The message to send

        Returns:
            Async iterator of message dicts
        """
        ...

    @abstractmethod
    def stream_events(self, message: str) -> AsyncIterator["StreamEvent"]:
        """
        Streams raw events (Mode 3: Events).

        Args:
            message: The message to send

        Returns:
            Async iterator of stream events
        """
        ...

    @abstractmethod
    async def get_messages(
        self, limit: Optional[int] = None, after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Gets all messages from this conversation's thread.

        This is a convenience method that retrieves the full message history
        for this conversation's thread. It delegates to the client's threads API.

        Args:
            limit: Maximum number of messages to return (optional)
            after: Return messages after this message ID (optional)

        Returns:
            List of message dicts in chronological order

        Raises:
            ValueError: If thread_id is not available. Send a message first
                to create a thread.

        Example:
            >>> conversation = client.create_conversation()
            >>> await conversation.send("Hello")
            >>> messages = await conversation.get_messages()
            >>> print(f"Found {len(messages)} messages")

        Note:
            This method requires an active thread. If you haven't sent any
            messages yet, call send() first to create the thread.
        """
        ...


class Conversation(IConversation):
    """
    Internal implementation of IConversation.
    """

    def __init__(
        self,
        client: "SimplifiedClient",
        thread_id: Optional[str],
        enable_logging: bool = False,
        log_directory: str = "logs/conversations"
    ):
        """
        Creates a conversation instance.

        Args:
            client: The client to use for API calls
            thread_id: Optional thread ID to resume
            enable_logging: Enable automatic logging to XML files
            log_directory: Directory path for saving conversation logs
        """
        self._client = client
        self._thread_id = thread_id
        self._messages: List[Dict[str, Any]] = []
        self._enable_logging = enable_logging
        self._log_directory = log_directory

    @property
    def thread_id(self) -> Optional[str]:
        """Gets the thread ID for this conversation"""
        return self._thread_id

    @property
    def messages(self) -> List[Dict[str, Any]]:
        """Gets all messages in this conversation (cached locally)"""
        return self._messages.copy()

    async def send(self, message: str) -> str:
        """
        Sends a message and returns the complete response as text.

        Args:
            message: The message to send

        Returns:
            The agent's text response
        """
        # Create user message
        user_message = {
            "role": "user",
            "contents": [{"kind": "text", "text": message}],
        }

        # Create run request
        request = {
            "thread_id": self._thread_id,
            "input": [user_message],
        }

        # Execute run and wait for completion
        response = await self._client.runs.create_and_wait(request)

        # Update thread ID if this was the first message
        if self._thread_id is None and "thread_id" in response:
            self._thread_id = response["thread_id"]

        # Add user message to cache
        self._messages.append(user_message)

        # Add agent response to cache
        output = response.get("output", [])
        if output:
            for msg in output:
                self._messages.append(msg)

        # Auto-save if logging is enabled
        self._auto_save_conversation()

        # Extract text from agent response
        if not output:
            return ""

        # Find first agent message
        for msg in output:
            if msg.get("role") == "agent":
                contents = msg.get("contents", [])
                for content in contents:
                    if content.get("kind") == "text":
                        return content.get("text", "")

        return ""

    async def send_structured(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a structured message and returns the complete response.

        Args:
            message: The message to send (as dict representation of ChatMessage)

        Returns:
            The agent's response message (as dict)
        """
        # Create run request
        request = {"thread_id": self._thread_id, "input": [message]}

        # Execute run and wait for completion
        response = await self._client.runs.create_and_wait(request)

        # Update thread ID if this was the first message
        if self._thread_id is None and "thread_id" in response:
            self._thread_id = response["thread_id"]

        # Add user message to cache
        self._messages.append(message)

        # Add agent response to cache
        output = response.get("output", [])
        if output:
            for msg in output:
                self._messages.append(msg)

        # Auto-save if logging is enabled
        self._auto_save_conversation()

        # Extract agent response
        if not output:
            return {"role": "agent", "contents": []}

        # Find first agent message
        for msg in output:
            if msg.get("role") == "agent":
                return msg

        return {"role": "agent", "contents": []}

    async def stream_messages(self, message: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Streams message responses as structured messages (Mode 2: Messages).

        Args:
            message: The message to send

        Yields:
            Message dicts
        """
        # Create run request
        request = {
            "thread_id": self._thread_id,
            "input": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": message}],
                }
            ],
        }

        # Track messages by ID
        message_map: Dict[str, Dict[str, Any]] = {}

        # Stream events
        async for evt in self._client._stream_run(request):
            # Update thread ID from first event
            if self._thread_id is None and evt["event_type"] == "run.started":
                run_data = evt.get("data", {})
                if "thread_id" in run_data:
                    self._thread_id = run_data["thread_id"]

            # Handle message events
            if evt["event_type"] == "message.created":
                message_data = evt.get("data", {})
                message_id = message_data.get("message_id")
                if message_id:
                    message_map[message_id] = message_data
                    yield message_data
            elif evt["event_type"] in ("message.updated", "message.delta"):
                message_data = evt.get("data", {})
                message_id = message_data.get("message_id")
                if message_id:
                    message_map[message_id] = message_data
                    yield message_data

    async def stream_events(self, message: str) -> AsyncIterator["StreamEvent"]:
        """
        Streams raw events (Mode 3: Events).

        Args:
            message: The message to send

        Yields:
            Stream events
        """
        from .stream_event import StreamEvent

        # Create run request
        request = {
            "thread_id": self._thread_id,
            "input": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": message}],
                }
            ],
        }

        # Stream events
        async for evt in self._client._stream_run(request):
            # Update thread ID from first event
            if self._thread_id is None and evt["event_type"] == "run.started":
                run_data = evt.get("data", {})
                if "thread_id" in run_data:
                    self._thread_id = run_data["thread_id"]

            yield StreamEvent(event_type=evt["event_type"], data=evt.get("data", {}))

    async def get_messages(
        self, limit: Optional[int] = None, after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Gets all messages from this conversation's thread.

        This is a convenience method that retrieves the full message history
        for this conversation's thread. It delegates to the client's threads API.

        Args:
            limit: Maximum number of messages to return (optional)
            after: Return messages after this message ID (optional)

        Returns:
            List of message dicts in chronological order

        Raises:
            ValueError: If thread_id is not available. Send a message first
                to create a thread.

        Example:
            >>> conversation = client.create_conversation()
            >>> await conversation.send("Hello")
            >>> messages = await conversation.get_messages()
            >>> print(f"Found {len(messages)} messages")

        Note:
            This method requires an active thread. If you haven't sent any
            messages yet, call send() first to create the thread.
        """
        if not self.thread_id:
            raise ValueError(
                "No thread ID available. Send a message to this conversation "
                "first to create a thread."
            )

        return await self._client.threads.get_messages(
            thread_id=self.thread_id, limit=limit, after=after
        )

    def _auto_save_conversation(self) -> None:
        """Automatically saves the conversation to XML if logging is enabled."""
        if not self._enable_logging or not self._thread_id:
            return

        try:
            from pathlib import Path

            # Ensure log directory exists
            log_path = Path(self._log_directory)
            log_path.mkdir(parents=True, exist_ok=True)

            # Save conversation to file
            file_path = log_path / f"{self._thread_id}.xml"
            file_path.write_text(str(self))
        except Exception:
            # Silently ignore logging errors to avoid breaking the main flow
            pass

    def __str__(self) -> str:
        """
        Returns the XML representation of all messages in this conversation.

        Returns:
            XML string with all messages wrapped in a thread element
        """
        if not self._messages:
            return '<?xml version="1.0" encoding="utf-8"?>\n<thread />'

        # Build simple XML representation
        lines = ['<?xml version="1.0" encoding="utf-8"?>', '<thread>']

        for msg in self._messages:
            role = msg.get("role", "unknown")
            lines.append(f'  <{role}>')

            contents = msg.get("contents", [])
            for content in contents:
                kind = content.get("kind", "")
                if kind == "text":
                    text = content.get("text", "")
                    # Escape XML special characters
                    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    lines.append(f'    <text>{text}</text>')

            lines.append(f'  </{role}>')

        lines.append('</thread>')
        return '\n'.join(lines)
