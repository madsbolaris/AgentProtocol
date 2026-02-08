#!/bin/bash

# Generate C# types from TypeSpec definitions using Roslyn code generator
# Usage: ./generate-csharp.sh [typespec-file] [output-dir]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
TYPESPEC_DIR="$REPO_ROOT/specs/typespec"
CODEGEN_PROJECT="$REPO_ROOT/dotnet/src/Microsoft.Agents.Xml/Microsoft.Agents.Xml.CodeGen"
OUTPUT_BASE="$REPO_ROOT/dotnet/src/Microsoft.Agents.Xml/Microsoft.Agents.Xml.Generated/Models"

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

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         C# Type Generation from TypeSpec               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

# Generate from messages.tsp
echo -e "${GREEN}📝 Generating from messages.tsp...${NC}"
$DOTNET run --project "$CODEGEN_PROJECT" -- \
  --typespec "$TYPESPEC_DIR/messages.tsp" \
  --language csharp \
  --output "$OUTPUT_BASE" \
  --namespace "Microsoft.Agents.Xml.Generated.Models"

echo
echo -e "${GREEN}✅ C# types generated successfully!${NC}"
echo -e "${BLUE}Output: $OUTPUT_BASE${NC}"
