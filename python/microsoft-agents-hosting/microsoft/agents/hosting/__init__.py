# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Microsoft Agents Protocol Hosting SDK

Build production-ready AI agents with LLM function calling, state management,
and operational best practices built-in.
"""

__version__ = "0.1.0"

# Core types
from .core import (
    TurnResult,
    IAgentContext,
    IThreadState,
    IStateStore,
    IQueueAdapter,
    CancellationToken,
    AgentError,
    ConfigurationError,
    ValidationError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    AuthenticationError,
    LLMError,
    FunctionExecutionError,
    ResourceLimitError,
    CircuitBreakerOpenError,
    # Protocol types
    ChatMessage,
    UserMessage,
    AgentMessage,
    AIContent,
    AITool,
    TextContent,
    MessageReaction,
)

# Builder classes
from .builder import (
    AgentHostBuilder,
    AgentBuilder,
    FunctionBuilder,
)

# Hosting
from .hosting import (
    AgentHost,
    OutOfBandPublisher,
)

# State management
from .state import (
    MemoryStateStore,
)

__all__ = [
    # Version
    "__version__",
    # Core types
    "TurnResult",
    "IAgentContext",
    "IThreadState",
    "IStateStore",
    "IQueueAdapter",
    "CancellationToken",
    # Errors
    "AgentError",
    "ConfigurationError",
    "ValidationError",
    "RateLimitError",
    "TimeoutError",
    "NetworkError",
    "AuthenticationError",
    "LLMError",
    "FunctionExecutionError",
    "ResourceLimitError",
    "CircuitBreakerOpenError",
    # Protocol types (from microsoft-agents-abstractions)
    "ChatMessage",
    "UserMessage",
    "AgentMessage",
    "AIContent",
    "AITool",
    "TextContent",
    "MessageReaction",
    # Builders
    "AgentHostBuilder",
    "AgentBuilder",
    "FunctionBuilder",
    # Hosting
    "AgentHost",
    "OutOfBandPublisher",
    # State
    "MemoryStateStore",
]
