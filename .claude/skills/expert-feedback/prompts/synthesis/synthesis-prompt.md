# Synthesize Expert Feedback

Consolidate feedback from multiple expert reviewers into unified recommendations and questions.

---

## Context

**Iteration:** {iteration}
**Workspace:** {workspace}
**Experts:** {experts}

**Review Context:**
{review_context}

---

## Input

Read expert review markdown files:
{expert_review_files}

---

## Output

**File:** {output_file}

**Format:** Read {format_spec_path} and follow it exactly. Python scripts parse this output, so deviations will cause errors.

---

## Task

### 1. Group Recommendations

Merge similar recommendations from multiple experts:

- If 2+ experts mention the same issue, create one grouped recommendation
- List all experts who mentioned it in **Experts:** field
- Combine their insights into Problem/Solution/Impact
- Keep each subsection concise (1-2 sentences)

### 2. Calculate Convergence

Use this formula: `(recommendations_with_2+_experts / total_grouped_recommendations) × 100`

Example:
- Expert 1 has 5 recommendations, Expert 2 has 5 recommendations
- After grouping: 6 unique recommendations total
- 4 of those were mentioned by both experts
- Convergence = (4 / 6) × 100 = **67%**
- Consensus = **no** (needs ≥80% for yes)

### 3. Consolidate Questions

Merge similar questions from multiple experts:

- If 2+ experts ask similar questions, merge into one
- List all experts who asked in **Asked by:** field
- **Critical:** Provide 2-3 clear **Options** for each question
- Set **Selection:** to `radio` (single choice) or `checkbox` (multiple choice)
- Explain trade-offs for each option

**Radio vs Checkbox:**
- Use `radio` when user must pick ONE option (e.g., "Which framework?" "What version?")
- Use `checkbox` when user can pick MULTIPLE options (e.g., "Which features?" "What docs formats?")

### 4. Prioritize

Order recommendations by priority (critical → high → medium → low), then by impact/complexity ratio.

### 5. Be Concise

- Problem/Solution/Impact: 1-2 sentences each (max 3 lines)
- Strengths: One sentence per bullet
- Next Steps: Specific, actionable bullets

---

## Field Values

### Summary

- **Convergence:** Integer 0-100 with `%` symbol
- **Consensus:** `yes` (≥80%) or `no` (<80%)
- **Expert Ratings:** Format `name X/5` for each expert

### Recommendations

- **Priority:** `critical`, `high`, `medium`, `low`
- **Complexity:** `low`, `medium`, `high`
- **Experts:** Array `[expert1, expert2]` not `expert1, expert2`

### Questions

- **Question number:** `Q1:`, `Q2:`, etc.
- **Selection:** `radio` or `checkbox`
- **Asked by:** Array `[expert1, expert2]`
- **Options:** 2-3 options per question with trade-offs

---

## Example Output

```markdown
# Synthesized Review - Iteration 1

## Summary

- **Convergence:** 67%
- **Consensus:** no
- **Expert Ratings:** typescript 2/5, python 1/5

---

## Top Recommendations 💡

### Add Type Safety (Python Type Hints + TypeScript Annotations)

**Priority:** critical
**Complexity:** low
**Experts:** [typescript, python]

**Problem:** Python has no type hints and TypeScript uses implicit 'any' types everywhere, preventing static analysis.

**Solution:** Add Union[int, float] type hints to Python functions and explicit type annotations to TypeScript parameters.

**Impact:** Enables IDE autocomplete, catches type errors at compile time, and prevents invalid usage before runtime.

---

## Questions for User ❓

### Q1: What are the target Python and TypeScript versions?

**Asked by:** [python, typescript]
**Selection:** radio
**Why it matters:** Version requirements affect language features and type hint syntax.

**Options:**
- **Option A:** Python 3.9+ and TypeScript 5.0+ - Modern syntax with latest type features
- **Option B:** Python 3.8 and TypeScript 4.5+ - Must use typing module imports
- **Option C:** Support older versions (3.7, TS 4.0) - Limited features, more testing

---

### Q2: Which documentation formats should be supported?

**Asked by:** [typescript, python]
**Selection:** checkbox
**Why it matters:** Determines documentation tooling and maintenance overhead.

**Options:**
- **Option A:** TSDoc/JSDoc comments - Enables IDE IntelliSense
- **Option B:** OpenAPI/Swagger - Generates interactive API docs
- **Option C:** README examples - Simple markdown quick start

---

## Strengths ✅

- Simple API surface with only 4 operations makes it easy to understand
- Minimal dependencies reduce maintenance burden

---

## Next Steps

- Add type annotations to both TypeScript and Python (critical, 2-3 hours)
- Implement input validation with Pydantic/Zod (critical, 4-6 hours)
```

---

## Begin

Read format reference, read expert reviews, write synthesis.
