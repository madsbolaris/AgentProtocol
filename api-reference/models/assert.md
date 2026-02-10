# Assert

Assert

<!-- GENERATED_START -->

## Assert

Assert
CEL expression assertion.
Evaluates to boolean using judge results.
CEL EXPRESSIONS:
- Boolean operators: &&, ||, !
- Comparison: ==, !=, <, >, <=, >=
- Math: +, -, *, /, %
- Functions: len(), contains(), matches()
VARIABLES:
- Judge results: {as}.passed, {as}.score, {as}.details
- Run context: run.completed, run.steps, run.durationMs
- Thread context: messages, user, agent
FLAKY TEST TOLERANCE:
- minPassRate: Required pass rate for repeated evaluations
- If repeat=5 and minPassRate=0.8, assertion must pass 4/5 times

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `expression` | `string` | Yes | CEL expression that evaluates to boolean. |
| `minPassRate` | `float32` | No | Minimum pass rate for repeated evaluations (0.0-1.0). |

### Examples

#### Simple assertion

```xml
<assert>t.passed</assert>
```

#### Complex assertion

```xml
<assert>t.passed && c.passed && quality.score >= 0.8</assert>
```

#### Flaky test tolerance

```xml
<assert minPassRate="0.8">creative.score >= 0.7</assert>
```

---
<!-- GENERATED_END -->