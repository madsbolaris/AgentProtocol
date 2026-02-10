#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Basic agent example demonstrating the core features of the hosting SDK.
"""

from microsoft.agents.hosting import (
    AgentHostBuilder,
    TurnResult,
    IAgentContext,
    CancellationToken,
    UserMessage,
    MessageReaction,
)
from datetime import datetime
from typing import Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define some functions that the agent can call
def get_time() -> str:
    """Get the current UTC time."""
    return datetime.utcnow().isoformat()


def word_count(text: str) -> str:
    """Count words in the provided text."""
    if not text:
        return "0"
    return str(len(text.split()))


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    IMPORTANT: This is a simplified example. In production, use a proper
    math expression parser library like 'numexpr' or 'simpleeval'.
    """
    try:
        # Basic validation
        expression = expression.strip()
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"

        # NOTE: eval() is dangerous! Use a proper parser in production!
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        logger.error(f"Calculate error: {e}")
        return f"Error: Could not calculate"


# Message handler for custom commands
async def on_user_message(
    message: UserMessage,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """Handle user messages and custom commands."""
    logger.info(f"Thread {context.thread_id}: User message received")

    # Get message text
    message_text = message.text or ""

    # Handle special commands
    if message_text.lower().startswith("/"):
        command = message_text.lower().split()[0]

        if command == "/help":
            help_text = """
Available commands:
/help - Show this help
/about - About this agent
/stats - Show conversation statistics

You can also:
- Ask me to tell you the time
- Ask me to count words in text
- Ask me to calculate math expressions
            """.strip()
            await context.respond_async(help_text)
            return TurnResult.REPLIED

        elif command == "/about":
            await context.respond_async(
                "I'm a helpful AI assistant built with the Microsoft Agents Protocol Hosting SDK. "
                "I can answer questions and perform various tasks using built-in functions."
            )
            return TurnResult.REPLIED

        elif command == "/stats":
            # Use state to track message count
            count = await context.state.get_async("message_count", default=0)
            await context.respond_async(
                f"This is message #{count + 1} in this conversation."
            )
            # Don't increment here, let it pass through
            return TurnResult.CONTINUE

    # Track message count in state
    count = await context.state.get_async("message_count", default=0)
    await context.state.set_async("message_count", count + 1)
    await context.state.set_async("last_message", message_text)
    await context.state.set_async("last_message_time", datetime.utcnow().isoformat())

    # Let LLM handle everything else
    return TurnResult.CONTINUE


# Reaction handler
async def on_reaction(
    reaction: MessageReaction,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """Handle emoji reactions."""
    emoji = reaction.type
    logger.info(f"Received reaction: {emoji}")

    if emoji == "👍":
        await context.respond_async("Thanks for the positive feedback!")
        return TurnResult.REPLIED

    # Just log other reactions, don't respond
    return TurnResult.CONSUMED


# Create the agent
agent_host = (
    AgentHostBuilder()
    .add_default_agent(lambda agent: agent
        .use_llm("gpt-4", "You are a helpful assistant with a friendly personality. "
                         "When users ask about time, use the get_time function. "
                         "When users ask about word counts, use the word_count function. "
                         "When users ask math questions, use the calculate function.")
        .add_functions(lambda f: f
            .add("get_time@v1", "Gets the current UTC time in ISO format", get_time)
            .add("calculate@v1",
                 "Evaluate a basic math expression (e.g., '2 + 2' or '10 * 5')",
                 calculate)
            .add("word_count@v1", "Count the number of words in text", word_count)
        )
        .on_user_message(on_user_message)
        .on_reaction(on_reaction)
    )
    .build()
)


if __name__ == "__main__":
    print("=" * 60)
    print("Basic Agent Example")
    print("=" * 60)
    print("\nAgent is starting...")
    print("Try sending messages or use commands like /help, /about, /stats")
    print("\nPress Ctrl+C to stop.\n")

    try:
        agent_host.run()
    except KeyboardInterrupt:
        print("\n\nAgent stopped.")
