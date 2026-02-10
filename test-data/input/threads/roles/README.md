# Role-Based Test Files

This directory contains test files organized by message roles and role patterns.

## Subdirectories

### agent-only/
Tests for threads containing only agent messages:
- `36-agent-only-thread.xml` - Thread with agent messages exclusively

**Total**: 1 file

**Purpose**: Validates agent-to-agent communication, autonomous agent threads, or system-generated content threads.

### tool-only/
Tests for threads containing only tool messages:
- `37-tool-only-thread.xml` - Thread with tool messages exclusively

**Total**: 1 file

**Purpose**: Validates tool result logging, batch tool execution results, or system integration threads.

### interleaved/
Tests for threads with mixed role patterns:
- `39-interleaved-roles.xml` - Thread with roles appearing in non-standard order
- `47-system-then-users.xml` - Thread starting with system, followed by multiple users

**Total**: 2 files

**Purpose**: Validates flexible role ordering, role transitions, and non-sequential conversation patterns.

### all-roles/
Tests for threads containing all available role types:
- `41-all-non-user-roles.xml` - Thread with system, developer, agent, tool, and channel roles (no user)

**Total**: 1 file

**Purpose**: Validates comprehensive role support and role interoperability.

## Role Types in Agent Protocol

The Agent Protocol defines six primary roles:

1. **system** - System instructions and configuration
2. **developer** - Developer instructions and hints
3. **user** - End-user messages
4. **agent** - AI agent responses
5. **tool** - Tool/function execution results
6. **channel** - Channel-specific messages (Teams, Slack, etc.)

## Purpose

These files validate:
- Role-specific message handling
- Role-based access control
- Role transitions and sequencing
- Role attribute requirements
- Special role behaviors

## Testing Focus

### Role Isolation
- Single-role threads must handle gracefully
- Role-specific validation rules apply
- Missing roles shouldn't break parsing

### Role Combinations
- Any role can follow any role (with exceptions)
- Tool messages must follow function calls
- System/developer typically appear early

### Role Attributes
- **system**: No user/agent identifiers
- **developer**: No user identifiers
- **user**: Requires `user-id`
- **agent**: Requires `agent-id`
- **tool**: Requires `call-id` and optionally `name`
- **channel**: May include channel-specific metadata

## Role Patterns

### Standard Pattern
```xml
<thread>
  <system>...</system>
  <user user-id="user1">...</user>
  <agent agent-id="agent1">...</agent>
</thread>
```

### Tool Pattern
```xml
<thread>
  <user>Call function</user>
  <agent><function-call call-id="call1"/></agent>
  <tool call-id="call1"><function-result/></tool>
  <agent>Here's the result</agent>
</thread>
```

### Multi-Agent Pattern
```xml
<thread>
  <agent agent-id="agent1">...</agent>
  <agent agent-id="agent2">...</agent>
</thread>
```

## Validation Rules

Role-specific validation includes:
- System messages should not contain function calls
- Tool messages must reference function calls
- User messages require user identification
- Agent messages require agent identification
- Channel messages may have platform-specific attributes

## Total Files

**5 files** across 4 subdirectories, covering all role patterns and combinations.

## Special Considerations

### Empty Threads
Not in this directory - see `../edge-cases/empty/`

### Invalid Roles
Not in this directory - see `../invalid/` for malformed role testing

### Role Mixing
Some platforms may restrict certain role combinations. These tests ensure protocol-level support, but platforms may add additional constraints.

## Usage Example

```python
# Python - Test agent-only thread
thread = parse_thread_xml("roles/agent-only/36-agent-only-thread.xml")
assert all(msg.role == "agent" for msg in thread.messages)

# Test all roles
thread = parse_thread_xml("roles/all-roles/41-all-non-user-roles.xml")
roles = {msg.role for msg in thread.messages}
assert "system" in roles
assert "agent" in roles
assert "tool" in roles
```

## Related Directories

- See `../basic/messages/` for individual role message examples
- See `../conversations/` for role interactions in conversations
- See `../invalid/` for invalid role testing
