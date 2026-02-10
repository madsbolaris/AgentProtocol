# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Simplified high-level client API for Agent Protocol.

Provides convenience methods for common operations matching the .NET implementation.
"""

import json
from typing import Optional, Callable, AsyncIterator, Dict, Any
from .agent_protocol_client import AgentProtocolClient
from .client_options import AgentProtocolClientOptions
from .chat_options import ChatOptions
from .conversation import IConversation, Conversation
from .stream_event import StreamEvent


class SimplifiedClient(AgentProtocolClient):
    """
    Simplified Agent Protocol client with high-level convenience methods.

    Extends AgentProtocolClient with methods like:
    - complete_chat: Simple text-in, text-out
    - complete_chat_structured: Full message objects
    - stream_chat: Streaming with text chunk callbacks
    - create_conversation: Stateful multi-turn conversations
    """

    async def complete_chat(
        self, message: str, options: Optional[ChatOptions] = None
    ) -> str:
        """
        Sends a message and returns the complete response as text (simple API).

        Args:
            message: The message to send
            options: Optional chat options including tools and metadata

        Returns:
            The agent's text response
        """
        # Build request
        request = {
            "input": [
                {"role": "user", "contents": [{"kind": "text", "text": message}]}
            ]
        }

        # Add optional fields
        if options:
            if options.agent_id:
                request["agent_id"] = options.agent_id
            if options.metadata:
                request["metadata"] = options.metadata

        # If tools are provided, handle tool execution automatically
        if options and options.tools:
            return await self._complete_chat_with_tools(request, options)

        # Execute run and wait for completion
        response = await self.runs.create_and_wait(request)

        # Extract text from agent response
        return self._extract_text_from_response(response)

    async def complete_chat_structured(
        self, message: Dict[str, Any], options: Optional[ChatOptions] = None
    ) -> Dict[str, Any]:
        """
        Sends a structured message and returns the complete response message.

        Args:
            message: The message to send (as dict representation of ChatMessage)
            options: Optional chat options

        Returns:
            The agent's response message (as dict)
        """
        # Build request
        request = {"input": [message]}

        # Add optional fields
        if options:
            if options.agent_id:
                request["agent_id"] = options.agent_id
            if options.metadata:
                request["metadata"] = options.metadata

        # Execute run and wait for completion
        response = await self.runs.create_and_wait(request)

        # Extract agent response
        output = response.get("output", [])
        if not output:
            return {"role": "agent", "contents": []}

        # Find first agent message
        for msg in output:
            if msg.get("role") == "agent":
                return msg

        return {"role": "agent", "contents": []}

    async def stream_chat(
        self, message: str, on_text_chunk: Callable[[str], None]
    ) -> None:
        """
        Streams a message response with text chunks delivered via callback.

        Args:
            message: The message to send
            on_text_chunk: Callback fired for each text chunk
        """
        # Build request
        request = {
            "input": [
                {"role": "user", "contents": [{"kind": "text", "text": message}]}
            ]
        }

        accumulated_text = ""

        # Stream events
        async for evt in self._stream_run(request):
            # Handle message delta events for text streaming
            if evt["event_type"] in ("message.delta", "message.updated"):
                message_data = evt.get("data", {})
                contents = message_data.get("contents", [])

                # Find text content
                for content in contents:
                    if content.get("kind") == "text":
                        full_text = content.get("text", "")
                        # Calculate new text since last update
                        if full_text.startswith(accumulated_text):
                            new_text = full_text[len(accumulated_text) :]
                            if new_text:
                                on_text_chunk(new_text)
                                accumulated_text = full_text
                        else:
                            # Full replacement
                            on_text_chunk(full_text)
                            accumulated_text = full_text

    def create_conversation(self) -> IConversation:
        """
        Creates a new conversation for maintaining state across multiple messages.

        Returns:
            A conversation instance
        """
        return Conversation(
            self,
            None,
            enable_logging=self._options.enable_logging,
            log_directory=self._options.log_directory
        )

    def resume_conversation(self, thread_id: str) -> IConversation:
        """
        Resumes an existing conversation using a thread ID.

        Args:
            thread_id: The thread ID to resume

        Returns:
            A conversation instance
        """
        return Conversation(
            self,
            thread_id,
            enable_logging=self._options.enable_logging,
            log_directory=self._options.log_directory
        )

    async def _stream_run(self, request: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Internal method to stream a run and parse SSE events.

        Args:
            request: Run request

        Yields:
            Parsed SSE events as dicts with 'event_type' and 'data'
        """
        current_event = None
        current_data = None

        async for line in self.runs.create_and_stream(request):
            line = line.strip()

            if not line:
                # Empty line signals end of event
                if current_event and current_data is not None:
                    yield {"event_type": current_event, "data": current_data}
                    current_event = None
                    current_data = None
                continue

            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str:
                    try:
                        current_data = json.loads(data_str)
                    except json.JSONDecodeError:
                        current_data = {"raw": data_str}

        # Yield last event if exists
        if current_event and current_data is not None:
            yield {"event_type": current_event, "data": current_data}

    async def _complete_chat_with_tools(
        self, request: Dict[str, Any], options: ChatOptions
    ) -> str:
        """
        Handles tool execution automatically during streaming.

        Args:
            request: Run request
            options: Chat options with tools

        Returns:
            Final text response
        """
        result_text = ""

        async for evt in self._stream_run(request):
            if evt["event_type"] in ("message.delta", "message.updated"):
                message_data = evt.get("data", {})
                contents = message_data.get("contents", [])

                # Extract text content
                for content in contents:
                    if content.get("kind") == "text":
                        result_text = content.get("text", "")

            elif evt["event_type"] == "run.requires_action":
                # Extract tool calls and execute them
                # TODO: Implement tool execution loop
                # This requires protocol-level support for submitting tool outputs
                pass

        return result_text

    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """
        Extracts text from a run response.

        Args:
            response: Run response

        Returns:
            Extracted text or empty string
        """
        output = response.get("output", [])
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


def create_simplified_client(
    base_url: str, api_key: Optional[str] = None
) -> SimplifiedClient:
    """
    Creates a simplified Agent Protocol client with convenience methods.

    Args:
        base_url: Base URL for the Agent Protocol API
        api_key: Optional API key for authentication

    Returns:
        Configured simplified client
    """
    options = AgentProtocolClientOptions(base_url=base_url, api_key=api_key)
    return SimplifiedClient(options)
