# AITool

AI Tool

<!-- GENERATED_START -->

## AITool

AI Tool

### Usage

Rationale:
- Removed type discriminator (all tools are essentially callable functions)
- Remote execution via endpoint (no separate MCPTool type)
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

---
<!-- GENERATED_END -->