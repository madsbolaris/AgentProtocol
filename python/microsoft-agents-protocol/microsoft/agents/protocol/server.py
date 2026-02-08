# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Agent Protocol Server

This module provides the main function to add all Agent Protocol routes to an aiohttp Application.
"""

from aiohttp.web import Application, Request, Response, json_response
from typing import TYPE_CHECKING, Dict, Any, List
import json
import uuid
from datetime import datetime
from lxml import etree

if TYPE_CHECKING:
    from microsoft.agents.hosting.core import AgentApplication


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

            # Create message element based on role
            msg_elem = etree.SubElement(thread_elem, role)

            # Add message-id if present
            if "messageId" in msg:
                msg_elem.set("message-id", msg["messageId"])

            # Add contents
            contents = msg.get("contents", [])
            for content in contents:
                kind = content.get("kind", "text")

                if kind == "text":
                    text_elem = etree.SubElement(msg_elem, "text")
                    text_elem.text = content.get("text", "")
                    # Add audience attribute if present
                    if "audience" in content:
                        text_elem.set("audience", content["audience"])

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
            responses = []
            async def capture_send(context, activities):
                for act in activities:
                    if hasattr(act, 'text'):
                        responses.append(act.text)
                return [{"id": f"mock-{i}"} for i in range(len(activities))]

            adapter.send_activities = capture_send
            turn_context.turn_state["ConnectorClient"] = MockConnectorClient()

            # Process through the agent
            await agent_app.on_turn(turn_context)

            # Convert response to Agent Protocol format
            if responses:
                response_activity = {"text": responses[0]}
            else:
                response_activity = {"text": ""}

            return convert_to_message(response_activity)

        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return empty response on error
            return convert_to_message({"text": ""})

    # Health check endpoint
    async def health_check(request: Request) -> Response:
        """Health check endpoint to verify the service is running."""
        return json_response({"status": "healthy", "version": "0.1.0"})

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
                    output = await process_message_through_agent(msg, agent_app)
                    output_messages.append(output)

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
                    output = await process_message_through_agent(msg, agent_app)
                    output_messages.append(output)

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
    async def create_and_stream(request: Request) -> Response:
        """Create a run and stream results."""
        agent_app: AgentApplication = request.app["agent_app"]

        try:
            data = await request.json()
            run_id = create_run_id()
            agent_id = data.get("agentId", "agent")
            input_messages: List[Dict[str, Any]] = data.get("input", [])

            # Set up streaming response
            response = Response(
                status=200,
                headers={
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
            await response.prepare(request)

            # Event 1: run.started
            event_seq = 1
            event = {
                "runId": run_id,
                "agentId": agent_id,
                "status": "in_progress",
                "eventSeq": event_seq,
                "startedAt": datetime.utcnow().isoformat()
            }
            await response.write(f'event: run.started\ndata: {json.dumps(event)}\n\n'.encode())

            # Process first user message
            first_user_message = next((msg for msg in input_messages if isinstance(msg, dict) and msg.get("role") == "user"), None)
            if first_user_message:
                output = await process_message_through_agent(first_user_message, agent_app)

                # Event 2: message.created
                event_seq += 1
                message_id = f"msg_{uuid.uuid4().hex[:16]}"
                event = {
                    "runId": run_id,
                    "agentId": agent_id,
                    "messageId": message_id,
                    "eventSeq": event_seq,
                    "message": {"role": "assistant", "contents": [{"kind": "text", "text": ""}]},
                    "createdAt": datetime.utcnow().isoformat()
                }
                await response.write(f'event: message.created\ndata: {json.dumps(event)}\n\n'.encode())

                # Stream the output text in chunks
                text = ""
                for content in output.get("contents", []):
                    if content.get("kind") == "text":
                        text = content.get("text", "")
                        break

                # Split by words and stream
                words = text.split()
                accumulated_text = ""
                for word in words:
                    if accumulated_text:
                        accumulated_text += " "
                    accumulated_text += word

                    event_seq += 1
                    event = {
                        "runId": run_id,
                        "agentId": agent_id,
                        "messageId": message_id,
                        "eventSeq": event_seq,
                        "message": {"contents": [{"kind": "text", "text": accumulated_text}]}
                    }
                    await response.write(f'event: message.updated\ndata: {json.dumps(event)}\n\n'.encode())

                # Event: message.completed
                event_seq += 1
                event = {
                    "runId": run_id,
                    "agentId": agent_id,
                    "messageId": message_id,
                    "eventSeq": event_seq,
                    "completedAt": datetime.utcnow().isoformat()
                }
                await response.write(f'event: message.completed\ndata: {json.dumps(event)}\n\n'.encode())

            # Event: run.completed
            event_seq += 1
            event = {
                "runId": run_id,
                "agentId": agent_id,
                "status": "completed",
                "eventSeq": event_seq,
                "completedAt": datetime.utcnow().isoformat()
            }
            await response.write(f'event: run.completed\ndata: {json.dumps(event)}\n\n'.encode())

            await response.write_eof()
            return response
        except Exception as e:
            return json_response({"error": str(e)}, status=400)

    # Stream specific run endpoint
    async def stream_run(request: Request) -> Response:
        """Stream a specific run by ID."""
        runs_db: Dict[str, Any] = request.app["runs_db"]
        run_id = request.match_info['runId']

        if run_id not in runs_db:
            return json_response({"error": "Run not found"}, status=404)

        run = runs_db[run_id]

        try:
            # Set up streaming response
            response = Response(
                status=200,
                headers={
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
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
    app.router.add_post(runs_path, create_run)
    app.router.add_post(f"{runs_path}/wait", create_and_wait)
    app.router.add_post(f"{runs_path}/stream", create_and_stream)
    app.router.add_get(f"{runs_path}/{{runId}}/stream", stream_run)

    # Only add messages endpoint if path is provided
    if messages_path is not None:
        app.router.add_post(messages_path, process_message)

    return app
