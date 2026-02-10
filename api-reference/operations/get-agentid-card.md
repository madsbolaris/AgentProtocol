# GET {agentId}/card

Get agent card (discovery/registration metadata).

<!-- GENERATED_START -->

## GET {agentId}/card

Get agent card (discovery/registration metadata).

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |

### Responses

**200**: OK
Agent card with capabilities, tools, and M365/Entra integration

**404**: Not Found
Agent not found

REQUEST:
- GET /agents/{agentId}/card

---

<!-- GENERATED_END -->