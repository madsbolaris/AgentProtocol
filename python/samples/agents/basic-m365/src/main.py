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
openai_client: Optional[AsyncOpenAI] = None
model: str = "gpt-4"
use_recordings: bool = False
recordings_dir: Optional[Path] = None

def init_llm():
    """Initialize OpenAI client if credentials are available."""
    global openai_client, model, use_recordings, recordings_dir

    if not OPENAI_AVAILABLE:
        print("⚠️  OpenAI package not installed. LLM features disabled.")
        return

    # Check if we should use LLM recordings (test mode)
    env_use_recordings = os.getenv("USE_LLM_RECORDINGS", "").lower() == "true"
    use_recordings = env_use_recordings

    print(f"🔧 Initializing LLM...")
    print(f"   USE_LLM_RECORDINGS: {env_use_recordings}")
    print(f"   useRecordings: {use_recordings}")

    # Find recordings directory
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    recordings_dir = repo_root / "test-data" / "llm-recordings" / "basic-m365"

    if use_recordings:
        # Test mode: Use recorded LLM responses
        model = "gpt-5-nano"  # Default model for recordings
        print(f"▶️  LLM Playback enabled (using recordings)")
        print(f"   Using recorded LLM responses (test mode)")
        return  # Don't initialize OpenAI client in playback mode

    # Generation mode: Use real LLM
    endpoint = os.getenv("FOUNDRY_ENDPOINT")
    api_key = os.getenv("FOUNDRY_API_KEY")

    if not endpoint or not api_key:
        print("⚠️  FOUNDRY_ENDPOINT or FOUNDRY_API_KEY not set. LLM features disabled.")
        return

    model = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4")

    try:
        openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint}/openai/v1/"
        )
        print(f"✅ OpenAI client initialized with model: {model}")
    except Exception as e:
        print(f"❌ Error creating OpenAI client: {e}")


def _hash_request(model: str, messages: list, tools: list) -> str:
    """Generate a hash for the LLM request to find/store recordings."""
    import hashlib
    import json

    # Create a deterministic representation of the request
    request_data = {
        "model": model,
        "messages": messages,
        "tools": tools
    }

    # Convert to JSON and hash
    request_str = json.dumps(request_data, sort_keys=True)
    hash_obj = hashlib.md5(request_str.encode())
    return hash_obj.hexdigest()[:16]


async def _replay_llm_response(messages: list, tools: list):
    """Replay recorded LLM response."""
    import json

    global model, recordings_dir

    # Generate hash to find recording
    hash_key = _hash_request(model, messages, tools)

    # Find response file
    response_file = recordings_dir / f"{hash_key}.response.json"

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

    # Build mock completion object that mimics OpenAI response
    class MockMessage:
        def __init__(self, data):
            self.content = data.get("content")
            self.role = data.get("role", "assistant")
            self.tool_calls = None

            # Handle tool calls if present
            if "tool_calls" in data and data["tool_calls"]:
                class ToolCall:
                    def __init__(self, tc_data):
                        self.id = tc_data["id"]
                        self.type = tc_data["type"]

                        class Function:
                            def __init__(self, fn_data):
                                self.name = fn_data["name"]
                                self.arguments = fn_data["arguments"]

                        self.function = Function(tc_data["function"])

                self.tool_calls = [ToolCall(tc) for tc in data["tool_calls"]]

    class MockChoice:
        def __init__(self, choice_data):
            self.message = MockMessage(choice_data["message"])
            self.finish_reason = choice_data.get("finish_reason", "stop")
            self.index = choice_data.get("index", 0)

    class MockCompletion:
        def __init__(self, response):
            self.choices = [MockChoice(choice) for choice in response["choices"]]
            self.id = response.get("id", "mock_id")
            self.model = response.get("model", model)

    return MockCompletion(response_data)


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
        global openai_client, model, use_recordings, recordings_dir

        # Debug: print global variable values
        print(f"🐛 DEBUG on_message: openai_client={openai_client}, use_recordings={use_recordings}")

        user_message = context.activity.text or ""
        if not user_message.strip():
            return

        # If LLM is not configured (and not in recording playback mode), provide a helpful message
        if not openai_client and not use_recordings:
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
                # Get completion from LLM (either real or replayed)
                if use_recordings and recordings_dir:
                    # Test mode: Replay recorded response
                    completion = await _replay_llm_response(conversation_states[conv_id], tools)
                elif openai_client:
                    # Generation mode: Use real LLM
                    completion = await openai_client.chat.completions.create(
                        model=model,
                        messages=conversation_states[conv_id],
                        tools=tools
                    )
                else:
                    raise ValueError("Neither OpenAI client nor recordings available")

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
