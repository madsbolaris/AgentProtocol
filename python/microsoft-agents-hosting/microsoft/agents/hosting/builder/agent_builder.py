# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Agent builder for configuring individual agents."""

from typing import Callable, Optional, Any, Union
from dataclasses import dataclass

from ..core import (
    FunctionDefinition,
    UserMessageHandler,
    ReactionHandler,
    ErrorHandler,
)
from .function_builder import FunctionBuilder


@dataclass
class AgentConfiguration:
    """Configuration for an agent."""

    model: Optional[Union[str, Any]]
    instructions: Optional[str]
    functions: list[FunctionDefinition]
    user_message_handlers: list[UserMessageHandler]
    reaction_handlers: list[ReactionHandler]
    error_handler: Optional[ErrorHandler]


class AgentBuilder:
    """Builder for configuring an individual agent."""

    def __init__(self, services: dict[type, Any]) -> None:
        """Initialize a new agent builder."""
        self._services = services
        self._llm_model: Optional[Union[str, Any]] = None
        self._llm_instructions: Optional[str] = None
        self._functions: list[FunctionDefinition] = []
        self._user_message_handlers: list[UserMessageHandler] = []
        self._reaction_handlers: list[ReactionHandler] = []
        self._error_handler: Optional[ErrorHandler] = None

    def use_llm(self, model: Union[str, Any], instructions: str) -> "AgentBuilder":
        """
        Configure the LLM to use for this agent.

        Args:
            model: Model identifier (string) or LLM client instance.
                   String: "gpt-4", "claude-3-5-sonnet-20241022" (requires FOUNDRY_ENDPOINT/FOUNDRY_API_KEY).
                   Instance: Custom LLM client with provider_info, generate(), and stream() methods.
            instructions: System instructions for the agent.

        Returns:
            A new AgentBuilder with LLM configured.

        Raises:
            ValueError: If model or instructions is None or empty.

        Example:
            ```python
            # String-based (requires environment variables)
            agent.use_llm("gpt-4", "You are a helpful assistant.")

            # Provider instance (no environment variables needed)
            agent.use_llm(my_custom_client, "You are a helpful assistant.")
            ```
        """
        if model is None or (isinstance(model, str) and not model):
            raise ValueError("model cannot be None or empty")
        if not instructions:
            raise ValueError("instructions cannot be None or empty")

        new_builder = AgentBuilder(self._services)
        new_builder._llm_model = model
        new_builder._llm_instructions = instructions
        new_builder._functions = self._functions.copy()
        new_builder._user_message_handlers = self._user_message_handlers.copy()
        new_builder._reaction_handlers = self._reaction_handlers.copy()
        new_builder._error_handler = self._error_handler
        return new_builder

    def add_functions(
        self, configure: Callable[[FunctionBuilder], FunctionBuilder]
    ) -> "AgentBuilder":
        """
        Add functions/tools that the agent can call.

        Args:
            configure: A function that configures a FunctionBuilder.

        Returns:
            A new AgentBuilder with functions added.

        Example:
            ```python
            agent.add_functions(lambda f: f
                .add("get_time@v1", "Gets current time", get_time)
                .add("search@v1", "Search database", search, timeout=10.0)
            )
            ```
        """
        function_builder = FunctionBuilder()
        configured = configure(function_builder)
        functions = configured._build()

        new_builder = AgentBuilder(self._services)
        new_builder._llm_model = self._llm_model
        new_builder._llm_instructions = self._llm_instructions
        new_builder._functions = self._functions + functions
        new_builder._user_message_handlers = self._user_message_handlers.copy()
        new_builder._reaction_handlers = self._reaction_handlers.copy()
        new_builder._error_handler = self._error_handler
        return new_builder

    def on_user_message(self, handler: UserMessageHandler) -> "AgentBuilder":
        """
        Register a handler for user messages.

        Handlers are executed in order. If a handler returns REPLIED or CONSUMED,
        the chain stops and subsequent handlers are not executed.

        Args:
            handler: The message handler function.

        Returns:
            A new AgentBuilder with the handler registered.

        Example:
            ```python
            async def my_handler(msg, ctx, ct):
                await ctx.log_async(f"Got: {msg.text}")
                return TurnResult.CONTINUE

            agent.on_user_message(my_handler)
            ```
        """
        new_builder = AgentBuilder(self._services)
        new_builder._llm_model = self._llm_model
        new_builder._llm_instructions = self._llm_instructions
        new_builder._functions = self._functions.copy()
        new_builder._user_message_handlers = self._user_message_handlers + [handler]
        new_builder._reaction_handlers = self._reaction_handlers.copy()
        new_builder._error_handler = self._error_handler
        return new_builder

    def on_reaction(self, handler: ReactionHandler) -> "AgentBuilder":
        """
        Register a handler for reactions (emoji, likes, etc.).

        Args:
            handler: The reaction handler function.

        Returns:
            A new AgentBuilder with the handler registered.

        Example:
            ```python
            async def my_handler(reaction, ctx, ct):
                if reaction.emoji == "👍":
                    await ctx.respond_async("Thanks!")
                    return TurnResult.REPLIED
                return TurnResult.CONSUMED

            agent.on_reaction(my_handler)
            ```
        """
        new_builder = AgentBuilder(self._services)
        new_builder._llm_model = self._llm_model
        new_builder._llm_instructions = self._llm_instructions
        new_builder._functions = self._functions.copy()
        new_builder._user_message_handlers = self._user_message_handlers.copy()
        new_builder._reaction_handlers = self._reaction_handlers + [handler]
        new_builder._error_handler = self._error_handler
        return new_builder

    def on_error(self, handler: ErrorHandler) -> "AgentBuilder":
        """
        Register a handler for errors.

        The error handler is called when an exception occurs during message processing.
        It can handle the error, retry, or propagate it.

        Args:
            handler: The error handler function.

        Returns:
            A new AgentBuilder with the error handler registered.

        Example:
            ```python
            async def my_error_handler(error, ctx, ct):
                if isinstance(error, RateLimitError):
                    await ctx.respond_async("Too many requests. Please try again later.")
                    return ErrorHandlingResult.HANDLED
                return ErrorHandlingResult.UNHANDLED

            agent.on_error(my_error_handler)
            ```
        """
        new_builder = AgentBuilder(self._services)
        new_builder._llm_model = self._llm_model
        new_builder._llm_instructions = self._llm_instructions
        new_builder._functions = self._functions.copy()
        new_builder._user_message_handlers = self._user_message_handlers.copy()
        new_builder._reaction_handlers = self._reaction_handlers.copy()
        new_builder._error_handler = handler
        return new_builder

    def _build(self) -> AgentConfiguration:
        """Build the agent configuration (internal)."""
        return AgentConfiguration(
            model=self._llm_model,
            instructions=self._llm_instructions,
            functions=self._functions,
            user_message_handlers=self._user_message_handlers,
            reaction_handlers=self._reaction_handlers,
            error_handler=self._error_handler,
        )
