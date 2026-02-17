# Synthesis Output Format Reference

**This is the REQUIRED format.** Deviations will cause parsing failures.

---

```markdown
# Synthesized Review - Iteration {N}

## Summary

- **Convergence:** {X}%
- **Consensus:** {yes|no}
- **Expert Ratings:** {expert1} {X}/5, {expert2} {Y}/5

---

## Top Recommendations 💡

### {Recommendation Title}

**Priority:** {critical|high|medium|low}
**Complexity:** {low|medium|high}
**Experts:** [{expert1}, {expert2}]

**Problem:** {1-2 sentences describing the issue}

**Solution:** {1-2 sentences describing the fix}

**Impact:** {1-2 sentences describing the benefit}

---

### {Next Recommendation}
...

---

## Questions for User ❓

### Q{N}: {Question text}?

**Asked by:** [{expert1}, {expert2}]
**Selection:** {radio|checkbox}
**Why it matters:** {1-2 sentences}

**Options:**
- **Option A:** {Brief description} - {Trade-off or consequence}
- **Option B:** {Brief description} - {Trade-off or consequence}
- **Option C (if applicable):** {Brief description} - {Trade-off or consequence}

---

### Q{N+1}: {Next Question}
...

---

## Strengths ✅

- {Specific strength from expert consensus}
- {Specific strength from expert consensus}
- {Specific strength from expert consensus}

---

## Next Steps

- {Actionable step based on critical/high priority recommendations}
- {Actionable step based on critical/high priority recommendations}
- {Actionable step based on critical/high priority recommendations}
```
