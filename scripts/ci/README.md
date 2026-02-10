# CI & Development Utilities

Scripts for continuous integration, development setup, and local testing.

## Overview

These scripts help with:

- **Git Hooks**: Automated pre-commit validation
- **Sample Management**: Start agent samples with optional chat UI
- **Development Setup**: Environment configuration

## Scripts Reference

### start_samples.py ⭐

**Purpose**: Start agent samples with optional chat UI (recommended)

**What it does**:
- Starts any sample (echo-m365, basic-m365, emoji-chat)
- Supports all languages (Python, .NET, TypeScript)
- Optionally starts chat UI for interactive testing
- Manages processes with cleanup on exit

**When to use**: Development, testing, demos

**Usage**:

```bash
# Start basic-m365 with chat UI
python scripts/ci/start_samples.py basic-m365 --ui

# Start echo-m365 (all languages)
python scripts/ci/start_samples.py echo-m365

# Start all samples with UI
python scripts/ci/start_samples.py all --ui

# Start specific language only
python scripts/ci/start_samples.py basic-m365 --lang python

# Start without waiting (returns immediately)
python scripts/ci/start_samples.py echo-m365 --no-wait
```

**Available samples**:
- **echo-m365**: Simple echo bot that repeats messages back
- **basic-m365**: Basic M365 agent with function calling
- **emoji-chat**: Chat bot with emoji reactions

**Ports** (defined in `agent-config.json`):
- echo-m365: 3978-3980
- basic-m365: 3981-3983
- emoji-chat: 3984-3986
- Chat UI: http://localhost:3000 (from demos/agent-demo.html)

**Logs**: Saved to `.logs/` directory
- `.logs/echo-m365-python.log`
- `.logs/basic-m365-dotnet.log`
- `.logs/chat-ui.log`

### install_git_hooks.py

**Purpose**: Install git hooks for automated validation

**What it does**:

- Creates symlinks from `.githooks/` to `.git/hooks/`
- Enables pre-commit validation
- Enables post-merge checks

**When to use**: Once per repository clone

**Usage**:

```bash
python install_git_hooks.py
```

**Installed hooks**:

- **pre-commit**: Validates tests against golden files
- **post-merge**: Validates after pulling changes

**Bypass** (not recommended):

```bash
git commit --no-verify
```

**Uninstall**:

```bash
rm .git/hooks/pre-commit .git/hooks/post-merge
```

## Common Workflows

### Initial Repository Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd AgentProtocol

# 2. Install git hooks
python scripts/ci/install_git_hooks.py

# 3. Install dependencies
# Python
cd python && pip install -r requirements.txt
# .NET
cd dotnet && dotnet restore
# TypeScript
cd typescript && npm install
```

### Local Testing with Samples

```bash
# 1. Start samples
python scripts/ci/start_samples.py echo-m365

# Or start with chat UI for interactive testing
python scripts/ci/start_samples.py basic-m365 --ui

# In another terminal:
# 2. Generate golden files
python scripts/testgen/generate_golden_datasets.py --sample echom365

# 3. Run tests
pytest python/microsoft-agents-protocol/tests/

# 4. Stop samples (Ctrl+C in first terminal)
```

### Pre-Commit Validation

Git hooks will automatically run before commits. To test manually:

```bash
# Check what pre-commit hook does
cat .githooks/pre-commit

# Run it manually
./.githooks/pre-commit
```

## Port Configuration

Ports are configured in `agent-config.json` at repository root. Each sample has port assignments for each language:

- echo-m365: 3978-3980
- basic-m365: 3981-3983
- emoji-chat: 3984-3986

Change ports in `agent-config.json` if defaults conflict with other services.

## Troubleshooting

### Git hooks not running

1. Check hooks are installed: `ls -la .git/hooks/`
2. Reinstall: `python scripts/ci/install_git_hooks.py`
3. Verify hooks are executable: `chmod +x .githooks/*`

### Samples fail to start

Check individual sample logs:

```bash
tail -f .logs/echo-m365-python.log
tail -f .logs/basic-m365-dotnet.log
tail -f .logs/chat-ui.log
```

Common issues:

- **Port already in use**: Change ports in `agent-config.json`
- **Dependencies missing**: Install sample dependencies
- **Build failures**: Build projects before running

### Port conflicts

```bash
# Find what's using a port
lsof -i :5000

# Kill process on port
kill -9 <PID>

# Or change port in echo-m365-ports.json
```

## Best Practices

1. **Always install git hooks**: Catches issues before push
2. **Don't bypass pre-commit**: It prevents broken commits
3. **Use start_samples.py for testing**: Flexible sample starter with chat UI support
4. **Start chat UI for interactive testing**: Use `--ui` flag for visual feedback
5. **Check sample logs on failure**: Detailed error information in `.logs/` directory
6. **Clean up processes**: Always stop samples when done (Ctrl+C)

## CI/CD Integration

These scripts can be used in CI/CD pipelines:

### GitHub Actions Example

```yaml
- name: Install git hooks
  run: python scripts/ci/install_git_hooks.py

- name: Start samples
  run: python scripts/ci/start_samples.py echo-m365 --no-wait &

- name: Run tests
  run: pytest python/tests/

- name: Stop samples
  run: pkill -f start_samples.py
```

## Related Documentation

- [Test Generation](../testgen/README.md)
- [Validation Scripts](../validation/README.md)
- [Git Hooks](../../.githooks/README.md)
