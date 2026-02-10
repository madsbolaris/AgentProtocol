# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Function builder for adding functions/tools to agents."""

import inspect
from typing import Callable, Any, Awaitable, get_type_hints

from ..core import FunctionDefinition, ConfigurationError


class FunctionBuilder:
    """Builder for adding functions/tools to an agent."""

    def __init__(self) -> None:
        """Initialize a new function builder."""
        self._functions: list[FunctionDefinition] = []

    def add(
        self,
        name: str,
        description: str,
        implementation: Callable[..., str] | Callable[..., Awaitable[str]],
        timeout: float = 30.0,
        require_approval: bool = False,
    ) -> "FunctionBuilder":
        """
        Add a function with automatic parameter type inference.

        Args:
            name: Function name (include @v1 suffix for versioning).
            description: Human-readable description for the LLM.
            implementation: The function implementation (sync or async).
            timeout: Maximum execution time in seconds (default: 30.0).
            require_approval: Whether this function requires user approval before execution.

        Returns:
            A new FunctionBuilder with the function added.

        Example:
            ```python
            # No parameters
            f.add("get_time@v1", "Gets time", lambda: datetime.now().isoformat())

            # With parameters (types inferred from hints)
            f.add("sum@v1", "Add numbers", lambda a: int, b: int: str(a + b))

            # Async function with timeout
            async def fetch_data(url: str) -> str:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    return response.text

            f.add("fetch@v1", "Fetch data", fetch_data, timeout=10.0)

            # Function requiring approval
            f.add("delete_data@v1", "Delete data", delete_data, require_approval=True)
            ```
        """
        # Extract parameter types from function signature
        try:
            sig = inspect.signature(implementation)
            type_hints = get_type_hints(implementation)
        except Exception as e:
            raise ConfigurationError(f"Failed to inspect function {name}: {e}")

        parameters: dict[str, type] = {}
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, Any)
            parameters[param_name] = param_type

        function_def = FunctionDefinition(
            name=name,
            description=description,
            implementation=implementation,
            parameters=parameters,
            timeout=timeout,
            require_approval=require_approval,
        )

        new_builder = FunctionBuilder()
        new_builder._functions = self._functions + [function_def]
        return new_builder

    def _build(self) -> list[FunctionDefinition]:
        """Build the function list (internal)."""
        return self._functions.copy()
