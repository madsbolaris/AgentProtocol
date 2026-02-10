# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Comprehensive tests for error classes."""

import pytest
from microsoft.agents.hosting import (
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


def test_agent_error():
    """Test base AgentError."""
    error = AgentError("Base error")
    assert str(error) == "Base error"
    assert isinstance(error, Exception)


def test_agent_error_inheritance():
    """Test that all errors inherit from AgentError."""
    errors = [
        ConfigurationError("test"),
        ValidationError("test"),
        RateLimitError("test"),
        TimeoutError("test"),
        NetworkError("test"),
        AuthenticationError("test"),
        LLMError("test"),
        ResourceLimitError("test"),
        CircuitBreakerOpenError("test"),
    ]

    for error in errors:
        assert isinstance(error, AgentError)
        assert isinstance(error, Exception)


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Invalid configuration")
    assert str(error) == "Invalid configuration"


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"


def test_timeout_error():
    """Test TimeoutError."""
    error = TimeoutError("Operation timed out")
    assert str(error) == "Operation timed out"


def test_network_error():
    """Test NetworkError."""
    error = NetworkError("Network connection failed")
    assert str(error) == "Network connection failed"


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Authentication failed")
    assert str(error) == "Authentication failed"


def test_llm_error():
    """Test LLMError."""
    error = LLMError("LLM API error")
    assert str(error) == "LLM API error"


def test_resource_limit_error():
    """Test ResourceLimitError."""
    error = ResourceLimitError("Resource limit exceeded")
    assert str(error) == "Resource limit exceeded"


def test_circuit_breaker_open_error():
    """Test CircuitBreakerOpenError."""
    error = CircuitBreakerOpenError("Circuit breaker is open")
    assert str(error) == "Circuit breaker is open"


def test_function_execution_error():
    """Test FunctionExecutionError with original error."""
    original = ValueError("Invalid value")
    error = FunctionExecutionError("my_function", original)

    assert error.function_name == "my_function"
    assert error.original_error == original
    assert "my_function" in str(error)
    assert "Invalid value" in str(error)


def test_function_execution_error_message():
    """Test FunctionExecutionError message format."""
    original = RuntimeError("Something went wrong")
    error = FunctionExecutionError("test_function@v1", original)

    error_message = str(error)
    assert "Function test_function@v1 failed:" in error_message
    assert "Something went wrong" in error_message


def test_errors_can_be_raised():
    """Test that errors can be raised and caught."""
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("Test error")

    assert str(exc_info.value) == "Test error"


def test_errors_can_be_caught_as_agent_error():
    """Test that specific errors can be caught as AgentError."""
    with pytest.raises(AgentError):
        raise ConfigurationError("Test error")


def test_function_execution_error_chaining():
    """Test exception chaining with FunctionExecutionError."""
    try:
        try:
            raise ValueError("Original error")
        except ValueError as e:
            raise FunctionExecutionError("my_func", e)
    except FunctionExecutionError as fe:
        assert fe.function_name == "my_func"
        assert isinstance(fe.original_error, ValueError)
        assert str(fe.original_error) == "Original error"


def test_error_with_no_message():
    """Test errors with no message."""
    error = AgentError()
    assert isinstance(error, AgentError)


def test_multiple_error_types():
    """Test catching different error types."""
    def raise_error(error_type: str):
        if error_type == "config":
            raise ConfigurationError("Config error")
        elif error_type == "validation":
            raise ValidationError("Validation error")
        elif error_type == "rate_limit":
            raise RateLimitError("Rate limit error")
        else:
            raise AgentError("Generic error")

    with pytest.raises(ConfigurationError):
        raise_error("config")

    with pytest.raises(ValidationError):
        raise_error("validation")

    with pytest.raises(RateLimitError):
        raise_error("rate_limit")

    with pytest.raises(AgentError):
        raise_error("other")


def test_error_isinstance_checks():
    """Test isinstance checks for error hierarchy."""
    config_error = ConfigurationError("test")

    assert isinstance(config_error, ConfigurationError)
    assert isinstance(config_error, AgentError)
    assert isinstance(config_error, Exception)
    assert not isinstance(config_error, ValidationError)


def test_function_execution_error_attributes():
    """Test that FunctionExecutionError stores attributes correctly."""
    original = IOError("File not found")
    error = FunctionExecutionError("read_file@v1", original)

    assert hasattr(error, "function_name")
    assert hasattr(error, "original_error")
    assert error.function_name == "read_file@v1"
    assert error.original_error is original


def test_retryable_error_types():
    """Test that retryable error types can be identified."""
    retryable_errors = [
        RateLimitError("test"),
        TimeoutError("test"),
        NetworkError("test"),
    ]

    non_retryable_errors = [
        AuthenticationError("test"),
        ValidationError("test"),
        ConfigurationError("test"),
    ]

    # This is a pattern test to ensure error types are distinct
    for error in retryable_errors:
        assert isinstance(error, AgentError)

    for error in non_retryable_errors:
        assert isinstance(error, AgentError)

    # Verify they're different types
    assert not isinstance(retryable_errors[0], type(non_retryable_errors[0]))
