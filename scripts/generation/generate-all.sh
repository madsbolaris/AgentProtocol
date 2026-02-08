#!/bin/bash

# Master script to generate all code artifacts from TypeSpec
# This orchestrates:
#   1. OpenAPI spec generation (for API docs)
#   2. C# type generation (for .NET SDK)
#   3. TypeScript type generation (for JS/TS SDK)
#   4. Python type generation (for Python SDK)
#
# Usage: ./generate-all.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}║          Agent Protocol Code Generation                ║${NC}"
echo -e "${CYAN}║                                                        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Generating all code artifacts from TypeSpec definitions...${NC}"
echo

# Step 1: Generate OpenAPI
echo -e "${YELLOW}[1/4] Generating OpenAPI specification...${NC}"
bash "$SCRIPT_DIR/generate-openapi.sh"
echo

# Step 2: Generate C# types
echo -e "${YELLOW}[2/4] Generating C# types...${NC}"
bash "$SCRIPT_DIR/generate-csharp.sh"
echo

# Step 3: Generate TypeScript types
echo -e "${YELLOW}[3/4] Generating TypeScript types...${NC}"
bash "$SCRIPT_DIR/generate-typescript.sh"
echo

# Step 4: Generate Python types
echo -e "${YELLOW}[4/4] Generating Python types...${NC}"
bash "$SCRIPT_DIR/generate-python.sh"
echo

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}║              ✅ All Code Generated!                     ║${NC}"
echo -e "${GREEN}║                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Summary:${NC}"
echo -e "  📄 OpenAPI:    .generated/openapi.json"
echo -e "  🔷 C# Types:   dotnet/src/Microsoft.Agents.Xml/Microsoft.Agents.Xml.Generated/"
echo -e "  📘 TS Types:   javascript/packages/agents-protocol-types/src/generated/"
echo -e "  🐍 PY Types:   python/microsoft-agents-abstractions/microsoft/agents/models/"
echo
echo -e "${CYAN}Next steps:${NC}"
echo -e "  • Review generated files"
echo -e "  • Run tests: ${BLUE}npm test${NC} or ${BLUE}dotnet test${NC}"
echo -e "  • Commit changes if everything looks good"
echo
