# Expert Feedback Prompts

This directory contains all prompts (Jinja2 templates) for the expert-feedback skill.

## Directory Structure

```
prompts/
├── base/                     # Base templates (shared components)
│   ├── synthesis-base.jinja2      # Base template for synthesis
│   └── expert-base.jinja2         # Base template for expert reviews
│
├── experts/                  # Expert agent prompts
│   ├── initial.jinja2             # First expert review (iteration 1)
│   ├── initial-compressed.jinja2  # Compressed version (token optimization)
│   ├── initial-refactored.jinja2  # Refactored version
│   ├── refinement.jinja2          # Subsequent expert reviews (iteration 2+)
│   ├── artifact-review.jinja2     # Expert review of draft artifact (final phase)
│   ├── synthesize-artifact-reviews.jinja2  # Synthesis of artifact reviews
│   ├── format-specification.md    # Format instructions for expert reviews
│   └── markdown-format.md         # Markdown formatting guide
│
├── synthesis/                # Synthesis agent prompts
│   ├── initial.jinja2             # First synthesis (iteration 1)
│   └── refinement.jinja2          # Subsequent synthesis (iteration 2+)
│
├── finalization/             # Finalization agent prompts
│   ├── adr.jinja2                 # ADR generation (review mode)
│   ├── improve.jinja2             # Implementation plan (improve mode)
│   ├── create.jinja2              # Architecture plan (create mode)
│   └── base-finalize.jinja2       # Base finalization template
│
├── rejection-handler/        # Rejection handler agent prompts
│   └── rejection-notice.jinja2    # Rejection handling prompt
│
├── common/                   # Common/shared utility prompts
│   └── parsing-error.jinja2       # Error recovery prompt (used by experts)
│
└── output-templates/         # Final artifact rendering templates
    └── adr.md.jinja2              # ADR markdown template (for rendering final ADR)
```

## Organizational Principles

**Folders map to agent types:** Each agent type has its own folder containing prompts sent to that agent:

- `experts/` - Prompts for expert agents
- `synthesis/` - Prompts for synthesis agents
- `finalization/` - Prompts for finalization agents
- `rejection-handler/` - Prompts for rejection handler agents

**Special folders:**

- `base/` - Base templates for template inheritance (Jinja2 extends/includes)
- `common/` - Shared utility prompts (error handling, validation, retries)
- `output-templates/` - Final artifact rendering templates (not prompts)

**Prompts (.jinja2):**

- Jinja2 files containing instructions sent to LLMs
- Include placeholders like `{{ topic }}`, `{{ expert_name }}`
- Define structure, format requirements, and guidance

**Format Specifications (.md):**

- `format-specification.md` - Detailed format requirements for expert reviews
- `markdown-format.md` - Markdown formatting guidelines
- These are reference documents embedded within prompts, not standalone prompts

**Note on Examples:** We decided against including example outputs in the prompts directory. The format specifications provide sufficient guidance, and adding examples would increase token usage and maintenance overhead without clear benefit.

## Migration from templates/

The old `templates/` directory has been consolidated into `prompts/`:

- `templates/artifact-review-instructions.jinja2` → `prompts/experts/artifact-review.jinja2`
- `templates/adr.md.jinja2` → `prompts/output-templates/adr.md.jinja2`
- `templates/base-finalize.jinja2` → `prompts/finalization/base-finalize.jinja2`

All script references have been updated accordingly.

## Workflow Phases

### 1. Expert Review Phase

**Agent:** Expert agents
**Templates:** `experts/initial.jinja2`, `experts/refinement.jinja2`

- Experts analyze the topic and provide recommendations
- Format guidance: `experts/format-specification.md`, `experts/markdown-format.md`
- Error recovery: `common/parsing-error.jinja2` (sent when format is invalid)

### 2. Synthesis Phase

**Agent:** Synthesis agents
**Templates:** `synthesis/initial.jinja2`, `synthesis/refinement.jinja2`

- Synthesizes expert feedback into unified recommendations
- Identifies areas of agreement and disagreement
- Generates questions for user clarification

### 3. Finalization Phase

**Agent:** Finalization agents
**Templates:** `finalization/adr.jinja2`, `finalization/improve.jinja2`, `finalization/create.jinja2`

- Generates final artifact (ADR, implementation plan, or architecture plan)
- Uses base template: `finalization/base-finalize.jinja2`

### 4. Artifact Review Phase

**Agent:** Expert agents
**Template:** `experts/artifact-review.jinja2`

- Experts review the draft artifact for critical issues
- Experts can approve, request minor tweaks, or raise critical concerns
- Happens before user approval to catch issues early

### 5. Rejection Handling (Optional)

**Agent:** Rejection handler agent
**Template:** `rejection-handler/rejection-notice.jinja2`

- Creates rejection notice when user rejects draft artifact
- Documents user feedback and prepares for next iteration
- Generates actionable changes for experts to address

---

## Numbered Prompt Convention

The workflow now uses **numbered prompts** with a clear sequential naming convention to indicate turn-based progression:

**Format:** `{sequence}-{action}-{context}.jinja2`

### Expert Prompts (4 total)

```
experts/
├── 01-review-topic.jinja2            # Iteration 1, Turn 1
├── 02-refine-with-synthesis.jinja2   # Iteration 2, Turn 2
├── 03-final-refinement.jinja2        # Iteration 3, Turn 3
├── 04-review-artifact.jinja2         # Artifact review (any iteration)
└── .legacy/                          # Archived old templates
```

### Synthesis Prompts (3 total)

```
synthesis/
├── 01-initial-synthesis.jinja2       # Iteration 1
├── 02-refine-synthesis.jinja2        # Iteration 2
├── 03-final-synthesis.jinja2         # Iteration 3 (if convergent >= 60%)
└── .legacy/                          # Archived old templates
```

### Artifact Generator Prompts (4 total)

```
artifact-generator/
├── 01-generate-adr.jinja2            # Review mode, Turn 1
├── 01-generate-plan.jinja2           # Improve mode, Turn 1
├── 01-generate-architecture.jinja2   # Create mode, Turn 1
└── 03-apply-tweaks.jinja2            # All modes, Turn 3 (minor tweaks)
```

### Key Benefits

- **Sequential numbering** makes conversation order obvious (01 → 02 → 03 → 04)
- **Action verbs** describe what the prompt does (review, refine, generate, regenerate, apply)
- **Context suffixes** clarify when/why the prompt is used (topic, synthesis, tweaks, artifact)
- **Turn-based progression** enables session reuse with 50-60% token savings

**For complete visual documentation:**
- [Session-Preserved Architecture Guide](../docs/session-preserved-architecture.md) - 14 diagrams showing how session preservation works
