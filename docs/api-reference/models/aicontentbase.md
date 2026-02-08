# AIContentBase

Base model for all AI content types

<!-- GENERATED_START -->

## AIContentBase

**TypeSpec Source**: [messages.tsp](../../typespec/messages.tsp) (lines 410-448)

AIContentBase provides common properties inherited by all 29 content types in the AIContent union. This design follows the DRY (Don't Repeat Yourself) principle by centralizing shared functionality.

## Purpose

AIContentBase enables:

1. **Audience Filtering**: Control which roles see specific content
2. **Content-Level Encryption**: Encrypt sensitive content items
3. **Extensibility**: Client-side metadata via additionalProperties

## Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | Encryption metadata (simplified as string for XML compatibility). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | Client-side extensibility metadata. Not serialized to XML. |

## Audience Filtering

The `audience` attribute controls content visibility by role:

**Values**:
- Omitted/null: Visible to all roles (default)
- `"user"`: Human-only content (UI hints, summaries)
- `"assistant"`: Agent-only content (reasoning, internal context)
- `"user,assistant"`: Explicitly visible to both

**Use Cases**:
- Mark internal reasoning for agent-only viewing
- Mark UI hints for human-only viewing
- Separate user-facing summaries from LLM context

**Examples**:

```json
// Internal reasoning (agent-only)
{
  "kind": "reasoning",
  "text": "Let me analyze the user's intent...",
  "audience": "assistant"
}

// User-facing summary (not sent to LLM)
{
  "kind": "text",
  "text": "Here's what I found for you:",
  "audience": "user"
}

// Visible to both (explicit)
{
  "kind": "text",
  "text": "This is visible to everyone",
  "audience": "user,assistant"
}
```

**XML Format**:

```xml
<thinking audience="assistant">Internal reasoning here</thinking>
<text audience="user">User-facing message</text>
```

## Content Encryption

The `encryption` attribute provides content-level encryption metadata:

**Format**: Simplified string for XML compatibility
- `"algorithm:keyId"` pattern
- Or named encryption scheme

**Examples**:

```json
// AES-256-GCM encryption
{
  "kind": "text",
  "text": "Encrypted sensitive data",
  "encryption": "aes-256-gcm:key-id-123"
}

// Named encryption scheme
{
  "kind": "functionResult",
  "callId": "call_456",
  "name": "lookup_patient_record",
  "result": "eyJwYXRpZW50...",
  "encryption": "hipaa-compliant-v1"
}
```

**XML Format**:

```xml
<text encryption="aes-256-gcm:key-id-123">Encrypted content</text>
```

**Use Cases**:
- HIPAA compliance for healthcare data
- PII protection (SSN, credit cards)
- Sensitive business data
- End-to-end encrypted messaging

## Additional Properties

The `additionalProperties` field provides client-side extensibility:

**NOT SERIALIZED**: Excluded from XML, used for transient state

**Examples**:
- Tracking IDs, correlation data
- Client-specific rendering hints
- Temporary computation results
- Cache keys or invalidation timestamps

```json
{
  "kind": "searchResult",
  "title": "Product Documentation",
  "snippet": "...",
  "additionalProperties": {
    "trackingId": "search-123",
    "cacheKey": "search:product-docs",
    "renderHint": "expandable-card"
  }
}
```

## Inheritance

All content types extend AIContentBase:

```typescript
// TextContent inherits audience, encryption, additionalProperties
model TextContent extends AIContentBase {
  kind: "text";
  text: string;
}

// FunctionCallContent inherits audience, encryption, additionalProperties
model FunctionCallContent extends AIContentBase {
  kind: "functionCall";
  callId: string;
  name: string;
  arguments: string;
}

// All 29 content types follow this pattern
```

## XML Serialization

AIContentBase properties are serialized as XML attributes:

```xml
<!-- Text with audience -->
<text audience="user">User-facing message</text>

<!-- Thinking with audience -->
<thinking audience="assistant">Internal reasoning</thinking>

<!-- Text with encryption -->
<text encryption="aes-256-gcm:key-id-123">Encrypted data</text>

<!-- Multiple attributes -->
<function-result call-id="call_123" name="get_weather" audience="assistant">
  {"temperature": 72, "conditions": "sunny"}
</function-result>
```

## Related Resources

- [Content Types](../content-types.md) - Overview of all 29 content types
- [Content Encryption Specification](../../specifications/content-encryption.md) - Encryption details
- [Message Lifecycle](../../specifications/message-lifecycle.md) - Message processing
- [TypeSpec Source](../../typespec/messages.tsp) - AIContentBase definition (lines 410-448)

---
<!-- GENERATED_END -->
