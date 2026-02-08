#!/bin/bash

# Generate TypeScript types from TypeSpec definitions using Roslyn code generator
# Generates from all major TypeSpec files
# Usage: ./generate-typescript.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
TYPESPEC_DIR="$REPO_ROOT/specs/typespec"
CODEGEN_PROJECT="$REPO_ROOT/dotnet/src/Microsoft.Agents.CodeGen"
OUTPUT_BASE="$REPO_ROOT/javascript/packages/agents/src/generated"

# Check if dotnet is available
if ! command -v dotnet &> /dev/null; then
    # Try full path on macOS
    DOTNET="/usr/local/share/dotnet/dotnet"
    if [ ! -f "$DOTNET" ]; then
        echo -e "${YELLOW}Error: dotnet not found${NC}"
        exit 1
    fi
else
    DOTNET="dotnet"
fi

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     TypeScript Type Generation from TypeSpec          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Clean previous generation
echo -e "${BLUE}🧹 Cleaning previous generated files...${NC}"
rm -rf "$OUTPUT_BASE"
mkdir -p "$OUTPUT_BASE"

# TypeSpec files to generate from (in order)
TYPESPEC_FILES=(
    "messages"      # Core message types (ChatMessage, AIContent, etc.)
    "threads"       # Thread/conversation types
    "execution"     # Run/execution types
    "tools"         # Tool/function types
    "agents"        # Agent configuration types
    "streaming"     # SSE streaming event types
    "subscriptions" # Webhook subscription types
    "common"        # Common/shared types
)

total=${#TYPESPEC_FILES[@]}
current=0

for file in "${TYPESPEC_FILES[@]}"; do
    current=$((current + 1))
    echo
    echo -e "${GREEN}[$current/$total] Generating from ${file}.tsp...${NC}"

    # Check if file exists
    if [ ! -f "$TYPESPEC_DIR/${file}.tsp" ]; then
        echo -e "${YELLOW}⚠️  Skipping ${file}.tsp (not found)${NC}"
        continue
    fi

    # Generate TypeScript types
    $DOTNET run --project "$CODEGEN_PROJECT" --no-build -- \
      --typespec "$TYPESPEC_DIR/${file}.tsp" \
      --language typescript \
      --output "$OUTPUT_BASE" \
      --namespace "Microsoft.Agents" \
      2>&1 | grep -v "warning NU"  # Filter out NuGet warnings
done

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ TypeScript types generated successfully!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Output directory: $OUTPUT_BASE${NC}"
echo -e "${BLUE}Generated from: ${total} TypeSpec files${NC}"
echo
