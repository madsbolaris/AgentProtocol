# POST /agents/{agentId}/subscriptions

Create a webhook subscription for an agent.

<!-- GENERATED_START -->

## POST /agents/{agentId}/subscriptions

Create a webhook subscription for an agent.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |

### Request Body

**Type:** `AgentSubscription`

### Responses

**201**: Created
Subscription created

**400**: Bad Request
Invalid webhookUrl or configuration

**404**: Not Found
Agent not found

REQUEST:
- POST /agents/{agentId}/subscriptions
- Body: AgentSubscription with webhookUrl and optional config

---

<!-- GENERATED_END -->