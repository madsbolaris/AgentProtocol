# ModelCapabilities

Model Capabilities

<!-- GENERATED_START -->

## ModelCapabilities

Model Capabilities
Key Capabilities:
- Feature flags (vision, tools, structured output, streaming, thinking)
- Token limits (context window, input, output)
- Content type support (text, image, audio, video)
- Provider and model family information

### Usage

Describes the capabilities and limits of an AI model.
Used for capability discovery, request validation, and intelligent model selection.
Computed from model configuration and included in AgentCard responses.

Key Capabilities:
- Feature flags (vision, tools, structured output, streaming, thinking)
- Token limits (context window, input, output)
- Content type support (text, image, audio, video)
- Provider and model family information

Use Cases:
- "Does this model support vision?" - Check capabilities.vision
- "What's the context window?" - Check capabilities.maxTokens
- "Can I use tools?" - Check capabilities.functionCalling
- "Validate request before sending" - Check against capabilities

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

### Examples

#### GPT-4o capabilities

```json
{
"vision": true,
"functionCalling": true,
"structuredOutput": true,
"streaming": true,
"thinking": false,
"parallelToolCalls": true,
"maxTokens": 128000,
"maxInputTokens": 128000,
"maxOutputTokens": 16384,
"supportedContentTypes": ["text", "image"],
"provider": "openai",
"modelFamily": "gpt-4"
}
```

#### Claude 3 Sonnet capabilities

```json
{
"vision": true,
"functionCalling": true,
"structuredOutput": true,
"streaming": true,
"thinking": true,
"parallelToolCalls": true,
"maxTokens": 200000,
"maxInputTokens": 200000,
"maxOutputTokens": 4096,
"supportedContentTypes": ["text", "image"],
"provider": "anthropic",
"modelFamily": "claude-3"
}
```

#### Text-only model capabilities

```json
{
"vision": false,
"functionCalling": true,
"structuredOutput": true,
"streaming": true,
"thinking": false,
"parallelToolCalls": false,
"maxTokens": 4096,
"maxInputTokens": 4096,
"maxOutputTokens": 2048,
"supportedContentTypes": ["text"],
"provider": "openai",
"modelFamily": "gpt-3.5"
}
```

---
<!-- GENERATED_END -->