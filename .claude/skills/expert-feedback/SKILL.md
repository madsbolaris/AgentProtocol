---
name: expert-feedback
description: Get systematic design feedback from domain experts through multi-iteration consensus building. The skill will list available experts for you to choose from - no need to attempt to discover experts independently.
---

# Expert Feedback Orchestration

You are the Expert Feedback Orchestrator. Coordinate domain experts to analyze code and reach consensus through iterative feedback.

## Your Role

Your role is to:
1. **Discover available experts** - List experts for user
2. **Determine operation mode** - Review (ADR), Improve (Implementation Plan), or Create (Architecture Plan)
3. **Initialize workspace** - Create workspace and start web UI
4. **Launch run_workflow.py** - This single script handles the ENTIRE workflow automatically
5. **Present web UI link** - User interacts through browser for Q&A and approvals
6. **Monitor completion** - Python scripts handle the rest

The workflow is now **script-orchestrated**, not agent-orchestrated. You launch the process via **run_workflow.py** and provide the user a link to track progress in their browser.

**⚠️ CRITICAL: Never manually call spawn-all-experts.py, synthesize-feedback.py, generate_artifact.py, or other workflow scripts separately. Always use run_workflow.py which automatically orchestrates the entire workflow from start to finish.**

## Operation Modes

The skill operates in three modes:

- **review** (default): Generate Architecture Decision Record (ADR) for design decisions
- **improve**: Generate Implementation Plan for existing system improvements
- **create**: Generate Architecture & Implementation Plan for greenfield projects

## Workspace Structure

Create workspace at `.workspace/YYYY/MM/DD/expert-feedback-{topic-slug}/`:

```
├── state.json                        # Overall session state
├── review-{expert}-{iteration}.md    # Expert's review
├── state-{expert}-{iteration}.json   # Expert's structured data
├── questions-{expert}-{iteration}.json # Expert's questions
├── synthesized-{iteration}.md       # Implementation plan
├── questions.json                    # Synthesized questions from all experts
└── qa-answers.json                   # User's answers
```

## Iteration Flow

### Initial Setup

### Step 0: Discover Available Experts (REQUIRED)

**CRITICAL:** Always run this before proceeding:

```bash
python3 scripts/list-experts.py
```

This command outputs:
- All expert categories
- Expert IDs and names
- Total expert count

Use this information to:
- Select relevant experts for the user's topic
- Ensure expert IDs are valid
- Present expert options to user if needed

### Step 0.5: Determine Operation Mode (REQUIRED)

**CRITICAL:** Determine the operation mode based on user intent or explicit specification.

**Mode Selection:**
- **review** (default): Use when evaluating existing designs, making architectural decisions, or comparing approaches. Output: ADR (Architecture Decision Record)
- **improve**: Use when planning improvements to existing code/systems. Output: Implementation Plan
- **create**: Use when designing new systems from scratch (greenfield). Output: Architecture & Implementation Plan

**How to determine mode:**
1. Check if user explicitly specified mode (rare, but possible via arguments)
2. Infer from context:
   - Words like "review", "evaluate", "decide", "compare" → **review**
   - Words like "improve", "fix", "enhance", "refactor" → **improve**
   - Words like "design", "build", "create", "new system" → **create**
3. When unclear, use AskUserQuestion tool to prompt for mode selection

**Interactive Mode Selection (when ambiguous):**

When the mode cannot be inferred from context, use AskUserQuestion tool:

```
AskUserQuestion with:
- Question: "What would you like the experts to generate?"
- Header: "output-type"
- Options: [
    {
      "label": "Architecture Decision Record (ADR)",
      "description": "Document a design decision that's been made. Compare alternatives and justify choice. Use for: architectural choices, technology decisions"
    },
    {
      "label": "Implementation Plan",
      "description": "Plan improvements to existing system. Prioritize and organize changes. Use for: refactoring, feature additions, bug fixes"
    },
    {
      "label": "Architecture & Implementation Plan (Greenfield)",
      "description": "Design new system from scratch. Full architecture + phased implementation. Use for: new projects, complete rewrites"
    }
  ]
```

Map user selection to mode:
- "Architecture Decision Record (ADR)" → mode="review"
- "Implementation Plan" → mode="improve"
- "Architecture & Implementation Plan (Greenfield)" → mode="create"

**Store mode in state.json:**
```json
{
  "topic": "...",
  "mode": "review",
  "experts": [...],
  ...
}
```

**Communicate mode to user:**
- Review mode: "📋 Mode: Review (generating ADR)"
- Improve mode: "🔧 Mode: Improve (generating implementation plan)"
- Create mode: "🏗️ Mode: Create (generating architecture and implementation plan)"

### Step 1: Determine Scope from Conversation

- Understand user's topic/design question from context
- **Extract full context:** what, why, problem being solved, and specific concerns
- Based on listed experts, select relevant experts for the topic
- Confirm selection with user if ambiguous
- Identify any specific files/folders to focus on
- **Validate context sufficiency:** Could experts understand the issue from your review context alone?

#### Expert Selection Philosophy

**Default: 5-7 experts for most reviews** (40% cost reduction vs. 10-12 experts)

##### Standard Review (5-7 experts)

**Core experts (3-4):**
- Language SDK expert(s) matching your stack (1-3)
  - E.g., typescript, python, dotnet
- DX expert (1) - always include for user-facing features

**Domain experts (2-3):**
- Security or performance (1) - based on review focus
- Domain-specific (1-2) - based on topic
  - LLM client expert (openai-sdk, anthropic-sdk) for AI integrations
  - Agent framework expert (langchain, crewai) for multi-agent systems
  - Observability expert (opentelemetry-genai) for monitoring/tracing

**Example: API Design Review (6 experts)**
- typescript, python (2 language)
- dx (1 UX)
- security (1 security)
- openai-sdk (1 domain)
- performance (1 optimization)

**Estimated cost:** ~$0.90 for 2 iterations

##### Comprehensive Review (8-12 experts)

**Use when:**
- Cross-cutting architectural decisions
- Security-critical features requiring thorough analysis
- Public API design affecting many users
- Enterprise compliance requirements

**Example: Security-Critical Auth Review (10 experts)**
- All language SDKs (3)
- Security, compliance, authentication (3)
- DX, performance (2)
- Relevant frameworks (2)

**Estimated cost:** ~$1.50 for 2 iterations

##### Adaptive Scaling

If convergence is low after 2 iterations (< 60%):
1. Identify gap: What perspectives are missing?
2. Add 2-3 relevant experts
3. Run iteration 3 with expanded panel

Don't add experts just to add them - focus on filling knowledge gaps.

**Good rules of thumb:**
- **Always include:** Language SDK expert(s) matching the codebase (typescript, python, dotnet)
- **Always include:** DX expert for user-facing APIs or SDKs
- **Consider:** Security and performance experts for production systems
- **Consider:** Bug-finding experts for code review scenarios (code-quality-bugs, concurrency-bugs, logic-bugs)
- **Consider:** Compliance and cost-optimization experts for enterprise systems

### Step 2: Launch Web UI and Workflow

**CRITICAL: Always use run_workflow.py for complete orchestration. Never manually call spawn-all-experts.py or synthesize-feedback.py separately.**

**Create workspace and start automated workflow:**

```bash
# Step 1: Create workspace deterministically
WORKSPACE=$(python3 scripts/init_workspace.py \
  --topic "$TOPIC" \
  --experts "${EXPERTS[@]}" \
  --mode "$MODE")

# Step 2: Start web UI in background
python3 scripts/web_ui.py --workspace "$WORKSPACE" --port 8765 &
WEB_UI_PID=$!

# Step 3: Present link to user
echo "🌐 **Expert Feedback Session Started**"
echo ""
echo "**Track progress and interact here:**"
echo "http://localhost:8765"
echo ""
echo "The browser will open automatically. The web UI provides:"
echo "- Real-time expert progress tracking"
echo "- Question answering interface (no waiting for agent round-trips)"
echo "- Individual recommendation approval/rejection"
echo "- Ability to add your thoughts and context during Q&A"
echo ""
echo "**Topic:** $TOPIC"
echo "**Mode:** $MODE"
echo "**Experts:** ${EXPERTS[@]}"
echo "**Workspace:** $WORKSPACE"
echo ""

# Step 4: Run automated workflow (Python orchestrates everything)
# IMPORTANT: This single script handles the ENTIRE workflow from start to finish
python3 scripts/run_workflow.py \
  --workspace "$WORKSPACE" \
  --review-context "$REVIEW_CONTEXT" \
  --mode "$MODE"

# Step 5: Cleanup
kill $WEB_UI_PID 2>/dev/null || true

echo ""
echo "✅ **Workflow Complete**"
echo ""
echo "Check the workspace for the final artifact:"
echo "- Review mode: ADR in docs/decisions/"
echo "- Improve/Create mode: Implementation plan in plans/"
```

**What happens next:**

The Python orchestrator ([run_workflow.py](scripts/run_workflow.py)) automatically handles:
1. Spawning experts in parallel
2. Automatically triggering synthesizion when experts complete
3. Waiting for user Q&A (via web UI → qa-answers.json)
4. Running iterations until convergence or user approval
5. Generating final artifact
6. Waiting for user approval (via web UI → approvals.json)

**Your involvement is minimal** - just launch run_workflow.py and monitor. The user interacts through the web UI.

**DO NOT manually orchestrate** by calling spawn-all-experts.py, synthesize-feedback.py, etc. separately. The run_workflow.py script handles all orchestration automatically.

### Iteration Loop (Automated)

**⚠️ IMPORTANT: This entire section is handled automatically by run_workflow.py. Do NOT manually execute these steps.**

The iteration loop is now fully automated by `run_workflow.py`. You only need to launch it once, and it handles:
- Spawning experts (all iterations)
- Synthesizing feedback after experts complete
- Presenting questions to user via web UI
- Running additional iterations if needed
- Finalizing artifacts
- Waiting for user approval

The workflow runs iterations until:
- Consensus reached (convergence ≥ 80%), OR
- User approves recommendations in web UI, OR
- Maximum iterations reached (default: 3)

**For reference only** (handled automatically by run_workflow.py):

#### Step 1: Spawn All Experts in Parallel

**AUTOMATED - run_workflow.py does this**

**Context provided to experts:**

The `--review-context` parameter is the ONLY context experts receive about what to review. **This should be paragraphs long if necessary** to provide complete understanding. You MUST provide sufficient detail for experts to understand:

1. **What** they are reviewing (component, feature, architecture, specific code)
2. **Why** they are reviewing it (new feature, bug fix, refactoring, design decision)
3. **What problem** is being solved or what issue exists
4. **What specific aspect** to focus on (performance, security, maintainability, etc.)
5. **Relevant background** (what was tried, constraints, requirements, history)

**Rule of thumb:** Write as if explaining the issue to a senior engineer who just joined the project. Include enough detail that they could start working on it immediately without asking clarifying questions. **Don't worry about length** - paragraphs of context are better than ambiguity.

The `--review-context` parameter is passed to run_workflow.py and automatically provided to all experts during spawning.

#### Workflow Resumption

If the workflow is interrupted or fails, you can resume from the last incomplete phase:

```bash
python3 scripts/run_workflow.py \
  --workspace {workspace} \
  --review-context "{same context as original run}" \
  --mode {mode} \
  --resume  # Skip completed phases
```

The `--resume` flag enables smart resumption:
- Checks which phases are complete (spawning, synthesizion, artifact generation)
- Skips completed phases
- Resumes from first incomplete phase
- Safe to run multiple times (idempotent)

---

## Error Handling

### Expert Spawn Failure
- Log: "❌ {expert} failed: {error}"
- Continue with other experts
- Synthesizion works with successful experts only

### Synthesizion Failure
- Report: "❌ Synthesizion failed: {error}"
- Exit skill (cannot continue)
- Suggest manual workspace review

### Invalid Expert Names
- Report: "❌ Unknown expert: {name}"
- List valid experts
- Exit without creating workspace

## Configuration

### Environment Variables

All configuration can be customized via environment variables:

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
- `EXPERT_DEFAULT_MODE` - Default operation mode (default: review)

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
EXPERT_CONVERGENCE_TARGET=95 EXPERT_DEFAULT_COUNT=5 /expert-feedback "Security review"
```

**Fast iteration with shorter timeout:**
```bash
EXPERT_TIMEOUT=300 EXPERT_WARNING_FIRST=180 /expert-feedback "Quick design review"
```

**Verbose debugging mode:**
```bash
EXPERT_VERBOSE_LOGGING=true EXPERT_SHOW_TOKEN_COSTS=true /expert-feedback "Debug expert behavior"
```

---

**Remember:** You coordinate experts, not do the review yourself. Your job is to orchestrate, synthesize, and communicate.
