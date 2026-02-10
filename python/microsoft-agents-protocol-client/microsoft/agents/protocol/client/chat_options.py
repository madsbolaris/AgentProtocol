# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Options for chat completion and streaming requests"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable, Awaitable

# Forward reference to avoid circular import
TYPE_CHECKING = False
if TYPE_CHECKING:
    from .tool_collection import ToolCollection


@dataclass
class ToolCallInfo:
    """Information about a tool call"""

    call_id: str
    name: str
    arguments: str


@dataclass
class ChatOptions:
    """
    Options for chat completion and streaming requests.
    """

    agent_id: Optional[str] = None
    """Agent ID to use (optional if only one agent registered)"""

    tools: Optional["ToolCollection"] = None
    """Tools available for the agent to call"""

    metadata: Optional[Dict[str, Any]] = None
    """Additional metadata for the request"""

    on_tool_call_started: Optional[Callable[[ToolCallInfo], Awaitable[None]]] = None
    """Callback fired when a tool call starts (for monitoring)"""

    on_tool_call_completed: Optional[Callable[[ToolCallInfo, Any], Awaitable[None]]] = None
    """Callback fired when a tool call completes (for monitoring)"""

    on_tool_call_failed: Optional[Callable[[ToolCallInfo, Exception], Awaitable[None]]] = None
    """Callback fired when a tool call fails (for monitoring)"""
