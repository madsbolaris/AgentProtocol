# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for ToolCollection"""

import pytest
from microsoft.agents.protocol.client import ToolCollection, ToolDefinition


def test_tool_collection_initialization():
    """Test ToolCollection can be initialized"""
    tools = ToolCollection()
    assert len(tools) == 0


def test_add_tool_basic():
    """Test adding a basic tool"""

    def simple_tool(message: str) -> str:
        return f"Echo: {message}"

    tools = ToolCollection()
    tools.add("echo", simple_tool, "Echoes a message")

    assert len(tools) == 1
    tool = tools.get("echo")
    assert tool is not None
    assert tool.name == "echo"
    assert tool.description == "Echoes a message"


def test_add_tool_without_description():
    """Test adding a tool without description uses default"""

    def my_function() -> str:
        return "result"

    tools = ToolCollection()
    tools.add("my_function", my_function)

    tool = tools.get("my_function")
    assert tool.description == "Executes my_function"


def test_get_nonexistent_tool():
    """Test getting a tool that doesn't exist returns None"""
    tools = ToolCollection()
    result = tools.get("nonexistent")
    assert result is None


def test_get_all_tools():
    """Test getting all tools"""

    def tool1() -> str:
        return "1"

    def tool2() -> str:
        return "2"

    tools = ToolCollection()
    tools.add("tool1", tool1)
    tools.add("tool2", tool2)

    all_tools = tools.get_all()
    assert len(all_tools) == 2
    names = {t.name for t in all_tools}
    assert "tool1" in names
    assert "tool2" in names


@pytest.mark.asyncio
async def test_execute_tool():
    """Test executing a tool with arguments"""

    def add(x: int, y: int) -> str:
        return str(x + y)

    tools = ToolCollection()
    tools.add("add", add)

    result = await tools.execute("add", '{"x": 10, "y": 20}')
    assert result == "30"


@pytest.mark.asyncio
async def test_execute_async_tool():
    """Test executing an async tool"""

    async def async_uppercase(text: str) -> str:
        return text.upper()

    tools = ToolCollection()
    tools.add("uppercase", async_uppercase)

    result = await tools.execute("uppercase", '{"text": "hello"}')
    assert result == "HELLO"


@pytest.mark.asyncio
async def test_execute_nonexistent_tool():
    """Test executing a tool that doesn't exist raises error"""
    tools = ToolCollection()

    with pytest.raises(ValueError, match="Tool 'missing' not found"):
        await tools.execute("missing", "{}")


@pytest.mark.asyncio
async def test_execute_with_invalid_json():
    """Test executing with invalid JSON raises error"""

    def dummy() -> str:
        return "result"

    tools = ToolCollection()
    tools.add("dummy", dummy)

    with pytest.raises(ValueError, match="Invalid JSON arguments"):
        await tools.execute("dummy", "not json")


@pytest.mark.asyncio
async def test_execute_missing_required_param():
    """Test executing without required parameter raises error"""

    def needs_param(required_arg: str) -> str:
        return required_arg

    tools = ToolCollection()
    tools.add("needs_param", needs_param)

    with pytest.raises(ValueError, match="Missing required parameter"):
        await tools.execute("needs_param", "{}")


def test_schema_generation_basic():
    """Test schema generation for basic types"""

    def typed_function(name: str, age: int, score: float, active: bool) -> str:
        return "result"

    tools = ToolCollection()
    tools.add("typed", typed_function)

    tool = tools.get("typed")
    schema = tool.schema

    assert schema["type"] == "object"
    assert "properties" in schema
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["age"]["type"] == "integer"
    assert schema["properties"]["score"]["type"] == "number"
    assert schema["properties"]["active"]["type"] == "boolean"
    assert set(schema["required"]) == {"name", "age", "score", "active"}


def test_schema_generation_optional_params():
    """Test schema generation with optional parameters"""

    def with_default(required: str, optional: str = "default") -> str:
        return required + optional

    tools = ToolCollection()
    tools.add("with_default", with_default)

    tool = tools.get("with_default")
    schema = tool.schema

    assert "required" in schema
    assert "required" in schema["required"]
    assert "optional" not in schema["required"]


def test_iteration():
    """Test iterating over tools"""

    def tool1() -> str:
        return "1"

    def tool2() -> str:
        return "2"

    tools = ToolCollection()
    tools.add("tool1", tool1)
    tools.add("tool2", tool2)

    tool_list = list(tools)
    assert len(tool_list) == 2
    assert all(isinstance(t, ToolDefinition) for t in tool_list)


@pytest.mark.asyncio
async def test_tool_definition_execute():
    """Test ToolDefinition execute method directly"""

    def multiply(a: int, b: int) -> str:
        return str(a * b)

    tool = ToolDefinition(
        name="multiply",
        description="Multiplies two numbers",
        schema={"type": "object", "properties": {}, "required": []},
        handler=multiply,
    )

    result = await tool.execute('{"a": 6, "b": 7}')
    assert result == "42"
