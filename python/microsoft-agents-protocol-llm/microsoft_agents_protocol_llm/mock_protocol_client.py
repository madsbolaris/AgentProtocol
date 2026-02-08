"""
Mock implementation of Protocol-Native LLM client for testing.
"""

import uuid
from typing import AsyncIterator, Optional
from microsoft_agents_protocol.models import ChatMessage, AgentMessage, TextContent, FunctionCallContent

from .protocol_llm_client import (
    ProtocolLLMClient,
    AgentMessageDelta,
    DeltaType,
    LLMProviderInfo,
    ToolDefinition,
)


class MockProtocolLLMClient(ProtocolLLMClient):
    """
    Mock implementation of IProtocolLLMClient for testing.
    Allows pre-queueing responses without making real API calls.
    """

    def __init__(self):
        self._queued_responses = []
        self._queued_streaming_responses = []
        self._call_history = []
        self._provider_info = LLMProviderInfo(
            provider="Mock",
            model="mock-model",
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_multimodal=True,
        )

    @property
    def provider_info(self) -> LLMProviderInfo:
        return self._provider_info

    @property
    def call_history(self) -> list[tuple[list[ChatMessage], Optional[list[ToolDefinition]]]]:
        """Gets the history of all generate calls made to this client."""
        return self._call_history

    @property
    def call_count(self) -> int:
        """Gets the number of generate calls made."""
        return len(self._call_history)

    def enqueue_response(self, message: AgentMessage):
        """Enqueues a response to be returned by the next generate call."""
        self._queued_responses.append(message)

    def enqueue_text_response(self, text: str):
        """Enqueues a text response to be returned by the next generate call."""
        self.enqueue_response(
            AgentMessage(
                message_id=f"msg_{uuid.uuid4().hex}", contents=[TextContent(text=text)]
            )
        )

    def enqueue_tool_call_response(
        self, tool_name: str, arguments: str, call_id: Optional[str] = None
    ):
        """Enqueues a tool call response to be returned by the next generate call."""
        self.enqueue_response(
            AgentMessage(
                message_id=f"msg_{uuid.uuid4().hex}",
                contents=[
                    FunctionCallContent(
                        call_id=call_id or f"call_{uuid.uuid4().hex}",
                        name=tool_name,
                        arguments=arguments,
                    )
                ],
            )
        )

    def enqueue_streaming_response(self, deltas: list[AgentMessageDelta]):
        """Enqueues a streaming response to be returned by the next stream call."""
        self._queued_streaming_responses.append(deltas)

    def enqueue_streaming_text_response(self, text: str, chunk_size: int = 10):
        """Enqueues a streaming text response."""
        message_id = f"msg_{uuid.uuid4().hex}"
        deltas = [AgentMessageDelta(message_id=message_id, type=DeltaType.MESSAGE_START)]

        text_buffer = ""
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            text_buffer += chunk

            deltas.append(
                AgentMessageDelta(
                    message_id=message_id,
                    type=DeltaType.TEXT_DELTA,
                    content=TextContent(text=text_buffer),
                )
            )

        deltas.append(
            AgentMessageDelta(
                message_id=message_id, type=DeltaType.MESSAGE_COMPLETE, is_complete=True
            )
        )

        self._queued_streaming_responses.append(deltas)

    def reset(self):
        """Clears all queued responses and call history."""
        self._queued_responses.clear()
        self._queued_streaming_responses.clear()
        self._call_history.clear()

    async def generate(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AgentMessage:
        """Generate a response using queued responses."""
        self._call_history.append((conversation_history, available_tools))

        if not self._queued_responses:
            raise RuntimeError(
                "No responses queued. Use enqueue_response() to add responses before calling generate()."
            )

        return self._queued_responses.pop(0)

    async def stream(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AsyncIterator[AgentMessageDelta]:
        """Stream a response using queued streaming responses."""
        self._call_history.append((conversation_history, available_tools))

        if not self._queued_streaming_responses:
            raise RuntimeError(
                "No streaming responses queued. Use enqueue_streaming_response() to add responses before calling stream()."
            )

        deltas = self._queued_streaming_responses.pop(0)

        for delta in deltas:
            yield delta
