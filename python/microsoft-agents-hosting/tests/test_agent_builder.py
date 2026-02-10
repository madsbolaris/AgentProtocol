# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Comprehensive tests for AgentBuilder."""

import pytest
from microsoft.agents.hosting.builder import AgentBuilder, FunctionBuilder
from microsoft.agents.hosting import (
    TurnResult,
    IAgentContext,
    CancellationToken,
    UserMessage,
    MessageReaction,
)
from typing import Optional


def test_agent_builder_creation():
    """Test creating an AgentBuilder."""
    services = {}
    builder = AgentBuilder(services)
    assert builder is not None
    assert builder._services == services


def test_agent_builder_use_llm():
    """Test configuring LLM."""
    services = {}
    builder = AgentBuilder(services)

    builder = builder.use_llm("gpt-4", "You are helpful.")

    config = builder._build()
    assert config.model == "gpt-4"
    assert config.instructions == "You are helpful."


def test_agent_builder_use_llm_validation():
    """Test that use_llm validates inputs."""
    services = {}
    builder = AgentBuilder(services)

    with pytest.raises(ValueError, match="model cannot be None or empty"):
        builder.use_llm("", "Instructions")

    with pytest.raises(ValueError, match="instructions cannot be None or empty"):
        builder.use_llm("gpt-4", "")


def test_agent_builder_add_functions():
    """Test adding functions to an agent."""
    services = {}
    builder = AgentBuilder(services)

    def test_func() -> str:
        return "test"

    builder = builder.add_functions(lambda f: f
        .add("test@v1", "Test function", test_func)
    )

    config = builder._build()
    assert len(config.functions) == 1
    assert config.functions[0].name == "test@v1"


def test_agent_builder_add_multiple_functions():
    """Test adding multiple functions."""
    services = {}
    builder = AgentBuilder(services)

    def func1() -> str:
        return "1"

    def func2() -> str:
        return "2"

    builder = builder.add_functions(lambda f: f
        .add("func1@v1", "Function 1", func1)
        .add("func2@v1", "Function 2", func2)
    )

    config = builder._build()
    assert len(config.functions) == 2


def test_agent_builder_chain_add_functions():
    """Test chaining multiple add_functions calls."""
    services = {}
    builder = AgentBuilder(services)

    def func1() -> str:
        return "1"

    def func2() -> str:
        return "2"

    builder = (builder
        .add_functions(lambda f: f.add("func1@v1", "Function 1", func1))
        .add_functions(lambda f: f.add("func2@v1", "Function 2", func2))
    )

    config = builder._build()
    assert len(config.functions) == 2
    assert config.functions[0].name == "func1@v1"
    assert config.functions[1].name == "func2@v1"


@pytest.mark.asyncio
async def test_agent_builder_on_user_message():
    """Test adding user message handler."""
    services = {}
    builder = AgentBuilder(services)

    async def handler(msg: UserMessage, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONTINUE

    builder = builder.on_user_message(handler)

    config = builder._build()
    assert len(config.user_message_handlers) == 1


@pytest.mark.asyncio
async def test_agent_builder_multiple_message_handlers():
    """Test adding multiple message handlers."""
    services = {}
    builder = AgentBuilder(services)

    async def handler1(msg: UserMessage, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONTINUE

    async def handler2(msg: UserMessage, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONTINUE

    builder = (builder
        .on_user_message(handler1)
        .on_user_message(handler2)
    )

    config = builder._build()
    assert len(config.user_message_handlers) == 2


@pytest.mark.asyncio
async def test_agent_builder_on_reaction():
    """Test adding reaction handler."""
    services = {}
    builder = AgentBuilder(services)

    async def handler(reaction: MessageReaction, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONSUMED

    builder = builder.on_reaction(handler)

    config = builder._build()
    assert len(config.reaction_handlers) == 1


@pytest.mark.asyncio
async def test_agent_builder_multiple_reaction_handlers():
    """Test adding multiple reaction handlers."""
    services = {}
    builder = AgentBuilder(services)

    async def handler1(reaction: MessageReaction, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONSUMED

    async def handler2(reaction: MessageReaction, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONSUMED

    builder = (builder
        .on_reaction(handler1)
        .on_reaction(handler2)
    )

    config = builder._build()
    assert len(config.reaction_handlers) == 2


@pytest.mark.asyncio
async def test_agent_builder_on_error():
    """Test adding error handler."""
    services = {}
    builder = AgentBuilder(services)

    async def handler(error: Exception, ctx: IAgentContext, ct: Optional[CancellationToken]) -> any:
        return None

    builder = builder.on_error(handler)

    config = builder._build()
    assert config.error_handler is not None


@pytest.mark.asyncio
async def test_agent_builder_error_handler_override():
    """Test that error handler is overridden."""
    services = {}
    builder = AgentBuilder(services)

    async def handler1(error: Exception, ctx: IAgentContext, ct: Optional[CancellationToken]) -> any:
        return "handler1"

    async def handler2(error: Exception, ctx: IAgentContext, ct: Optional[CancellationToken]) -> any:
        return "handler2"

    builder = builder.on_error(handler1).on_error(handler2)

    config = builder._build()
    assert config.error_handler == handler2


def test_agent_builder_immutability():
    """Test that AgentBuilder is immutable."""
    services = {}
    builder1 = AgentBuilder(services)
    builder2 = builder1.use_llm("gpt-4", "Instructions")

    assert builder1 is not builder2
    assert builder1._llm_model is None
    assert builder2._llm_model == "gpt-4"


def test_agent_builder_full_configuration():
    """Test building a fully configured agent."""
    services = {}

    def test_func() -> str:
        return "test"

    async def message_handler(msg: UserMessage, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONTINUE

    async def reaction_handler(reaction: MessageReaction, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONSUMED

    async def error_handler(error: Exception, ctx: IAgentContext, ct: Optional[CancellationToken]) -> any:
        return None

    builder = (AgentBuilder(services)
        .use_llm("gpt-4", "You are helpful.")
        .add_functions(lambda f: f.add("test@v1", "Test", test_func))
        .on_user_message(message_handler)
        .on_reaction(reaction_handler)
        .on_error(error_handler)
    )

    config = builder._build()
    assert config.model == "gpt-4"
    assert config.instructions == "You are helpful."
    assert len(config.functions) == 1
    assert len(config.user_message_handlers) == 1
    assert len(config.reaction_handlers) == 1
    assert config.error_handler is not None


def test_agent_builder_build_without_llm():
    """Test building an agent without LLM configuration."""
    services = {}
    builder = AgentBuilder(services)

    config = builder._build()
    assert config.model is None
    assert config.instructions is None


def test_agent_builder_build_empty():
    """Test building an empty agent."""
    services = {}
    builder = AgentBuilder(services)

    config = builder._build()
    assert config.model is None
    assert config.instructions is None
    assert len(config.functions) == 0
    assert len(config.user_message_handlers) == 0
    assert len(config.reaction_handlers) == 0
    assert config.error_handler is None


def test_agent_builder_preserves_services():
    """Test that services are preserved across builder operations."""
    services = {"key": "value"}
    builder1 = AgentBuilder(services)
    builder2 = builder1.use_llm("gpt-4", "Instructions")

    assert builder1._services == services
    assert builder2._services == services


def test_agent_builder_async_function():
    """Test adding an async function."""
    services = {}
    builder = AgentBuilder(services)

    async def async_func() -> str:
        return "async result"

    builder = builder.add_functions(lambda f: f
        .add("async@v1", "Async function", async_func)
    )

    config = builder._build()
    assert len(config.functions) == 1


def test_agent_builder_function_with_parameters():
    """Test adding a function with parameters."""
    services = {}
    builder = AgentBuilder(services)

    def func_with_params(a: int, b: str) -> str:
        return f"{a} {b}"

    builder = builder.add_functions(lambda f: f
        .add("with_params@v1", "Function with params", func_with_params)
    )

    config = builder._build()
    assert len(config.functions) == 1
    func = config.functions[0]
    assert "a" in func.parameters
    assert "b" in func.parameters


def test_agent_builder_chaining():
    """Test method chaining."""
    services = {}

    def func1() -> str:
        return "1"

    async def handler1(msg: UserMessage, ctx: IAgentContext, ct: Optional[CancellationToken]) -> TurnResult:
        return TurnResult.CONTINUE

    builder = (AgentBuilder(services)
        .use_llm("gpt-4", "Instructions")
        .add_functions(lambda f: f.add("func1@v1", "Function 1", func1))
        .on_user_message(handler1)
    )

    config = builder._build()
    assert config.model == "gpt-4"
    assert len(config.functions) == 1
    assert len(config.user_message_handlers) == 1


def test_agent_builder_independence():
    """Test that multiple builders are independent."""
    services = {}

    builder1 = AgentBuilder(services).use_llm("gpt-4", "Instructions 1")
    builder2 = AgentBuilder(services).use_llm("claude-3", "Instructions 2")

    config1 = builder1._build()
    config2 = builder2._build()

    assert config1.model == "gpt-4"
    assert config2.model == "claude-3"
    assert config1.instructions == "Instructions 1"
    assert config2.instructions == "Instructions 2"


def test_agent_builder_state_isolation():
    """Test that builder state is isolated between instances."""
    services = {}

    def func1() -> str:
        return "1"

    def func2() -> str:
        return "2"

    builder1 = (AgentBuilder(services)
        .add_functions(lambda f: f.add("func1@v1", "Function 1", func1))
    )

    builder2 = (AgentBuilder(services)
        .add_functions(lambda f: f.add("func2@v1", "Function 2", func2))
    )

    config1 = builder1._build()
    config2 = builder2._build()

    assert len(config1.functions) == 1
    assert len(config2.functions) == 1
    assert config1.functions[0].name == "func1@v1"
    assert config2.functions[0].name == "func2@v1"
