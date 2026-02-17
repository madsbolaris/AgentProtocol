# Expert Review Markdown Format Specification

This document defines the exact structure for expert review markdown files. The markdown you write will be automatically parsed by Python scripts to extract structured data.

## Overview

Write your review as structured markdown with specific sections and metadata fields. The parser extracts:
- **DX Rating** with stars, confidence, and justification
- **Concerns** with severity, impact, evidence, and fixes
- **Recommendations** with priority, complexity, implementation, benefits, and risks
- **Strengths** with descriptions
- **Questions** with context and importance

## Complete Template

```markdown
# {Expert Name} Review - Iteration {N}

## DX Rating

**Rating:** {1-5}/5 ⭐⭐⭐⭐⭐
**Confidence:** {low|medium|high}

{Justification paragraph explaining the rating. Be specific about what influenced your assessment.}

## Concerns ⚠️

### {Concern Title}

**Severity:** {critical|high|medium|low}
**Impact:** {high|medium|low}

{Detailed description of the concern. Explain what the problem is, why it matters, and who it affects.}

**Evidence:**
- {File reference with line numbers, e.g., `src/client.ts#L42-L50`}
- {Code snippets or examples demonstrating the issue}
- {Additional supporting evidence}

**Fix:**
{Recommended solution. Be specific and actionable. Include code examples if helpful.}

### {Additional concerns...}

## Recommendations 💡

### {Recommendation Title}

**Priority:** {critical|high|medium|low}
**Complexity:** {low|medium|high}
**DX Impact:** {high|medium|low}

{Detailed description of the recommendation. Explain what you're proposing and why it's valuable.}

**Implementation:**
{Step-by-step approach to implementing this recommendation. Be as concrete as possible.}

**Benefits:**
- {Specific benefit 1}
- {Specific benefit 2}
- {Additional benefits}

**Risks:**
- {Potential risk 1 and how to mitigate it}
- {Potential risk 2 and mitigation strategy}

### {Additional recommendations...}

## Strengths ✅

### {Strength Title}

{Description of what's working well. Be specific about why this is a strength and how it benefits developers.}

### {Additional strengths...}

## Questions ❓

### {Question text as a complete question?}

**Context:** {Why you're asking this question and how the answer will inform your recommendations}
**Importance:** {critical|high|medium|low}

{Additional clarification or context that helps the user understand what you need to know}

### {Additional questions...}
```

## Section Details

### DX Rating Section

**Purpose:** Provide an overall assessment of developer experience

**Format:**
```markdown
## DX Rating

**Rating:** 4/5 ⭐⭐⭐⭐
**Confidence:** high

The SDK provides a clean, intuitive API that follows TypeScript best practices.
The type system is well-designed and catches most common errors at compile time.
However, error handling could be more ergonomic, and some edge cases are not
well-documented, preventing a 5-star rating.
```

**Fields:**
- `**Rating:**` - Number from 1-5 followed by `/5` and corresponding star emojis
- `**Confidence:**` - One of: `low`, `medium`, `high`
- Justification paragraph(s) after the metadata

### Concerns Section

**Purpose:** Identify problems, anti-patterns, or areas of concern (40-50% of your review)

**Format:**
```markdown
## Concerns ⚠️

### No cancellation support in streaming APIs

**Severity:** high
**Impact:** high

The streaming API does not support cancellation, which means once a stream starts,
there's no standard way to abort it. This can lead to resource leaks and poor UX
in applications that need to cancel long-running operations.

**Evidence:**
- `src/streaming.ts#L125-L150` - Stream implementation has no abort mechanism
- `examples/streaming.ts#L42` - Example shows no cancellation pattern
- Similar APIs (fetch, axios) all support AbortController pattern

**Fix:**
Add AbortSignal support following web standards:

\`\`\`typescript
interface StreamOptions {
  signal?: AbortSignal;
}

async function* streamMessages(
  request: StreamRequest,
  options?: StreamOptions
): AsyncGenerator<Message> {
  if (options?.signal?.aborted) {
    throw new DOMException('Aborted', 'AbortError');
  }

  options?.signal?.addEventListener('abort', () => {
    // Clean up resources
  });

  // ... streaming implementation
}
\`\`\`
```

**Fields:**
- `**Severity:**` - One of: `critical`, `high`, `medium`, `low`
- `**Impact:**` - One of: `high`, `medium`, `low`
- Description paragraph(s)
- `**Evidence:**` - Bulleted list of file references, code snippets, examples
- `**Fix:**` - Detailed recommendation for addressing the concern

**Guidelines:**
- Focus on specific, concrete problems
- Provide file references with line numbers
- Include code examples when helpful
- Suggest actionable fixes
- This should be the largest section of your review

### Recommendations Section

**Purpose:** Propose specific improvements with implementation details

**Format:**
```markdown
## Recommendations 💡

### Add builder pattern for complex configurations

**Priority:** high
**Complexity:** medium
**DX Impact:** high

The current configuration approach requires passing a large options object with
many optional fields. This leads to unclear code and makes it hard to discover
available options. A builder pattern would provide better discoverability and
more readable code.

**Implementation:**
1. Create a `ClientBuilder` class with fluent methods:

\`\`\`typescript
class ClientBuilder {
  private options: ClientOptions = {};

  withTimeout(timeout: number): this {
    this.options.timeout = timeout;
    return this;
  }

  withRetry(config: RetryConfig): this {
    this.options.retry = config;
    return this;
  }

  build(): Client {
    return new Client(this.options);
  }
}
\`\`\`

2. Update Client constructor to accept either options object or builder
3. Add factory method: `Client.builder()` for discoverability
4. Update documentation with builder pattern examples
5. Keep existing constructor for backwards compatibility

**Benefits:**
- Better IDE autocomplete and discoverability
- More readable configuration code
- Type-safe method chaining
- Easier to add new options without breaking changes
- Clearer documentation structure

**Risks:**
- Additional API surface to maintain
- Potential confusion between builder and constructor patterns
- **Mitigation:** Clearly document both approaches and recommend builder for new code
```

**Fields:**
- `**Priority:**` - One of: `critical`, `high`, `medium`, `low`
- `**Complexity:**` - One of: `low`, `medium`, `high` (implementation difficulty)
- `**DX Impact:**` - One of: `high`, `medium`, `low` (developer experience impact)
- Description paragraph(s)
- `**Implementation:**` - Step-by-step approach with code examples
- `**Benefits:**` - Bulleted list of specific advantages
- `**Risks:**` - Bulleted list of potential downsides with mitigation strategies

**Guidelines:**
- Be concrete and actionable
- Include code examples
- Consider migration path for existing users
- Balance benefits against complexity
- Provide mitigation strategies for risks

### Strengths Section

**Purpose:** Acknowledge what's working well (be concise but specific)

**Format:**
```markdown
## Strengths ✅

### Excellent type safety with discriminated unions

The use of discriminated unions for message types provides excellent compile-time
safety and makes it impossible to access fields that don't exist on a given message
type. This is a best practice in TypeScript and prevents a whole class of runtime
errors.

### Comprehensive error types

The error hierarchy is well-designed with specific error types for different failure
modes. The `isRetryableError()` helper makes it easy to implement retry logic
correctly.

### Clear examples and documentation

The examples directory contains realistic use cases that demonstrate the API
effectively. Each example is self-contained and includes comments explaining
the key concepts.
```

**Guidelines:**
- Be specific about why something is a strength
- Reference concrete examples
- Keep descriptions concise but meaningful
- Don't just list features - explain the benefit

### Questions Section

**Purpose:** Ask for clarification to refine your recommendations

**Format:**
```markdown
## Questions ❓

### Should the SDK support multiple concurrent streams per client instance?

**Context:** The current implementation appears to support only one active stream
at a time, based on the connection pooling logic in `src/streaming.ts#L78`. However,
this constraint isn't documented, and some users might expect to be able to run
multiple streams in parallel.
**Importance:** high

Understanding the intended usage pattern would help me recommend appropriate
safeguards and documentation. If single-stream is intended, we should make this
clear and add runtime checks. If multi-stream should be supported, the connection
pooling needs refactoring.

### What's the expected migration path from v1 to v2?

**Context:** The proposed breaking changes would require significant code updates
for existing users. I want to ensure my recommendations consider the migration
burden appropriately.
**Importance:** high

Are you planning to provide automated migration tools, maintain v1 in parallel,
or recommend a specific migration timeline?

### Are there specific performance requirements for the streaming API?

**Context:** Some of my recommendations involve additional abstractions that might
add overhead. Understanding performance requirements would help prioritize
optimizations.
**Importance:** medium

Specific metrics like throughput targets, latency budgets, or memory constraints
would help evaluate trade-offs between ergonomics and performance.
```

**Fields:**
- Question text as the heading (should be a complete question)
- `**Context:**` - Why you're asking and how the answer affects your recommendations
- `**Importance:**` - One of: `critical`, `high`, `medium`, `low`
- Additional clarification paragraph(s) if needed

**Guidelines:**
- Ask questions that would genuinely inform your recommendations
- Provide enough context that the user understands what you need
- Don't ask questions you can answer by reading the code
- Focus on trade-offs, requirements, and ambiguities
- No limit on number of questions - ask as many as you need

## Parsing Rules

The Python parser extracts data using these rules:

1. **Sections:** Split by `## {Section Name}` headers
2. **Subsections:** Split by `### {Subsection Title}` within sections
3. **Metadata:** Extract fields like `**Field:** value` from each subsection
4. **Stars:** Count emoji stars in rating (⭐)
5. **Lists:** Extract bullet points following `**Evidence:**`, `**Benefits:**`, etc.
6. **Code blocks:** Preserve formatting in descriptions and fixes
7. **Line numbers:** Recognize patterns like `file.ts#L42` or `file.ts:42-50`

## Common Mistakes to Avoid

❌ **Missing metadata fields:** Every concern/recommendation needs all required fields
❌ **Inconsistent formatting:** Use exact field names (`**Priority:**` not `Priority:`)
❌ **Empty sections:** If you have nothing to say, explain why (e.g., "No significant concerns found")
❌ **Vague descriptions:** Be specific with file references and examples
❌ **Missing evidence:** Concerns should always include concrete evidence
❌ **No code examples:** Include code for fixes and implementations
❌ **Questions without context:** Explain why you're asking and how it affects your analysis

## Example: Complete Minimal Review

```markdown
# TypeScript Expert Review - Iteration 1

## DX Rating

**Rating:** 3/5 ⭐⭐⭐
**Confidence:** high

The SDK has a solid foundation with good type safety, but several ergonomic
issues prevent a higher rating. Error handling is inconsistent, streaming lacks
cancellation support, and documentation could be clearer about edge cases.

## Concerns ⚠️

### No cancellation support in streaming

**Severity:** high
**Impact:** high

Streaming operations cannot be cancelled once started, leading to resource leaks.

**Evidence:**
- `src/streaming.ts#L125` - No abort mechanism in stream implementation
- Standard practice in web APIs (fetch, XHR) is to support AbortController

**Fix:**
Add AbortSignal parameter to streaming methods following web standards.

## Recommendations 💡

### Add AbortSignal support to streaming APIs

**Priority:** high
**Complexity:** medium
**DX Impact:** high

Implement standard cancellation pattern using AbortSignal.

**Implementation:**
Add optional `signal?: AbortSignal` parameter to `streamMessages()` and handle
abort events by cleaning up resources and throwing `AbortError`.

**Benefits:**
- Prevents resource leaks
- Follows web platform standards
- Enables timeout implementations

**Risks:**
- Breaking change if added to existing signatures
- Mitigation: Make parameter optional for backwards compatibility

## Strengths ✅

### Strong type safety with discriminated unions

The message type system prevents accessing undefined fields at compile time,
which is a TypeScript best practice.

## Questions ❓

### Should streaming support concurrent streams per client?

**Context:** The connection pooling suggests single-stream-at-a-time, but this
isn't documented. Clarification would inform recommendations about safeguards.
**Importance:** high

Would help determine if we need mutex locks or should refactor pooling for
concurrent streams.
```

## Tips for Writing Great Reviews

1. **Start with concerns** - They're the most valuable feedback
2. **Be specific** - Include file references, line numbers, code examples
3. **Provide evidence** - Back up claims with concrete examples
4. **Suggest solutions** - Don't just identify problems, propose fixes
5. **Consider DX** - Think about the developer using the API day-to-day
6. **Reference best practices** - Compare to well-known APIs and patterns
7. **Balance thoroughness with conciseness** - Be detailed but not verbose
8. **Use code examples** - Show, don't just tell
9. **Think about migration** - Consider impact on existing code
10. **Ask clarifying questions** - Better to ask than make assumptions

This format ensures your review is both human-readable and machine-parseable,
providing maximum value to both the development team and the automated tooling.
