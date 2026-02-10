# AIContentBase

Base model for all AI content types.

<!-- GENERATED_START -->

## AIContentBase

Base model for all AI content types.
Provides common properties for audience filtering, encryption, and extensibility.
PROPERTIES:
- audience: Content-level audience filtering (e.g., reasoning visible to assistant only)
- encryption: Content-level encryption metadata
- additionalProperties: Client-side extensibility (not serialized to XML)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties for extensibility. |
| `audience` | `string` | No | Target audience filter (comma-separated roles). |
| `encryption` | `string` | No | Encryption information (simplified as string for XML). |

---
<!-- GENERATED_END -->