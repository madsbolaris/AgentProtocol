# microsoft-agents-common

Shared utilities for Microsoft Agents Protocol Client and Hosting SDKs.

## Overview

This package provides common utilities that are used by both the Client SDK (`microsoft-agents-protocol`) and the Hosting SDK (`microsoft-agents-hosting`). It eliminates duplication of tool-related functionality across the SDKs.

## Features

### Tool Schema Generation

Automatic JSON schema generation from Python function signatures:

```python
from microsoft.agents.common import ToolSchemaGenerator

def greet(name: str, age: int) -> str:
    return f"{name} is {age}"

schema = ToolSchemaGenerator.generate_schema(greet)

# schema["type"] == "object"
# schema["properties"]["name"]["type"] == "string"
# schema["properties"]["age"]["type"] == "integer"
# schema["required"] == ["name", "age"]
```

### Tool Execution

Centralized tool execution with JSON argument binding and validation:

```python
from microsoft.agents.common import ToolExecutor

async def greet(name: str, age: int) -> str:
    return f"{name} is {age}"

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

result = await ToolExecutor.execute(
    greet,
    schema,
    '{"name": "Alice", "age": 30}'
)
# result == "Alice is 30"
```

## Installation

```bash
pip install microsoft-agents-common
```

## Dependencies

- `microsoft-agents-abstractions>=0.1.0` - Protocol models (auto-generated from TypeSpec)

## Usage

### In Client SDK

```python
from microsoft.agents.common import ToolSchemaGenerator, ToolExecutor
from microsoft.agents.protocol.client import ToolCollection

tools = ToolCollection()

def my_function(param1: str, param2: int) -> str:
    return f"Result: {param1} - {param2}"

# Internally uses ToolSchemaGenerator and ToolExecutor
tools.add("my_tool", my_function, "My tool description")
```

### In Hosting SDK

```python
from microsoft.agents.common import ToolSchemaGenerator
from microsoft.agents.hosting import FunctionBuilder

builder = FunctionBuilder()

async def my_function(query: str, limit: int = 10) -> str:
    # Function implementation
    return f"Results for {query}"

# Internally uses ToolSchemaGenerator
builder.add(
    "search",
    "Search for items",
    my_function,
    timeout=30.0
)
```

## API Reference

### ToolSchemaGenerator

Static utility class for generating JSON schemas:

- `generate_schema(handler)` - Generate schema from function signature
- `generate_schema_with_descriptions(handler, descriptions)` - Generate with custom descriptions
- `create_object_schema(properties, required)` - Create object schema
- `create_array_schema(items, description, min_items, max_items)` - Create array schema
- `validate_schema(schema)` - Validate a JSON schema

### ToolExecutor

Static utility class for executing tools:

- `execute(handler, schema, arguments_json)` - Execute with validation (async)
- `execute_unsafe(handler, arguments_json)` - Execute without validation (async)
- `validate_arguments(args, schema)` - Validate arguments against schema

## Type Mapping

| Python Type | JSON Schema Type |
|-------------|------------------|
| `str` | `"string"` |
| `int` | `"integer"` |
| `float` | `"number"` |
| `bool` | `"boolean"` |
| `list`, `List[T]` | `"array"` |
| `dict`, `Dict[K, V]` | `"object"` |
| `Optional[T]` | Type of `T` (nullable) |

## Error Handling

- `ValueError` - If validation fails or JSON is malformed
- `json.JSONDecodeError` - If JSON parsing fails
- `TypeError` - If handler is not callable
- Original exceptions from handler are preserved

## Examples

### Creating Complex Schemas

```python
from microsoft.agents.common import ToolSchemaGenerator

# Array of strings
tags_schema = ToolSchemaGenerator.create_array_schema(
    items={"type": "string"},
    description="List of tags",
    min_items=1,
    max_items=10
)

# Object with nested properties
user_schema = ToolSchemaGenerator.create_object_schema(
    properties={
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "integer", "minimum": 0, "maximum": 120},
        "tags": tags_schema
    },
    required=["name", "age"]
)
```

### Tool Execution with Validation

```python
from microsoft.agents.common import ToolExecutor

async def search_database(query: str, limit: int = 10) -> str:
    # Search implementation
    results = await db.search(query, limit)
    return f"Found {len(results)} results"

schema = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "limit": {"type": "integer", "minimum": 1, "maximum": 100}
    },
    "required": ["query"]
}

try:
    result = await ToolExecutor.execute(
        search_database,
        schema,
        '{"query": "python", "limit": 10}'
    )
    print(result)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Type Hints

This package includes type hints (PEP 561) for better IDE support:

```python
from microsoft.agents.common import ToolSchemaGenerator
from typing import Dict, Any

def my_tool(name: str, age: int) -> str:
    return f"{name} is {age}"

# Type hints work correctly
schema: Dict[str, Any] = ToolSchemaGenerator.generate_schema(my_tool)
```

## License

MIT - Copyright (c) Microsoft Corporation

## Related Packages

- [microsoft-agents-abstractions](../microsoft-agents-abstractions) - Protocol models
- [microsoft-agents-protocol](../microsoft-agents-protocol) - Client SDK
- [microsoft-agents-hosting](../microsoft-agents-hosting) - Hosting SDK
