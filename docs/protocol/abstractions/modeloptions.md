# ModelOptions

Model Options

<!-- GENERATED_START -->

## ModelOptions

Model Options
EXAMPLES OF PROVIDER-SPECIFIC PROPERTIES:
- "reasoningEffort": "high" (OpenAI o1/o3 reasoning models)
- "extendedThinking": true (Anthropic extended thinking)
- "safetySettings": [...] (Gemini safety configuration)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `allowMultipleToolCalls` | `boolean` | No | Enable parallel tool calling. |
| `frequencyPenalty` | `float32` | No | Frequency penalty (-2 to 2). |
| `maxOutputTokens` | `int32` | No | Maximum generation length (tokens). |
| `presencePenalty` | `float32` | No | Presence penalty (-2 to 2). |
| `seed` | `int32` | No | Deterministic generation seed. |
| `stopSequences` | `string[]` | No | Stop sequences. |
| `temperature` | `float32` | No | Sampling temperature (0-2). |
| `topK` | `int32` | No | Top-K sampling. |
| `topP` | `float32` | No | Top-P sampling (nucleus sampling, 0-1). |

---
<!-- GENERATED_END -->