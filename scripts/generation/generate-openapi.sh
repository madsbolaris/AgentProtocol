#!/bin/bash

# Generate OpenAPI specification from TypeSpec definitions
# Usage: ./generate-openapi.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
TYPESPEC_DIR="$REPO_ROOT/specs/typespec"
OUTPUT_DIR="$REPO_ROOT/.generated"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OpenAPI Specification Generation                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo

cd "$TYPESPEC_DIR"

echo -e "${GREEN}📝 Compiling TypeSpec to OpenAPI...${NC}"
npm run compile

echo
echo -e "${GREEN}✅ OpenAPI specification generated successfully!${NC}"
echo -e "${BLUE}Output: $OUTPUT_DIR/openapi.json${NC}"
