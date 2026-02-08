#!/bin/bash
# Install git hooks for Agent Protocol

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "🔧 Installing git hooks..."
echo ""

# Check if .git directory exists
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create symlinks for all hooks
INSTALLED=0
for hook in "$HOOKS_DIR"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        target="$GIT_HOOKS_DIR/$hook_name"

        # Remove existing hook or symlink
        if [ -e "$target" ] || [ -L "$target" ]; then
            echo "  Replacing existing hook: $hook_name"
            rm "$target"
        fi

        # Create symlink
        ln -s "$hook" "$target"
        echo "  ✓ Installed: $hook_name"
        INSTALLED=$((INSTALLED + 1))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✓ Installed $INSTALLED git hooks"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Hooks installed:"
echo "  • pre-commit  - Validates tests against golden files"
echo "  • post-merge  - Validates after pulling changes"
echo ""
echo "To bypass pre-commit hook (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To uninstall hooks:"
echo "  rm .git/hooks/pre-commit .git/hooks/post-merge"
