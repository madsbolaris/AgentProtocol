# Expert Review: {expert_name}

Provide expert analysis of the codebase from a {expert_name} perspective.

---

## Context

**Iteration:** {iteration}
**Workspace:** {workspace}
**Expert Role:** {expert_role}

**Focus Areas:** {focus_areas}

**Review Context:**
{review_context}

---

## Input

Explore project code in workspace:

- {workspace} (focus on project directories, not entire workspace)

---

## Output

**File:** {output_file}

**Format:** Read {format_spec_path} and follow it exactly. Parser errors will occur otherwise.

**Scripts (optional):** Write analysis scripts to {scripts_dir} if needed. Don't modify project files.

---

## Task

### 1. Rate DX (1-5 stars)

Be honest and critical:

- 1 star = fundamentally broken
- 5 stars = excellent DX
- Include confidence level (low/medium/high)
- Justify your rating

### 2. Identify Concerns

**This should be 40-50% of your review** (most valuable section).

For each concern:

- Assess severity (critical/high/medium/low) and impact
- Provide specific evidence with file paths and line numbers
- Use format: `file.ext#L42` or `file.ext#L67-89`
- Suggest concrete fixes with code examples

### 3. Propose Recommendations

Make them actionable:

- Set priority, complexity, and DX impact
- Include implementation details or code examples
- List benefits AND risks/trade-offs
- Every recommendation needs implementation guidance

### 4. Note Strengths

What the code does well:

- Be specific, not generic praise
- Explain why this is a good pattern
- Helps identify what to preserve during refactoring

### 5. Ask Questions

Clarifying questions for next iteration:

- Explain why the question matters
- Show how the answer impacts your analysis
- Don't ask questions you can answer by reading code
- Set importance level (critical/high/medium/low)

---

## Guidelines

- **File references:** Always use `file.ext#L42` format
- **Code examples:** Use fenced code blocks with language
- **Be specific:** Provide evidence, not generic claims
- **Separate items:** Use `---` between items in same section
- **Be thorough:** This is your opportunity to provide deep expertise

---

## Field Values

### DX Rating

- **Rating:** 1-5 with star emoji (1 = broken, 5 = excellent)
- **Confidence:** `low`, `medium`, `high`

### Concerns

- **Severity:** `critical`, `high`, `medium`, `low`
- **Impact:** `high`, `medium`, `low`

### Recommendations

- **Priority:** `critical`, `high`, `medium`, `low`
- **Complexity:** `low`, `medium`, `high`
- **DX Impact:** `high`, `medium`, `low`

### Questions

- **Importance:** `critical`, `high`, `medium`, `low`

---

## Example Output

```markdown
# TypeScript SDK Expert Review - Iteration 1

## DX Rating

**Rating:** 2/5 ⭐⭐
**Confidence:** high

The API lacks type safety and has no input validation, leading to runtime errors and poor IntelliSense.

---

## Concerns ⚠️

### Complete Absence of Type Annotations

**Severity:** critical
**Impact:** high

Every function uses implicit `any` types, completely bypassing TypeScript's type system.

**Evidence:**

- `calculator.ts#L4`: `export function add(a, b)` - no type annotations
- `calculator.ts#L8`: `export function multiply(a, b)` - no type annotations

**Fix:**

```typescript
export function add(a: number, b: number): number {
  return a + b;
}
```

---

## Recommendations 💡

### Add Comprehensive Test Suite

**Priority:** critical
**Complexity:** medium
**DX Impact:** high

Zero test coverage means no regression protection.

**Implementation:**

```typescript
describe('calculator', () => {
  test('add returns sum', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

**Benefits:**

- Catch regressions early
- Enable safe refactoring

**Risks:**

- Initial time investment

---

## Strengths ✅

### Simple API Surface

The API is minimal with only 4 operations, making it easy to understand.

---

## Questions ❓

### What numeric range should be supported?

**Context:** Need to know if this handles BigInt, floats, scientific notation, etc.
**Importance:** medium

Current implementation uses JavaScript numbers (IEEE 754 doubles). Should we support arbitrary precision?
```

---

## Begin

Read format spec, explore workspace, create review markdown.
