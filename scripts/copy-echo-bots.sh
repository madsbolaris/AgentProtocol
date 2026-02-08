#!/bin/bash

# Script to copy clean echo bot samples from M365 Agents SDK
# and replace the existing ones in this repository

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_SDK_PATH="$HOME/repos/Agents"

echo "🚀 Copying echo bot samples from M365 Agents SDK..."
echo ""

# Check if Agents SDK exists
if [ ! -d "$AGENTS_SDK_PATH" ]; then
    echo "❌ Error: M365 Agents SDK not found at $AGENTS_SDK_PATH"
    exit 1
fi

# Function to delete and copy
copy_sample() {
    local lang=$1
    local source_dir=$2
    local dest_dir=$3

    echo "📦 Processing $lang echo bot..."

    # Delete existing sample (but keep the directory structure)
    if [ -d "$dest_dir" ]; then
        echo "  🗑️  Deleting existing sample at $dest_dir"
        rm -rf "$dest_dir"
    fi

    # Copy fresh sample
    echo "  📋 Copying from $source_dir"
    cp -r "$source_dir" "$dest_dir"

    echo "  ✅ $lang echo bot copied successfully"
    echo ""
}

# Copy Python echo bot
copy_sample \
    "Python" \
    "$AGENTS_SDK_PATH/samples/python/quickstart" \
    "$REPO_ROOT/python/samples/agents/echo-bot"

# Copy .NET echo bot
copy_sample \
    ".NET" \
    "$AGENTS_SDK_PATH/samples/dotnet/quickstart" \
    "$REPO_ROOT/dotnet/samples/agents/EchoBot"

# Copy TypeScript echo bot
copy_sample \
    "TypeScript" \
    "$AGENTS_SDK_PATH/samples/nodejs/quickstart" \
    "$REPO_ROOT/typescript/samples/echo-bot"

echo "✨ All echo bot samples copied successfully!"
echo ""
echo "Next steps:"
echo "1. Update package imports to use our new packages"
echo "2. Add Agent Protocol routes using SDK helpers (few lines of code)"
echo "3. Test each sample"
