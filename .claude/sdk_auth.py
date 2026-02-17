"""
Claude Agent SDK Authentication Helper

This module provides authentication utilities for Claude Agent SDK scripts
running within Claude Code. It automatically extracts API credentials from
the macOS Keychain and configures the environment for SDK usage.

Usage:
    from sdk_auth import setup_claude_auth

    # At the start of your script (before importing claude_agent_sdk)
    setup_claude_auth()

    # Now use claude_agent_sdk normally
    from claude_agent_sdk import query, ClaudeAgentOptions
    async for message in query(prompt="...", options=...):
        ...
"""
import os
import subprocess
import sys
from typing import Optional


def get_api_key_from_keychain() -> Optional[str]:
    """
    Extract Claude API key from macOS Keychain.

    Returns:
        The API key string if found, None otherwise.

    Example:
        >>> api_key = get_api_key_from_keychain()
        >>> if api_key:
        >>>     print(f"Found key: {api_key[:15]}...")
    """
    try:
        api_key = subprocess.check_output(
            [
                'security',
                'find-generic-password',
                '-s', 'Claude Code',
                '-a', os.getenv('USER', ''),
                '-w'  # Return only the password
            ],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()

        # Validate it looks like an Anthropic API key
        if api_key and api_key.startswith('sk-ant-'):
            return api_key

        return None

    except subprocess.CalledProcessError:
        return None
    except Exception as e:
        print(f"Warning: Error accessing keychain: {e}", file=sys.stderr)
        return None


def setup_claude_auth(verbose: bool = False) -> bool:
    """
    Configure authentication for Claude Agent SDK.

    This function:
    1. Checks if ANTHROPIC_API_KEY is already set
    2. If not, extracts it from Claude Code's keychain entry
    3. Unsets CLAUDECODE to allow nested execution
    4. Sets up the environment for SDK usage

    Args:
        verbose: If True, print status messages to stdout

    Returns:
        True if authentication was successfully configured, False otherwise

    Example:
        >>> if not setup_claude_auth(verbose=True):
        >>>     print("Failed to configure authentication")
        >>>     sys.exit(1)
    """
    # Check if API key is already set
    if os.environ.get('ANTHROPIC_API_KEY'):
        if verbose:
            print("✅ ANTHROPIC_API_KEY already set")
        # Still need to handle nested sessions
        _allow_nested_execution(verbose)
        return True

    # Extract from keychain
    if verbose:
        print("🔑 Extracting API key from Claude Code keychain...")

    api_key = get_api_key_from_keychain()

    if api_key:
        os.environ['ANTHROPIC_API_KEY'] = api_key
        if verbose:
            print(f"✅ API key configured: {api_key[:15]}...{api_key[-4:]}")
    else:
        if verbose:
            print("❌ Could not find API key in keychain", file=sys.stderr)
            print("   Make sure Claude Code is authenticated", file=sys.stderr)
        return False

    # Allow nested execution
    _allow_nested_execution(verbose)

    return True


def _allow_nested_execution(verbose: bool = False) -> None:
    """
    Allow Claude Agent SDK to run inside an existing Claude Code session.

    This unsets Claude Code environment variables which prevent
    nested sessions from detecting each other.

    Args:
        verbose: If True, print status message when unsetting
    """
    claude_vars_to_unset = ['CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING']
    unset_any = False
    for var in claude_vars_to_unset:
        if var in os.environ:
            del os.environ[var]
            unset_any = True

    if verbose and unset_any:
        print("⚠️  Unset Claude Code environment variables to allow nested execution")


def require_claude_auth(verbose: bool = True) -> None:
    """
    Setup authentication and exit if it fails.

    This is a convenience function that calls setup_claude_auth()
    and exits the script with an error code if authentication fails.

    Args:
        verbose: If True, print status messages

    Example:
        >>> # At the start of your script
        >>> require_claude_auth()
        >>> # If we get here, authentication succeeded
    """
    if not setup_claude_auth(verbose=verbose):
        print("\n❌ Authentication failed", file=sys.stderr)
        print("Make sure Claude Code is authenticated with:", file=sys.stderr)
        print("  1. An API key (https://console.anthropic.com/settings/keys)", file=sys.stderr)
        print("  2. Or run: claude-code auth", file=sys.stderr)
        sys.exit(1)


# For backwards compatibility and convenience
def setup_auth(verbose: bool = False) -> bool:
    """Alias for setup_claude_auth()."""
    return setup_claude_auth(verbose=verbose)


if __name__ == "__main__":
    # Test the authentication helper
    print("Testing Claude Agent SDK Authentication Helper")
    print("=" * 60)

    success = setup_claude_auth(verbose=True)

    print("=" * 60)
    if success:
        print("✅ Authentication configured successfully")
        print("\nEnvironment:")
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if api_key:
            print(f"  ANTHROPIC_API_KEY: {api_key[:15]}...{api_key[-4:]}")
        print(f"  CLAUDECODE: {os.environ.get('CLAUDECODE', '(not set)')}")
    else:
        print("❌ Authentication configuration failed")
        sys.exit(1)
