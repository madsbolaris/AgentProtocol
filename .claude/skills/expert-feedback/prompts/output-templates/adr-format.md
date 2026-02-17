# ADR (Architecture Decision Record) Format Reference

Use this structure for review mode outputs.

## Multiple ADR Guidelines

Consider creating separate ADRs when decisions are logically separable:
- **Independent subsystems** - Separate components/modules
- **Tactical vs Strategic** - Short-term vs long-term choices
- **Different domains** - Data model vs API vs deployment
- **Orthogonal concerns** - Security vs performance vs DX

**Numbering:** Sequential (0042, 0043, 0044)
**Cross-references:** Link related ADRs in "More Information"
**Default:** One comprehensive ADR unless clearly separable

## ADR JSON Output Schema

**CRITICAL:** Output JSON, not markdown. Python script renders JSON to markdown later.

**File:** `{workspace}/adr-data.json`

**Schema:** `.claude/skills/expert-feedback/schemas/adr-output.schema.json`

```json
{
  "title": "Short decision title (no ADR number prefix)",
  "status": "accepted or proposed (accepted if convergence >= 80%)",
  "deciders": ["Expert1", "Expert2", "User"],
  "date": "YYYY-MM-DD",
  "technical_story": "Workspace: {workspace_path}",

  "context": {
    "problem_statement": "What problem is being solved?",
    "background": "Why is this decision needed?",
    "constraints": [
      "Technical limitations",
      "Business requirements",
      "Expert feedback constraints"
    ]
  },

  "decision_drivers": [
    "Extract from expert concerns",
    "DX impact considerations",
    "Implementation complexity",
    "Migration/compatibility concerns"
  ],

  "considered_options": [
    {
      "title": "Option 1: Current Approach",
      "description": "Detailed description",
      "pros": [
        "Benefits from expert feedback",
        "DX improvements",
        "Best practice alignment"
      ],
      "cons": [
        "Expert concerns",
        "Implementation challenges",
        "Migration complexity"
      ]
    },
    {
      "title": "Option 2: Recommended Approach",
      "description": "Based on expert synthesis",
      "pros": ["..."],
      "cons": ["..."]
    }
  ],

  "decision_outcome": {
    "chosen_option": "Option name chosen",
    "rationale": "Based on convergence % and expert agreement",
    "implementation_notes": [
      "Specific steps",
      "Expert recommendations"
    ]
  },

  "consequences": {
    "good": [
      "DX improvements",
      "Benefits from experts"
    ],
    "bad": [
      "Implementation challenges",
      "Trade-offs and complexity"
    ],
    "neutral": [
      "Neither good nor bad trade-offs"
    ]
  },

  "links": [
    {
      "description": "Related ADR or design doc",
      "url": "path/to/document"
    }
  ]
}
```

## Key Requirements

1. **Extract from synthesis** - Read all `synthesized-*.md` files
2. **Map expert feedback** - Capture all major concerns/recommendations
3. **Set correct status** - "accepted" if convergence >= 80%, else "proposed"
4. **Include all deciders** - List all experts + "User"
5. **Date format** - YYYY-MM-DD
6. **Actionable** - Decision should be implementable
7. **Valid JSON** - Verify syntax before saving
