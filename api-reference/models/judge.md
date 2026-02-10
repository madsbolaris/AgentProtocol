# Judge

Judge

<!-- GENERATED_START -->

## Judge

Judge
Evaluation function invocation.
Runs a judge agent and stores result in variable.
JUDGES: Functions that evaluate output and produce pass/fail + score
DETERMINISTIC JUDGES (free, zero-cost):
- text_contains: Keyword presence
- text_regex: Pattern matching
- text_exact_match: Exact string comparison
- tool_call_match: Tool validation
- file_exists: File presence check
- file_min_bytes: File size check
LLM JUDGES (optional, costs money):
- semantic_similarity: Embedding similarity (uses embedding model)
- llm_helpfulness: Subjective quality (uses LLM)
- llm_groundedness: Factual grounding (uses LLM)
- llm_policy_compliance: Policy checks (uses LLM)
RESULT STORAGE:
Judge result stored in variable named by `as` attribute.
Available in assertions as: {as}.passed, {as}.score, {as}.details

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agent` | `string` | Yes | Judge agent name. |
| `args` | `string` | No | Judge-specific arguments. |
| `as` | `string` | Yes | Variable name to store result. |
| `scope` | `JudgeScope` | No | Evaluation scope. |

### Examples

#### Deterministic judge

```xml
<judge agent="text_contains" as="t" scope="last" contains="Seattle,52"/>
<assert>t.passed</assert>
```

#### LLM judge

```xml
<judge agent="llm_helpfulness" as="h" scope="last"/>
<assert>h.score >= 0.8</assert>
```

#### Judge with JSON args

```xml
<judge agent="tool_call_match" as="c" scope="turn" tool="get_weather">
{ "location": "Seattle", "units": "imperial" }
</judge>
```

---
<!-- GENERATED_END -->