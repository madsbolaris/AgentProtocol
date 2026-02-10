"""
Tests to validate SSE streaming format correctness.

These tests prevent regression of issues where:
- Event types were duplicated in JSON data
- Event types were not properly parsed from "event:" line
- Property names were inconsistent (snake_case vs camelCase)
"""

import json
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer


@pytest.mark.asyncio
async def test_runs_stream_sends_event_type_on_event_line():
    """Verify that event types are sent on 'event:' line in SSE format."""
    from microsoft.agents.hosting.hosting.agent_host import add_agent_protocol_routes

    app = web.Application()
    add_agent_protocol_routes(app, agent_application=None, auth_configuration=None)

    async with TestClient(TestServer(app)) as client:
        # Send request to /runs/stream
        resp = await client.post(
            '/runs/stream',
            json={
                'input': [{
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': 'test'}]
                }]
            }
        )

        assert resp.status == 200
        assert resp.content_type == 'text/event-stream'

        # Read first few chunks to get at least one complete event
        lines = []
        async for line in resp.content:
            decoded = line.decode('utf-8')
            lines.append(decoded)
            if len(lines) > 10:
                break

        output = ''.join(lines)

        # Assert - SSE format has event type on "event:" line
        assert 'event: run.created' in output, "SSE events must have event type on 'event:' line"
        assert 'event: run.started' in output, "SSE events must have event type on 'event:' line"


@pytest.mark.asyncio
async def test_runs_stream_data_line_contains_json_without_event_field():
    """Verify that data line contains JSON without duplicate event field."""
    from microsoft.agents.hosting.hosting.agent_host import add_agent_protocol_routes

    app = web.Application()
    add_agent_protocol_routes(app, agent_application=None, auth_configuration=None)

    async with TestClient(TestServer(app)) as client:
        resp = await client.post(
            '/runs/stream',
            json={
                'input': [{
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': 'test'}]
                }]
            }
        )

        # Parse SSE format to find first complete event
        current_event = None
        data_line = None

        async for line in resp.content:
            decoded = line.decode('utf-8').strip()

            if decoded.startswith('event: '):
                current_event = decoded[7:]
            elif decoded.startswith('data: ') and current_event:
                data_line = decoded[6:]
                break

        assert data_line is not None, "SSE events must have data line"

        # Parse JSON
        data = json.loads(data_line)

        # Event type should NOT be duplicated in the JSON data
        assert 'event' not in data, \
            "Event type should be on 'event:' line, not duplicated in JSON data"

        # Verify expected properties exist with camelCase naming
        assert 'runId' in data, "JSON should use camelCase property names"
        assert 'threadId' in data, "JSON should use camelCase property names"
        assert 'eventSeq' in data, "JSON should include event sequence number"


@pytest.mark.asyncio
async def test_runs_stream_uses_camel_case_property_names():
    """Verify that property names use camelCase consistently."""
    from microsoft.agents.hosting.hosting.agent_host import add_agent_protocol_routes

    app = web.Application()
    add_agent_protocol_routes(app, agent_application=None, auth_configuration=None)

    async with TestClient(TestServer(app)) as client:
        resp = await client.post(
            '/runs/stream',
            json={
                'input': [{
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': 'test'}]
                }]
            }
        )

        # Collect all data lines
        data_lines = []
        async for line in resp.content:
            decoded = line.decode('utf-8').strip()
            if decoded.startswith('data: '):
                data_lines.append(decoded[6:])
            if len(data_lines) > 5:
                break

        all_data = '\n'.join(data_lines)

        # Assert - verify camelCase is used consistently
        assert '"runId"' in all_data, "Property names should be camelCase"
        assert '"threadId"' in all_data, "Property names should be camelCase"
        assert '"agentId"' in all_data, "Property names should be camelCase"
        assert '"createdAt"' in all_data, "Property names should be camelCase"
        assert '"eventSeq"' in all_data, "Property names should be camelCase"

        # These snake_case names should NOT appear
        assert '"run_id"' not in all_data, "Should not use snake_case"
        assert '"thread_id"' not in all_data, "Should not use snake_case"


@pytest.mark.asyncio
async def test_runs_stream_sends_all_required_event_types():
    """Verify that all required event types are sent during streaming."""
    from microsoft.agents.hosting.hosting.agent_host import add_agent_protocol_routes

    app = web.Application()
    add_agent_protocol_routes(app, agent_application=None, auth_configuration=None)

    async with TestClient(TestServer(app)) as client:
        resp = await client.post(
            '/runs/stream',
            json={
                'input': [{
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': 'test'}]
                }]
            }
        )

        # Collect all event types
        events = []
        async for line in resp.content:
            decoded = line.decode('utf-8').strip()
            if decoded.startswith('event: '):
                events.append(decoded[7:])
            # Stop after collecting enough events
            if 'run.completed' in events:
                break

        # Assert - verify all required event types are sent
        assert 'run.created' in events, "Must send run.created event"
        assert 'run.started' in events, "Must send run.started event"
        assert 'message.created' in events, "Must send message.created event"
        assert 'message.updated' in events, "Must send message.updated events for streaming"
        assert 'message.completed' in events, "Must send message.completed event"
        assert 'run.completed' in events, "Must send run.completed event"


@pytest.mark.asyncio
async def test_sse_format_no_nested_event_data_structure():
    """Verify that SSE data does NOT contain nested {event, data} structure."""
    from microsoft.agents.hosting.hosting.agent_host import add_agent_protocol_routes

    app = web.Application()
    add_agent_protocol_routes(app, agent_application=None, auth_configuration=None)

    async with TestClient(TestServer(app)) as client:
        resp = await client.post(
            '/runs/stream',
            json={
                'input': [{
                    'role': 'user',
                    'contents': [{'kind': 'text', 'text': 'test'}]
                }]
            }
        )

        # Parse first data line
        data_line = None
        async for line in resp.content:
            decoded = line.decode('utf-8').strip()
            if decoded.startswith('data: '):
                data_line = decoded[6:]
                break

        assert data_line is not None

        # Parse JSON
        data = json.loads(data_line)

        # Should NOT have nested structure like {"event": "...", "data": {...}}
        assert not (
            'event' in data and 'data' in data and isinstance(data.get('data'), dict)
        ), "Should not use nested {event, data} structure - event type is on 'event:' line"
