# TranscriptContent

Transcript Content

<!-- GENERATED_START -->

## TranscriptContent

Transcript Content

### Usage

Use Cases:
1. **Audio Message Transcripts**: User sends voice message, transcript shown in UI
2. **Video Captions**: Video content with transcript for accessibility
3. **Meeting Transcripts**: Audio recording with human-readable transcript
4. **Accessibility**: Screen reader support for audio/video content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `associatedContentId` | `string` | No | Reference to associated audio/video content. |
| `confidence` | `float32` | No | Confidence score (0.0 - 1.0). |
| `kind` | `"transcript"` | Yes |  |
| `language` | `string` | No | Language code (ISO 639-1 or BCP 47). |
| `speaker` | `string` | No | Speaker identification. |
| `text` | `string` | Yes | Transcript text. |
| `wordTimings` | `WordTiming[]` | No | Timestamp offsets for word-level timing. |

---
<!-- GENERATED_END -->