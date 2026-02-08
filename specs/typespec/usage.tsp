/**
 * Usage & Token Tracking Models
 *
 * This file defines token usage tracking for cost management and quota enforcement.
 *
 * BASE: Microsoft.Extensions.AI.UsageDetails
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/UsageDetails.cs
 *
 * ADDITIONS FROM:
 * - Azure Agent API: CompletionUsage with inputTokenDetails/outputTokenDetails
 * - OpenAI Agents SDK: RequestUsage for per-request tracking
 * - LLMProxy: Extended thinking token tracking (exposed_trace vs internal_trace)
 *
 * M365 AGENT PLATFORM REQUIREMENTS SATISFIED:
 * - Cost tracking and attribution
 * - Quota enforcement
 * - Per-run and per-turn usage tracking
 */

import "@typespec/http";

using TypeSpec.Http;

namespace Microsoft.Agents.AI;

/**
 * Completion Usage
 *
 * FROM: Azure Agent API (CompletionUsage) + MAF (UsageDetails)
 *
 * MERGED: Azure's CompletionUsage with MAF's UsageDetails
 * - Azure uses camelCase and nested objects for details
 * - MAF uses PascalCase and flat properties
 *
 * CHOSEN: Azure's structure (camelCase, nested details) for consistency with TypeSpec conventions
 */
model CompletionUsage {
  /**
   * Number of input/prompt tokens.
   * BASE: MAF UsageDetails.InputTokenCount (long?)
   * FROM: Azure Agent API CompletionUsage.inputTokens (int64)
   */
  inputTokens: int64;

  /**
   * Number of output/completion tokens.
   * BASE: MAF UsageDetails.OutputTokenCount (long?)
   * FROM: Azure Agent API CompletionUsage.outputTokens (int64)
   */
  outputTokens: int64;

  /**
   * Total tokens (input + output).
   * BASE: MAF UsageDetails.TotalTokenCount (long?)
   * FROM: Azure Agent API CompletionUsage.totalTokens (int64)
   */
  totalTokens: int64;

  /**
   * Input token details.
   * FROM: Azure Agent API
   */
  inputTokenDetails?: InputTokenDetails;

  /**
   * Output token details.
   * FROM: Azure Agent API
   */
  outputTokenDetails?: OutputTokenDetails;

  /**
   * Additional usage counts (provider-specific).
   * BASE: MAF UsageDetails.AdditionalCounts (AdditionalPropertiesDictionary<long>)
   *
   * EXAMPLES: Audio tokens, image tokens, etc.
   */
  additionalCounts?: Record<int64>;
}

/**
 * Input Token Details
 *
 * FROM: Azure Agent API (CompletionUsage.inputTokenDetails)
 * BASE: MAF UsageDetails.CachedInputTokenCount (counted in InputTokenCount)
 */
model InputTokenDetails {
  /**
   * Number of cached prompt tokens.
   * BASE: MAF UsageDetails.CachedInputTokenCount
   *
   * NOTE: These are counted in inputTokens (not additional)
   *
   * M365: Important for cost optimization (cached tokens are cheaper)
   */
  cachedTokens?: int32;

  /**
   * Number of audio input tokens (future).
   * ADDITION: For future voice scenarios
   */
  audioTokens?: int32;
}

/**
 * Output Token Details
 *
 * FROM: Azure Agent API (CompletionUsage.outputTokenDetails)
 * BASE: MAF UsageDetails.ReasoningTokenCount (counted in OutputTokenCount)
 */
model OutputTokenDetails {
  /**
   * Tokens generated for reasoning (extended thinking).
   * BASE: MAF UsageDetails.ReasoningTokenCount
   * FROM: Azure Agent API + Anthropic (exposed_trace)
   *
   * NOTE: These are counted in outputTokens (not additional)
   *
   * RATIONALE: Extended thinking models (GPT-o1, Claude 3.7 Sonnet) generate
   * internal reasoning traces that consume tokens
   *
   * M365: Important for cost tracking (reasoning tokens are expensive)
   */
  reasoningTokens?: int32;

  /**
   * Number of audio output tokens (future).
   * ADDITION: For future voice scenarios
   */
  audioTokens?: int32;
}

/**
 * Usage Details (MAF-Compatible)
 *
 * BASE: Microsoft.Extensions.AI.UsageDetails
 * SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/UsageDetails.cs
 *
 * RATIONALE: Provides compatibility with MAF's usage tracking pattern
 * while maintaining TypeSpec naming conventions
 *
 * NOTE: This is essentially an alias/wrapper for CompletionUsage
 */
model UsageDetails {
  /**
   * Input token count.
   * BASE: MAF UsageDetails.InputTokenCount
   */
  inputTokenCount?: int64;

  /**
   * Output token count.
   * BASE: MAF UsageDetails.OutputTokenCount
   */
  outputTokenCount?: int64;

  /**
   * Total token count.
   * BASE: MAF UsageDetails.TotalTokenCount
   */
  totalTokenCount?: int64;

  /**
   * Cached input token count.
   * BASE: MAF UsageDetails.CachedInputTokenCount
   */
  cachedInputTokenCount?: int64;

  /**
   * Reasoning token count.
   * BASE: MAF UsageDetails.ReasoningTokenCount
   */
  reasoningTokenCount?: int64;

  /**
   * Additional counts.
   * BASE: MAF UsageDetails.AdditionalCounts
   */
  additionalCounts?: Record<int64>;
}

/**
 * Request Usage
 *
 * FROM: OpenAI Agents SDK (RequestUsage)
 * SOURCE: /openai-agents-python/src/agents/usage.py
 *
 * ADDITION: Not in MAF or Azure Agent API
 *
 * RATIONALE: Tracks usage for individual LLM API requests within a run
 * - Useful for per-request cost calculation
 * - Enables accurate cost attribution when requests have different pricing (batch vs real-time)
 *
 * M365: Enables detailed cost tracking for multi-turn runs
 */
model RequestUsage {
  /** Input tokens for this request */
  inputTokens: int32;

  /** Output tokens for this request */
  outputTokens: int32;

  /** Total tokens for this request */
  totalTokens: int32;

  /** Input token details for this request */
  inputTokenDetails?: InputTokenDetails;

  /** Output token details for this request */
  outputTokenDetails?: OutputTokenDetails;

  /** Timestamp of the request */
  timestamp?: utcDateTime;

  /** Model used for this request */
  `model`?: string;

  /** Additional metadata */
  metadata?: Record<unknown>;
}

/**
 * Usage Aggregation
 *
 * FROM: OpenAI Agents SDK (Usage)
 * SOURCE: /openai-agents-python/src/agents/usage.py
 *
 * ADDITION: Not in MAF or Azure Agent API
 *
 * RATIONALE: Aggregates usage across multiple requests in a run
 *
 * M365: Run-level cost tracking and quota enforcement
 */
model AggregatedUsage {
  /** Total number of requests made */
  requests: int32 = 0;

  /** Total input tokens across all requests */
  inputTokens: int64 = 0;

  /** Input token details (aggregated) */
  inputTokenDetails?: InputTokenDetails;

  /** Total output tokens across all requests */
  outputTokens: int64 = 0;

  /** Output token details (aggregated) */
  outputTokenDetails?: OutputTokenDetails;

  /** Total tokens (input + output) */
  totalTokens: int64 = 0;

  /** Per-request usage entries (for detailed cost calculation) */
  requestUsageEntries?: RequestUsage[];
}

/**
 * Cost Estimation
 *
 * ADDITION: Not in any framework
 *
 * RATIONALE: Enables cost estimation and quota enforcement
 *
 * M365: Critical for cost management and budgeting
 */
model CostEstimation {
  /** Input token cost (USD) */
  inputCost: float64;

  /** Output token cost (USD) */
  outputCost: float64;

  /** Cached token cost (USD) - usually lower than regular input */
  cachedCost?: float64;

  /** Reasoning token cost (USD) - usually higher than regular output */
  reasoningCost?: float64;

  /** Total estimated cost (USD) */
  totalCost: float64;

  /** Currency code */
  currency: string = "USD";

  /** Pricing model used for estimation */
  pricingModel: string;

  /** Timestamp of cost calculation */
  calculatedAt: utcDateTime;
}
