# Code Generation Scripts

This directory contains scripts for generating code artifacts from TypeSpec definitions.

## Architecture Decision

**Why separate scripts instead of integrating into TypeSpec emitters?**

We use **orchestrated build scripts** rather than native TypeSpec emitters because:

1. **Multi-language consistency** - The same Roslyn generator produces both C# and TypeScript with identical structures
2. **Full control** - Custom patterns for message inheritance and content type polymorphism
3. **Maintainability** - Each tool does what it's best at (TypeSpec → OpenAPI, Roslyn → Types)
4. **Flexibility** - Easy to run individually or together
5. **Proven approach** - Works across C#, TypeScript, and future Python implementations

## Scripts

### `generate-all.sh` ⭐
**Master script** - Generates all code artifacts

```bash
./scripts/generation/generate-all.sh
```

This runs:
1. OpenAPI generation (for API docs)
2. C# type generation (for .NET SDK)
3. TypeScript type generation (for JS/TS SDK)

### `generate-typescript.sh`
Generates TypeScript types from all TypeSpec files

```bash
./scripts/generation/generate-typescript.sh
```

Generates from:
- `messages.tsp` → Message and content types (ChatMessage, AIContent, 29+ content types)
- `threads.tsp` → Thread/conversation types
- `execution.tsp` → Run/execution types
- `tools.tsp` → Tool/function types
- `agents.tsp` → Agent configuration types
- `streaming.tsp` → SSE streaming event types
- `subscriptions.tsp` → Webhook subscription types
- `common.tsp` → Shared types

**Output**: `javascript/packages/agents-protocol-types/src/generated/`

### `generate-csharp.sh`
Generates C# types from TypeSpec files

```bash
./scripts/generation/generate-csharp.sh
```

**Output**: `dotnet/src/Microsoft.Agents.Xml/Microsoft.Agents.Xml.Generated/Models/`

### `generate-openapi.sh`
Generates OpenAPI 3.0 specification

```bash
./scripts/generation/generate-openapi.sh
```

**Output**: `.generated/openapi.json`

## Integration with Build Process

### JavaScript/TypeScript Package

The `agents-protocol-types` package automatically runs generation on build:

```bash
cd javascript/packages/agents-protocol-types
npm run build      # Generates types + compiles TypeScript
npm run generate   # Just generates types
```

### .NET Package

The C# types can be regenerated:

```bash
./scripts/generation/generate-csharp.sh
```

## How Code Generation Works

### TypeSpec → Roslyn → TypeScript/C#

```
TypeSpec Files              Roslyn Generator            Output
(source of truth)           (custom parser)         (generated code)
──────────────────────────────────────────────────────────────────
messages.tsp        ─→      TypeSpecReader      ─→   TypeScript
  • ChatMessage            • Parses models              • Interfaces
  • ChatRole               • Parses enums               • Discriminated unions
  • AIContent              • Parses unions              • Type guards
  • 29+ content types      • Extracts metadata          • Helper functions

                           TypeScriptGenerator      ─→  C#
                           • MessageGenerator           • Classes
                           • ContentGenerator           • XML attributes
                           • ModelGenerator             • Polymorphism
```

### Key Features

1. **Discriminated Unions**
   - TypeScript: `type AIContent = TextContent | ImageContent | ...`
   - C#: `abstract class AIContent { abstract string Kind; }`

2. **Type Guards** (TypeScript only)
   ```typescript
   function isTextContent(content: AIContent): content is TextContent {
     return content.kind === 'text';
   }
   ```

3. **Message Hierarchy**
   - Base: `ChatMessage` with abstract `role` property
   - Derived: `UserMessage`, `AgentMessage`, `ToolMessage`, etc.

4. **Content Polymorphism**
   - Base: `AIContentBase` with `kind` discriminator
   - 29+ derived types with specialized properties

## Troubleshooting

### `dotnet: command not found`

The scripts automatically try `/usr/local/share/dotnet/dotnet` on macOS. If that doesn't work:

```bash
# Find dotnet
which dotnet

# Or add to PATH
export PATH="/path/to/dotnet:$PATH"
```

### Types not updating

Clean and regenerate:

```bash
cd javascript/packages/agents-protocol-types
npm run clean
npm run generate
```

### Merge conflicts in generated files

Generated files should **not be manually edited**. Resolve by regenerating:

```bash
./scripts/generation/generate-typescript.sh
```

## Adding New TypeSpec Files

1. Create new `.tsp` file in `specs/typespec/`
2. Add to `TYPESPEC_FILES` array in `generate-typescript.sh` and `generate-csharp.sh`
3. Run generation scripts

Example:
```bash
# Edit generate-typescript.sh
TYPESPEC_FILES=(
    "messages"
    "threads"
    "new-feature"  # ← Add here
)

# Regenerate
./scripts/generation/generate-typescript.sh
```

## CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Generate code
  run: ./scripts/generation/generate-all.sh

- name: Check for changes
  run: |
    if [ -n "$(git status --porcelain)" ]; then
      echo "Generated code is out of sync"
      exit 1
    fi
```

## See Also

- [TypeSpec Documentation](https://typespec.io/)
- [Roslyn Code Generator](../../dotnet/src/Microsoft.Agents.Xml/Microsoft.Agents.Xml.CodeGen/)
- [Generated TypeScript Types](../../javascript/packages/agents-protocol-types/)
