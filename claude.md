You're currently working on improving the development process for Claude Code for this proejct. You're doing this by creating tools for claude code using the claude SDK. IGNORE THE REST OF THE REPO STRUCTURE AND FOCUS ONLY ON CLAUDE CODE. 

For planning, analysis, or intermediate work on new projects, create dated folders: `.workspace/YYYY/MM/DD/project-name/README.md` (e.g., `.workspace/2026/02/14/refactor-plan/README.md`).

You must use python3, not python
Do not worry about breaking changes; if you notice code that supports backwards compatibility remove it and update any references to it. We should only have code that supports the current design, not old designs because it hasn't shipped yet.

When testing the workflow. Always run it in the background so you can then investigate it while it's running.

CRITICAL: When running tests that take more than 30 seconds (like integration tests that make real API calls):

- ALWAYS use run_in_background=true
- Monitor progress by checking the output file periodically
- Check that tests are progressing through expected steps
- DO NOT wait indefinitely - if a test hangs, investigate and fix it
- This prevents getting stuck waiting for tests that may hang or take too long

You should never use List prompt (system blocks) for the query field of Claude Code SDK. It's always a string. If you see code that uses List for the query, change it to a string and update any references to it.

## CRITICAL: Prompt Caching Does NOT Work in Claude Agent SDK

**DO NOT implement prompt caching in this project - it will not work.**

**Why caching fails:**

- Claude Agent SDK does not expose cache_control API ([Issue #89](https://github.com/anthropics/claude-agent-sdk-typescript/issues/89))
- `.claude/skills/expert-feedback/scripts/agents/spawn.py:273-278` flattens all system blocks to strings, stripping cache_control markers
- The former `scripts/prompts/cache_control.py` file was 602 lines of unused infrastructure (now deleted)
- Only string prompts work reliably; list prompts with cache_control trigger subprocess transport that fails

**If you see caching code:**

- Remove it immediately like an infestation
- Caching implementation is WRONG and will be silently ignored
- Use prompt size reduction instead to save tokens

**Future:** Once Agent SDK supports caching (if ever), implement from scratch and verify it actually works first.
