#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Emoji Chat Bot demonstrating:
1. Tool calling with function decorators
2. System event handling
3. Emoji reaction handling
4. State management
"""

from microsoft.agents.hosting import (
    AgentHostBuilder,
    TurnResult,
    IAgentContext,
    CancellationToken,
)
from typing import Optional
import logging

try:
    from .emoji_types import AddEmojiResult, EmojiSuggestion
except ImportError:
    from emoji_types import AddEmojiResult, EmojiSuggestion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Tool functions
async def add_emoji_to_message(message_id: str, emoji: str) -> AddEmojiResult:
    """
    Add an emoji reaction to a specific message.

    Use this when the user wants to react to a message with an emoji.

    Args:
        message_id: The ID of the message to add emoji to
        emoji: The emoji to add (e.g., '👍', '❤️', '😊')

    Returns:
        AddEmojiResult with success status and details
    """
    # In a real implementation, this would call an API to add the reaction
    # For this demo, we'll just return a success message
    logger.info(f"Adding emoji {emoji} to message {message_id}")

    return AddEmojiResult(
        success=True,
        message_id=message_id,
        emoji=emoji,
        message=f"Added {emoji} reaction to message {message_id}"
    )


async def suggest_emoji(message_text: str) -> EmojiSuggestion:
    """
    Suggest appropriate emojis based on the sentiment or content of a message.

    Args:
        message_text: The message text to analyze

    Returns:
        EmojiSuggestion with suggested emojis
    """
    # Simple sentiment-based emoji suggestion
    lower_text = message_text.lower()
    suggested_emojis = []

    if any(word in lower_text for word in ["happy", "great", "awesome", "excellent"]):
        suggested_emojis.extend(["😊", "🎉", "👍"])
    elif any(word in lower_text for word in ["sad", "sorry", "unfortunately"]):
        suggested_emojis.extend(["😢", "💔", "🤗"])
    elif "love" in lower_text:
        suggested_emojis.extend(["❤️", "💕", "😍"])
    elif "thank" in lower_text:
        suggested_emojis.extend(["🙏", "😊", "👍"])
    else:
        suggested_emojis.extend(["👍", "😊", "✨"])

    logger.info(f"Suggested emojis for '{message_text[:50]}...': {suggested_emojis}")

    return EmojiSuggestion(
        message_text=message_text,
        suggested_emojis=suggested_emojis
    )


# Event handlers
async def handle_user_joined(
    event: any,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """
    Handle system event: user joined the conversation.

    This augments the LLM with knowledge about system events it wasn't trained on.
    """
    user_name = getattr(event, 'name', None) or "Someone"

    # Send welcome message
    await context.respond_async(
        f"👋 Welcome {user_name}! I'm an emoji bot. I can help you add emojis to messages and react with emojis!"
    )

    logger.info(f"User {user_name} joined the conversation")
    return TurnResult.REPLIED


async def handle_user_left(
    event: any,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """Handle system event: user left the conversation."""
    user_name = getattr(event, 'name', None) or "Someone"

    # Log the departure (in real app, might update context or send notification)
    logger.info(f"User {user_name} left the conversation")

    return TurnResult.CONSUMED


async def handle_emoji_reaction(
    reaction: any,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """
    Handle incoming emoji reactions.

    This teaches the LLM about emoji reactions, which are domain-specific events.
    """
    # Get emoji from reaction
    emoji = getattr(reaction, 'emoji', None) or getattr(reaction, 'type', '?')
    is_added = getattr(reaction, 'is_added', True)

    # Update context to remember the last emoji
    await context.state.set_async("last_emoji_used", emoji)

    # Respond based on reaction type
    if is_added:
        await context.respond_async(
            f"I see you reacted with {emoji}! That's a great choice! 😊"
        )
    else:
        await context.respond_async(
            f"You removed the {emoji} reaction. No problem!"
        )

    logger.info(f"Emoji reaction: {emoji} ({'added' if is_added else 'removed'})")
    return TurnResult.REPLIED


async def on_user_message(
    message: any,
    context: IAgentContext,
    cancellation_token: Optional[CancellationToken]
) -> TurnResult:
    """Handle user messages and track state."""
    message_text = getattr(message, 'text', str(message))

    # Track message count
    count = await context.state.get_async("message_count", default=0)
    await context.state.set_async("message_count", count + 1)

    # Handle special commands
    if message_text.lower() == "/stats":
        last_emoji = await context.state.get_async("last_emoji_used", default="None")
        stats = f"""
📊 Conversation Statistics:
- Total messages: {count + 1}
- Last emoji used: {last_emoji}
- Thread ID: {context.thread_id}
        """.strip()
        await context.respond_async(stats)
        return TurnResult.REPLIED

    # Log the message
    await context.log_async(
        f"Processing message #{count + 1}: {message_text[:50]}...",
        level="INFO"
    )

    # Let LLM handle everything else
    return TurnResult.CONTINUE


# Create the agent host
def create_agent_host():
    """Create and configure the emoji chat bot agent host."""
    import os

    # Get model from environment (matches basic-m365 pattern)
    model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4")

    return (
        AgentHostBuilder()
        .add_default_agent(lambda agent: agent
            .use_llm(
                model,
                "You are an emoji bot assistant with a friendly personality. "
                "You help users add emoji reactions to messages and suggest appropriate emojis. "
                "When users ask about emojis or reactions, use the available functions. "
                "Be enthusiastic and creative with your emoji suggestions!"
            )
            .add_functions(lambda f: f
                .add(
                    "add_emoji_to_message@v1",
                    "Add an emoji reaction to a specific message. "
                    "Use this when the user wants to react to a message with an emoji.",
                    add_emoji_to_message
                )
                .add(
                    "suggest_emoji@v1",
                    "Suggest appropriate emojis based on the sentiment or content of a message.",
                    suggest_emoji
                )
            )
            .on_user_message(on_user_message)
            .on_reaction(handle_emoji_reaction)
        )
        .build()
    )


def main():
    """Main entry point for the emoji chat bot."""
    print("=" * 60)
    print("Emoji Chat Bot")
    print("=" * 60)
    print("\nFeatures:")
    print("  🎨 Add emoji reactions to messages")
    print("  💡 Suggest emojis based on sentiment")
    print("  📊 Track conversation statistics")
    print("  🎉 Handle system events (user joined/left)")
    print("\nCommands:")
    print("  /stats - Show conversation statistics")
    print("\nPress Ctrl+C to stop.\n")

    try:
        agent_host = create_agent_host()
        logger.info("Emoji Chat Bot is starting...")
        # Use port 3985 as configured in agent-config.json
        agent_host.run(port=3985)
    except KeyboardInterrupt:
        print("\n\nEmoji Chat Bot stopped.")
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
