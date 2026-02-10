#!/usr/bin/env python3
"""
Install git hooks for Agent Protocol.

This script creates symlinks from .githooks/ to .git/hooks/ for all hook scripts.
"""

import sys
from pathlib import Path


def install_hooks():
    """Install git hooks by creating symlinks."""
    # Get paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    hooks_dir = repo_root / ".githooks"
    git_hooks_dir = repo_root / ".git" / "hooks"

    print("🔧 Installing git hooks...")
    print()

    # Check if .git directory exists
    if not git_hooks_dir.exists():
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    # Create symlinks for all hooks
    installed_count = 0

    if not hooks_dir.exists():
        print(f"❌ Error: Hooks directory not found: {hooks_dir}")
        sys.exit(1)

    for hook_file in hooks_dir.iterdir():
        if hook_file.is_file():
            hook_name = hook_file.name
            target = git_hooks_dir / hook_name

            # Remove existing hook or symlink
            if target.exists() or target.is_symlink():
                print(f"  Replacing existing hook: {hook_name}")
                target.unlink()

            # Create symlink
            target.symlink_to(hook_file)
            print(f"  ✓ Installed: {hook_name}")
            installed_count += 1

    print()
    print("═" * 63)
    print(f"✓ Installed {installed_count} git hooks")
    print("═" * 63)
    print()
    print("Hooks installed:")
    print("  • pre-commit  - Validates tests against golden files")
    print("  • post-merge  - Validates after pulling changes")
    print()
    print("To bypass pre-commit hook (not recommended):")
    print("  git commit --no-verify")
    print()
    print("To uninstall hooks:")
    print("  rm .git/hooks/pre-commit .git/hooks/post-merge")
    print()


if __name__ == "__main__":
    install_hooks()
