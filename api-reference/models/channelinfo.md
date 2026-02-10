# ChannelInfo

Channel Information

<!-- GENERATED_START -->

## ChannelInfo

Channel Information

### Usage

Use Cases:
- Teams Integration: channelId="msteams", externalConversationId="19:meeting@thread.v2"
- Slack Integration: channelId="slack", externalConversationId="C123456", workspaceId="T123456"
- Discord Integration: channelId="discord", externalConversationId="123456789012345678"
- Web Chat: channelId="webchat" (no external ID needed)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `channelId` | `string` | Yes | Channel identifier (platform type). |
| `externalConversationId` | `string` | No | External conversation ID from the channel. |
| `externalTenantId` | `string` | No | External tenant/workspace/server ID. |
| `metadata` | `Record<unknown>` | No | Channel-specific metadata. |
| `serviceUrl` | `string` | No | Channel-specific service URL. |

---
<!-- GENERATED_END -->