#!/bin/bash
# Generate TypeScript types for the TypeScript packages directory

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TYPESPEC_DIR="$REPO_ROOT/specs/typespec"
CODEGEN_PROJECT="$REPO_ROOT/dotnet/src/Microsoft.Agents.CodeGen"
JS_OUTPUT="$REPO_ROOT/javascript/packages/agents/src/generated"
TS_OUTPUT="$REPO_ROOT/typescript/packages/agents/src/generated"

# Check if dotnet is available
if ! command -v dotnet &> /dev/null; then
    DOTNET="/usr/local/share/dotnet/dotnet"
    if [ ! -f "$DOTNET" ]; then
        echo -e "${YELLOW}Error: dotnet not found${NC}"
        exit 1
    fi
else
    DOTNET="dotnet"
fi

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     TypeScript Type Generation (for TS packages)      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo

# First run the standard generation
echo -e "${BLUE}Running standard TypeScript generation...${NC}"
bash "$REPO_ROOT/scripts/generation/generate-typescript.sh"

# Copy generated files to TypeScript packages
echo -e "${GREEN}Copying generated types to TypeScript packages...${NC}"
rm -rf "$TS_OUTPUT"
mkdir -p "$TS_OUTPUT"
cp -r "$JS_OUTPUT/"* "$TS_OUTPUT/" 2>/dev/null || true

# Update index.ts to export generated types
echo -e "${GREEN}Updating TypeScript package index...${NC}"
cat > "$REPO_ROOT/typescript/packages/agents/src/index.ts" << 'EOF'
/**
 * Microsoft Agents - Core TypeScript Types
 *
 * This package provides TypeScript types generated from TypeSpec definitions
 * for the Microsoft Agents Protocol.
 *
 * @packageDocumentation
 */

// Generated types
export * from './generated/messages';
export * from './generated/threads';
export * from './generated/execution';
export * from './generated/tools';
export * from './generated/agents';
export * from './generated/streaming';
export * from './generated/subscriptions';
export * from './generated/common';

// Utility functions
export * from './utilities';
EOF

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ TypeScript types generated successfully!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Output directory: $TS_OUTPUT${NC}"
echo
