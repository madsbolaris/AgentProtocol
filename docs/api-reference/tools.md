# Tools Reference

Complete reference for tool definitions, execution patterns, and lifecycle hooks.

**TypeSpec Source**: [tools.tsp](../typespec/tools.tsp), [Tool Execution Spec](../specifications/tool-execution.md)

---

## Overview

Tools enable agents to interact with external systems, APIs, and functions. The Agent Runtime API uses a client-side tool execution model where:

1. **Agent generates tool call** (functionCall content)
2. **Client executes tool** (local function or API call)
3. **Client submits result** (POST /runs/{runId}/submit_tool_outputs)
4. **Agent processes result** (continues execution)

**Key Concept**: Server does NOT execute tools. Client has full control over tool execution.

---

## AITool Model

**TypeSpec**: [tools.tsp](../typespec/tools.tsp) lines 1-68

```typescript
model AITool {
  name: string;                        // Tool identifier (unique per agent)
  description: string;                 // What the tool does (LLM sees this)
  parameters?: JSONSchema;             // Input schema (JSON Schema Draft 7)
  returnType?: JSONSchema;             // Output schema (optional)
  strict?: boolean;                    // Strict schema enforcement (default: false)
  scopes?: Scopes;                     // OAuth2 scopes required
  lifecycleHooks?: ToolLifecycleHooks; // Before/after execution guardrails
  metadata?: Record<unknown>;          // Custom metadata
}
```

### Fields

#### `name` (required)
- **Type**: `string`
- **Purpose**: Unique identifier for the tool
- **Format**: lowercase, snake_case recommended
- **Examples**: `search`, `send_email`, `get_weather`

#### `description` (required)
- **Type**: `string`
- **Purpose**: Explains what the tool does to the LLM
- **Best Practice**: Be specific and include when to use the tool
- **Example**: "Search the web for current information about topics, news, or recent events. Use when user asks for up-to-date information."

#### `parameters` (optional)
- **Type**: `JSONSchema` (JSON Schema Draft 7)
- **Purpose**: Defines expected input structure
- **Required Fields**: `type`, `properties`
- **Best Practice**: Always include descriptions for each property

#### `returnType` (optional)
- **Type**: `JSONSchema` (JSON Schema Draft 7)
- **Purpose**: Documents expected output structure
- **Note**: Not enforced by runtime, but useful for documentation

#### `strict` (optional)
- **Type**: `boolean`
- **Default**: `false`
- **Purpose**: Enable strict schema validation (OpenAI-style)
- **Effect**: LLM must generate arguments that exactly match schema

#### `scopes` (optional)
- **Type**: `Record<string>` (scope URI → description)
- **Purpose**: OAuth2 scopes required for tool execution
- **Example**: `{"https://graph.microsoft.com/Mail.Send": "Send mail as user"}`
- **Behavior**: If scopes missing, run transitions to `auth_required`

#### `lifecycleHooks` (optional)
- **Type**: `ToolLifecycleHooks`
- **Purpose**: Guardrails before/after tool execution
- **See**: [Hooks Specification](../specifications/hooks.md)

#### `metadata` (optional)
- **Type**: `Record<unknown>`
- **Purpose**: Custom key-value pairs for client use
- **Example**: `{"timeout": 30000, "retries": 3}`

---

## JSON Schema Format

Tools use JSON Schema Draft 7 for parameter validation.

### Basic Example

```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name or zip code"
      },
      "units": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "default": "fahrenheit"
      }
    },
    "required": ["location"]
  }
}
```

### Complex Example

```json
{
  "name": "search",
  "description": "Search the web for information",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "filters": {
        "type": "object",
        "properties": {
          "dateRange": {
            "type": "string",
            "enum": ["day", "week", "month", "year"]
          },
          "domains": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      },
      "maxResults": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 10
      }
    },
    "required": ["query"]
  }
}
```

---

## Tool Execution Flow

### Standard Flow

```
1. Agent generates FunctionCallContent
   {
     "kind": "functionCall",
     "callId": "call_123",
     "name": "search",
     "arguments": "{\"query\": \"AI news\"}"
   }

2. Run status: in_progress → requires_action

3. Client receives tool call via:
   - GET /runs/{runId} (polling)
   - GET /runs/{runId}/stream (streaming)

4. Client executes tool locally
   result = await executeSearch("AI news")

5. Client submits result
   POST /runs/{runId}/submit_tool_outputs
   {
     "tool_outputs": [{
       "callId": "call_123",
       "result": "Search results: ..."
     }]
   }

6. Run status: requires_action → in_progress

7. Agent processes result and continues
```

### Parallel Tool Calls

Agents may generate multiple tool calls simultaneously:

```json
{
  "role": "assistant",
  "contents": [
    {"kind": "functionCall", "callId": "call_1", "name": "get_weather", ...},
    {"kind": "functionCall", "callId": "call_2", "name": "get_news", ...}
  ]
}
```

Client should execute in parallel and submit all results together:

```json
{
  "tool_outputs": [
    {"callId": "call_1", "result": "..."},
    {"callId": "call_2", "result": "..."}
  ]
}
```

---

## OAuth2 Scope Enforcement

Tools can require OAuth2 scopes for protected resources.

### Tool with Scopes

```json
{
  "name": "send_email",
  "description": "Send email via Microsoft Graph",
  "scopes": {
    "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user"
  },
  "parameters": {
    "type": "object",
    "properties": {
      "to": {"type": "string"},
      "subject": {"type": "string"},
      "body": {"type": "string"}
    },
    "required": ["to", "subject", "body"]
  }
}
```

### Scope Validation Flow

```
1. Agent generates tool call for send_email

2. Server checks: Does agent have Mail.Send scope?

3a. If YES: Run → requires_action (normal flow)

3b. If NO:  Run → auth_required
            Client must obtain user consent

4. Client initiates OAuth2 flow
   POST /runs/{runId}/submit_auth
   {
     "connection": {
       "kind": "reference",
       "connectionId": "conn-msgraph-user1"
     }
   }

5. Run → in_progress, retries tool call
```

**See**: [Authentication Specification](../specifications/authentication.md)

---

## Tool Lifecycle Hooks

Hooks enable guardrails before and after tool execution.

**TypeSpec**: [tools.tsp](../typespec/tools.tsp) lines 88-135

```typescript
model ToolLifecycleHooks {
  beforeExecution?: Hook[];  // Run before tool call
  afterExecution?: Hook[];   // Run after tool result
}
```

### Use Cases

- **Content Filtering**: Block inappropriate tool calls
- **PII Redaction**: Remove sensitive data from results
- **Compliance Logging**: Audit all tool executions
- **Rate Limiting**: Prevent excessive API calls

### Example

```json
{
  "name": "search",
  "description": "Search the web",
  "lifecycleHooks": {
    "beforeExecution": [{
      "kind": "block",
      "name": "block-sensitive-queries",
      "condition": {
        "kind": "expression",
        "expression": "contains(arguments.query, 'password')"
      },
      "message": "Cannot search for sensitive information"
    }],
    "afterExecution": [{
      "kind": "modify",
      "name": "redact-pii",
      "predefinedPatterns": ["email", "phone", "ssn"]
    }]
  }
}
```

**See**: [Hooks Specification](../specifications/hooks.md)

---

## Error Handling

### Tool Execution Errors

If tool execution fails, return error in tool result:

```json
{
  "callId": "call_123",
  "exception": {
    "type": "error",
    "code": "TOOL_EXECUTION_ERROR",
    "message": "API rate limit exceeded"
  }
}
```

**Common Error Codes**:
- `TOOL_NOT_FOUND`: Tool name not recognized
- `INVALID_ARGUMENTS`: Arguments don't match schema
- `EXECUTION_TIMEOUT`: Tool took too long
- `PERMISSION_DENIED`: Missing required scopes
- `RATE_LIMIT_EXCEEDED`: API rate limit hit
- `TOOL_EXECUTION_ERROR`: Tool threw exception

Agent will receive error and can adjust strategy or inform user.

---

## Best Practices

### Tool Design

1. **Clear Descriptions**: Help LLM understand when to use the tool
2. **Minimal Parameters**: Only require necessary inputs
3. **Default Values**: Provide sensible defaults
4. **Validation**: Use JSON Schema constraints
5. **Documentation**: Include examples in descriptions

### Schema Design

1. **Use Enums**: Constrain to valid values
2. **Set Limits**: min/max for numbers, maxLength for strings
3. **Describe Everything**: Add descriptions to all properties
4. **Make Optional**: Use required[] sparingly

### Execution

1. **Timeout Protection**: Set timeouts for external calls
2. **Retry Logic**: Retry transient failures
3. **Error Context**: Include helpful error messages
4. **Idempotency**: Make tools safe to retry

### Security

1. **Validate Scopes**: Check OAuth2 scopes before execution
2. **Sanitize Inputs**: Validate and escape all inputs
3. **Limit Access**: Restrict tool capabilities appropriately
4. **Audit Logs**: Log all tool executions

---

## Examples

### Search Tool

```json
{
  "name": "search",
  "description": "Search the web for current information. Use for factual queries about recent events, news, or topics requiring up-to-date information.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query string",
        "maxLength": 200
      }
    },
    "required": ["query"]
  },
  "returnType": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "url": {"type": "string"},
            "snippet": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### Database Query Tool

```json
{
  "name": "query_database",
  "description": "Execute read-only SQL queries against the customer database. Only SELECT queries are allowed.",
  "scopes": {
    "https://api.example.com/database.read": "Read customer data"
  },
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL SELECT query",
        "pattern": "^SELECT\\s"
      },
      "maxRows": {
        "type": "integer",
        "minimum": 1,
        "maximum": 1000,
        "default": 100
      }
    },
    "required": ["query"]
  },
  "lifecycleHooks": {
    "afterExecution": [{
      "kind": "modify",
      "name": "redact-pii",
      "predefinedPatterns": ["email", "ssn", "phone"]
    }]
  }
}
```

---

## Related Resources

- [Tool Execution Specification](../specifications/tool-execution.md)
- [Hooks Specification](../specifications/hooks.md)
- [Authentication Specification](../specifications/authentication.md)
- [Human-in-the-Loop Guide](../guides/human-in-loop.md)
- [Run Operations](./operations/runs.md)
