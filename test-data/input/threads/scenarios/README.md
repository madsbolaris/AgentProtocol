# Scenario Test Files

This directory contains test files for real-world usage scenarios and patterns.

## Subdirectories

### queries/
Tests for query-based scenarios:
- `50-weather-query.xml` - Weather information query
- `51-time-query.xml` - Time/date query

**Total**: 2 files

**Purpose**: Validates common information retrieval patterns.

### functions/
Tests for function calling scenarios:
- `52-multi-function.xml` - Multiple function calls scenario
- `53-no-function.xml` - Scenario without function calls

**Total**: 2 files

**Purpose**: Validates function calling patterns and non-function scenarios.

### events/
Tests for event-based scenarios:
- `78-user-joined-event.xml` - User joined conversation event
- `79-user-left-event.xml` - User left conversation event
- `80-emoji-reaction-added.xml` - Emoji reaction added event
- `81-emoji-reaction-removed.xml` - Emoji reaction removed event
- `82-user-request-add-emoji.xml` - User requests to add emoji
- `83-user-request-suggest-emoji.xml` - User requests emoji suggestions
- `84-multiple-emoji-reactions.xml` - Multiple emoji reactions in thread

**Total**: 7 files

**Purpose**: Validates event-driven interactions, particularly for collaborative platforms.

## Purpose

These files validate real-world usage patterns that combine multiple protocol features into cohesive scenarios.

## Testing Focus

### Query Scenarios
- Information retrieval patterns
- Question-answering flows
- Search and lookup operations
- API integration queries

Example: Weather Query
```xml
<user>What's the weather in Seattle?</user>
<agent>
  <function-call name="get_weather" call-id="call1">
    {"location": "Seattle"}
  </function-call>
</agent>
<tool call-id="call1">
  <function-result>{"temp": 65, "condition": "Sunny"}</function-result>
</tool>
<agent>It's 65°F and sunny in Seattle!</agent>
```

### Function Scenarios
- Function discovery and selection
- Argument passing and validation
- Result handling and formatting
- Multi-function orchestration
- Fallback when functions unavailable

Example: Multi-Function
```xml
<user>Book a flight and hotel</user>
<agent>
  <function-call name="search_flights" call-id="call1">...</function-call>
  <function-call name="search_hotels" call-id="call2">...</function-call>
</agent>
```

### Event Scenarios
- User lifecycle events (join/leave)
- Interaction events (reactions, edits)
- Presence and activity updates
- Notification patterns
- Real-time collaboration

Example: User Joined
```xml
<event type="user_joined">
  <user-id>user_123</user-id>
  <timestamp>2024-02-09T12:00:00Z</timestamp>
</event>
<agent>Welcome user_123!</agent>
```

Example: Emoji Reactions
```xml
<user>Great idea! 👍</user>
<event type="reaction_added">
  <message-id>msg_001</message-id>
  <reaction>👍</reaction>
  <user-id>user_123</user-id>
</event>
```

## Scenario Categories

### 1. Information Access
- Queries for data
- API integrations
- Knowledge retrieval
- Search operations

### 2. Task Execution
- Multi-step workflows
- Function orchestration
- Resource management
- Error handling

### 3. Collaboration
- Multi-user coordination
- Event notifications
- Presence awareness
- Social interactions (reactions, mentions)

### 4. Platform Integration
- Teams/Slack events
- Emoji and reactions
- User management
- Channel operations

## Emoji Reaction Scenarios

The emoji scenarios (80-84) test platform-specific features:
- Adding reactions to messages
- Removing reactions
- Multiple reactions on one message
- User requests for emoji suggestions
- Emoji as communication primitives

These are particularly relevant for:
- Microsoft Teams integration
- Slack integration
- Discord integration
- Social collaboration platforms

## Total Files

**11 files** across 3 subdirectories, covering common real-world usage patterns.

## Validation Rules

Scenario tests ensure:
- End-to-end flows complete successfully
- Multi-step processes maintain context
- Events trigger appropriate responses
- Functions are called with correct arguments
- Results are properly formatted for users

## Usage Example

```python
# Python - Test weather query scenario
thread = parse_thread_xml("scenarios/queries/50-weather-query.xml")

# Find the user query
user_msg = [m for m in thread.messages if m.role == "user"][0]
assert "weather" in user_msg.text.lower()

# Find the function call
agent_msg = [m for m in thread.messages if m.role == "agent"][0]
assert any(c.kind == "function_call" for c in agent_msg.contents)

# Find the tool result
tool_msg = [m for m in thread.messages if m.role == "tool"][0]
assert tool_msg.call_id is not None
```

```typescript
// TypeScript - Test emoji reaction scenario
const thread = parseThreadXml("scenarios/events/84-multiple-emoji-reactions.xml");

// Verify multiple reactions are present
const reactions = thread.messages.filter(m =>
  m.contents.some(c => c.kind === "message-reaction")
);
expect(reactions.length).toBeGreaterThan(1);
```

## Related Directories

- See `../conversations/` for conversation flow patterns
- See `../content-types/functions/` for function call details
- See `../content-types/system/` for event content types
- See `../basic/` for individual message types used in scenarios
