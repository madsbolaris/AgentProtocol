# Shared Analysis Scripts

This directory contains shared utility scripts that can be used by all expert agents to avoid duplication.

## Purpose

When experts need to perform common analysis tasks (token usage, code duplication, workspace structure, etc.), they should use these shared scripts instead of creating their own. This prevents:

- Code duplication across expert workspaces (256+ lines wasted per workflow)
- Inconsistent analysis methodologies
- Maintenance burden (update once vs. updating N expert scripts)

## Available Scripts

### analyze_token_usage.py
Analyze token usage across all iterations and phases.

**Usage:**
```bash
python3 scripts/shared/analyze_token_usage.py --workspace /path/to/workspace
```

**Output:** JSON with token breakdown by phase, expert, and iteration

---

### analyze_duplication.py
Detect code duplication across the codebase.

**Usage:**
```bash
python3 scripts/shared/analyze_duplication.py --path /path/to/analyze
```

**Output:** JSON with duplicate code blocks and locations

---

### analyze_codebase.py
Analyze codebase structure, complexity, and metrics.

**Usage:**
```bash
python3 scripts/shared/analyze_codebase.py --path /path/to/codebase
```

**Output:** JSON with file counts, LOC, complexity metrics

---

### analyze_workspace.py
Analyze workspace structure and organization.

**Usage:**
```bash
python3 scripts/shared/analyze_workspace.py --workspace /path/to/workspace
```

**Output:** JSON with workspace structure analysis

---

### analyze_web_ui.py
Analyze web UI implementation and patterns.

**Usage:**
```bash
python3 scripts/shared/analyze_web_ui.py --file /path/to/web_ui.py
```

**Output:** JSON with UI analysis (components, patterns, issues)

---

## Before Creating a New Script

**Check if a shared script already exists:**
```bash
ls scripts/shared/
```

**Only create a new script if:**
1. No shared script covers your need
2. Your analysis is truly expert-specific (e.g., TypeScript type analysis for typescript expert)
3. You've confirmed with other experts that no duplicate exists

## Script Coordination

The workflow uses a **script registry** in `state.json` to coordinate script creation across experts. Before creating a script, experts should:

1. Check if shared version exists
2. Register intent to create script
3. Check if another expert is already working on it
4. Share completed scripts with other experts

See `scripts/state_manager.py` → `WorkflowState` class for coordination APIs.

## Contributing

When creating a shared script:

1. **Use standard format:**
   - Accept paths via CLI arguments
   - Output JSON to stdout
   - Use argparse for argument parsing
   - Include docstrings and type hints

2. **Make it reusable:**
   - Don't hardcode paths
   - Support multiple input formats
   - Provide clear error messages
   - Document expected input/output

3. **Test thoroughly:**
   - Test with various workspace structures
   - Handle missing files gracefully
   - Validate input before processing

4. **Document in this README:**
   - Add usage example
   - Describe output format
   - Note any dependencies
