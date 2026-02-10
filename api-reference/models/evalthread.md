# EvalThread

Evaluation Thread

<!-- GENERATED_START -->

## EvalThread

Evaluation Thread
Test specification for evaluating agent behavior.
Contains messages, expectations, run instructions, and reviews in execution order.
INHERITANCE: Extends ThreadBase (inherits threadId, status, createdAt, metadata)
CONTENT MODEL:
- Heterogeneous array of messages and evaluation steps
- Messages: ChatMessage (user, agent, tool, system)
- Evaluation steps: Expect, EvalRun, Review
- Ordering preserved from XML document order
FEATURES:
- Linear script execution (messages + expectations in order)
- CEL-based assertions
- Deterministic and LLM judges
- Flaky test tolerance (repeat + minPassRate)
- Goal-based evaluation (run + review)
XML SERIALIZATION:
All elements become direct children of <thread> in document order:
- <user>, <agent>, <tool>, <system> → ChatMessage
- <expect> → Expect
- <run> → EvalRun
- <review> → Review
<expect>
<agent><text>Sacramento</text></agent>
<judge agent="text_contains" as="t" scope="last" contains="Sacramento"/>
<assert>t.passed</assert>
</expect>
</thread>
```
<expect>
<judge agent="tool_call_match" as="c" scope="turn" tool="get_weather"/>
<assert>c.passed</assert>
</expect>
<tool name="get_weather" call-id="call_001">
<function-result>{"temp_f": 52, "condition": "cloudy"}</function-result>
</tool>
<expect>
<judge agent="text_contains" as="t" scope="last" contains="Seattle,52"/>
<assert>t.passed</assert>
</expect>
</thread>
```
<expect>
<judge agent="llm_helpfulness" as="q" scope="last"/>
<assert minPassRate="0.8">q.score >= 0.7</assert>
</expect>
</thread>
```

**Extends:** `ThreadBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `description` | `string` | No | Evaluation description. |
| `elements` | `ThreadElement[]` | Yes | Ordered thread content. |
| `repeat` | `int32` | No | Number of times to repeat this evaluation. |

### Examples

#### Simple test

```xml
<thread thread-id="test_001" desc="Agent answers correctly">
<user>What's the capital of California?</user>

<expect>
<agent><text>Sacramento</text></agent>
<judge agent="text_contains" as="t" scope="last" contains="Sacramento"/>
<assert>t.passed</assert>
</expect>
</thread>
```

#### With tool message

```xml
<thread thread-id="test_002" desc="Agent uses weather tool">
<user>What's the weather in Seattle?</user>

<expect>
<judge agent="tool_call_match" as="c" scope="turn" tool="get_weather"/>
<assert>c.passed</assert>
</expect>

<tool name="get_weather" call-id="call_001">
<function-result>{"temp_f": 52, "condition": "cloudy"}</function-result>
</tool>

<expect>
<judge agent="text_contains" as="t" scope="last" contains="Seattle,52"/>
<assert>t.passed</assert>
</expect>
</thread>
```

#### Flaky test tolerance

```xml
<thread thread-id="test_003" desc="Creative response" repeat="5">
<user>Write a creative opening line for a mystery novel.</user>

<expect>
<judge agent="llm_helpfulness" as="q" scope="last"/>
<assert minPassRate="0.8">q.score >= 0.7</assert>
</expect>
</thread>
```

---
<!-- GENERATED_END -->