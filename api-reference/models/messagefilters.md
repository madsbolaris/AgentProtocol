# MessageFilters

Message Filters

<!-- GENERATED_START -->

## MessageFilters

Message Filters

### Usage

Filter webhook notifications by message characteristics.
Reduces notification volume by subscribing only to relevant messages.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentIds` | `string[]` | No |  |
| `audience` | `string[]` | No |  |
| `contentTypes` | `string[]` | No |  |
| `roles` | `string[]` | No |  |
| `userIds` | `string[]` | No |  |

### Examples

#### Filter user messages only

```json
{
"roles": ["user"]
}
```

#### Filter messages with images or videos

```json
{
"contentTypes": ["image", "video"]
}
```

---
<!-- GENERATED_END -->