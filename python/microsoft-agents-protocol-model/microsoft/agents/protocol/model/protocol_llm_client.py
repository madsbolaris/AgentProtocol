"""
Core abstractions for Protocol-Native LLM clients.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Any, Optional
from microsoft_agents_protocol.models import ChatMessage, AgentMessage, AIContent


class DeltaType(Enum):
    """Types of delta updates during streaming."""

    MESSAGE_START = "message_start"
    TEXT_DELTA = "text_delta"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_DELTA = "tool_call_delta"
    TOOL_CALL_COMPLETE = "tool_call_complete"
    MESSAGE_COMPLETE = "message_complete"


@dataclass
class AgentMessageDelta:
    """
    Delta update for streaming responses, using Agent Protocol native types.
    """

    message_id: str
    type: DeltaType
    content: Optional[AIContent] = None
    tool_call: Optional[dict[str, Any]] = None
    is_complete: bool = False
    metadata: Optional[dict[str, Any]] = None


@dataclass
class LLMProviderInfo:
    """Information about the LLM provider and its capabilities."""

    provider: str
    model: str
    supports_streaming: bool = True
    supports_function_calling: bool = True
    supports_vision: bool = False
    supports_multimodal: bool = False
    additional_capabilities: Optional[dict[str, bool]] = None


@dataclass
class FunctionDefinition:
    """Definition of a function that can be called."""

    name: str
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None


@dataclass
class ToolDefinition:
    """Defines a tool/function that can be called by the LLM."""

    function: FunctionDefinition
    type: str = "function"


class ProtocolLLMClient(ABC):
    """
    LLM client that speaks Agent Protocol types natively.

    Eliminates the need for conversion layers between provider-specific types
    and Agent Protocol types.
    """

    @property
    @abstractmethod
    def provider_info(self) -> LLMProviderInfo:
        """Provider-specific metadata and capabilities."""
        pass

    @abstractmethod
    async def generate(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AgentMessage:
        """
        Generate a response using Agent Protocol message types.

        Args:
            conversation_history: The conversation history using Protocol message types
            available_tools: Optional tool definitions in Protocol format

        Returns:
            Agent message with Protocol content types
        """
        pass

    @abstractmethod
    async def stream(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AsyncIterator[AgentMessageDelta]:
        """
        Stream a response using Agent Protocol message types.

        Args:
            conversation_history: The conversation history using Protocol message types
            available_tools: Optional tool definitions in Protocol format

        Yields:
            Async stream of deltas with Protocol content types
        """
        pass
