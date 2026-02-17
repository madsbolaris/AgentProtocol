# Implementation Plan Format Reference

Use this structure for improvement plans (IMPROVE mode).

## Template Structure

```markdown
# Implementation Plan: {Title}

**Created:** {date}
**Status:** Ready for Implementation
**Estimated Total Time:** {X-Y hours}

## Overview
{Brief summary of improvements based on expert feedback}

### Key Improvements
- {Major improvement 1}
- {Major improvement 2}
- {Major improvement 3}

### Success Criteria
- {Measurable outcome 1}
- {Measurable outcome 2}

## Critical Files
**Files to modify/create:**
- `path/to/file1.ext` - {Change description}
- `path/to/file2.ext` - {Change description}

---

## Phases

### Phase {N}: {Name} ({time})
**Goal:** {Phase objective}

#### {N}.{M} {Improvement Name} ({time})
**Priority:** {High/Medium/Low}
**Complexity:** {Low/Medium/High}
**Expert Consensus:** {Expert names}
**File(s):** `path/to/file`

**Current Situation:**
{What exists and why it needs improvement}

**Proposed Change:**
{Description of improvement}

**Current Code:** (optional)
```language
{current snippet}
```

**New Code:** (optional)
```language
{proposed snippet}
```

**Why:** {Rationale from experts}

**Benefits:**
- {Benefit 1}
- {Benefit 2}

**Risks:**
- {Risk and mitigation}

**Dependencies:** {Other improvements this depends on}

**Testing:** {Validation approach}

---

## Implementation Order
1. **Phase 1 items** (parallel)
   - Item 1.1
   - Item 1.2
2. **Phase 2 items** (depends on Phase 1)
3. **Phase 3 items** (depends on Phase 2)

## Quick Wins
{Low-effort, high-impact items}

## High-Impact Changes
{Significant value, requires effort}

## Testing Strategy
**Unit Tests:** {Test scenarios}
**Integration Tests:** {Interaction testing}
**Regression Tests:** {Existing functionality}

## Rollback Plan
1. {Rollback step 1}
2. {Rollback step 2}

## Success Metrics
- Metric 1: {Measurement}
- Metric 2: {Measurement}

## Risks & Mitigations
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {Risk} | {High/Med/Low} | {High/Med/Low} | {Strategy} |

---

**Experts Consulted:** {list}
**Convergence:** {percent}%
**Review Workspace:** [link]

---

## 🤖 Implementing with Claude Code
\`\`\`bash
claude-code "implement the plan at {workspace}/draft-plan.md"
\`\`\`

**Claude Code will:**
1. Enter plan mode automatically
2. Explore critical files
3. Design implementation approach
4. Execute phase by phase
5. Run tests after each phase

**Plan Mode Hints:**
<!-- PLAN MODE: This is an implementation plan -->
<!-- CRITICAL FILES: {list} -->
<!-- PHASES: {count} -->
<!-- COMPLEXITY: {HIGH/MEDIUM/LOW} -->
<!-- ESTIMATED DURATION: {time} -->
```

## Key Guidelines

- **Organize by priority** - High-impact, low-complexity first
- **Be specific** - File paths, line numbers, concrete examples
- **Explain rationale** - Reference expert feedback
- **Estimate time** - Realistic based on complexity
- **Show dependencies** - Sequential vs parallel work
- **Include testing** - Validation for each change
- **Address risks** - Issues and mitigations
