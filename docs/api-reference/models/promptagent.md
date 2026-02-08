# PromptAgent

Prompt Agent (Direct Execution)

<!-- GENERATED_START -->

## PromptAgent

Prompt Agent (Direct Execution)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalInstructions` | `string | ChatMessage[]` | No | Additional guidance context. |
| `autoResponse` | `AutoResponseConfig` | No | Auto-response configuration for thread participation. |
| `description` | `string` | No | Agent capabilities description. |
| `displayName` | `string` | No | UI display name (human-friendly). |
| `inputSchema` | `PropertySchema` | No | Input parameters structure. |
| `instructions` | `string | ChatMessage[]` | No | System instructions (agent behavior directives). |
| `kind` | `"prompt"` | Yes | Agent type discriminator. |
| `metadata` | `Record<unknown>` | No | Custom metadata. |
| `model` | `string | AgentModel` | Yes | Model configuration. |
| `name` | `string` | No | Unique agent identifier. |
| `outputSchema` | `PropertySchema` | No | Expected output format. |
| `template` | `PromptTemplate` | No | Prompt template rendering configuration. |
| `toolChoice` | `ToolChoiceBehavior` | No | Tool calling behavior. |
| `tools` | `AITool[]` | No | Available tools. |

---
<!-- GENERATED_END -->