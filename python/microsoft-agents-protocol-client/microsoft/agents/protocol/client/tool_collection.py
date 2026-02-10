# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tool collection for registering and executing functions"""

import json
import inspect
from typing import Callable, Optional, List, Dict, Any, Union, Awaitable
from dataclasses import dataclass
from microsoft.agents.protocol.runtime.tools.schema_generator import ToolSchemaGenerator
from microsoft.agents.protocol.runtime.tools.executor import ToolExecutor


@dataclass
class ToolDefinition:
    """Represents a single tool definition"""

    name: str
    """Tool name"""

    description: str
    """Tool description"""

    schema: Dict[str, Any]
    """JSON schema for tool parameters"""

    handler: Callable[..., Union[str, Awaitable[str]]]
    """Handler function (sync or async)"""

    async def execute(self, arguments_json: str) -> Any:
        """
        Executes the tool with JSON arguments.

        Args:
            arguments_json: JSON string with arguments

        Returns:
            Tool execution result
        """
        return await ToolExecutor.execute(self.handler, self.schema, arguments_json)


class ToolCollection:
    """
    Collection of tools (functions) that can be called by the agent.
    Supports lambda functions with automatic schema generation.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def add(
        self,
        name: str,
        handler: Callable[..., Union[str, Awaitable[str]]],
        description: Optional[str] = None,
    ) -> None:
        """
        Adds a tool to the collection.

        Args:
            name: Tool name
            handler: Handler function (sync or async)
            description: Optional tool description
        """
        tool = ToolDefinition(
            name=name,
            description=description or f"Executes {name}",
            schema=ToolSchemaGenerator.generate_schema(handler),
            handler=handler,
        )
        self._tools[name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        """
        Gets a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool definition or None if not found
        """
        return self._tools.get(name)

    def get_all(self) -> List[ToolDefinition]:
        """
        Gets all tool definitions.

        Returns:
            List of all tools
        """
        return list(self._tools.values())

    async def execute(self, tool_name: str, arguments_json: str) -> Any:
        """
        Executes a tool by name with JSON arguments.

        Args:
            tool_name: Name of tool to execute
            arguments_json: JSON string with arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        return await tool.execute(arguments_json)

    def __iter__(self):
        """Allows iteration over tool definitions"""
        return iter(self._tools.values())

    def __len__(self):
        """Returns number of tools"""
        return len(self._tools)
