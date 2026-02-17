# Expert Review Output Format Reference

**This is the REQUIRED format.** Deviations will cause parsing failures.

---

```markdown
# {Expert Name} Expert Review - Iteration {N}

## DX Rating

**Rating:** {1-5}/5 ⭐⭐⭐⭐⭐
**Confidence:** {low|medium|high}

{Justification paragraph explaining the rating}

---

## Concerns ⚠️

### {Concern Title}

**Severity:** {critical|high|medium|low}
**Impact:** {high|medium|low}

{Description of the problem}

**Evidence:**
- `file.ext#L42`: {specific example}
- `file.ext#L67-89`: {another example}

**Fix:**
{Concrete solution with code examples if relevant}

---

### {Next Concern}
...

---

## Recommendations 💡

### {Recommendation Title}

**Priority:** {critical|high|medium|low}
**Complexity:** {low|medium|high}
**DX Impact:** {high|medium|low}

{Description of what to change and why}

**Implementation:**
{Step-by-step or code example}

**Benefits:**
- {Benefit 1}
- {Benefit 2}

**Risks:**
- {Potential downside or trade-off}

---

### {Next Recommendation}
...

---

## Strengths ✅

### {Strength Title}

{Description of what's good and why it matters}

---

### {Next Strength}
...

---

## Questions ❓

### {Question text?}

**Context:** {Why you're asking - what you need to know}
**Importance:** {critical|high|medium|low}

{Additional clarification of what answer would help with}

---

### {Next Question}
...
```
