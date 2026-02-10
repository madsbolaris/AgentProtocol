# ContentAnnotations

Content Annotations

<!-- GENERATED_START -->

## ContentAnnotations

Content Annotations
2. **Context Window Management**:
- Priority 1.0: Critical context (system instructions, recent messages)
- Priority 0.5: Useful context (search results, tool outputs)
- Priority 0.0: Optional context (old messages, verbose logs)
- When context limit reached, trim lowest priority content first
3. **Cache Invalidation**:
- Track when content was last updated
- Invalidate cached embeddings or summaries
- Example: Document content with lastModified timestamp
4. **Content Encryption**:
- End-to-end encryption for sensitive content
- Applies to all content types (text, reasoning, tool results, images, etc.)
- Client-side encryption/decryption with external key management
// Critical system context (high priority)
{
kind: "text",
text: "You are a helpful assistant...",
annotations: { priority: 1.0 }
}
// Search result (medium priority, with freshness)
{
kind: "searchResult",
title: "Product docs",
snippet: "...",
annotations: {
priority: 0.6,
lastModified: "2026-01-29T10:00:00Z"
}
}
// Encrypted patient data (HIPAA compliance)
{
kind: "functionResult",
callId: "call_456",
name: "lookup_patient_record",
result: "eyJwYXRpZW50SWQiOiAiMTIzNCIsICJkaWFnbm9zaXMiOiAi...",
annotations: {
audience: ["assistant"],
encryption: {
algorithm: "AES-256-GCM",
keyId: "key-hipaa-compliance",
iv: "randomIvValue123==",
authTag: "authTagValue456=="
}
}
}
```

### Usage

- Audience filtering: Control which content is visible to humans vs agents
- Priority-based trimming: Guide context window management
- Cache invalidation: Track content freshness
- Content encryption: Universal encryption support for all content types


Use Cases:
1. **Audience Filtering**:
- Mark internal reasoning for agent-only viewing
- Mark UI hints for human-only viewing
- Example: Search results visible to agent, but summary cards for humans

2. **Context Window Management**:
- Priority 1.0: Critical context (system instructions, recent messages)
- Priority 0.5: Useful context (search results, tool outputs)
- Priority 0.0: Optional context (old messages, verbose logs)
- When context limit reached, trim lowest priority content first

3. **Cache Invalidation**:
- Track when content was last updated
- Invalidate cached embeddings or summaries
- Example: Document content with lastModified timestamp

4. **Content Encryption**:
- End-to-end encryption for sensitive content
- Applies to all content types (text, reasoning, tool results, images, etc.)
- Client-side encryption/decryption with external key management

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `algorithm` | `"AES-256-GCM" | "ChaCha20-Poly1305"` | Yes | Encryption algorithm used. |
| `audience` | `ChatRole[]` | No | Target audience for this content. |
| `authTag` | `string` | No | Authentication tag (base64 encoded). |
| `iv` | `string` | Yes | Initialization vector (base64 encoded). |
| `keyId` | `string` | Yes | Key identifier for decryption. |
| `lastModified` | `utcDateTime` | No | Last modified timestamp for cache invalidation. |

### Examples

```typescript
// Internal reasoning (agent-only)
{
kind: "text",
text: "Analyzing user intent...",
annotations: { audience: ["assistant"], priority: 0.3 }
}

// Critical system context (high priority)
{
kind: "text",
text: "You are a helpful assistant...",
annotations: { priority: 1.0 }
}

// Search result (medium priority, with freshness)
{
kind: "searchResult",
title: "Product docs",
snippet: "...",
annotations: {
priority: 0.6,
lastModified: "2026-01-29T10:00:00Z"
}
}

// Encrypted patient data (HIPAA compliance)
{
kind: "functionResult",
callId: "call_456",
name: "lookup_patient_record",
result: "eyJwYXRpZW50SWQiOiAiMTIzNCIsICJkaWFnbm9zaXMiOiAi...",
annotations: {
audience: ["assistant"],
encryption: {
algorithm: "AES-256-GCM",
keyId: "key-hipaa-compliance",
iv: "randomIvValue123==",
authTag: "authTagValue456=="
}
}
}
```

---
<!-- GENERATED_END -->