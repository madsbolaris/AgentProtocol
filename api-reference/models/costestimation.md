# CostEstimation

Cost Estimation

<!-- GENERATED_START -->

## CostEstimation

Cost Estimation

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `cachedCost` | `float64` | No | Cached token cost (USD) - usually lower than regular input |
| `calculatedAt` | `utcDateTime` | Yes | Timestamp of cost calculation |
| `currency` | `string = "USD"` | Yes | Currency code |
| `inputCost` | `float64` | Yes | Input token cost (USD) |
| `outputCost` | `float64` | Yes | Output token cost (USD) |
| `pricingModel` | `string` | Yes | Pricing model used for estimation |
| `reasoningCost` | `float64` | No | Reasoning token cost (USD) - usually higher than regular output |
| `totalCost` | `float64` | Yes | Total estimated cost (USD) |

---
<!-- GENERATED_END -->