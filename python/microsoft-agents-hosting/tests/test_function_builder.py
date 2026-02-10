# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for FunctionBuilder."""

import pytest
from microsoft.agents.hosting.builder import FunctionBuilder
from microsoft.agents.hosting import ConfigurationError


def test_function_builder_add():
    """Test adding a simple function."""
    def get_time() -> str:
        return "2024-01-01T00:00:00"

    builder = FunctionBuilder()
    builder = builder.add("get_time@v1", "Gets the current time", get_time)

    functions = builder._build()
    assert len(functions) == 1
    assert functions[0].name == "get_time@v1"
    assert functions[0].description == "Gets the current time"
    assert functions[0].timeout == 30.0
    assert functions[0].require_approval is False


def test_function_builder_add_with_parameters():
    """Test adding a function with parameters."""
    def add(a: int, b: int) -> str:
        return str(a + b)

    builder = FunctionBuilder()
    builder = builder.add("add@v1", "Add two numbers", add)

    functions = builder._build()
    assert len(functions) == 1
    assert functions[0].name == "add@v1"
    assert "a" in functions[0].parameters
    assert "b" in functions[0].parameters


def test_function_builder_add_multiple():
    """Test adding multiple functions."""
    def func1() -> str:
        return "1"

    def func2() -> str:
        return "2"

    builder = FunctionBuilder()
    builder = builder.add("func1@v1", "Function 1", func1)
    builder = builder.add("func2@v1", "Function 2", func2)

    functions = builder._build()
    assert len(functions) == 2
    assert functions[0].name == "func1@v1"
    assert functions[1].name == "func2@v1"


def test_function_builder_with_timeout():
    """Test adding a function with custom timeout."""
    def slow_func() -> str:
        return "slow"

    builder = FunctionBuilder()
    builder = builder.add("slow@v1", "Slow function", slow_func, timeout=60.0)

    functions = builder._build()
    assert functions[0].timeout == 60.0


def test_function_builder_with_approval():
    """Test adding a function that requires approval."""
    def dangerous_func() -> str:
        return "danger"

    builder = FunctionBuilder()
    builder = builder.add(
        "dangerous@v1",
        "Dangerous function",
        dangerous_func,
        require_approval=True
    )

    functions = builder._build()
    assert functions[0].require_approval is True


def test_function_builder_immutability():
    """Test that builder is immutable."""
    def func1() -> str:
        return "1"

    def func2() -> str:
        return "2"

    builder1 = FunctionBuilder()
    builder2 = builder1.add("func1@v1", "Function 1", func1)
    builder3 = builder2.add("func2@v1", "Function 2", func2)

    # Original builder should be unchanged
    assert len(builder1._build()) == 0
    assert len(builder2._build()) == 1
    assert len(builder3._build()) == 2


def test_function_builder_add_with_invalid_function():
    """Test adding a function that cannot be inspected."""
    # Create a non-introspectable object
    class NonCallable:
        pass

    builder = FunctionBuilder()
    with pytest.raises(ConfigurationError, match="Failed to inspect function"):
        builder.add("invalid@v1", "Invalid function", NonCallable())


def test_function_builder_add_async_function():
    """Test adding an async function."""
    async def async_func(x: int) -> str:
        return str(x * 2)

    builder = FunctionBuilder()
    builder = builder.add("async_func@v1", "Async function", async_func)

    functions = builder._build()
    assert len(functions) == 1
    assert functions[0].name == "async_func@v1"
    assert "x" in functions[0].parameters
