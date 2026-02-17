# Expert Feedback Skill

Get systematic design feedback from domain experts through multi-iteration consensus building.

## Overview

This skill spawns multiple expert agents (TypeScript, .NET, Python, SDK, DX experts) who independently review your code/design, provide structured feedback, and iterate until reaching consensus (≥80% convergence).

**Key Features:**

- 🤖 **Multiple Expert Agents** - Language experts (TS/C#/Python) + SDK experts (OpenAI/Anthropic) + DX expert + many more
- 🔄 **Iterative Refinement** - Experts refine recommendations based on your answers (no artificial question limits)
- 📊 **Convergence Metrics** - Automatic calculation of expert agreement with configurable thresholds
- ✅ **Consensus Building** - Iterates until ≥80% convergence (max 3 iterations, all configurable)
- 🎯 **Three Operation Modes** - ADR generation, Implementation Plans, or Architecture Plans
- 📈 **Real-time Progress** - Live progress tracking with timestamps, token usage, and costs
- ⏱️ **Timeout Management** - Configurable timeouts with progressive warnings (default 15 min)
- 🔍 **Artifact Review** - Experts review generated output before final approval
- 💰 **Cost Optimized** - Efficient prompt design minimizes token usage
- 🔧 **Highly Configurable** - 20+ environment variables for fine-tuning behavior

## Quick Start

```bash
/expert-feedback "IStreamable interface design" typescript dotnet python
```

> **💡 Development Tip:** When working on this skill, use `python3 scripts/analyze_recordings.py <recording_dir>` to quickly analyze expert performance, timing, and tool usage. See [ANALYSIS_TOOLS.md](ANALYSIS_TOOLS.md) for details.

**This will:**
1. Spawn 3 expert agents (TypeScript, .NET, Python)
2. Each expert explores your codebase and provides feedback
3. Synthesize recommendations and calculate convergence
4. Ask you clarifying questions (if needed)
5. Refine recommendations based on your answers
6. Generate final recommendations document

## Usage

```bash
/expert-feedback "topic to review" expert1 expert2 [expert3...]
```

### Available Experts

| Expert | Focus Area |
|--------|------------|
| `typescript` | TypeScript SDK design, type safety, async patterns |
| `dotnet` | C# SDK design, .NET conventions, async/await, DI |
| `python` | Python SDK design, Pythonic APIs, type hints |
| `openai-sdk` | OpenAI SDK patterns, compatibility, migration |
| `anthropic-sdk` | Anthropic SDK patterns, Claude-specific features |
| `dx` | Developer experience, usability, documentation |

### Examples

**Review an API design:**
```bash
/expert-feedback "IStreamable interface design" typescript dotnet python
```

**Review error handling:**
```bash
/expert-feedback "Error handling patterns across SDKs" typescript dotnet python dx
```

**Review tool calling API:**
```bash
/expert-feedback "Tool calling API" typescript dotnet python openai-sdk anthropic-sdk
```

**Review from DX perspective:**
```bash
/expert-feedback "Overall SDK developer experience" dx typescript dotnet python
```

## How It Works

### Iteration 1: Expert Exploration

1. **Spawn Experts** - Each expert agent is spawned in parallel via Claude Agent SDK
2. **Explore Codebase** - Experts use Read, Grep, Glob tools to explore relevant code
3. **Provide Feedback** - Each expert outputs structured feedback:
   - DX rating (1-5 stars)
   - Strengths
   - Concerns (with severity)
   - Recommendations (with DX impact and implementation complexity)
   - Questions for clarification

4. **Synthesize** - A synthesizion agent analyzes all feedback:
   - Groups similar recommendations
   - Calculates convergence percentage
   - Identifies conflicts
   - Prioritizes questions

### Iteration 2-3: Refinement (if needed)

If convergence < 80%:

1. **Present Questions** - Top 4 questions from experts presented to you
2. **Collect Answers** - You answer the questions
3. **Resume Experts** - Experts resume their sessions with your answers
4. **Refine Recommendations** - Experts update recommendations based on new info
5. **Re-synthesize** - Calculate new convergence percentage

### Artifact Generation

Once convergence ≥ 80% or max iterations reached:
- Generate final recommendations markdown
- Save all data to workspace for reference

## Output Structure

### Individual Expert Feedback

Each expert produces:
- **DX Rating** - 1-5 stars with confidence level
- **Strengths** - What works well
- **Concerns** - Issues with severity (high/medium/low)
- **Recommendations** - Actionable improvements with:
  - Problem statement
  - Current vs proposed approach
  - Rationale
  - DX impact (high/medium/low)
  - Implementation complexity (high/medium/low)
- **Questions** - Clarifying questions with context

### Synthesized Analysis

The synthesizion produces:
- **Convergence Metrics** - Agreement percentage, consensus status
- **Grouped Recommendations** - Similar recommendations grouped together with:
  - Agreement level (high/medium/low)
  - Which experts agree
  - Representative recommendation
  - Alternative views (if any)
- **Conflicts** - Where experts disagree (with arguments from each side)
- **Open Questions** - Deduplicated questions sorted by importance

### Final Report

`{workspace}/final-recommendations.md` contains:
- Summary of findings
- Top recommendations (sorted by agreement)
- Conflicts that need resolution
- Full convergence metrics
- Links to detailed data files

## Architecture

```
.claude/skills/expert-feedback/
├── SKILL.md                           # Main skill (bash orchestration)
├── README.md                          # This file
├── experts.json                       # Expert catalog (6 experts)
├── expert-instructions.md             # Prompt template for experts
└── scripts/
    ├── common.py                      # Shared utilities
    ├── spawn-all-experts.py           # Spawn/resume experts in parallel (Claude Agent SDK)
    └── synthesize-feedback.py        # Synthesize feedback (Claude Agent SDK)
```

### Session-Preserved Architecture

The workflow uses a **session-preserved conversational architecture** that dramatically reduces token costs and improves conversational coherence. Key benefits:

- **50-60% token reduction** on iteration/turn 2+ through session reuse
- **Better coherence** - agents remember previous turns and can reference past recommendations

**For detailed visual documentation:**
- [Session-Preserved Architecture Guide](docs/session-preserved-architecture.md) - 14 diagrams, 6 reference tables, comprehensive implementation details

### Data Flow

```
SKILL.md (orchestrator)
    ↓
spawn-all-experts.py → Claude Agent SDK → Expert Agents (parallel)
    ↓
{expert}_feedback.json
    ↓
synthesize-feedback.py → Claude Agent SDK → Synthesizion Agent
    ↓
synthesized.json (with convergence %)
    ↓
[If convergence < 80%: Ask questions, resume experts]
    ↓
final-recommendations.md
```

### Workspace Structure

```
.workspace/YYYY/MM/DD/expert-feedback-{topic}/
├── state.json                        # Session state (session IDs, iteration, convergence)
├── feedback-{expert}-{N}.json        # Expert feedback per iteration
├── synthesized-{N}.json             # Synthesized analysis per iteration
├── qa-answers.json                   # User answers to questions (if any)
└── final-recommendations.md          # Final approved recommendations
```

## Cost & Performance

### Performance
- **Time per iteration:** 5-7 minutes (parallel expert execution)
- **Typical workflow:** 2 iterations to reach consensus
- **Total time:** ~10-15 minutes for full workflow

### Cost Estimates

**Per Expert:**

- Input tokens: 5,000-7,000 per expert
- Output tokens: 3,000-5,000 per expert
- Cost per expert: $0.06-$0.12

**Per Iteration (7 experts):**

- Total tokens: ~70,000-85,000
- Cost: $0.90-$1.50

**Typical Sessions:**

- **3 experts, 1 iteration:** $0.30-$0.50
- **7 experts, 1 iteration:** $0.90-$1.50
- **7 experts, 2 iterations:** $1.80-$3.00

**Synthesis:**

- Per iteration: $0.20-$0.40 (10-20k tokens)

### Token Usage

**Per Expert:**

- Input tokens: 5,000-7,000
- Output tokens: 3,000-5,000
- Total per expert: ~8,000-12,000 tokens

**Session Totals (7 experts × 2 iterations):**

- Input: ~70,000-100,000 tokens
- Output: ~50,000-70,000 tokens
- **Total: ~120,000-170,000 tokens**
- **Total cost: ~$2.00-$3.50**

## Requirements

### Dependencies
```bash
pip3 install claude-agent-sdk
```

### Environment Variables

The skill supports 20+ configuration options via environment variables. See the Configuration section below for full details.

**Required:**
```bash
export ANTHROPIC_API_KEY=your-api-key
```

**Optional (commonly used):**
```bash
# Adjust convergence target (default: 80)
export EXPERT_CONVERGENCE_TARGET=70

# Reduce expert timeout (default: 900s = 15 min)
export EXPERT_TIMEOUT=600

# Reduce number of experts (default: 7)
export EXPERT_DEFAULT_COUNT=5

# Enable verbose logging
export EXPERT_VERBOSE_LOGGING=true
```

### Python Version
- Python 3.8 or higher

## Testing

### Test Expert Spawning

```bash
python3 .claude/skills/expert-feedback/scripts/spawn-all-experts.py \
  --experts typescript python \
  --topic "Test topic" \
  --workspace /tmp/test-expert-feedback \
  --iteration 1
```

Expected output: JSON with expert results and session IDs.

### Test Synthesizion

After spawning experts (as above), synthesize their feedback:

```bash
python3 .claude/skills/expert-feedback/scripts/synthesize-feedback.py \
  --workspace /tmp/test-expert-feedback \
  --iteration 1
```

Expected output: JSON with `convergence_percent` and `grouped_recommendations`.

### Test Full Workflow

```bash
/expert-feedback "Test topic" typescript python
```

Expected:
1. Both experts spawn and explore
2. Feedback is synthesized
3. Convergence is calculated
4. Questions are presented (if convergence < 80%)
5. Final recommendations are generated

## Troubleshooting

### Issue: "claude-agent-sdk not installed"

**Solution:**
```bash
pip3 install claude-agent-sdk
```

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
```bash
export ANTHROPIC_API_KEY=your-api-key
```

### Issue: Expert feedback parsing fails

**Symptom:** `feedback` field is mostly empty in output JSON

**Cause:** Expert output didn't match expected format

**Solution:** Check `raw_output` field in JSON for actual expert output. The parser is best-effort and handles various formats, but may need adjustment for unusual formatting.

### Issue: Synthesizion returns error status

**Symptom:** `"status": "error"` in synthesizion output

**Solutions:**
1. Check that feedback files exist in workspace
2. Check `error` field in JSON for details
3. Verify feedback files contain valid JSON

### Issue: Low convergence after multiple iterations

**Cause:** Experts have genuinely different perspectives

**Solution:** This is expected! Review the `conflicts` section in synthesized output to understand disagreements. You may need to make a judgment call or bring in additional experts.

## Configuration

The expert-feedback skill is highly configurable through environment variables. All settings have sensible defaults and can be customized per-session or globally.

### Core Settings

**Convergence & Iterations:**

- `EXPERT_CONVERGENCE_TARGET` - Target convergence percentage (default: 80)
- `EXPERT_MAX_ITERATIONS` - Maximum iterations before stopping (default: 3)
- `EXPERT_DEFAULT_COUNT` - Default number of experts to spawn (default: 7)

**Timeouts & Warnings:**

- `EXPERT_TIMEOUT` - Expert timeout in seconds (default: 900 = 15 minutes)
- `EXPERT_WARNING_FIRST` - First warning time in seconds (default: 600 = 10 minutes)
- `EXPERT_WARNING_INTERVAL` - Warning interval after first warning (default: 60 = 1 minute)

**Repository Management:**

- `EXPERT_REPO_STALENESS_DAYS` - Days before repo is considered stale (default: 7)
- `EXPERT_AUTO_UPDATE_REPOS` - Auto-update repos if stale (default: true)

**Workspace & Output:**

- `EXPERT_WORKSPACE_BASE` - Base workspace directory (default: .workspace)
- `EXPERT_ORGANIZE_BY_ITERATION` - Organize files by iteration (default: true)
- `EXPERT_DEFAULT_MODE` - Default operation mode: review/improve/create (default: review)

**Display Options:**

- `EXPERT_VERBOSE_LOGGING` - Enable verbose logging (default: false)
- `EXPERT_SHOW_WORKSPACE_LINK` - Show clickable workspace link (default: true)
- `EXPERT_SHOW_PROGRESS_TIMESTAMPS` - Show elapsed time in progress (default: true)
- `EXPERT_SHOW_TOKEN_COSTS` - Show token costs and estimates (default: true)

**Session Management:**

- `EXPERT_CLEANUP_SESSIONS` - Cleanup sessions on completion (default: true)
- `EXPERT_REUSE_SYNTHESIS` - Reuse synthesizion session across iterations (default: true)
- `EXPERT_REUSE_ARTIFACT_GENERATION` - Reuse artifact generation session (default: true)
- `EXPERT_MAX_CONCURRENT` - Max concurrent experts (default: unlimited)

### Configuration Examples

**Quick security review with high convergence:**
```bash
EXPERT_CONVERGENCE_TARGET=95 EXPERT_DEFAULT_COUNT=5 /expert-feedback "Security review of authentication"
```

**Fast iteration with shorter timeout:**
```bash
EXPERT_TIMEOUT=300 EXPERT_WARNING_FIRST=180 /expert-feedback "Quick design review"
```

**Verbose debugging mode:**
```bash
EXPERT_VERBOSE_LOGGING=true EXPERT_SHOW_TOKEN_COSTS=true /expert-feedback "Debug expert behavior"
```

**Cost-optimized mode:**
```bash
EXPERT_DEFAULT_COUNT=3 EXPERT_CONVERGENCE_TARGET=70 /expert-feedback "Budget-friendly review"
```

## Extending

### Adding New Experts

1. **Edit `experts.json`** - Add new expert definition:
```json
{
  "new-expert": {
    "name": "Expert Name",
    "background": "Background description",
    "perspective": "What they focus on",
    "focus_areas": ["area1", "area2"],
    "anti_patterns": ["anti1", "anti2"]
  }
}
```

2. **Update VALID_EXPERTS** in `SKILL.md`:
```bash
VALID_EXPERTS=("typescript" "dotnet" "python" "openai-sdk" "anthropic-sdk" "dx" "new-expert")
```

3. **Test:**
```bash
/expert-feedback "Test topic" new-expert
```

### Customizing Expert Instructions

Edit [expert-instructions.md](expert-instructions.md) to:
- Change output format
- Add new sections
- Modify guidelines
- Add examples

### Adjusting Convergence Threshold

Edit `SKILL.md`:
```bash
# Change from 80% to your desired threshold
if (( $(echo "$convergence >= 70" | bc -l) )); then
```

Also update in `synthesize-feedback.py` prompt:
```python
"target_convergence": 70  # Changed from 80
```

## Implementation Details

### Session Persistence

Experts maintain conversation state through Claude Agent SDK sessions:
- `session_id` captured from first `init` message
- Resume with `ClaudeAgentOptions(resume=session_id)`
- Allows multi-iteration refinement without context loss

### Parallel Execution

Experts execute in parallel (not sequential) for performance:
- Each expert spawned in separate async task
- Synthesizion waits for all experts to complete
- Typical speedup: 3x-5x vs sequential

### Convergence Calculation

- **High agreement:** 3+ experts agree OR all available experts agree
- **Convergence %:** (high_agreement / total_recommendations) × 100
- **Consensus threshold:** 80%

This is calculated by the synthesizion agent using AI analysis, not simple string matching.

## License

Part of the AgentProtocol project.

## Support

For issues or questions:
1. Check workspace files for detailed logs
2. Review `raw_output` fields in JSON for debugging
3. Verify all dependencies are installed
4. Check ANTHROPIC_API_KEY is set correctly

---

**Ready to get expert feedback?**

```bash
/expert-feedback "your topic here" typescript dotnet python
```
