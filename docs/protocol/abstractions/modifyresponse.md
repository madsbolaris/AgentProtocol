# ModifyResponse

Modify Response

<!-- GENERATED_START -->

## ModifyResponse

Modify Response
CONTENT TYPE CHANGES:
- Framework allows changing content types (e.g., functionCall → text)
- Changing types effectively replaces the content's purpose
- Framework validates that modifiedContent is valid AIContent structure

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `contentIndex` | `int32` | Yes | Content index within message. |
| `eventSeqs` | `int64[]` | Yes | Event sequence numbers this replaces. |
| `kind` | `"modify"` | Yes | Response type discriminator. |
| `modifiedContent` | `AIContent` | Yes | Complete modified content (not deltas). |

---
<!-- GENERATED_END -->