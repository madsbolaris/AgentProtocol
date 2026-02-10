# Participant

Participant - User or Agent in a Conversation

<!-- GENERATED_START -->

## Participant

Participant - User or Agent in a Conversation
USED BY:
- execution.tsp (Session.participants, Thread.participants)
- messages.tsp (aligns with ChatMessage.userId, ChatMessage.agentId)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | `string` | Yes | Participant identifier. |
| `kind` | `"user" | "agent" | "system"` | Yes | Participant type. |
| `metadata` | `Record<unknown>` | No | Participant metadata. |
| `name` | `string` | No | Display name. |
| `role` | `string` | No | Role in the conversation. |

---
<!-- GENERATED_END -->