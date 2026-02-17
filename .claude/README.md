# Claude Code Configuration

This directory contains Claude Code configuration, settings, and shared utilities.

## Structure

```
.claude/
├── settings.local.json    # Local permissions and settings
├── sdk_auth.py           # Shared authentication helper for SDK scripts
├── keybindings.json      # Custom keyboard shortcuts
└── skills/               # Custom skills and commands
    └── expert-feedback/  # Expert feedback skill
        └── scripts/      # Skill scripts
```

## Shared Utilities

### SDK Authentication Helper

The `sdk_auth.py` module provides authentication utilities for scripts using the Claude Agent SDK.

#### Usage

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add .claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '.claude'))
from sdk_auth import setup_claude_auth

# Setup authentication at the start of your script
if not setup_claude_auth(verbose=True):
    print("Failed to setup authentication")
    sys.exit(1)

# Now use claude_agent_sdk normally
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(prompt="...", options=...):
    print(message)
```

#### Quick Start Alternative

For simpler scripts, use `require_claude_auth()` which exits on failure:

```python
from sdk_auth import require_claude_auth

# This will exit if authentication fails
require_claude_auth()

# Continue with your script...
from claude_agent_sdk import query
```

#### Functions

- **`setup_claude_auth(verbose=False)`** - Setup authentication, returns True/False
- **`require_claude_auth(verbose=True)`** - Setup authentication, exits on failure
- **`get_api_key_from_keychain()`** - Extract API key from macOS Keychain

#### How It Works

1. Checks if `ANTHROPIC_API_KEY` environment variable is already set
2. If not, extracts API key from Claude Code's macOS Keychain entry
3. Unsets `CLAUDECODE` to allow nested execution (running SDK inside CLI)
4. Configures the environment for Claude Agent SDK usage

#### Testing

Test the authentication helper:

```bash
cd .claude
python3 sdk_auth.py
```

## Skills

Custom skills and commands are stored in the `skills/` directory. Each skill can import the shared authentication helper.

### Example: Updating a Skill to Use sdk_auth

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add .claude to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '.claude'))

# Use the shared authentication helper
from sdk_auth import require_claude_auth
require_claude_auth()

# Now your skill code...
from claude_agent_sdk import query, ClaudeAgentOptions
# ...
```

## Settings

### permissions

Controls what operations Claude Code can perform. See `settings.local.json` for current configuration.

### keybindings

Custom keyboard shortcuts. See `keybindings.json` for current mappings.

## Best Practices

1. **Always use `sdk_auth.py`** for authentication in skill scripts
2. **Never hardcode API keys** - always use keychain or environment variables
3. **Handle nested execution** - sdk_auth automatically handles running inside Claude Code sessions
4. **Add `.claude` to path** for imports: `sys.path.insert(0, str(Path(__file__).parent.parent / '.claude'))`

## Troubleshooting

### "Could not find API key in keychain"

**Cause**: Claude Code hasn't stored credentials yet

**Solution**: Authenticate Claude Code first:
```bash
claude-code auth
```

Or set `ANTHROPIC_API_KEY` manually:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Claude Code cannot be launched inside another Claude Code session"

**Cause**: Running SDK inside CLI without unsetting `CLAUDECODE`

**Solution**: Use `sdk_auth.py` which automatically handles this

### Import errors

**Cause**: `.claude` directory not in Python path

**Solution**: Add to path before importing:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / '.claude'))
```
