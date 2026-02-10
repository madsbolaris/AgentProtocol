# MessageWithMetadata

Example showing properties that are ignored in XML.

<!-- GENERATED_START -->

## MessageWithMetadata

Example showing properties that are ignored in XML.
XML Output:
```xml
<message message-id="msg_789" created-at="2026-02-07T10:00:00Z">
<text>Hello</text>
</message>
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `createdAt` | `utcDateTime` | Yes |  |
| `messageId` | `string` | Yes |  |
| `metadata` | `Record<unknown>` | No |  |
| `rawRepresentation` | `unknown` | No |  |
| `text` | `string` | Yes |  |

---
<!-- GENERATED_END -->