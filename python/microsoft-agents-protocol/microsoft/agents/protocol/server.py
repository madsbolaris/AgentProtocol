# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Agent Protocol Server

This module provides the main function to add all Agent Protocol routes to an aiohttp Application.
"""

from aiohttp.web import Application, Request, Response, StreamResponse, json_response, middleware
from typing import TYPE_CHECKING, Dict, Any, List, Callable, Awaitable
import json
import uuid
from datetime import datetime
from lxml import etree

if TYPE_CHECKING:
    from microsoft.agents.hosting.core import AgentApplication


@middleware
async def cors_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
    """CORS middleware to add headers to all responses."""
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = Response(status=204)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response

    # Process the request
    response = await handler(request)

    # Add CORS headers to response
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = '*'

    return response


def _create_sse_response() -> StreamResponse:
    """Create a Server-Sent Events response with CORS headers."""
    response = StreamResponse(
        status=200,
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )
    # Add CORS headers for browser access
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = '*'
    return response


def add_agent_protocol_routes(
    app: Application,
    agent_application: "AgentApplication",
    health_path: str = "/health",
    runs_path: str = "/runs",
    messages_path: str | None = "/api/messages"
) -> Application:
    """
    Add Agent Protocol routes to the aiohttp application.

    This is the one-liner that adds all Agent Protocol endpoints:
    - /health - Health check endpoint
    - /runs - Create a new run
    - /runs/wait - Create a run and wait for completion
    - /runs/stream - Create a run and stream results
    - /runs/{runId}/stream - Stream a specific run
    - /api/messages - Process messages directly

    Args:
        app: The aiohttp Application
        agent_application: The AgentApplication instance from M365 Agents SDK
        health_path: Path for health check endpoint (default: "/health")
        runs_path: Base path for runs endpoints (default: "/runs")
        messages_path: Path for direct message processing (default: "/api/messages")

    Returns:
        The aiohttp Application (for chaining)

    Example:
        from aiohttp.web import Application
        from microsoft.agents.hosting.core import AgentApplication
        from microsoft.agents.protocol import add_agent_protocol_routes

        agent_app = AgentApplication(...)
        app = Application()
        add_agent_protocol_routes(app, agent_app)
    """

    # Add CORS middleware to handle all routes
    if not any(m.__name__ == 'cors_middleware' for m in app.middlewares):
        app.middlewares.append(cors_middleware)

    # Store agent_application in app for access in route handlers
    app["agent_app"] = agent_application
    app["runs_db"] = {}  # Simple in-memory runs database

    # Helper functions
    def create_run_id() -> str:
        """Generate a unique run ID."""
        return f"run_{uuid.uuid4().hex[:16]}"

    def convert_to_activity(message: Dict[str, Any]) -> Any:
        """
        Convert an Agent Protocol message to a Bot Framework Activity.

        TODO: This is a placeholder implementation.
        In a real implementation, this would properly convert the message
        structure to the M365 Agents SDK Activity format.
        """
        # Extract role from message (default to "user")
        role = message.get("role", "user")

        # Extract text from message contents
        text = ""
        if "contents" in message and isinstance(message["contents"], list):
            for content in message["contents"]:
                if isinstance(content, dict) and content.get("kind") == "text":
                    text = content.get("text", "")
                    break

        # Return a simple dict representing an Activity
        return {
            "type": "message",
            "text": text,
            "from": {"id": "user", "name": "User"},
            "recipient": {"id": "bot", "name": "Bot"},
            "conversation": {"id": str(uuid.uuid4())},
            "channelId": "agent-protocol",
            "serviceUrl": "https://agent-protocol",
            "channelData": {"role": role}  # Preserve role information
        }

    def convert_to_message(activity: Any) -> Dict[str, Any]:
        """
        Convert a Bot Framework Activity to an Agent Protocol message.

        TODO: This is a placeholder implementation.
        In a real implementation, this would properly convert the Activity
        to the Agent Protocol message format.
        """
        text = activity.get("text", "") if isinstance(activity, dict) else str(activity)
        return {
            "role": "assistant",
            "contents": [
                {
                    "kind": "text",
                    "text": text
                }
            ]
        }

    def parse_xml_message(xml_string: str) -> Dict[str, Any]:
        """
        Parse XML message string into Agent Protocol message format.

        Supports XML messages like:
        <user user-id="..." author-name="..." created-at="...">
          <text audience="...">Message text</text>
        </user>

        Args:
            xml_string: XML string to parse

        Returns:
            Message dict with role and contents
        """
        try:
            # Parse XML
            root = etree.fromstring(xml_string.encode('utf-8'))

            # Extract role from root element tag
            role = root.tag  # e.g., "user", "assistant", "system"

            # Extract text content
            text_elem = root.find(".//text")
            text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

            # Build message dict
            return {
                "role": role,
                "contents": [
                    {
                        "kind": "text",
                        "text": text
                    }
                ]
            }
        except Exception as e:
            # If parsing fails, treat as plain text user message
            return {
                "role": "user",
                "contents": [
                    {
                        "kind": "text",
                        "text": xml_string
                    }
                ]
            }

    def build_thread_xml(thread_id: str, output_messages: List[Dict[str, Any]],
                        created_at: str, status: str = "active") -> str:
        """
        Build Thread XML from output messages.

        Args:
            thread_id: The thread identifier
            output_messages: List of output message dictionaries
            created_at: ISO timestamp when thread was created
            status: Thread status (default: "active")

        Returns:
            XML string representation of the Thread
        """
        # Create root thread element with attributes
        thread_elem = etree.Element("thread")
        thread_elem.set("thread-id", thread_id)
        thread_elem.set("status", status)
        thread_elem.set("created-at", created_at)

        # Add each message as a child element
        for msg in output_messages:
            role = msg.get("role", "agent")

            # Get contents first to determine if message is empty
            contents = msg.get("contents", [])
            has_contents = bool(contents)

            # Create message element based on role
            msg_elem = etree.SubElement(thread_elem, role)

            # Note: message-id attribute omitted for consistency with .NET and TypeScript echo bots
            # Even if messageId exists in the message dictionary, we don't serialize it to XML
            # if "messageId" in msg:
            #     msg_elem.set("message-id", msg["messageId"])

            # Add contents if present
            if has_contents:
                for content in contents:
                    kind = content.get("kind", "text")

                    if kind == "text":
                        text_elem = etree.SubElement(msg_elem, "text")
                        text_elem.text = content.get("text", "")
                        # Add audience attribute if present
                        if "audience" in content:
                            text_elem.set("audience", content["audience"])

                    elif kind == "functionCall":
                        func_call_elem = etree.SubElement(msg_elem, "function-call")
                        func_call_elem.set("call-id", content.get("callId", ""))
                        func_call_elem.set("name", content.get("name", ""))
                        func_call_elem.text = content.get("arguments", "")

                    elif kind == "functionResult":
                        func_result_elem = etree.SubElement(msg_elem, "function-result")
                        func_result_elem.set("call-id", content.get("callId", ""))
                        func_result_elem.text = content.get("result", "")

        # Generate XML string with declaration and pretty printing
        xml_str = etree.tostring(
            thread_elem,
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=True
        ).decode("utf-8")

        return xml_str

    async def process_message_through_agent(
        input_message: Dict[str, Any],
        agent_app: "AgentApplication"
    ) -> Dict[str, Any]:
        """
        Process a message through the agent using the M365 Agents SDK.
        """
        try:
            # Convert to Activity dictionary
            activity_data = convert_to_activity(input_message)

            # Import required classes
            from microsoft_agents.activity import Activity
            from microsoft_agents.hosting.core import TurnContext
            from microsoft_agents.hosting.aiohttp import CloudAdapter

            # Create Activity object
            activity = Activity(**activity_data)

            # Create adapter and turn context
            adapter = CloudAdapter()
            turn_context = TurnContext(adapter, activity)

            # Mock connector client to avoid errors
            class MockConnectorClient:
                def __init__(self):
                    self.conversations = self
                async def send_to_conversation(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}
                async def reply_to_activity(self, *args, **kwargs):
                    return {"id": "mock-activity-id"}

            # Capture responses sent by the agent
            output_messages = []
            async def capture_send(context, activities):
                from datetime import datetime
                for act in activities:
                    # Check if activity has Agent Protocol formatted value
                    if hasattr(act, 'value') and act.value:
                        message = act.value
                        # Ensure message has required fields
                        # Note: messageId omitted for consistency with .NET and TypeScript echo bots
                        # if "messageId" not in message:
                        #     message["messageId"] = f"msg_{uuid.uuid4().hex[:12]}"
                        if "createdAt" not in message:
                            message["createdAt"] = datetime.utcnow().isoformat() + "Z"
                        # CRITICAL: Ensure role is "agent" not "assistant"
                        # Agent Protocol uses "agent" role, NOT "assistant"
                        # DO NOT CHANGE THIS TO "assistant" - see TypeSpec ChatRole enum
                        if message.get("role") == "assistant":
                            message["role"] = "agent"
                        output_messages.append(message)
                    elif hasattr(act, 'text') and act.text:
                        # Fallback to text-only response
                        # CRITICAL: Role must be "agent" not "assistant"
                        # Agent Protocol uses "agent" role, NOT "assistant"
                        # DO NOT CHANGE THIS TO "assistant" - see TypeSpec ChatRole enum
                        output_messages.append({
                            # Note: messageId omitted for consistency with .NET and TypeScript echo bots
                            # "messageId": f"msg_{uuid.uuid4().hex[:12]}",
                            "role": "agent",
                            "createdAt": datetime.utcnow().isoformat() + "Z",
                            "contents": [{"kind": "text", "text": act.text}]
                        })
                return [{"id": f"mock-{i}"} for i in range(len(activities))]

            adapter.send_activities = capture_send
            turn_context.turn_state["ConnectorClient"] = MockConnectorClient()

            # Process through the agent
            await agent_app.on_turn(turn_context)

            # Return ALL output messages generated by the agent
            return output_messages if output_messages else []

        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return empty response on error
            return convert_to_message({"text": ""})

    def _add_cors_headers(response: Response) -> Response:
        """Add CORS headers to response for browser access."""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Expose-Headers'] = '*'
        return response

    # Health check endpoint
    async def health_check(request: Request) -> Response:
        """Health check endpoint to verify the service is running."""
        response = json_response({"status": "healthy", "version": "0.1.0"})
        return _add_cors_headers(response)

    async def get_agent_card(request: Request) -> Response:
        """Get agent card with capabilities."""
        agent_card = {
            "agentId": "basic-m365",
            "name": "Basic M365 Agent",
            "description": "A basic agent that can check weather and tell time",
            "version": "1.0.0",
            "outputModes": ["text"],
            "inputModes": ["text"]
        }
        response = json_response(agent_card)
        return _add_cors_headers(response)

    # Create run endpoint
    async def create_run(request: Request) -> Response:
        """Create a new run with the agent."""
        agent_app: AgentApplication = request.app["agent_app"]
        runs_db: Dict[str, Any] = request.app["runs_db"]

        # Get format query parameter (default to json)
        response_format = request.query.get("format", "json")

        try:
            data = await request.json()
            run_id = create_run_id()
            agent_id = data.get("agentId", data.get("agent", {}).get("id", "agent"))
            thread_id = data.get("threadId", f"thread_{uuid.uuid4().hex[:16]}")

            # Support both direct "input" and nested "thread.messages" formats
            input_messages: List[Any] = data.get("input", [])
            if not input_messages and "thread" in data:
                input_messages = data["thread"].get("messages", [])

            # Parse messages (convert XML strings to dicts if needed)
            parsed_messages = []
            for msg in input_messages:
                if isinstance(msg, str):
                    # Parse XML string
                    parsed_messages.append(parse_xml_message(msg))
                elif isinstance(msg, dict):
                    parsed_messages.append(msg)

            # Process each message through the agent (only user messages)
            output_messages = []
            for msg in parsed_messages:
                # Only process user messages
                if isinstance(msg, dict) and msg.get("role") == "user":
                    agent_responses = await process_message_through_agent(msg, agent_app)
                    # Extend with all messages from agent (could be multiple: assistant, tool, assistant)
                    output_messages.extend(agent_responses)

            created_at = datetime.utcnow().isoformat()
            completed_at = datetime.utcnow().isoformat()

            # Per TypeSpec, input field has @visibility("create") which means it should
            # ONLY appear in request bodies, NOT in response bodies.
            run = {
                "runId": run_id,
                "agentId": agent_id,
                "threadId": thread_id,
                "status": "completed",
                "output": output_messages,
                "createdAt": created_at,
                "completedAt": completed_at
            }

            runs_db[run_id] = run

            # Return XML or JSON based on format parameter
            if response_format == "xml":
                xml_str = build_thread_xml(thread_id, output_messages, created_at)
                return Response(
                    body=xml_str,
                    content_type="application/xml",
                    status=201
                )
            else:
                return json_response(run, status=201)
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Create and wait endpoint
    async def create_and_wait(request: Request) -> Response:
        """Create a run and wait for completion."""
        agent_app: AgentApplication = request.app["agent_app"]
        runs_db: Dict[str, Any] = request.app["runs_db"]

        # Get format query parameter (default to json)
        response_format = request.query.get("format", "json")

        try:
            data = await request.json()
            run_id = create_run_id()
            agent_id = data.get("agentId", data.get("agent", {}).get("id", "agent"))
            thread_id = data.get("threadId", f"thread_{uuid.uuid4().hex[:16]}")

            # Support both direct "input" and nested "thread.messages" formats
            input_messages: List[Any] = data.get("input", [])
            if not input_messages and "thread" in data:
                input_messages = data["thread"].get("messages", [])

            # Parse messages (convert XML strings to dicts if needed)
            parsed_messages = []
            for msg in input_messages:
                if isinstance(msg, str):
                    # Parse XML string
                    parsed_messages.append(parse_xml_message(msg))
                elif isinstance(msg, dict):
                    parsed_messages.append(msg)

            # Process each message through the agent (only user messages)
            output_messages = []
            for msg in parsed_messages:
                # Only process user messages
                if isinstance(msg, dict) and msg.get("role") == "user":
                    agent_responses = await process_message_through_agent(msg, agent_app)
                    # Extend with all messages from agent (could be multiple: assistant, tool, assistant)
                    output_messages.extend(agent_responses)

            created_at = datetime.utcnow().isoformat()
            completed_at = datetime.utcnow().isoformat()

            # Per TypeSpec, input field has @visibility("create") which means it should
            # ONLY appear in request bodies, NOT in response bodies.
            run = {
                "runId": run_id,
                "agentId": agent_id,
                "threadId": thread_id,
                "status": "completed",
                "output": output_messages,
                "createdAt": created_at,
                "completedAt": completed_at
            }

            runs_db[run_id] = run

            # Return XML or JSON based on format parameter
            if response_format == "xml":
                xml_str = build_thread_xml(thread_id, output_messages, created_at)
                return Response(
                    body=xml_str,
                    content_type="application/xml",
                    status=200
                )
            else:
                return json_response(run, status=200)
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Create and stream endpoint
    async def create_and_stream(request: Request) -> StreamResponse:
        """Create a run and stream results."""
        agent_app: AgentApplication = request.app["agent_app"]

        try:
            data = await request.json()
            run_id = create_run_id()
            agent_id = data.get("agentId", "agent")
            thread_id = data.get("threadId", f"thread_{uuid.uuid4().hex[:16]}")
            input_messages: List[Dict[str, Any]] = data.get("input", [])

            # Set up streaming response with CORS headers
            response = _create_sse_response()
            await response.prepare(request)

            created_at = datetime.utcnow().isoformat()

            # Helper to send SSE event
            async def send_event(event_name: str, event_data: dict):
                # Send SSE event with proper format: event line + data line
                # Don't wrap event_data - SSE format already provides event/data structure
                await response.write(f'event: {event_name}\ndata: {json.dumps(event_data)}\n\n'.encode())
                await response.drain()  # Flush the data to the client

            # Event: run.started
            await send_event('run.started', {
                "runId": run_id,
                "agentId": agent_id,
                "threadId": thread_id,
                "status": "in_progress",
                "createdAt": created_at
            })

            # Process each message through the agent (only user messages)
            output_messages = []
            for msg in input_messages:
                if isinstance(msg, dict) and msg.get("role") == "user":
                    agent_responses = await process_message_through_agent(msg, agent_app)
                    output_messages.extend(agent_responses)

            # Get the response text for streaming
            full_output_text = ""
            if output_messages:
                last_message = output_messages[-1]
                if isinstance(last_message, dict):
                    for content in last_message.get("contents", []):
                        if content.get("kind") == "text":
                            full_output_text = content.get("text", "")
                            break

            # Stream the output text in chunks (word-by-word for visual effect)
            if full_output_text:
                words = full_output_text.split()

                for i, word in enumerate(words):
                    chunk = word if i == 0 else " " + word

                    # Event: message.delta with delta containing the text chunk
                    # CRITICAL: Role must be "agent" not "assistant"
                    # Agent Protocol uses "agent" role, NOT "assistant"
                    # DO NOT CHANGE THIS TO "assistant" - see TypeSpec ChatRole enum
                    await send_event('message.delta', {
                        "runId": run_id,
                        "agentId": agent_id,
                        "threadId": thread_id,
                        "delta": {
                            "role": "agent",
                            "contents": [{"kind": "text", "text": chunk}]
                        }
                    })

                    # Small delay to simulate streaming effect
                    import asyncio
                    await asyncio.sleep(0.03)

            completed_at = datetime.utcnow().isoformat()

            # Event: run.completed
            await send_event('run.completed', {
                "runId": run_id,
                "agentId": agent_id,
                "threadId": thread_id,
                "status": "completed",
                "output": output_messages,
                "createdAt": created_at,
                "completedAt": completed_at
            })

            await response.write_eof()
            return response
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Stream specific run endpoint
    async def stream_run(request: Request) -> StreamResponse:
        """Stream a specific run by ID."""
        runs_db: Dict[str, Any] = request.app["runs_db"]
        run_id = request.match_info['runId']

        if run_id not in runs_db:
            return json_response({"error": "Run not found"}, status=404)

        run = runs_db[run_id]

        try:
            # Set up streaming response with CORS headers
            response = _create_sse_response()
            await response.prepare(request)

            # Event 1: run.started
            event = {
                "runId": run_id,
                "status": "in_progress",
                "eventSeq": 1
            }
            await response.write(f'event: run.started\ndata: {json.dumps(event)}\n\n'.encode())

            # Event 2: run.completed
            event = {
                "runId": run_id,
                "status": "completed",
                "output": run.get("output", []),
                "eventSeq": 2
            }
            await response.write(f'event: run.completed\ndata: {json.dumps(event)}\n\n'.encode())

            await response.write_eof()
            return response
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Process message directly endpoint
    async def process_message(request: Request) -> Response:
        """Process a message directly through the agent."""
        agent_app: AgentApplication = request.app["agent_app"]

        try:
            data = await request.json()
            output = await process_message_through_agent(data, agent_app)
            return json_response(output)
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Register all routes
    app.router.add_get(health_path, health_check)
    app.router.add_get("/agent-card", get_agent_card)
    app.router.add_post(runs_path, create_run)
    app.router.add_post(f"{runs_path}/wait", create_and_wait)
    app.router.add_post(f"{runs_path}/stream", create_and_stream)
    app.router.add_get(f"{runs_path}/{{runId}}/stream", stream_run)

    # Only add messages endpoint if path is provided
    if messages_path is not None:
        app.router.add_post(messages_path, process_message)

    return app
