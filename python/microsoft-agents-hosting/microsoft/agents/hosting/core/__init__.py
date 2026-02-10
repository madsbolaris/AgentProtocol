# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Core types and interfaces for the hosting SDK."""

from .turn_result import TurnResult
from .errors import (
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
)
from .types import (
    IAgentContext,
    IThreadState,
    IStateStore,
    IQueueAdapter,
    CancellationToken,
    FunctionDefinition,
    ConcurrencyConfig,
    SandboxConfig,
    RetryConfig,
    TelemetryConfig,
    LoggingConfig,
    FailedMessage,
    DLQConfig,
    UserMessageHandler,
    ReactionHandler,
    ErrorHandler,
    DEFAULT_ALLOWED_MODULES,
    # Re-export protocol types for convenience
    ChatMessage,
    UserMessage,
    AgentMessage,
    AIContent,
    AITool,
    TextContent,
    MessageReaction,
)
from .agent_context import AgentContext, ThreadState

__all__ = [
    # Enums
    "TurnResult",
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
    # Protocols
    "IAgentContext",
    "IThreadState",
    "IStateStore",
    "IQueueAdapter",
    # Types
    "CancellationToken",
    "FunctionDefinition",
    "ConcurrencyConfig",
    "SandboxConfig",
    "RetryConfig",
    "TelemetryConfig",
    "LoggingConfig",
    "FailedMessage",
    "DLQConfig",
    "UserMessageHandler",
    "ReactionHandler",
    "ErrorHandler",
    "DEFAULT_ALLOWED_MODULES",
    # Protocol types (re-exported from abstractions)
    "ChatMessage",
    "UserMessage",
    "AgentMessage",
    "AIContent",
    "AITool",
    "TextContent",
    "MessageReaction",
    # Implementations
    "AgentContext",
    "ThreadState",
]
