# POST /agents/inspect

Inspect ephemeral agent (capability discovery without persisting).

<!-- GENERATED_START -->

## POST /agents/inspect

Inspect ephemeral agent (capability discovery without persisting).

### Usage

- Capability discovery for anonymous/ephemeral agents
- Validate agent configuration before running
- Check model support (vision, tools, thinking, etc.) before creating run
- Preview agent capabilities without persisting to registry


Use Cases:
- "Does this model support vision?" - inspect({ agent: { model: "gpt-4o" } })
- "What are the token limits?" - inspect({ agent: { model: "claude-3-sonnet" } })
- "Can this agent use tools?" - inspect({ agent: { model: "...", tools: [...] } })
- "Validate agent config" - inspect({ agent: {...} }) before POST /runs


Rationale:
- Capabilities belong in AgentCard (not separate /models endpoint)
- Works for both named agents (GET /agents/{id}) and ephemeral agents (POST /agents/inspect)
- Single source of truth for agent capabilities
- No side effects - purely inspection (no persistence)

DIFFERENCES FROM GET /agents/{agentId}:
- Does NOT persist agent
- agentId will be null in response
- Used for validation and capability discovery
- GET /agents/{agentId} retrieves persisted agents

### Request Body

**Type:** `{ agent: AgentDefinition }`

### Responses

**200**: OK
AgentCard with capabilities (agentId will be null - not persisted)

**400**: Bad Request
Invalid agent definition

REQUEST:
- POST /agents/inspect
- Body: { agent: AgentDefinition } - inline agent configuration

### Examples

#### Check model capabilities

```http
POST /agents/inspect
{
"agent": {
"model": "gpt-4o",
"instructions": "You are a helpful assistant"
}
}
Response: AgentCard with capabilities.vision=true, maxTokens=128000
```

#### Check Anthropic extended thinking support

```http
POST /agents/inspect
{
"agent": {
"model": "claude-3-sonnet",
"instructions": "You are a research analyst"
}
}
Response: AgentCard with capabilities.thinking=true, maxTokens=200000
```

#### Inspect with full agent config

```http
POST /agents/inspect
{
"agent": {
"model": { "id": "gpt-4o", "provider": "openai" },
"instructions": "You help with customer support",
"tools": [{ "type": "function", "function": {...} }]
}
}
Response: AgentCard with full capabilities, tool signatures, etc.
```

---

<!-- GENERATED_END -->