"""
LLM client abstractions for Microsoft Agents Protocol.

This module provides the core abstractions for Protocol-Native LLM clients
that speak Agent Protocol types natively.
"""

from .protocol_llm_client import (
    ProtocolLLMClient,
    AgentMessageDelta,
    DeltaType,
    LLMProviderInfo,
    ToolDefinition,
    FunctionDefinition,
)

__all__ = [
    "ProtocolLLMClient",
    "AgentMessageDelta",
    "DeltaType",
    "LLMProviderInfo",
    "ToolDefinition",
    "FunctionDefinition",
]

__version__ = "0.2.0"
