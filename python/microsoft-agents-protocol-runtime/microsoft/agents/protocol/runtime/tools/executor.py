# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tool execution utilities.

Executes tools/functions with JSON arguments and validation.
"""

import asyncio
import inspect
import json
from typing import Any, Callable, Dict, Union, Awaitable


class ToolExecutor:
    """
    Executes tools/functions with JSON arguments.

    Shared utility across Client and Hosting SDKs for consistent tool execution.

    Example:
        >>> async def greet(name: str, age: int) -> str:
        ...     return f"{name} is {age}"
        >>>
        >>> schema = {"type": "object", "properties": {...}, "required": ["name", "age"]}
        >>> result = await ToolExecutor.execute(greet, schema, '{"name": "Alice", "age": 30}')
        >>> result
        'Alice is 30'
    """

    @staticmethod
    async def execute(
        handler: Union[Callable[..., str], Callable[..., Awaitable[str]]],
        schema: Dict[str, Any],
        arguments_json: str
    ) -> str:
        """
        Execute a tool with JSON arguments.

        Args:
            handler: The function to execute (sync or async)
            schema: JSON schema for validation
            arguments_json: JSON-encoded arguments

        Returns:
            Tool execution result as string

        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If validation fails
            Exception: If handler execution fails

        Example:
            >>> async def search(query: str, limit: int = 10) -> str:
            ...     return f"Found {limit} results for {query}"
            >>>
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {
            ...         "query": {"type": "string"},
            ...         "limit": {"type": "integer"}
            ...     },
            ...     "required": ["query"]
            ... }
            >>>
            >>> result = await ToolExecutor.execute(
            ...     search,
            ...     schema,
            ...     '{"query": "python", "limit": 5}'
            ... )
            >>> result
            'Found 5 results for python'
        """
        # Parse JSON arguments
        try:
            args = json.loads(arguments_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}")

        # Validate arguments against schema
        ToolExecutor.validate_arguments(args, schema)

        # Get function signature
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())

        # Build keyword arguments
        kwargs = {}
        for param in params:
            param_name = param.name
            if param_name in ('self', 'cls'):
                continue

            if param_name in args:
                kwargs[param_name] = args[param_name]
            elif param.default is not inspect.Parameter.empty:
                # Use default value
                kwargs[param_name] = param.default
            else:
                raise ValueError(f"Missing required parameter: {param_name}")

        # Execute handler
        try:
            result = handler(**kwargs)

            # Handle async results
            if inspect.iscoroutine(result):
                result = await result

            return str(result) if result is not None else ""

        except Exception:
            # Re-raise original exception
            raise

    @staticmethod
    async def execute_unsafe(
        handler: Union[Callable[..., str], Callable[..., Awaitable[str]]],
        arguments_json: str
    ) -> str:
        """
        Execute a tool without schema validation (use with caution).

        Args:
            handler: The function to execute
            arguments_json: JSON-encoded arguments

        Returns:
            Tool execution result as string

        Example:
            >>> async def echo(message: str) -> str:
            ...     return message
            >>>
            >>> result = await ToolExecutor.execute_unsafe(
            ...     echo,
            ...     '{"message": "Hello!"}'
            ... )
            >>> result
            'Hello!'
        """
        # Parse JSON arguments
        try:
            args = json.loads(arguments_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON arguments: {e}")

        # Get function signature
        sig = inspect.signature(handler)
        params = list(sig.parameters.values())

        # Build keyword arguments
        kwargs = {}
        for param in params:
            param_name = param.name
            if param_name in ('self', 'cls'):
                continue

            if param_name in args:
                kwargs[param_name] = args[param_name]

        # Execute handler
        result = handler(**kwargs)

        # Handle async results
        if inspect.iscoroutine(result):
            result = await result

        return str(result) if result is not None else ""

    @staticmethod
    def validate_arguments(args: Any, schema: Dict[str, Any]) -> None:
        """
        Validate arguments against a JSON schema.

        Args:
            args: The arguments to validate
            schema: The schema to validate against

        Raises:
            ValueError: If validation fails

        Example:
            >>> schema = {
            ...     "type": "object",
            ...     "properties": {"name": {"type": "string"}},
            ...     "required": ["name"]
            ... }
            >>>
            >>> ToolExecutor.validate_arguments({"name": "Alice"}, schema)  # OK
            >>> ToolExecutor.validate_arguments({}, schema)  # Raises ValueError
        """
        schema_type = schema.get("type")

        # Type validation
        if schema_type == "object" and not isinstance(args, dict):
            raise ValueError(f"Expected object, got {type(args).__name__}")

        if schema_type == "array" and not isinstance(args, list):
            raise ValueError(f"Expected array, got {type(args).__name__}")

        if schema_type == "string" and not isinstance(args, str):
            raise ValueError(f"Expected string, got {type(args).__name__}")

        if schema_type == "number" and not isinstance(args, (int, float)):
            raise ValueError(f"Expected number, got {type(args).__name__}")

        if schema_type == "integer" and not isinstance(args, int):
            raise ValueError(f"Expected integer, got {type(args).__name__}")

        if schema_type == "boolean" and not isinstance(args, bool):
            raise ValueError(f"Expected boolean, got {type(args).__name__}")

        # Required properties validation
        if schema_type == "object" and "required" in schema:
            for required_prop in schema["required"]:
                if required_prop not in args:
                    raise ValueError(f"Missing required parameter: {required_prop}")

        # Property type validation
        if schema_type == "object" and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in args:
                    try:
                        ToolExecutor.validate_arguments(args[prop_name], prop_schema)
                    except ValueError as e:
                        raise ValueError(f"Validation error for property '{prop_name}': {e}")

        # Array items validation
        if schema_type == "array" and "items" in schema:
            for i, item in enumerate(args):
                try:
                    ToolExecutor.validate_arguments(item, schema["items"])
                except ValueError as e:
                    raise ValueError(f"Validation error for item [{i}]: {e}")

        # Enum validation
        if "enum" in schema and args not in schema["enum"]:
            raise ValueError(f"Value must be one of: {', '.join(map(str, schema['enum']))}")

        # Number range validation
        if schema_type in ("number", "integer"):
            if "minimum" in schema and args < schema["minimum"]:
                raise ValueError(f"Value {args} is less than minimum {schema['minimum']}")
            if "maximum" in schema and args > schema["maximum"]:
                raise ValueError(f"Value {args} is greater than maximum {schema['maximum']}")

        # String length validation
        if schema_type == "string":
            if "minLength" in schema and len(args) < schema["minLength"]:
                raise ValueError(
                    f"String length {len(args)} is less than minimum {schema['minLength']}"
                )
            if "maxLength" in schema and len(args) > schema["maxLength"]:
                raise ValueError(
                    f"String length {len(args)} is greater than maximum {schema['maxLength']}"
                )
            if "pattern" in schema:
                import re
                if not re.match(schema["pattern"], args):
                    raise ValueError(f"String does not match pattern: {schema['pattern']}")

        # Array length validation
        if schema_type == "array":
            if "minItems" in schema and len(args) < schema["minItems"]:
                raise ValueError(
                    f"Array length {len(args)} is less than minimum {schema['minItems']}"
                )
            if "maxItems" in schema and len(args) > schema["maxItems"]:
                raise ValueError(
                    f"Array length {len(args)} is greater than maximum {schema['maxItems']}"
                )
