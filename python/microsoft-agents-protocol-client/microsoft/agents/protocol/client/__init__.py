# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Agent Protocol Client

Python client library for interacting with Agent Protocol APIs.
"""

from .agent_protocol_client import AgentProtocolClient
from .client_options import AgentProtocolClientOptions
from .simplified_client import SimplifiedClient, create_simplified_client
from .conversation import IConversation, Conversation
from .chat_options import ChatOptions, ToolCallInfo
from .tool_collection import ToolCollection, ToolDefinition
from .stream_event import StreamEvent

__all__ = [
    "AgentProtocolClient",
    "AgentProtocolClientOptions",
    "SimplifiedClient",
    "create_simplified_client",
    "IConversation",
    "Conversation",
    "ChatOptions",
    "ToolCallInfo",
    "ToolCollection",
    "ToolDefinition",
    "StreamEvent",
]
