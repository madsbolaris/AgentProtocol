# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tool schema generation utilities.

Generates JSON schemas from Python function signatures using introspection.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, get_args, get_origin


class ToolSchemaGenerator:
    """
    Generates JSON schemas from Python functions using introspection.

    Shared utility across Client and Hosting SDKs for consistent schema generation.

    Example:
        >>> def greet(name: str, age: int) -> str:
        ...     return f"{name} is {age}"
        >>>
        >>> schema = ToolSchemaGenerator.generate_schema(greet)
        >>> schema["type"]
        'object'
        >>> schema["properties"]["name"]["type"]
        'string'
        >>> schema["required"]
        ['name', 'age']
    """

    @staticmethod
    def generate_schema(handler: Callable[..., Any]) -> Dict[str, Any]:
        """
        Generate JSON schema from function signature.

        Args:
            handler: The function to analyze

        Returns:
            JSON Schema dictionary describing the parameters

        Raises:
            TypeError: If handler is not callable

        Example:
            >>> def search(query: str, limit: int = 10) -> str:
            ...     return f"Searching for {query}"
            >>>
            >>> schema = ToolSchemaGenerator.generate_schema(search)
            >>> schema["properties"]["query"]["type"]
            'string'
            >>> schema["required"]
            ['query']
        """
        if not callable(handler):
            raise TypeError(f"Expected callable, got {type(handler).__name__}")

        sig = inspect.signature(handler)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip self/cls parameters
            if param_name in ('self', 'cls'):
                continue

            param_type = param.annotation
            properties[param_name] = {
                "type": ToolSchemaGenerator._get_json_type(param_type),
                "description": f"Parameter {param_name}"
            }

            # Check if parameter is required (no default value)
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required if required else []
        }

    @staticmethod
    def generate_schema_with_descriptions(
        handler: Callable[..., Any],
        descriptions: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON schema with custom parameter descriptions.

        Args:
            handler: The function to analyze
            descriptions: Dictionary mapping parameter names to descriptions

        Returns:
            JSON Schema dictionary with custom descriptions

        Example:
            >>> def greet(name: str, age: int) -> str:
            ...     return f"{name} is {age}"
            >>>
            >>> descriptions = {
            ...     "name": "The person's name",
            ...     "age": "The person's age in years"
            ... }
            >>> schema = ToolSchemaGenerator.generate_schema_with_descriptions(
            ...     greet, descriptions
            ... )
            >>> schema["properties"]["name"]["description"]
            "The person's name"
        """
        schema = ToolSchemaGenerator.generate_schema(handler)

        if descriptions:
            for param_name, description in descriptions.items():
                if param_name in schema["properties"]:
                    schema["properties"][param_name]["description"] = description

        return schema

    @staticmethod
    def _get_json_type(python_type: Any) -> str:
        """
        Map Python type annotations to JSON Schema types.

        Args:
            python_type: The Python type annotation

        Returns:
            JSON Schema type string
        """
        # Handle None/NoneType
        if python_type is None or python_type is type(None):
            return "null"

        # Handle Any
        if python_type is Any:
            return "string"  # Default to string for Any

        # Get origin type for generics (List[str] -> list)
        origin = get_origin(python_type)

        if origin is not None:
            # Handle List, list
            if origin in (list, List):
                return "array"
            # Handle Dict, dict
            if origin in (dict, Dict):
                return "object"
            # Handle Optional (Union with None)
            if hasattr(python_type, '__args__'):
                args = get_args(python_type)
                if type(None) in args:
                    # Optional[T] - return type of T
                    non_none_types = [t for t in args if t is not type(None)]
                    if non_none_types:
                        return ToolSchemaGenerator._get_json_type(non_none_types[0])

        # Handle basic types
        if python_type == str:
            return "string"
        elif python_type == int:
            return "integer"
        elif python_type in (float, complex):
            return "number"
        elif python_type == bool:
            return "boolean"
        elif python_type in (list, List):
            return "array"
        elif python_type in (dict, Dict):
            return "object"

        # Default to string for unknown types
        return "string"

    @staticmethod
    def create_object_schema(
        properties: Dict[str, Dict[str, Any]],
        required: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a JSON schema for an object with specified properties.

        Args:
            properties: Dictionary of property schemas
            required: Optional list of required property names

        Returns:
            JSON Schema dictionary

        Example:
            >>> schema = ToolSchemaGenerator.create_object_schema(
            ...     properties={
            ...         "name": {"type": "string", "description": "User name"},
            ...         "age": {"type": "integer", "description": "User age"}
            ...     },
            ...     required=["name"]
            ... )
            >>> schema["type"]
            'object'
            >>> schema["required"]
            ['name']
        """
        return {
            "type": "object",
            "properties": properties,
            "required": required or []
        }

    @staticmethod
    def create_array_schema(
        items: Dict[str, Any],
        description: Optional[str] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a JSON schema for an array.

        Args:
            items: Schema for array items
            description: Optional array description
            min_items: Optional minimum number of items
            max_items: Optional maximum number of items

        Returns:
            JSON Schema dictionary

        Example:
            >>> schema = ToolSchemaGenerator.create_array_schema(
            ...     items={"type": "string"},
            ...     description="List of tags",
            ...     min_items=1,
            ...     max_items=10
            ... )
            >>> schema["type"]
            'array'
            >>> schema["minItems"]
            1
        """
        schema = {
            "type": "array",
            "items": items
        }

        if description:
            schema["description"] = description
        if min_items is not None:
            schema["minItems"] = min_items
        if max_items is not None:
            schema["maxItems"] = max_items

        return schema

    @staticmethod
    def validate_schema(schema: Dict[str, Any]) -> None:
        """
        Validate a JSON schema.

        Args:
            schema: The schema to validate

        Raises:
            ValueError: If schema is invalid

        Example:
            >>> schema = {"type": "object", "properties": {}}
            >>> ToolSchemaGenerator.validate_schema(schema)  # OK
            >>>
            >>> invalid = {"properties": {}}  # Missing type
            >>> ToolSchemaGenerator.validate_schema(invalid)  # Raises ValueError
        """
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

        if "type" not in schema:
            raise ValueError("Schema must have a 'type' field")

        schema_type = schema["type"]

        if schema_type == "object" and "properties" not in schema:
            raise ValueError("Object schema must have 'properties' field")

        if schema_type == "array" and "items" not in schema:
            raise ValueError("Array schema must have 'items' field")

        # Recursively validate nested schemas
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                try:
                    ToolSchemaGenerator.validate_schema(prop_schema)
                except ValueError as e:
                    raise ValueError(f"Invalid schema for property '{prop_name}': {e}")

        if "items" in schema and isinstance(schema["items"], dict):
            ToolSchemaGenerator.validate_schema(schema["items"])
