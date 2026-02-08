# Content Types Reference

Complete reference of all content types available in the Agent Runtime API.

**TypeSpec Source**: [messages.tsp](../typespec/messages.tsp) (lines 370-409)

---

## Overview

Content types represent different kinds of data that can appear in message contents. Each content type has:
- A `kind` discriminator for type identification
- Type-specific fields for the content data
- Optional annotations for metadata

**Total Content Types**: 29

---

## Text & Basic Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **TextContent** | `text` | Plain text or markdown | user, assistant, system |
| **TextReasoningContent** | `textReasoning` | Agent's internal reasoning | assistant (thinking) |
| **DataContent** | `data` | Structured data (JSON, XML, etc.) | assistant, tool |
| **UriContent** | `uri` | URI/URL reference | user, assistant |

---

## Media Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **ImageContent** | `image` | Image file or URL | user, assistant |
| **AudioContent** | `audio` | Audio file or stream | user, assistant |
| **VideoContent** | `video` | Video file or URL | user, assistant |
| **TranscriptContent** | `transcript` | Real-time transcription | system (real-time audio) |

**Note**: Media content can reference files via URL or include base64-encoded data inline.

---

## File Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **FileContent** | `file` | Generic file attachment | user, assistant |

---

## Hosted Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **HostedFileContent** | `hostedFile` | Provider-hosted file reference | assistant, system |
| **HostedVectorStoreContent** | `hostedVectorStore` | Provider-managed vector store reference | assistant, system |

**HostedFileContent**: References files stored by the provider (e.g., OpenAI file-abc123, Azure blob storage). Used when the provider processes files for embeddings, image analysis, or transcription.

**HostedVectorStoreContent**: References provider-managed vector stores (e.g., OpenAI vs_abc123, Azure AI Search indexes). Used for RAG (Retrieval-Augmented Generation) scenarios where the provider manages embeddings.

---

## Function & Tool Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **FunctionCallContent** | `functionCall` | Function call request | assistant |
| **FunctionResultContent** | `functionResult` | Function execution result | tool, user |
| **ErrorContent** | `error` | Error information | tool, system |

**Tool Pattern**: Agent generates `functionCall`, client executes and returns `functionResult`.

---

## Document Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **DocumentContent** | `document` | Structured document | user, assistant |
| **SearchResultContent** | `searchResult` | Search/query results | tool, assistant |
| **AdaptiveCardContent** | `adaptiveCard` | Rich UI card (Adaptive Cards) | assistant, system |

---

## Structured Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **EventContent** | `event` | External system event | channel (proactive triggers) |
| **TraceContent** | `trace` | Runtime trace/diagnostic | system (debugging) |
| **RefusalContent** | `refusal` | Policy violation refusal | assistant |
| **ContentFilterResultContent** | `contentFilterResult` | Content moderation result | system |

**Special Roles**:
- `channel`: External events triggering proactive messages
- `system`: Runtime metadata and diagnostics

---

## Interactive Content

| Content Type | Kind | Description | Typical Roles |
|--------------|------|-------------|---------------|
| **UserInputRequestContent** | `userInputRequest` | Request user input (HITL) | assistant |
| **SuggestedActionsContent** | `suggestedActions` | Suggested quick replies | assistant |
| **ActionContent** | `action` | Executable action | assistant |
| **TypingIndicatorContent** | `typingIndicator` | Typing status | assistant |
| **MessageReactionContent** | `messageReaction` | Reaction to message | user |
| **MessageDeleteContent** | `messageDelete` | Message deletion | user, system |
| **MessageUpdateContent** | `messageUpdate` | Message edit | user, assistant |

**Human-in-the-Loop**: `UserInputRequestContent` triggers `input_required` run state.

---

## History Retrieval Filtering

### Included by Default

Most content types are included in conversation history retrieval:
- All text and media content
- File and document content
- Function calls and results
- Interactive content

### Excluded by Default

These are excluded from history to reduce noise:
- **TranscriptContent**: Real-time transcription fragments
- **TraceContent**: Runtime diagnostics and debugging

**Override**: Use explicit content type filters to include/exclude specific types.

---

## Content-Level Metadata

All content types inherit from **AIContentBase**, which provides common properties for audience filtering, encryption, and extensibility. These properties are specified on **individual content items**, allowing fine-grained control.

### Audience Filtering

The `audience` attribute controls which roles should see a specific content item:

```json
{
  "kind": "text",
  "text": "This is only visible to users, not sent to the LLM",
  "audience": "user"
}
```

**Audience Values**:

- Omitted/null: Visible to all roles (default)
- `"user"`: Human-only content (UI hints, summaries)
- `"assistant"`: Agent-only content (internal reasoning, context)
- `"user,assistant"`: Explicitly visible to both

**Common Use Cases**:

```json
// Internal reasoning visible only to assistant
{
  "kind": "reasoning",
  "text": "Let me think through this step by step...",
  "audience": "assistant"
}

// User-facing summary not sent to LLM
{
  "kind": "text",
  "text": "Here's what I found for you:",
  "audience": "user"
}
```

### Encryption

The `encryption` attribute specifies encryption metadata for individual content items:

```json
{
  "kind": "text",
  "text": "Encrypted sensitive data",
  "encryption": "aes-256-gcm:key-id-123"
}
```

**Encryption Examples**:

- `"aes-256-gcm:key-id-123"`: AES-256-GCM with key reference
- `"hipaa-compliant-v1"`: Named encryption scheme

**XML Format**:

```xml
<text audience="user">User-facing message</text>
<thinking audience="assistant">Internal reasoning</thinking>
<text encryption="aes-256-gcm:key-id-123">Sensitive data</text>
```

**TypeSpec Source**: [messages.tsp](../typespec/messages.tsp) (lines 410-448) - AIContentBase model

---

## Examples

### Text Content
```json
{
  "kind": "text",
  "text": "Hello! How can I help you today?"
}
```

### Function Call Content
```json
{
  "kind": "functionCall",
  "callId": "call_abc123",
  "name": "search",
  "arguments": "{\"query\": \"weather in Seattle\"}"
}
```

### Image Content
```json
{
  "kind": "image",
  "uri": "https://example.com/image.png",
  "mimeType": "image/png"
}
```

### Hosted File Content

```json
{
  "kind": "hostedFile",
  "fileId": "file-abc123",
  "filename": "document.pdf",
  "mediaType": "application/pdf",
  "sizeBytes": 102400
}
```

### Hosted Vector Store Content

```json
{
  "kind": "hostedVectorStore",
  "vectorStoreId": "vs_abc123",
  "name": "product-documentation",
  "documentCount": 150
}
```

### User Input Request (HITL)
```json
{
  "kind": "userInputRequest",
  "requestId": "input_001",
  "prompt": "Please confirm your email address",
  "inputType": "text"
}
```

### Event Content (Proactive)
```json
{
  "kind": "event",
  "name": "timer.daily",
  "timestamp": "2026-02-07T08:00:00Z"
}
```

### Content with Audience Filtering

```json
{
  "kind": "text",
  "text": "Here's a summary for you (this won't be sent to the LLM in future turns)",
  "audience": "user"
}
```

```json
{
  "kind": "reasoning",
  "text": "Let me analyze the user's request step by step...",
  "audience": "assistant"
}
```

### Content with Encryption

```json
{
  "kind": "text",
  "text": "Sensitive patient information",
  "encryption": "aes-256-gcm:key-id-123"
}
```

---

## Related Resources

- [ChatMessage Model](./models/ChatMessage.md)
- [Message Lifecycle Specification](../specifications/message-lifecycle.md)
