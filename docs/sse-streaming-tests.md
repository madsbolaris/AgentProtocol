# SSE Streaming Format Tests

This document describes the tests created to prevent regression of SSE streaming format issues.

## Background

During development, several issues occurred with the SSE streaming implementation:

1. **Event Type Duplication**: Event types were duplicated in the JSON data payload when they should only appear on the `event:` line
2. **UI Parsing Issues**: The UI was expecting event types in the JSON data instead of reading them from the `event:` line
3. **Property Name Inconsistency**: The .NET server was sending PascalCase property names while JavaScript expected camelCase
4. **Missing Event Handlers**: The UI didn't have handlers for `message.updated` events

## Test Coverage

### .NET Tests

Location: `dotnet/tests/Microsoft.Agents.Protocol.Hosting.Tests/SseStreamingFormatTests.cs`

#### Test: `RunsStreamEndpoint_SendsEventTypeOnEventLine`
- **Purpose**: Verifies that event types are sent on the `event:` line in SSE format
- **What it prevents**: Event types missing from SSE stream or only in JSON data
- **Example assertion**: `output.Should().Contain("event: run.created")`

#### Test: `RunsStreamEndpoint_DataLineContainsJsonWithoutEventField`
- **Purpose**: Verifies that the JSON data does NOT contain a duplicate `event` field
- **What it prevents**: Duplicating event type in both SSE `event:` line and JSON data
- **Example assertion**: `root.TryGetProperty("event", out _).Should().BeFalse()`

#### Test: `RunsStreamEndpoint_UsesCamelCasePropertyNames`
- **Purpose**: Verifies that all property names use camelCase, not PascalCase
- **What it prevents**: JavaScript parsing errors due to property name mismatches
- **Example assertions**:
  - `dataLines.Should().Contain("\"runId\"")`
  - `dataLines.Should().NotContain("\"RunId\"")`

#### Test: `RunsStreamEndpoint_SendsAllRequiredEventTypes`
- **Purpose**: Verifies that all required event types are sent during streaming
- **What it prevents**: Missing events that the UI expects
- **Example assertions**:
  - `eventList.Should().Contain("event: run.created")`
  - `eventList.Should().Contain("event: message.updated")`
  - `eventList.Should().Contain("event: run.completed")`

### Python Tests

Location: `python/microsoft-agents-hosting/tests/test_sse_streaming_format.py`

#### Test: `test_runs_stream_sends_event_type_on_event_line`
- **Purpose**: Same as .NET version - verifies event types on `event:` line
- **Example assertion**: `assert 'event: run.created' in output`

#### Test: `test_runs_stream_data_line_contains_json_without_event_field`
- **Purpose**: Same as .NET version - verifies no duplicate event field in JSON
- **Example assertion**: `assert 'event' not in data`

#### Test: `test_runs_stream_uses_camel_case_property_names`
- **Purpose**: Verifies camelCase property names (not snake_case)
- **What it prevents**: Python's tendency to use snake_case causing UI parsing errors
- **Example assertions**:
  - `assert '"runId"' in all_data`
  - `assert '"run_id"' not in all_data`

#### Test: `test_runs_stream_sends_all_required_event_types`
- **Purpose**: Same as .NET version - verifies all required events
- **Example assertion**: `assert 'run.completed' in events`

#### Test: `test_sse_format_no_nested_event_data_structure`
- **Purpose**: Explicitly verifies NO nested `{event, data}` structure
- **What it prevents**: The double-nesting mistake that was made during development
- **Example assertion**: `assert not ('event' in data and 'data' in data)`

## SSE Format Specification

The correct SSE format for Agent Protocol streaming is:

```
event: run.created
data: {"runId": "...", "threadId": "...", "status": "queued", ...}

event: run.started
data: {"runId": "...", "threadId": "...", "status": "in_progress", ...}

event: message.created
data: {"runId": "...", "threadId": "...", "message": {...}, ...}

event: message.updated
data: {"runId": "...", "threadId": "...", "messageId": "...", "message": {...}, ...}

event: message.completed
data: {"runId": "...", "threadId": "...", "messageId": "...", "usage": {...}, ...}

event: run.completed
data: {"runId": "...", "threadId": "...", "status": "completed", "output": [...], ...}
```

### Key Requirements

1. **Event Type Location**: Event type MUST be on the `event:` line, NOT in the JSON data
2. **No Duplication**: The JSON data MUST NOT contain an `event` field
3. **Property Naming**: All property names MUST use camelCase (e.g., `runId`, not `RunId` or `run_id`)
4. **Event Sequence**: Events MUST include an `eventSeq` field for ordering

## UI Requirements

The UI (`demos/agent-demo.html`) has been updated to:

1. **Parse Event Line**: Read event type from `event:` line and store in `currentEventType`
2. **Parse Data Line**: Parse JSON from `data:` line as `eventData`
3. **Handle Case Variations**: Support both camelCase and PascalCase property names for compatibility
4. **Handle All Events**: Process `message.updated` events for streaming text display

## Running the Tests

### .NET
```bash
cd dotnet/tests/Microsoft.Agents.Protocol.Hosting.Tests
dotnet test --filter "FullyQualifiedName~SseStreamingFormatTests"
```

### Python
```bash
cd python/microsoft-agents-hosting
pytest tests/test_sse_streaming_format.py -v
```

## Integration with CI/CD

These tests should be run as part of the CI/CD pipeline to prevent regression. They validate the contract between the server and client for SSE streaming.
