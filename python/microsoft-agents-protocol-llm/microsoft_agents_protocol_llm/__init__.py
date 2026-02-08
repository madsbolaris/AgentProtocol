"""
Protocol-Native LLM Client for Agent Protocol.

This package provides LLM clients that speak Agent Protocol types natively,
eliminating the need for conversion layers between provider-specific types
and Agent Protocol types.
"""

from .protocol_llm_client import (
    ProtocolLLMClient,
    AgentMessageDelta,
    DeltaType,
    LLMProviderInfo,
    ToolDefinition,
    FunctionDefinition,
)
from .openai_protocol_client import OpenAIProtocolClient
from .mock_protocol_client import MockProtocolLLMClient

__all__ = [
    "ProtocolLLMClient",
    "AgentMessageDelta",
    "DeltaType",
    "LLMProviderInfo",
    "ToolDefinition",
    "FunctionDefinition",
    "OpenAIProtocolClient",
    "MockProtocolLLMClient",
]

__version__ = "0.1.0"
