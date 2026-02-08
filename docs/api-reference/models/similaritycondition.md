# SimilarityCondition

Similarity Condition (HookCondition-specific)

<!-- GENERATED_START -->

## SimilarityCondition

Similarity Condition (HookCondition-specific)

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `kind` | `"similarity"` | Yes | Condition type discriminator. |
| `method` | `"fuzzy" | "semantic" | "keyword"` | Yes | Similarity method. |
| `referenceTexts` | `string[]` | Yes | Reference texts for similarity comparison. |
| `threshold` | `float32` | Yes | Similarity threshold (0.0 to 1.0). |

---
<!-- GENERATED_END -->