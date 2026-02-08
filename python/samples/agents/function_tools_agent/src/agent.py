# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os.path as path
import re
import sys
import json
import traceback
from datetime import datetime, timezone
from random import randint
from dotenv import load_dotenv
from pathlib import Path

from os import environ
from openai import AsyncOpenAI
from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env

# Load .env from repository root
env_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)

agents_sdk_config = load_configuration_from_env(environ)

STORAGE = MemoryStorage()

# Simple anonymous mode - no authentication required
try:
    CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
    ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
    AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)
except (ValueError, Exception):
    # If auth config is missing, create without authentication for local testing
    CONNECTION_MANAGER = None
    ADAPTER = CloudAdapter()
    AUTHORIZATION = None

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION
)

# OpenAI client - can be overridden for testing
_openai_client = None
foundry_model = environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-nano")


def create_openai_client(injected_client=None):
    """Create OpenAI client for production or testing.

    Args:
        injected_client: Optional pre-configured client (for testing)

    Returns:
        AsyncOpenAI client instance
    """
    if injected_client is not None:
        return injected_client

    # Production path - create from environment variables
    foundry_endpoint = environ.get("FOUNDRY_ENDPOINT")
    foundry_api_key = environ.get("FOUNDRY_API_KEY")

    if not foundry_endpoint or not foundry_api_key:
        raise ValueError("FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables are required")

    return AsyncOpenAI(
        api_key=foundry_api_key,
        base_url=f"{foundry_endpoint}/openai/v1"
    )


def set_openai_client(client):
    """Override OpenAI client for testing.

    Args:
        client: AsyncOpenAI client or mock/recording wrapper
    """
    global _openai_client
    _openai_client = client


def get_openai_client():
    """Get OpenAI client (lazy initialization).

    Returns:
        AsyncOpenAI client instance (real or injected)
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = create_openai_client()
    return _openai_client


# Conversation history storage (in-memory for demo)
conversation_history = {}


# Function Tools
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    # Use deterministic seed for testing (based on location)
    import random
    seed_value = sum(ord(c) for c in location) + 42
    random.seed(seed_value)

    conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "stormy"]
    condition = conditions[random.randint(0, len(conditions) - 1)]
    temperature = random.randint(10, 35)
    return f"🌤️ The weather in {location} is {condition} with a temperature of {temperature}°C."


def get_time() -> str:
    """Get the current UTC time."""
    now = datetime.now(timezone.utc)
    return f"🕐 The current UTC time is {now.strftime('%Y-%m-%d %H:%M:%S')}."


def extract_location(message: str) -> str:
    """Extract location from user message."""
    patterns = [" in ", " at ", " for "]
    for pattern in patterns:
        index = message.lower().find(pattern)
        if index >= 0:
            location_start = index + len(pattern)
            location_part = message[location_start:].strip(' ?!.')
            if location_part:
                words = location_part.split(' ')
                return words[0].capitalize()
    return "your location"


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity(
        "Hello! I'm a Function Tools Agent. "
        "I can help you with weather and time information. "
        "Try asking: 'What's the weather in Seattle?' or 'What time is it?'"
    )
    return True


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    # Extract role from channelData (default to "user" if not present)
    role = "user"
    if hasattr(context.activity, "channel_data") and isinstance(context.activity.channel_data, dict):
        role = context.activity.channel_data.get("role", "user")

    # Only respond to user messages
    if role != "user":
        return

    user_message = context.activity.text if context.activity.text else ""
    conversation_id = context.activity.conversation.id

    # Initialize conversation history if needed
    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users."
            }
        ]

    # Add user message to history
    conversation_history[conversation_id].append({
        "role": "user",
        "content": user_message
    })

    # Define available functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather for a given location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get the weather for."
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get the current UTC time.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    # Call LLM with function calling in a loop
    response_text = ""
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get completion from LLM (using injected or real client)
        client = get_openai_client()
        completion = await client.chat.completions.create(
            model=foundry_model,
            messages=conversation_history[conversation_id],
            tools=tools,
            tool_choice="auto",
            temperature=0.0,  # Deterministic for testing
            seed=42  # Additional determinism
        )

        choice = completion.choices[0]
        message = choice.message

        # Check if the model wants to call functions
        if choice.finish_reason == "tool_calls" and message.tool_calls:
            # Add assistant message with tool calls to history
            conversation_history[conversation_id].append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "get_weather":
                    location = function_args.get("location", "unknown")
                    function_result = get_weather(location)
                elif function_name == "get_time":
                    function_result = get_time()
                else:
                    function_result = "Unknown function"

                # Add function result to conversation history
                conversation_history[conversation_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                })
        else:
            # Model provided a final response
            response_text = message.content or "I apologize, but I wasn't able to complete your request."
            conversation_history[conversation_id].append({
                "role": "assistant",
                "content": response_text
            })
            break

    if not response_text:
        response_text = "I apologize, but I wasn't able to complete your request."

    await context.send_activity(response_text)


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
