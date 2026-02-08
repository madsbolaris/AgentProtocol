#!/bin/bash
# Script to port the React UI package from JavaScript to TypeScript

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

SRC_DIR="$REPO_ROOT/javascript/packages/agents-react-ui"
DEST_DIR="$REPO_ROOT/typescript/packages/agents-react"

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Porting React UI Package to TypeScript            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}Source: $SRC_DIR${NC}"
echo -e "${BLUE}Destination: $DEST_DIR${NC}"
echo

# Create destination directory structure
echo -e "${GREEN}Creating directory structure...${NC}"
mkdir -p "$DEST_DIR/src"/{providers,components,hooks,renderers,styles,utils}
mkdir -p "$DEST_DIR/examples"

# Copy source files
echo -e "${GREEN}Copying source files...${NC}"
cp -r "$SRC_DIR/src/"* "$DEST_DIR/src/" 2>/dev/null || true

# Copy examples
cp -r "$SRC_DIR/examples/"* "$DEST_DIR/examples/" 2>/dev/null || true

# Copy README
cp "$SRC_DIR/README.md" "$DEST_DIR/README.md" 2>/dev/null || true

# Update package.json
echo -e "${GREEN}Creating package.json...${NC}"
cat > "$DEST_DIR/package.json" << 'EOF'
{
  "name": "@microsoft/agents-react",
  "version": "0.1.0",
  "description": "React component library for Microsoft Agents Protocol chat interfaces",
  "main": "./dist/index.js",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./styles": "./dist/styles/default-theme.css"
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "scripts": {
    "build": "tsc -b",
    "clean": "rm -rf dist *.tsbuildinfo storybook-static",
    "dev": "tsc -b --watch",
    "test": "jest",
    "test:watch": "jest --watch",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  },
  "keywords": [
    "react",
    "agents",
    "protocol",
    "chat",
    "ui",
    "components",
    "microsoft",
    "conversational-ai"
  ],
  "author": "Microsoft",
  "license": "MIT",
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "dependencies": {
    "@microsoft/agents-protocol-client": "^0.1.0",
    "@microsoft/agents": "^0.1.0"
  },
  "devDependencies": {
    "@storybook/react": "^7.6.0",
    "@storybook/react-vite": "^7.6.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@types/jest": "^29.5.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "storybook": "^7.6.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.8.0"
  }
}
EOF

# Create tsconfig.json
echo -e "${GREEN}Creating tsconfig.json...${NC}"
cat > "$DEST_DIR/tsconfig.json" << 'EOF'
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src",
    "jsx": "react",
    "lib": ["ES2020", "DOM", "DOM.Iterable"]
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.test.tsx"],
  "references": [
    { "path": "../agents" },
    { "path": "../agents-protocol-client" }
  ]
}
EOF

# Update imports in all TypeScript files
echo -e "${GREEN}Updating imports...${NC}"
find "$DEST_DIR/src" -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i '' \
  -e 's/@microsoft\/agents-protocol-types/@microsoft\/agents/g' \
  -e 's/@microsoft\/agents-react-ui/@microsoft\/agents-react/g' \
  {} \;

# Update README
echo -e "${GREEN}Updating README...${NC}"
sed -i '' \
  -e 's/@microsoft\/agents-react-ui/@microsoft\/agents-react/g' \
  -e 's/@microsoft\/agents-protocol-types/@microsoft\/agents/g' \
  "$DEST_DIR/README.md"

echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ React UI package ported successfully!            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Location: $DEST_DIR${NC}"
echo
