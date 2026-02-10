#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Production agent example with state management, error handling, and monitoring.
"""

from microsoft.agents.hosting import (
    AgentHostBuilder,
    TurnResult,
    IAgentContext,
    CancellationToken,
    RateLimitError,
    UserMessage,
)
from datetime import datetime
from typing import Optional
import logging
import asyncio

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(thread_id)s] %(message)s'
)
logger = logging.getLogger(__name__)


# Function implementations
def get_time() -> str:
    """Get the current UTC time."""
    return datetime.utcnow().isoformat()


async def fetch_data(url: str) -> str:
    """
    Fetch data from a URL (simulated).

    In production, use httpx or aiohttp with proper error handling.
    """
    await asyncio.sleep(0.1)  # Simulate network delay
    return f"Data from {url}"


def calculate_tax(amount: float, rate: float = 0.1) -> str:
    """Calculate tax on an amount."""
    if amount < 0:
        return "Error: Amount cannot be negative"
    if rate < 0 or rate > 1:
        return "Error: Rate must be between 0 and 1"

    tax = amount * rate
    total = amount + tax
    return f"Amount: ${amount:.2f}, Tax: ${tax:.2f}, Total: ${total:.2f}"


# Message handler with state tracking
async def on_user_message(
    message: UserMessage,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """Handle user messages with state tracking."""
    message_text = message.text or ""

    # Track conversation statistics
    count = await context.state.get_async("message_count", default=0)
    await context.state.set_async("message_count", count + 1)
    await context.state.set_async("last_message_time", datetime.utcnow().isoformat())

    # Log with context
    await context.log_async(
        f"Processing message #{count + 1}: {message_text[:50]}...",
        level="INFO"
    )

    # Handle commands
    if message_text.lower() == "/stats":
        first_message = await context.state.get_async("first_message_time")
        if not first_message:
            await context.state.set_async(
                "first_message_time",
                datetime.utcnow().isoformat()
            )

        stats = f"""
📊 Conversation Statistics:
- Total messages: {count + 1}
- Thread ID: {context.thread_id}
- Run ID: {context.run_id}
        """.strip()
        await context.respond_async(stats)
        return TurnResult.REPLIED

    elif message_text.lower() == "/reset":
        await context.state.clear_async()
        await context.respond_async("Conversation state has been reset.")
        return TurnResult.REPLIED

    return TurnResult.CONTINUE


# Error handler
async def on_error(
    error: Exception,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> any:
    """Handle errors gracefully."""
    await context.log_async(f"Error occurred: {type(error).__name__}", level="ERROR")

    if isinstance(error, RateLimitError):
        await context.respond_async(
            "I'm receiving too many requests right now. Please try again in a moment."
        )
        return "HANDLED"

    # Log unexpected errors
    await context.log_async(f"Unexpected error: {error}", level="ERROR")
    return "UNHANDLED"


# Create production-ready agent
agent_host = (
    AgentHostBuilder()
    # Enable production defaults
    .use_production_defaults()
    # Configure concurrency limits
    .configure_concurrency(
        max_concurrent_requests=100,
        request_timeout=120.0,
        function_timeout=30.0
    )
    # Configure sandboxing for security
    .configure_sandbox(
        max_memory_mb=512,
        max_cpu_percent=50.0,
        allow_network=True,  # Allow for API functions
        allow_filesystem_write=False,
        allowed_modules=["json", "datetime", "asyncio"]
    )
    # Configure retries
    .configure_retries(
        max_attempts=3,
        backoff_base=2.0
    )
    # Configure logging
    .configure_logging(
        level="INFO",
        format="json",
        mask_secrets=True,
        include_thread_id=True
    )
    # Add the agent
    .add_default_agent(lambda agent: agent
        .use_llm(
            "gpt-4",
            "You are a professional business assistant. You help with calculations, "
            "data retrieval, and answering questions. Be concise and accurate."
        )
        .add_functions(lambda f: f
            .add("get_time@v1", "Gets the current UTC time", get_time)
            .add(
                "calculate_tax@v1",
                "Calculate tax on an amount with optional rate (default 10%)",
                calculate_tax
            )
            .add(
                "fetch_data@v1",
                "Fetch data from a URL (requires network access)",
                fetch_data,
                timeout=10.0
            )
        )
        .on_user_message(on_user_message)
        .on_error(on_error)
    )
    .build()
)


if __name__ == "__main__":
    print("=" * 70)
    print("Production Agent Example")
    print("=" * 70)
    print("\nFeatures enabled:")
    print("  ✅ Production defaults (retries, logging, etc.)")
    print("  ✅ State management across conversations")
    print("  ✅ Function sandboxing with security controls")
    print("  ✅ Error handling and recovery")
    print("  ✅ Structured logging")
    print("\nCommands:")
    print("  /stats - Show conversation statistics")
    print("  /reset - Reset conversation state")
    print("\nPress Ctrl+C to stop.\n")

    try:
        # Get publisher for out-of-band messages
        publisher = agent_host.get_publisher()
        logger.info("Out-of-band publisher available")

        # Run the agent
        agent_host.run()
    except KeyboardInterrupt:
        print("\n\nAgent stopped.")
