# ModelCapabilities

Model Capabilities

<!-- GENERATED_START -->

## ModelCapabilities

Model Capabilities

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `functionCalling` | `boolean` | Yes | Function/tool calling support. |
| `maxInputTokens` | `int32` | Yes | Maximum input tokens. |
| `maxOutputTokens` | `int32` | Yes | Maximum output tokens (generation limit). |
| `maxTokens` | `int32` | Yes | Maximum total tokens (context window). |
| `modelFamily` | `string` | Yes | Model family/series. |
| `parallelToolCalls` | `boolean` | Yes | Parallel tool calling support (multiple tools in one turn). |
| `provider` | `string` | Yes | Provider name. |
| `streaming` | `boolean` | Yes | Streaming support (incremental token generation). |
| `structuredOutput` | `boolean` | Yes | Structured output support (JSON schema validation). |
| `supportedContentTypes` | `string[]` | Yes | Supported content types. |
| `thinking` | `boolean` | Yes | Extended thinking/reasoning support. |
| `vision` | `boolean` | Yes | Vision support (image understanding). |

---
<!-- GENERATED_END -->