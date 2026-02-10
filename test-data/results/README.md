# Test Results & Golden Datasets

This directory contains golden datasets and test results organized by sample name. Golden datasets are language-agnostic and used for cross-platform validation across .NET, Python, and TypeScript implementations.

## Directory Structure

```
test-data/results/
├── echo-m365/           # EchoM365 sample results
│   ├── json/            # JSON format outputs
│   ├── xml/             # XML format outputs
│   ├── streaming/       # Streaming response outputs
│   └── wait/            # Wait pattern outputs
├── basic-m365/          # BasicM365 sample results
│   ├── json/
│   └── xml/
├── emoji-chat/          # EmojiChatBot sample results
│   ├── json/
│   └── xml/
├── evals/               # Evaluation test results
│   └── json/
└── {other-samples}/     # Additional samples follow same structure
    ├── json/
    └── xml/
```

## Golden Files

Golden files serve as the "source of truth" for expected outputs. All language implementations should produce output that matches these golden files.

### Golden File Format

Golden files are stored in `{sample}/golden/` and include:

**For JSON outputs:**
```json
{
  "timestamp": "2026-02-08T12:00:00Z",
  "content": { ... },
  "hash": "sha256-hash-of-content",
  "metadata": {
    "input_file": "01-user-message.xml",
    "sample": "echo-m365",
    "generator": "dotnet"
  }
}
```

**For XML outputs:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<agent message-id="msg-123">
  <text>Response text</text>
</agent>
```

With metadata sidecar (`.meta.json`):
```json
{
  "timestamp": "2026-02-08T12:00:00Z",
  "hash": "sha256-hash-of-content",
  "metadata": {
    "input_file": "01-user-message.xml",
    "sample": "echo-m365"
  }
}
```

## Generating Golden Datasets

Use the unified golden dataset generation script. **The .NET implementation is the canonical source** - all other languages must conform to its output.

```bash
# Generate for all samples (automatically starts .NET bots)
python scripts/generate_golden_datasets.py

# Generate for specific sample
python scripts/generate_golden_datasets.py --sample echo-m365

# Generate for emoji-chat sample
python scripts/generate_golden_datasets.py --sample emoji-chat

# Use custom paths
python scripts/generate_golden_datasets.py --inputs test-data/input --results test-data/results
```

### How It Works

The script will:
1. Discover sample configurations from `agent-config.json`
2. **Automatically start the .NET bot** for the specified sample
3. Send test inputs from `test-data/input/` to the .NET bot
4. Generate golden files from .NET output in `test-data/results/{sample}/golden/`
5. Stop the bot when complete

**No manual setup required!** The script handles everything automatically.

### Why .NET is Canonical

- .NET implementation is the **source of truth** for expected behavior
- Python and TypeScript implementations **must match** .NET output exactly
- Golden files are generated exclusively from .NET
- Other languages validate against these golden files

## Validating Against Golden Files

### Python

```bash
# Set sample name and run tests
SAMPLE_NAME=echom365 pytest python/microsoft-agents-xml/tests/

# Update golden files if needed
UPDATE_GOLDEN=1 SAMPLE_NAME=echom365 pytest python/microsoft-agents-xml/tests/
```

### TypeScript

```bash
# Set sample name and run tests
SAMPLE_NAME=echom365 npm test

# Update golden files if needed
UPDATE_GOLDEN=1 SAMPLE_NAME=echom365 npm test
```

### .NET

```bash
# Set sample name and run tests
SAMPLE_NAME=echom365 dotnet test

# Update golden files (requires code changes to read environment variable)
UPDATE_GOLDEN=1 SAMPLE_NAME=echom365 dotnet test
```

## Cross-Platform Validation

All language implementations must produce outputs identical to .NET. To validate:

1. Generate golden files from .NET (canonical source):
   ```bash
   python scripts/generate_golden_datasets.py --sample echom365
   ```
   This automatically starts the .NET bot and generates golden files.

2. Validate Python and TypeScript implementations:
   ```bash
   # Python - must match .NET golden files
   SAMPLE_NAME=echom365 pytest python/microsoft-agents-xml/tests/

   # TypeScript - must match .NET golden files
   SAMPLE_NAME=echom365 npm test
   ```

3. If tests fail, fix Python/TypeScript to match .NET output (not the other way around).

**Important:** .NET is the source of truth. Other languages conform to it.

## Migration from Old Structure

If you have deprecated language-specific directories (`python/`, `typescript/`, `shared/`), use the cleanup script:

```bash
./scripts/cleanup_deprecated_results.sh
```

This will:
1. Create a backup of existing directories
2. Delete deprecated directories
3. Provide instructions for restoration if needed

## Adding a New Sample

To add golden files for a new sample:

1. Add the sample configuration to `agent-config.json`:
   ```json
   {
     "bots": {
       "dotnet-my-sample": {
         "name": "My Sample (.NET)",
         "port": 3985,
         "baseUrl": "http://localhost"
       }
     }
   }
   ```

2. Start the bot and generate golden files:
   ```bash
   python scripts/generate_golden_datasets.py --sample my-sample
   ```

3. Update tests to validate against the new golden files:
   ```bash
   SAMPLE_NAME=my-sample pytest tests/
   ```

## File Naming Convention

Golden files follow the naming convention:
- `{input-name}-result.json` - JSON format results
- `{input-name}-result.xml` - XML format results

For example:
- Input: `test-data/input/01-user-message.xml`
- JSON Result: `test-data/results/echo-m365/json/01-user-message-result.json`
- XML Result: `test-data/results/echo-m365/xml/01-user-message-result.xml`
- Golden: `test-data/results/echo-m365/golden/01-user-message-result.json`

## Troubleshooting

### Tests failing with "golden file not found"

Generate golden files first:
```bash
python scripts/generate_golden_datasets.py --sample {sample-name}
```

### Tests failing with "output mismatch"

If the change is intentional, update golden files:
```bash
UPDATE_GOLDEN=1 SAMPLE_NAME={sample-name} pytest tests/
```

If the change is NOT intentional, fix the code to match the golden files.

### Bot fails to start automatically

The script automatically starts the .NET bot. If it fails:

1. Check that `dotnet` is installed and in PATH:
   ```bash
   dotnet --version
   ```

2. Verify the bot directory exists:
   ```bash
   ls dotnet/samples/agents/EchoM365/
   ```

3. Try starting manually to see error messages:
   ```bash
   cd dotnet/samples/agents/EchoM365
   dotnet run
   ```

4. Check port availability (default: 3979 for .NET EchoM365):
   ```bash
   lsof -i :3979
   ```

## Related Documentation

- [Agent Configuration](../../agent-config.json) - Sample bot configurations
- [Test Inputs](../input/) - Input test files
- [Generation Script](../../scripts/generate_golden_datasets.py) - Golden dataset generation
- [Cleanup Script](../../scripts/cleanup_deprecated_results.sh) - Remove deprecated directories
