# CompletionUsage

Completion Usage

<!-- GENERATED_START -->

## CompletionUsage

Completion Usage
MERGED: Azure's CompletionUsage with MAF's UsageDetails
- Azure uses camelCase and nested objects for details
- MAF uses PascalCase and flat properties
CHOSEN: Azure's structure (camelCase, nested details) for consistency with TypeSpec conventions

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalCounts` | `Record<int64>` | No | Additional usage counts (provider-specific). |
| `inputTokenDetails` | `InputTokenDetails` | No | Input token details. |
| `inputTokens` | `int64` | Yes | Number of input/prompt tokens. |
| `outputTokenDetails` | `OutputTokenDetails` | No | Output token details. |
| `outputTokens` | `int64` | Yes | Number of output/completion tokens. |
| `totalTokens` | `int64` | Yes | Total tokens (input + output). |

---
<!-- GENERATED_END -->