"""
OpenAI implementation of Protocol-Native LLM client.
"""

import uuid
from typing import AsyncIterator, Optional, Any
from openai import AsyncOpenAI
from microsoft_agents_protocol.models import (
    ChatMessage,
    AgentMessage,
    SystemMessage,
    UserMessage,
    ToolMessage,
    TextContent,
    ImageContent,
    FunctionCallContent,
    FunctionResultContent,
    AIContent,
)

from .protocol_llm_client import (
    ProtocolLLMClient,
    AgentMessageDelta,
    DeltaType,
    LLMProviderInfo,
    ToolDefinition,
)


class OpenAIProtocolClient(ProtocolLLMClient):
    """
    OpenAI implementation of IProtocolLLMClient that returns Agent Protocol types directly.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        """
        Creates a new OpenAI protocol client.

        Args:
            api_key: OpenAI API key
            model: Model identifier (default: gpt-4o)
            base_url: Optional custom base URL (for Azure, Foundry, etc.)
            temperature: Temperature for generation (0.0 = deterministic, 2.0 = very random)
            max_tokens: Maximum number of tokens to generate
            seed: Random seed for deterministic generation
        """
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._seed = seed

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = AsyncOpenAI(**client_kwargs)

    @property
    def provider_info(self) -> LLMProviderInfo:
        return LLMProviderInfo(
            provider="OpenAI",
            model=self._model,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision="vision" in self._model or "4o" in self._model or "gpt-4" in self._model,
            supports_multimodal="4o" in self._model,
        )

    async def generate(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AgentMessage:
        """Generate a response using Agent Protocol message types."""
        openai_messages = self._convert_to_openai_messages(conversation_history)
        openai_tools = self._convert_to_openai_tools(available_tools) if available_tools else None

        completion_kwargs = {
            "model": self._model,
            "messages": openai_messages,
            "temperature": self._temperature,
        }

        if openai_tools:
            completion_kwargs["tools"] = openai_tools

        if self._max_tokens:
            completion_kwargs["max_tokens"] = self._max_tokens

        if self._seed is not None:
            completion_kwargs["seed"] = self._seed

        completion = await self._client.chat.completions.create(**completion_kwargs)

        return self._convert_to_agent_message(completion)

    async def stream(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AsyncIterator[AgentMessageDelta]:
        """Stream a response using Agent Protocol message types."""
        openai_messages = self._convert_to_openai_messages(conversation_history)
        openai_tools = self._convert_to_openai_tools(available_tools) if available_tools else None

        completion_kwargs = {
            "model": self._model,
            "messages": openai_messages,
            "temperature": self._temperature,
            "stream": True,
        }

        if openai_tools:
            completion_kwargs["tools"] = openai_tools

        if self._max_tokens:
            completion_kwargs["max_tokens"] = self._max_tokens

        if self._seed is not None:
            completion_kwargs["seed"] = self._seed

        stream = await self._client.chat.completions.create(**completion_kwargs)

        message_id = f"msg_{uuid.uuid4().hex}"
        text_buffer = ""
        tool_call_buffers = {}

        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Start of message
            if delta.role:
                yield AgentMessageDelta(
                    message_id=message_id, type=DeltaType.MESSAGE_START
                )

            # Text content
            if delta.content:
                text_buffer += delta.content
                yield AgentMessageDelta(
                    message_id=message_id,
                    type=DeltaType.TEXT_DELTA,
                    content=TextContent(text=text_buffer),
                )

            # Tool calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    index = tool_call.index

                    if index not in tool_call_buffers:
                        tool_call_buffers[index] = {
                            "call_id": tool_call.id or f"call_{uuid.uuid4().hex}",
                            "name": tool_call.function.name if tool_call.function else "",
                            "arguments": "",
                        }

                        yield AgentMessageDelta(
                            message_id=message_id,
                            type=DeltaType.TOOL_CALL_START,
                            tool_call={
                                "call_id": tool_call_buffers[index]["call_id"],
                                "name": tool_call_buffers[index]["name"],
                            },
                        )

                    if tool_call.function and tool_call.function.arguments:
                        tool_call_buffers[index]["arguments"] += tool_call.function.arguments

                        yield AgentMessageDelta(
                            message_id=message_id,
                            type=DeltaType.TOOL_CALL_DELTA,
                            tool_call={
                                "call_id": tool_call_buffers[index]["call_id"],
                                "name": tool_call_buffers[index]["name"],
                                "arguments": tool_call_buffers[index]["arguments"],
                            },
                        )

            # End of message
            if chunk.choices[0].finish_reason:
                # Complete any pending tool calls
                for builder in tool_call_buffers.values():
                    yield AgentMessageDelta(
                        message_id=message_id,
                        type=DeltaType.TOOL_CALL_COMPLETE,
                        tool_call=builder,
                    )

                yield AgentMessageDelta(
                    message_id=message_id,
                    type=DeltaType.MESSAGE_COMPLETE,
                    is_complete=True,
                )

    def _convert_to_agent_message(self, completion: Any) -> AgentMessage:
        """Convert OpenAI completion to Agent Protocol message."""
        contents = []

        message = completion.choices[0].message

        # Text content
        if message.content:
            contents.append(TextContent(text=message.content))

        # Tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                contents.append(
                    FunctionCallContent(
                        call_id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                )

        return AgentMessage(
            message_id=f"msg_{completion.id or uuid.uuid4().hex}", contents=contents
        )

    def _convert_to_openai_messages(
        self, protocol_messages: list[ChatMessage]
    ) -> list[dict[str, Any]]:
        """Convert Agent Protocol messages to OpenAI format."""
        openai_messages = []

        for msg in protocol_messages:
            if isinstance(msg, SystemMessage):
                text_content = next((c.text for c in msg.contents if isinstance(c, TextContent)), None)
                if text_content:
                    openai_messages.append({"role": "system", "content": text_content})

            elif isinstance(msg, UserMessage):
                # Handle multimodal content
                content_parts = []
                for content in msg.contents:
                    if isinstance(content, TextContent):
                        content_parts.append({"type": "text", "text": content.text})
                    elif isinstance(content, ImageContent) and content.image_url:
                        content_parts.append(
                            {"type": "image_url", "image_url": {"url": content.image_url}}
                        )

                if len(content_parts) == 1 and content_parts[0]["type"] == "text":
                    openai_messages.append(
                        {"role": "user", "content": content_parts[0]["text"]}
                    )
                elif content_parts:
                    openai_messages.append({"role": "user", "content": content_parts})

            elif isinstance(msg, AgentMessage):
                openai_msg = {"role": "assistant"}

                text_parts = [c.text for c in msg.contents if isinstance(c, TextContent)]
                if text_parts:
                    openai_msg["content"] = " ".join(text_parts)

                tool_calls = [c for c in msg.contents if isinstance(c, FunctionCallContent)]
                if tool_calls:
                    openai_msg["tool_calls"] = [
                        {
                            "id": tc.call_id or f"call_{uuid.uuid4().hex}",
                            "type": "function",
                            "function": {"name": tc.name or "", "arguments": tc.arguments or "{}"},
                        }
                        for tc in tool_calls
                    ]

                openai_messages.append(openai_msg)

            elif isinstance(msg, ToolMessage):
                for content in msg.contents:
                    if isinstance(content, FunctionResultContent):
                        openai_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": content.call_id or f"call_{uuid.uuid4().hex}",
                                "content": content.result or "",
                            }
                        )

        return openai_messages

    def _convert_to_openai_tools(
        self, protocol_tools: list[ToolDefinition]
    ) -> list[dict[str, Any]]:
        """Convert Agent Protocol tools to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description or "",
                    "parameters": tool.function.parameters or {},
                },
            }
            for tool in protocol_tools
        ]
