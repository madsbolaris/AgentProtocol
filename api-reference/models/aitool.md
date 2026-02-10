# AITool

AI Tool

<!-- GENERATED_START -->

## AITool

AI Tool
Key Capabilities:
- JSON Schema parameter validation
- Remote tool execution via endpoint URLs
- Lifecycle hooks for guardrails and audit logging
- Human-in-the-loop approval for sensitive operations
- OAuth2 scope requirements per tool
Unified Design:
- All tools are callable functions (no type discriminator)
- Remote execution via endpoint property (no separate MCPTool type)
- Lifecycle hooks via optional config (no separate GuardrailTool type)
- Handoff/dispatch via regular function calls (no special HandoffTool type)

### Usage

Tool definition for agent capabilities. Represents callable functions that agents can invoke.
Supports both local (in-process) and remote (endpoint-based) execution.

Key Capabilities:
- JSON Schema parameter validation
- Remote tool execution via endpoint URLs
- Lifecycle hooks for guardrails and audit logging
- Human-in-the-loop approval for sensitive operations
- OAuth2 scope requirements per tool

Unified Design:
- All tools are callable functions (no type discriminator)
- Remote execution via endpoint property (no separate MCPTool type)
- Lifecycle hooks via optional config (no separate GuardrailTool type)
- Handoff/dispatch via regular function calls (no special HandoffTool type)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `connection` | `Connection` | No | Authentication for remote endpoint. |
| `description` | `string` | Yes | Tool description for LLM. |
| `endpoint` | `string` | No | Execution endpoint for remote tools. |
| `lifecycleHooks` | `ToolLifecycleHooks` | No | Lifecycle hooks for this tool. |
| `metadata` | `Record<unknown>` | No | Additional properties. |
| `name` | `string` | Yes | Tool name (unique identifier). |
| `parameters` | `JSONSchema` | No | Tool parameters (JSON Schema). |
| `requiresApproval` | `boolean` | No | Requires user approval before execution (HITL). |
| `scopes` | `Scopes` | No | OAuth2 scopes required for this tool. |
| `strict` | `boolean` | No | Strict schema validation (OpenAI-specific). |

### Examples

#### Simple local tool

```json
{
"name": "get_current_time",
"description": "Get the current time in a specified timezone",
"parameters": {
"type": "object",
"properties": {
"timezone": {
"type": "string",
"description": "IANA timezone (e.g., 'America/New_York')"
}
},
"required": ["timezone"]
}
}
```

#### Remote tool with authentication

```json
{
"name": "send_email",
"description": "Send an email via Microsoft Graph API",
"parameters": {
"type": "object",
"properties": {
"to": { "type": "string" },
"subject": { "type": "string" },
"body": { "type": "string" }
},
"required": ["to", "subject", "body"]
},
"endpoint": "https://graph.microsoft.com/v1.0/me/sendMail",
"scopes": {
"https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user"
},
"requiresApproval": true
}
```

#### Tool with lifecycle hooks

```json
{
"name": "search_documents",
"description": "Search company documents with content filtering",
"parameters": {
"type": "object",
"properties": {
"query": { "type": "string" }
},
"required": ["query"]
},
"lifecycleHooks": {
"beforeExecute": {
"name": "validate_search_query",
"endpoint": "https://guardrails.example.com/validate"
},
"afterExecute": {
"name": "log_search_audit",
"endpoint": "https://audit.example.com/log"
}
}
}
```

---
<!-- GENERATED_END -->