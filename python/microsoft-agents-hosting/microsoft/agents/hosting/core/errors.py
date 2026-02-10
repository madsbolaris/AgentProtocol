# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Error types for the hosting SDK."""


class AgentError(Exception):
    """Base exception for agent errors."""

    pass


class ConfigurationError(AgentError):
    """Configuration is invalid."""

    pass


class ValidationError(AgentError):
    """Input validation failed."""

    pass


class RateLimitError(AgentError):
    """Rate limit exceeded."""

    pass


class TimeoutError(AgentError):
    """Operation timed out."""

    pass


class NetworkError(AgentError):
    """Network operation failed."""

    pass


class AuthenticationError(AgentError):
    """Authentication failed."""

    pass


class LLMError(AgentError):
    """LLM API error."""

    pass


class FunctionExecutionError(AgentError):
    """Function execution failed."""

    def __init__(self, function_name: str, original_error: Exception):
        self.function_name = function_name
        self.original_error = original_error
        super().__init__(f"Function {function_name} failed: {original_error}")


class ResourceLimitError(AgentError):
    """Resource limit exceeded."""

    pass


class CircuitBreakerOpenError(AgentError):
    """Circuit breaker is open."""

    pass
