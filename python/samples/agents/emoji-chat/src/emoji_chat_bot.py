#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Emoji Chat Bot demonstrating:
1. LLM-powered emoji suggestions
2. LLM recording/playback for deterministic testing
3. Modern Agent Protocol hosting (NO legacy SDK)

============================================================================
MODERN SAMPLE - New Hosting Package Only
============================================================================
This sample demonstrates the NEW way to build agents using ONLY the
microsoft.agents.hosting package. This is the recommended approach for
new applications.

For examples of adapting LEGACY M365 Agents SDK apps to speak Agent Protocol,
see the echo-m365 and basic-m365 samples.
============================================================================
"""

import os
import logging
from pathlib import Path
from typing import Optional

from microsoft.agents.hosting import (
    AgentHostBuilder,
    TurnResult,
    IAgentContext,
    CancellationToken,
)

try:
    from .llm_recorder import LLMRecorder, LLMPlayer
except ImportError:
    from llm_recorder import LLMRecorder, LLMPlayer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmojiBot:
    """Emoji bot with LLM support and recording/replay capabilities."""

    def __init__(self):
        """Initialize emoji bot with LLM configuration."""
        # ============================================================================
        # ENVIRONMENT VARIABLES - Set automatically by scripts/ci/start_samples.py
        # ============================================================================
        # These environment variables are loaded from .env file at repo root:
        #   - FOUNDRY_ENDPOINT: LLM endpoint URL
        #   - FOUNDRY_API_KEY: API key for authentication
        #   - FOUNDRY_MODEL_DEPLOYMENT: Model name (default: gpt-5-nano)
        #   - USE_LLM_RECORDINGS: Set to "true" for test mode (replays recordings)
        #   - RECORD_LLM: Set to "true" to record LLM interactions
        #
        # Developers should NEVER manually set these variables.
        # Use: python3 scripts/ci/start_samples.py emoji-chat --lang python --ui
        # ============================================================================

        self.conversation_history = []
        self.use_recordings = os.environ.get("USE_LLM_RECORDINGS", "").lower() == "true"
        self.model = "gpt-5-nano"
        self.client = None
        self.recorder = None
        self.player = None

        # Find recordings directory (navigate up to repo root)
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        recordings_dir = repo_root / "test-data" / "llm-recordings" / "emoji-bot"

        if self.use_recordings:
            # Test mode: Use recorded LLM responses
            self.player = LLMPlayer(str(recordings_dir))
            logger.info(f"▶️  LLM Playback enabled: {recordings_dir}")
            logger.info("   Using recorded LLM responses (test mode)")
        else:
            # Generation mode: Use real LLM and optionally record
            endpoint = os.environ.get("FOUNDRY_ENDPOINT")
            api_key = os.environ.get("FOUNDRY_API_KEY")

            if endpoint and api_key:
                self.model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-nano")

                try:
                    from openai import AsyncOpenAI
                    self.client = AsyncOpenAI(
                        api_key=api_key,
                        base_url=f"{endpoint}/openai/v1/"
                    )

                    # Check if LLM recording is enabled
                    record_llm = os.environ.get("RECORD_LLM", "").lower() == "true"
                    if record_llm:
                        recordings_dir.mkdir(parents=True, exist_ok=True)
                        self.recorder = LLMRecorder(str(recordings_dir))
                        logger.info(f"🔴 LLM Recording enabled: {recordings_dir}")
                        logger.info(f"   Model: {self.model}")
                    else:
                        logger.info(f"🤖 Using LLM: {self.model} (recording disabled)")

                except ImportError:
                    logger.error("⚠️  OpenAI package not installed!")
                    logger.error("   Install with: pip install openai")
                    logger.error("   Or set USE_LLM_RECORDINGS=true to use recorded responses.")
            else:
                logger.warning("⚠️  No LLM credentials found!")
                logger.warning("   Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables to use LLM.")
                logger.warning("   Or set USE_LLM_RECORDINGS=true to use recorded responses.")
                logger.warning("   EmojiBot will fail without LLM configuration.")

    async def handle_user_message(
        self,
        message: any,
        context: IAgentContext,
        cancellation_token: Optional[CancellationToken]
    ) -> TurnResult:
        """Handle user messages and respond with LLM-generated emoji suggestions."""
        # Extract text from message
        message_text = ""
        if hasattr(message, 'text'):
            message_text = message.text
        else:
            message_text = str(message)

        # Track message count
        count = await context.state.get_async("message_count", default=0)
        await context.state.set_async("message_count", count + 1)

        # Handle special commands
        if message_text.lower() == "/stats":
            last_emoji = await context.state.get_async("last_emoji_used", default="None")
            stats = f"""📊 Conversation Statistics:
- Total messages: {count + 1}
- Last emoji used: {last_emoji}
- Thread ID: {context.thread_id}"""
            await context.respond_async(stats)
            return TurnResult.REPLIED

        # Initialize conversation with system prompt
        if not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": """You are an emoji expert bot. Your responses should:
1. Acknowledge what the user said
2. Suggest 3-5 relevant emojis based on the sentiment, topic, or mood
3. Be friendly and enthusiastic about emojis
4. Keep responses concise (2-3 sentences max)

Examples:
- User: 'I'm happy today!' → 'That's wonderful! 😊 Here are some joyful emojis: 😊 🎉 ☀️ ✨'
- User: 'I love pizza' → 'Pizza is amazing! 🍕 Perfect emojis: 🍕 ❤️ 😋 👨‍🍳'
- User: 'Feeling tired' → 'Hope you get some rest! 😴 Cozy emojis: 😴 💤 🛌 ☕'"""
            })

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": message_text
        })

        # Get LLM response
        try:
            if self.use_recordings and self.player:
                # Test mode: Replay recorded response
                response_text = await self.player.replay_async(
                    self.model,
                    self.conversation_history
                )
            elif self.client:
                # Generation mode: Use real LLM
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history
                )
                response_text = response.choices[0].message.content

                # Record LLM interaction if recorder is enabled
                if self.recorder:
                    await self.recorder.record_async(
                        self.model,
                        self.conversation_history,
                        None,
                        response
                    )
            else:
                raise RuntimeError(
                    "LLM is not configured. Please use the startup script: "
                    "python3 scripts/ci/start_samples.py emoji-chat --lang python --ui"
                )

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            # Send response
            await context.respond_async(response_text)
            return TurnResult.REPLIED

        except FileNotFoundError as e:
            error_msg = f"❌ Recording not found: {e}\nRun with RECORD_LLM=true to create recordings."
            logger.error(error_msg)
            await context.respond_async(error_msg)
            return TurnResult.REPLIED

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            logger.error(f"Error processing message: {e}", exc_info=True)
            await context.respond_async(error_msg)
            return TurnResult.REPLIED


# Create the agent host
def create_agent_host():
    """Create and configure the emoji chat bot agent host."""
    emoji_bot = EmojiBot()

    return (
        AgentHostBuilder()
        .add_default_agent(lambda agent: agent
            .on_user_message(emoji_bot.handle_user_message)
        )
        .build()
    )


def main():
    """Main entry point for the emoji chat bot."""
    print("=" * 60)
    print("Emoji Chat Bot - LLM Powered")
    print("=" * 60)
    print("\nFeatures:")
    print("  🤖 LLM-powered emoji suggestions")
    print("  💾 LLM recording for testing")
    print("  ▶️  LLM playback for deterministic tests")
    print("  📊 Conversation statistics")
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
