# Copyright (c) Microsoft. All rights reserved.

# Sample that shows how to create an Agent Framework agent that is hosted using the M365 Agent SDK.
# The agent can then be consumed from various M365 channels.
# See the README.md for more information.

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "microsoft-agents-hosting-aiohttp",
#   "microsoft-agents-hosting-core",
#   "microsoft-agents-authentication-msal",
#   "microsoft-agents-activity",
#   "microsoft-agents-protocol",
#   "openai>=1.0.0",
#   "aiohttp"
# ]
# ///

import os
from dataclasses import dataclass
from pathlib import Path
from random import randint, choice
from typing import Optional

from aiohttp import web
from aiohttp.web_middlewares import middleware
from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.hosting.aiohttp import CloudAdapter, start_agent_process
from microsoft_agents.hosting.core import (
    AgentApplication,
    AuthenticationConstants,
    Authorization,
    ClaimsIdentity,
    MemoryStorage,
    TurnContext,
    TurnState,
)
from microsoft.agents.protocol.server import add_agent_protocol_routes

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from testing_chat_client import TestingChatClient

"""
Demo application using Microsoft Agent 365 SDK with LLM integration.

This sample demonstrates how to build an AI agent with LLM function calling,
integrating with Microsoft 365 authentication and hosting components.

The agent uses OpenAI for LLM capabilities with function calling for weather and time tools.
It can be run in either anonymous mode (no authentication required) or authenticated mode using MSAL and Azure AD.

Key features:
- LLM integration with OpenAI function calling
- Weather and time function tools
- Loads configuration from environment variables
- Supports both anonymous and authenticated scenarios
- Uses aiohttp for web hosting

To run, set the appropriate environment variables (check .env.example file) for authentication or use
anonymous mode for local testing.
"""


@dataclass
class AppConfig:
    use_anonymous_mode: bool
    port: int
    agents_sdk_config: dict


def load_app_config() -> AppConfig:
    """Load application configuration from environment variables.

    Returns:
        AppConfig: Consolidated configuration including anonymous mode flag, port, and SDK config.
    """
    agents_sdk_config = load_configuration_from_env(os.environ)
    use_anonymous_mode = os.environ.get("USE_ANONYMOUS_MODE", "true").lower() == "true"
    port_str = os.getenv("PORT", "3982")
    try:
        port = int(port_str)
    except ValueError:
        port = 3982
    return AppConfig(use_anonymous_mode=use_anonymous_mode, port=port, agents_sdk_config=agents_sdk_config)


# Tool functions
def get_weather(location: str) -> str:
    """Generate a mock weather report for the provided location.

    Args:
        location: The geographic location name.
    Returns:
        str: Human-readable weather summary.
    """
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "stormy"]
    condition = choice(conditions)
    temperature = randint(10, 30)
    return f"🌤️ The weather in {location} is {condition} with a temperature of {temperature}°C."


def get_current_time() -> str:
    """Get the current UTC time.

    Returns:
        str: Current UTC time formatted as a string.
    """
    from datetime import datetime
    now = datetime.utcnow()
    return f"🕐 The current UTC time is {now.strftime('%Y-%m-%d %H:%M:%S')}."


# LLM client setup
testing_client: Optional[TestingChatClient] = None
model: str = "gpt-4"

def init_llm():
    """Initialize TestingChatClient with appropriate mode."""
    global testing_client, model

    if not OPENAI_AVAILABLE:
        print("⚠️  OpenAI package not installed. LLM features disabled.")
        return

    # Check mode from environment variables
    use_recordings = os.getenv("USE_LLM_RECORDINGS", "").lower() == "true"
    record_llm = os.getenv("RECORD_LLM", "").lower() == "true"

    playback_mode = use_recordings
    record_mode = record_llm

    # Find recordings directory
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    recordings_dir = repo_root / "test-data" / "llm-recordings" / "basic-m365"

    # Create real OpenAI client if needed (for normal or recording mode)
    real_client = None
    if not playback_mode:
        endpoint = os.getenv("FOUNDRY_ENDPOINT")
        api_key = os.getenv("FOUNDRY_API_KEY")

        if not endpoint or not api_key:
            print("⚠️  FOUNDRY_ENDPOINT or FOUNDRY_API_KEY not set. LLM features disabled.")
            return

        model = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4")

        try:
            real_client = AsyncOpenAI(
                api_key=api_key,
                base_url=f"{endpoint}/openai/v1/"
            )
        except Exception as e:
            print(f"❌ Error creating OpenAI client: {e}")
            return
    else:
        model = "gpt-5-nano"

    # Create TestingChatClient wrapper
    testing_client = TestingChatClient(
        real_client=real_client,
        recordings_dir=str(recordings_dir),
        model_id=model,
        record_mode=record_mode,
        playback_mode=playback_mode
    )




# Conversation state storage
conversation_states = {}


def build_connection_manager(config: AppConfig) -> MsalConnectionManager | None:
    """Build the connection manager unless running in anonymous mode."""
    if config.use_anonymous_mode:
        return None
    return MsalConnectionManager(**config.agents_sdk_config)


def build_adapter(connection_manager: MsalConnectionManager | None) -> CloudAdapter:
    """Instantiate the CloudAdapter with the optional connection manager."""
    return CloudAdapter(connection_manager=connection_manager)


def build_authorization(
    storage: MemoryStorage, connection_manager: MsalConnectionManager | None, config: AppConfig
) -> Authorization | None:
    """Create Authorization component if not in anonymous mode."""
    if config.use_anonymous_mode:
        return None
    return Authorization(storage, connection_manager, **config.agents_sdk_config)


def build_agent_application(
    storage: MemoryStorage,
    adapter: CloudAdapter,
    authorization: Authorization | None,
    config: AppConfig,
) -> AgentApplication[TurnState]:
    """Compose and return the AgentApplication instance."""
    return AgentApplication[TurnState](
        storage=storage, adapter=adapter, authorization=authorization, **config.agents_sdk_config
    )


def build_anonymous_claims_middleware(use_anonymous_mode: bool):
    """Return a middleware that injects anonymous claims when enabled."""

    @middleware
    async def anonymous_claims_middleware(request, handler):
        """Inject claims for anonymous users if anonymous mode is active."""
        if use_anonymous_mode:
            request["claims_identity"] = ClaimsIdentity(
                {
                    AuthenticationConstants.AUDIENCE_CLAIM: "anonymous",
                    AuthenticationConstants.APP_ID_CLAIM: "anonymous-app",
                },
                False,
                "Anonymous",
            )
        return await handler(request)

    return anonymous_claims_middleware


def create_app(config: AppConfig) -> web.Application:
    """Create and configure the aiohttp web application."""
    # Initialize LLM
    init_llm()

    middleware_fn = build_anonymous_claims_middleware(config.use_anonymous_mode)
    app = web.Application(middlewares=[middleware_fn])

    storage = MemoryStorage()
    connection_manager = build_connection_manager(config)
    adapter = build_adapter(connection_manager)
    authorization = build_authorization(storage, connection_manager, config)
    agent_app = build_agent_application(storage, adapter, authorization, config)

    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather for a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get the weather for"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current UTC time",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    @agent_app.activity("message")
    async def on_message(context: TurnContext, _: TurnState):
        global testing_client, model

        user_message = context.activity.text or ""
        if not user_message.strip():
            return

        # If LLM is not configured, provide a helpful message
        if not testing_client:
            await context.send_activity(
                "Hello! I'm a Basic M365 Agent with LLM capabilities. "
                "To enable AI features, please start this sample using:\n"
                "python3 scripts/ci/start_samples.py basic-m365 --lang python"
            )
            return

        # Get conversation ID
        conv_id = context.activity.conversation.id if context.activity.conversation else "default"

        # Initialize conversation history if needed
        if conv_id not in conversation_states:
            conversation_states[conv_id] = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users."
                }
            ]

        # Add user message to history
        conversation_states[conv_id].append({
            "role": "user",
            "content": user_message
        })

        # Call LLM with function calling
        max_iterations = 5
        iteration = 0
        response_text = ""

        while iteration < max_iterations:
            iteration += 1

            try:
                # Get completion from LLM (transparently handles recording/playback)
                completion = await testing_client.create_completion(
                    messages=conversation_states[conv_id],
                    tools=tools
                )

                choice = completion.choices[0]

                # Check if model wants to call functions
                if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                    # Add assistant message with tool calls
                    conversation_states[conv_id].append({
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
                            }
                            for tc in choice.message.tool_calls
                        ]
                    })

                    # Execute tool calls
                    import json
                    for tool_call in choice.message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        # Call the appropriate function
                        if function_name == "get_weather":
                            result = get_weather(function_args.get("location", "Seattle"))
                        elif function_name == "get_current_time":
                            result = get_current_time()
                        else:
                            result = "Unknown function"

                        # Add function result to conversation
                        conversation_states[conv_id].append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })
                else:
                    # Model provided final response
                    response_text = choice.message.content or ""
                    conversation_states[conv_id].append({
                        "role": "assistant",
                        "content": response_text
                    })
                    break

            except Exception as e:
                print(f"Error during LLM call: {e}")
                response_text = "I apologize, but I encountered an error while processing your request."
                break

        if not response_text:
            response_text = "I apologize, but I wasn't able to complete your request."

        await context.send_activity(response_text)

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    # ==================================================================================
    # LEGACY ENDPOINT - DO NOT MODIFY
    # This is the Bot Framework /api/messages endpoint for backwards compatibility.
    # It receives incoming messages from Azure Bot Service or other M365 channels.
    # For Agent Protocol functionality, use add_agent_protocol_routes below.
    # ==================================================================================
    async def entry_point(req: web.Request) -> web.Response:
        return await start_agent_process(req, req.app["agent_app"], req.app["adapter"])

    app.add_routes([
        web.get("/api/health", health),
        web.get("/api/messages", lambda _: web.Response(status=200)),
        web.post("/api/messages", entry_point),
    ])

    app["agent_app"] = agent_app
    app["adapter"] = adapter

    # AGENT PROTOCOL EXTENSION: Add Agent Protocol routes
    # This is the Python equivalent of .NET's app.MapAgentProtocol()
    add_agent_protocol_routes(app, agent_app)

    return app


def main() -> None:
    """Entry point: load configuration, build app, and start server."""
    config = load_app_config()
    app = create_app(config)
    web.run_app(app, host="localhost", port=config.port)


if __name__ == "__main__":
    main()
