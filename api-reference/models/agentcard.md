# AgentCard

Agent Card (Discovery/Registration Metadata)

<!-- GENERATED_START -->

## AgentCard

Agent Card (Discovery/Registration Metadata)

### Usage

Metadata card describing an agent's capabilities for discovery and registration.
Used for agent marketplace listing, capability queries, and M365/Entra integration.

Rationale:
- Separates discovery (what agents advertise) from execution (how they run)
- A2A cards enable interoperability across frameworks
- Extended with M365/Entra-specific fields for enterprise integration

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | Yes | Unique agent identifier. |
| `agentUserId` | `string` | No | M365/Entra Agent User ID. |
| `blueprintId` | `string` | No | M365/Entra Blueprint ID. |
| `capabilities` | `ModelCapabilities` | No | Model capabilities (computed from agent's model configuration). |
| `connections` | `Connection[]` | No | Required connections for this agent. |
| `createdAt` | `utcDateTime` | No | Timestamp when agent was registered. |
| `description` | `string` | Yes | Human-readable description |
| `displayName` | `string` | No | UI display name (localized, friendly). |
| `email` | `string` | No | Support email address |
| `iconUrl` | `string` | No | Agent icon/logo URL. |
| `inputModes` | `string[]` | No | Supported input content types. |
| `metadata` | `Record<unknown>` | No | Custom metadata. |
| `name` | `string` | No | Contact name (person or team) |
| `outputModes` | `string[]` | No | Supported output content types. |
| `scopes` | `Scopes` | No | OAuth2 scopes this agent requires. |
| `tags` | `string[]` | No | Tags for discovery and filtering. |
| `type` | `"reference" | "guide" | "tutorial" | "video" | "example" | "changelog"` | No | Documentation type for categorization |
| `updatedAt` | `utcDateTime` | No | Timestamp of last update to agent card. |
| `url` | `string` | Yes | Documentation URL |
| `version` | `string` | No | Agent version (semantic versioning). |

### Examples

#### Agent card with capabilities

```json
{
"agentId": "support-agent-123",
"displayName": "Customer Support Agent",
"description": "Handles customer inquiries and support tickets",
"capabilities": {
"vision": false,
"audio": false,
"tools": true,
"streaming": true,
"thinking": false
},
"scopes": {
"https://graph.microsoft.com/Mail.Read": "Read user emails"
},
"tags": ["support", "customer-service"],
"iconUrl": "https://example.com/icon.png"
}
```

---
<!-- GENERATED_END -->