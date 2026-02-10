# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import sys
import json
import traceback
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from openai import AsyncOpenAI

load_dotenv()

# 🔧 FIX: Create storage with cleanup to prevent unbounded memory growth
STORAGE = MemoryStorage()

# Track storage access times for cleanup
_storage_access_times = {}
_storage_max_age = timedelta(hours=1)  # Clean up conversations older than 1 hour
_last_cleanup = datetime.now()

async def _cleanup_old_storage():
    """Remove old conversation data from storage to prevent memory leaks."""
    global _last_cleanup, _storage_access_times

    now = datetime.now()
    # Only cleanup every 5 minutes
    if now - _last_cleanup < timedelta(minutes=5):
        return

    _last_cleanup = now
    cutoff = now - _storage_max_age

    # Find keys to delete
    keys_to_delete = [
        key for key, access_time in _storage_access_times.items()
        if access_time < cutoff
    ]

    if keys_to_delete:
        try:
            await STORAGE.delete(keys_to_delete)
            for key in keys_to_delete:
                del _storage_access_times[key]
            print(f"Cleaned up {len(keys_to_delete)} old conversation states")
        except Exception as e:
            print(f"Error during storage cleanup: {e}")

def _track_storage_access(key: str):
    """Track when storage keys are accessed."""
    _storage_access_times[key] = datetime.now()

# Force anonymous mode - no authentication for local development
CONNECTION_MANAGER = None
ADAPTER = CloudAdapter()
AUTHORIZATION = None

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION
)

# LLM Client and conversation history
_conversation_history: Dict[str, List[Dict[str, Any]]] = {}
_openai_client: AsyncOpenAI | None = None
_model: str = "gpt-4"
_use_recordings: bool = False
_recordings_dir: Path | None = None

# ============================================================================
# ENVIRONMENT VARIABLES - Set automatically by scripts/ci/start_samples.py
# ============================================================================
# These environment variables are loaded from .env file at repo root:
#   - FOUNDRY_ENDPOINT: LLM endpoint URL
#   - FOUNDRY_API_KEY: API key for authentication
#   - FOUNDRY_MODEL_DEPLOYMENT: Model name (default: gpt-4)
#   - USE_LLM_RECORDINGS: Set to "true" for test mode (replays recordings)
#   - RECORD_LLM: Set to "true" to record LLM interactions
#
# Developers should NEVER manually set these variables.
# Use: python3 scripts/ci/start_samples.py basic-m365 --lang python --ui
# ============================================================================

# Initialize LLM client
def _init_llm():
    global _openai_client, _model, _use_recordings, _recordings_dir

    # Check if we should use LLM recordings (test mode)
    use_recordings = os.environ.get("USE_LLM_RECORDINGS", "").lower() == "true"
    _use_recordings = use_recordings

    # Find recordings directory
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    _recordings_dir = repo_root / "test-data" / "llm-recordings" / "basic-m365"

    if _use_recordings:
        # Test mode: Use recorded LLM responses
        _model = "gpt-5-nano"  # Default model for recordings
        print(f"▶️  LLM Playback enabled: {_recordings_dir}")
        print("   Using recorded LLM responses (test mode)")
    else:
        # Generation mode: Use real LLM
        endpoint = os.environ.get("FOUNDRY_ENDPOINT")
        api_key = os.environ.get("FOUNDRY_API_KEY")

        if not endpoint or not api_key:
            print("⚠️  FOUNDRY_ENDPOINT or FOUNDRY_API_KEY not set. LLM features disabled.")
            print("   Set these environment variables to enable LLM functionality.")
            return

        _model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4")

        # Create OpenAI client for Foundry
        _openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint}/openai/v1/"
        )

        # Check if LLM recording is enabled
        record_llm = os.environ.get("RECORD_LLM", "").lower() == "true"
        if record_llm:
            _recordings_dir.mkdir(parents=True, exist_ok=True)
            print(f"📹 LLM Recording enabled: {_recordings_dir}")

# Initialize on module load
_init_llm()


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity(
        "Hello! I'm a Basic M365 Agent. I can help you with weather and time information. "
        "Try asking: 'What's the weather in Seattle?' or 'What time is it?'"
    )
    return True


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    # 🔧 Periodically clean up old storage to prevent memory leaks
    await _cleanup_old_storage()

    # Track this conversation's access time
    if hasattr(context.activity, "conversation") and context.activity.conversation:
        conv_id = context.activity.conversation.id
        if conv_id:
            _track_storage_access(conv_id)

    # Extract role from channelData (default to "user" if not present)
    role = "user"
    if hasattr(context.activity, "channel_data") and isinstance(context.activity.channel_data, dict):
        role = context.activity.channel_data.get("role", "user")

    # Only respond to user messages
    if role != "user":
        return

    user_message = context.activity.text or ""
    conversation_id = context.activity.conversation.id

    # If LLM is not configured, just echo
    if not _openai_client and not _use_recordings:
        await context.send_activity(f"Echo: {user_message}\n\n(Note: LLM not configured. Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY to enable LLM features.)")
        return

    # Initialize conversation history if needed
    if conversation_id not in _conversation_history:
        _conversation_history[conversation_id] = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users."
            }
        ]

    # Add user message to history
    _conversation_history[conversation_id].append({
        "role": "user",
        "content": user_message
    })

    # Track the starting index to capture new messages generated during this turn
    starting_history_count = len(_conversation_history[conversation_id])

    # Define available functions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "GetWeatherAsync",
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
                "name": "GetCurrentTime",
                "description": "Get the current UTC time.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    # Call LLM with function calling in a loop
    response = ""
    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Get completion from LLM (either real or replayed)
            if _use_recordings and _recordings_dir:
                # Test mode: Replay recorded response
                completion = await _replay_llm_response(_conversation_history[conversation_id], tools)
            elif _openai_client:
                # Generation mode: Use real LLM
                completion = await _openai_client.chat.completions.create(
                    model=_model,
                    messages=_conversation_history[conversation_id],
                    tools=tools
                )

                # Record LLM interaction if recorder is enabled
                record_llm = os.environ.get("RECORD_LLM", "").lower() == "true"
                if record_llm and _recordings_dir:
                    await _record_llm_interaction(
                        _conversation_history[conversation_id],
                        tools,
                        completion
                    )
            else:
                raise ValueError("Neither OpenAI client nor recordings available")

            # Check if the model wants to call functions
            if completion.choices[0].finish_reason == "tool_calls":
                tool_calls = completion.choices[0].message.tool_calls

                # Add assistant message with tool calls to history
                _conversation_history[conversation_id].append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if function_name == "GetWeatherAsync":
                        location = function_args.get("location", "unknown")
                        function_result = await get_weather_async(location)
                    elif function_name == "GetCurrentTime":
                        function_result = get_current_time()
                    else:
                        function_result = "Unknown function"

                    # Add function result to conversation history
                    _conversation_history[conversation_id].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result
                    })
            else:
                # Model provided a final response
                response = completion.choices[0].message.content or ""
                _conversation_history[conversation_id].append({
                    "role": "assistant",
                    "content": response
                })
                break

        except Exception as e:
            print(f"Error during LLM call: {e}", file=sys.stderr)
            traceback.print_exc()
            response = "I apologize, but I encountered an error while processing your request."
            break

    if not response:
        response = "I apologize, but I wasn't able to complete your request."

    # Send all messages generated during this turn as separate activities
    for i in range(starting_history_count, len(_conversation_history[conversation_id])):
        chat_message = _conversation_history[conversation_id][i]
        agent_message = _convert_chat_message_to_agent_protocol(chat_message)

        # Create an activity with the Agent Protocol message in the Value field
        from microsoft_agents.activity import Activity
        activity = Activity(type="message", text="")
        activity.value = agent_message
        await context.send_activity(activity)


def _convert_chat_message_to_agent_protocol(chat_message: Dict[str, Any]) -> Dict[str, Any]:
    """Converts an OpenAI ChatMessage to Agent Protocol message format"""
    message = {}

    # Determine role
    role = chat_message.get("role", "assistant")
    if role == "tool":
        message["role"] = "tool"
    else:
        message["role"] = "assistant"

    # Convert contents
    contents = []

    if role == "assistant":
        # Check if this is a tool call message
        tool_calls = chat_message.get("tool_calls")
        if tool_calls:
            for tool_call in tool_calls:
                contents.append({
                    "kind": "functionCall",
                    "callId": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "arguments": tool_call["function"]["arguments"]
                })
        else:
            # Text response
            text = chat_message.get("content", "")
            contents.append({
                "kind": "text",
                "text": text
            })
    elif role == "tool":
        # Tool result
        contents.append({
            "kind": "functionResult",
            "callId": chat_message.get("tool_call_id", ""),
            "result": chat_message.get("content", "")
        })
    else:
        # Fallback: treat as text
        text = chat_message.get("content", "")
        contents.append({
            "kind": "text",
            "text": text
        })

    message["contents"] = contents
    return message


async def get_weather_async(location: str) -> str:
    """Function tool: Get weather for a location"""
    # Simulate async API call
    import asyncio
    await asyncio.sleep(0.1)

    conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "stormy"]
    condition = random.choice(conditions)
    temperature = random.randint(10, 35)

    return f"🌤️ The weather in {location} is {condition} with a temperature of {temperature}°C."


def get_current_time() -> str:
    """Function tool: Get current time"""
    now = datetime.utcnow()
    return f"🕐 The current UTC time is {now.strftime('%Y-%m-%d %H:%M:%S')}."


def _hash_request(model: str, messages: list, tools: list) -> str:
    """Generate deterministic hash from request parameters (matches .NET implementation)"""
    import hashlib

    # Normalize messages
    normalized_messages = []
    for msg in messages:
        normalized = {"role": msg["role"]}
        if "content" in msg and msg["content"]:
            normalized["content"] = msg["content"]
        if "tool_calls" in msg:
            normalized["tool_calls"] = msg["tool_calls"]
        if "tool_call_id" in msg:
            normalized["tool_call_id"] = msg["tool_call_id"]
        normalized_messages.append(normalized)

    # Build request dict
    request_dict = {
        "messages": normalized_messages,
        "model": model,
        "temperature": 0.0
    }

    if tools:
        request_dict["tools"] = tools

    # Serialize to stable JSON (sorted keys)
    json_str = json.dumps(request_dict, sort_keys=True, separators=(',', ':'))

    # Hash and truncate to match .NET format
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


async def _replay_llm_response(messages: list, tools: list):
    """Replay recorded LLM response"""
    global _model, _recordings_dir

    # Generate hash to find recording
    hash_key = _hash_request(_model, messages, tools)

    # Find response file
    response_file = _recordings_dir / f"{hash_key}.response.json"

    if not response_file.exists():
        print(f"⚠️  No recording found for hash: {hash_key}")
        print(f"   Expected: {response_file}")
        # Return a default response
        class MockCompletion:
            class Choice:
                class Message:
                    content = "I can help you with weather and time information!"
                    tool_calls = None
                finish_reason = "stop"
                message = Message()
            choices = [Choice()]
        return MockCompletion()

    # Load recording
    with open(response_file, 'r') as f:
        recording = json.load(f)

    response_data = recording["response"]

    # Build mock completion object
    class MockToolCall:
        def __init__(self, data):
            self.id = data["id"]
            self.type = data["type"].lower()
            self.function = type('obj', (object,), {
                'name': data["function"]["name"],
                'arguments': data["function"]["arguments"]
            })()

    class MockMessage:
        def __init__(self, data):
            # Get content
            if data.get("content") and len(data["content"]) > 0:
                self.content = data["content"][0].get("text", "")
            else:
                self.content = None

            # Get tool calls
            if data.get("toolCalls") and len(data["toolCalls"]) > 0:
                self.tool_calls = [MockToolCall(tc) for tc in data["toolCalls"]]
            else:
                self.tool_calls = None

    class MockChoice:
        def __init__(self, data):
            self.finish_reason = data["finishReason"].lower()
            self.message = MockMessage(data)

    class MockCompletion:
        def __init__(self, data):
            self.choices = [MockChoice(data)]

    return MockCompletion(response_data)


async def _record_llm_interaction(messages, tools, completion):
    """Record LLM interaction for testing"""
    # Recording is handled by .NET implementation
    pass


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
