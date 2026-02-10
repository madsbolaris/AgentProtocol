# Thread Test Data Migration Guide

## What Changed

The thread test data has been reorganized from a flat structure to a multi-layer hierarchical structure for better organization and maintainability.

### Before (Flat Structure)
```
test-data/input/threads/
├── 01-system-message.xml
├── 02-developer-message.xml
├── 03-user-text-only.xml
├── ... (84 files in root directory)
└── invalid/
    └── ... (17 invalid test files)
```

### After (Hierarchical Structure)
```
test-data/input/threads/
├── basic/
│   ├── messages/           (11 files)
│   └── simple-content/     (15 files)
├── content-types/
│   ├── media/             (5 files)
│   ├── documents/         (3 files)
│   ├── ui/                (4 files)
│   ├── system/            (4 files)
│   ├── functions/         (2 files)
│   ├── messages/          (3 files)
│   └── specialized/       (8 files)
├── conversations/
│   ├── single-turn/       (1 file)
│   ├── multi-turn/        (3 files)
│   ├── multi-user/        (3 files)
│   └── tool-use/          (3 files)
├── roles/
│   ├── agent-only/        (1 file)
│   ├── tool-only/         (1 file)
│   ├── interleaved/       (2 files)
│   └── all-roles/         (1 file)
├── scenarios/
│   ├── queries/           (2 files)
│   ├── functions/         (2 files)
│   └── events/            (7 files)
├── edge-cases/
│   ├── empty/             (1 file)
│   ├── duplicates/        (1 file)
│   ├── long/              (0 files - reserved)
│   └── special/           (1 file)
└── invalid/               (17 files - unchanged)
```

## File Mapping

### Basic Messages (`basic/messages/`)
- `01-system-message.xml`
- `02-developer-message.xml`
- `03-user-text-only.xml`
- `04-user-simple-text.xml`
- `05-user-multimodal.xml`
- `06-agent-thinking-and-call.xml`
- `07-tool-result-success.xml`
- `08-tool-result-simple.xml`
- `09-tool-result-error.xml`
- `10-agent-with-text-response.xml`
- `11-channel-message.xml`

### Basic Simple Content (`basic/simple-content/`)
- `19-text-content.xml`
- `19-refusal-content.xml`
- `20-function-call-content.xml`
- `21-function-result-content.xml`
- `21-typing-indicator-content.xml`
- `22-error-content.xml`
- `22-message-reaction-content.xml`
- `23-message-delete-content.xml`
- `23-text-reasoning-content.xml`
- `24-data-content.xml`
- `24-message-update-content.xml`
- `25-uri-content.xml`
- `25-hosted-file-content.xml`
- `26-image-content.xml`
- `26-hosted-vector-store-content.xml`

### Media Content (`content-types/media/`)
- `12-all-media-types.xml`
- `27-audio-content.xml`
- `28-transcript-content.xml`
- `29-video-content.xml`
- `30-file-content.xml`

### Documents (`content-types/documents/`)
- `13-document-content.xml`
- `17-transcript-content.xml`
- `32-document-content.xml`

### UI Content (`content-types/ui/`)
- `14-ui-content.xml`
- `33-adaptive-card-content.xml`
- `37-suggested-actions-content.xml`
- `41-typing-indicator-content.xml`

### System Content (`content-types/system/`)
- `15-system-content.xml`
- `20-content-filter-result-content.xml`
- `35-content-filter-result-content.xml`
- `38-event-content.xml`

### Function Content (`content-types/functions/`)
- `31-function-call-complete-flow.xml`
- `32-multiple-function-calls.xml`

### Message Content (`content-types/messages/`)
- `42-message-reaction-content.xml`
- `43-message-delete-content.xml`
- `44-message-update-content.xml`

### Specialized Content (`content-types/specialized/`)
- `16-data-and-uri-content.xml`
- `31-search-result-content.xml`
- `34-refusal-content.xml`
- `36-user-input-request-content.xml`
- `39-trace-content.xml`
- `40-action-content.xml`
- `45-hosted-file-content.xml`
- `46-hosted-vector-store-content.xml`

### Conversations - Single Turn (`conversations/single-turn/`)
- `27-thread-single-system.xml`

### Conversations - Multi Turn (`conversations/multi-turn/`)
- `28-thread-conversation.xml`
- `38-full-conversation.xml`
- `43-long-conversation.xml`

### Conversations - Multi User (`conversations/multi-user/`)
- `33-multi-user-conversation.xml`
- `34-user-to-user-with-agent.xml`
- `35-multiple-user-messages.xml`

### Conversations - Tool Use (`conversations/tool-use/`)
- `29-thread-with-tool-use.xml`
- `30-thread-multimodal.xml`
- `48-tools-between-users.xml`

### Roles - Agent Only (`roles/agent-only/`)
- `36-agent-only-thread.xml`

### Roles - Tool Only (`roles/tool-only/`)
- `37-tool-only-thread.xml`

### Roles - Interleaved (`roles/interleaved/`)
- `39-interleaved-roles.xml`
- `47-system-then-users.xml`

### Roles - All Roles (`roles/all-roles/`)
- `41-all-non-user-roles.xml`

### Scenarios - Queries (`scenarios/queries/`)
- `50-weather-query.xml`
- `51-time-query.xml`

### Scenarios - Functions (`scenarios/functions/`)
- `52-multi-function.xml`
- `53-no-function.xml`

### Scenarios - Events (`scenarios/events/`)
- `78-user-joined-event.xml`
- `79-user-left-event.xml`
- `80-emoji-reaction-added.xml`
- `81-emoji-reaction-removed.xml`
- `82-user-request-add-emoji.xml`
- `83-user-request-suggest-emoji.xml`
- `84-multiple-emoji-reactions.xml`

### Edge Cases - Empty (`edge-cases/empty/`)
- `40-empty-thread.xml`

### Edge Cases - Duplicates (`edge-cases/duplicates/`)
- `42-duplicate-user-messages.xml`

### Edge Cases - Special (`edge-cases/special/`)
- `18-edge-cases.xml`

## What Was Updated

### 1. Directory Structure
- Created 6 top-level categories: `basic/`, `content-types/`, `conversations/`, `roles/`, `scenarios/`, `edge-cases/`
- Created 27 subcategories total
- Moved all 84 valid XML files to appropriate subdirectories
- Left `invalid/` directory unchanged (17 files)

### 2. Test Files
All three language implementations were updated to recursively scan directories:

**Python** (`python/microsoft-agents-protocol/tests/test_integration.py`):
```python
# Changed from:
all_files = self.input_dir.glob("*.xml")

# To:
all_files = self.input_dir.rglob("*.xml")
```

**TypeScript** (`typescript/packages/agents-protocol-client/tests/integration.test.ts`):
```typescript
// Added recursive directory walking
async function walkDir(dir: string): Promise<void> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  // ... recursively process subdirectories
}
```

**.NET** (`dotnet/tests/EchoM365.Tests/IntegrationTests/EchoM365GoldenFileTests.cs`):
```csharp
// Changed from:
Directory.GetFiles(inputDir, "*.xml")

// To:
Directory.GetFiles(inputDir, "*.xml", SearchOption.AllDirectories)
```

### 3. Generation Scripts
Updated scripts to recursively scan directories:

**Golden Dataset Generator** (`scripts/testgen/generate_golden_datasets.py`):
```python
# Changed from:
input_files = sorted(self.inputs_dir.glob("*.xml"))

# To:
all_input_files = sorted(self.inputs_dir.rglob("*.xml"))
input_files = [f for f in all_input_files if "invalid" not in f.parts]
```

**Validation Script** (`scripts/validation/validate_test_infrastructure.py`):
```python
# Updated to check the new directory structure
threads_dir = repo_root / "test-data" / "input" / "threads"
all_input_files = list(threads_dir.rglob("*.xml"))
input_files = [f for f in all_input_files if "invalid" not in f.parts]
```

### 4. Documentation
Created comprehensive README.md files:
- Main threads README with complete directory overview
- README for each of the 6 top-level categories
- Total of 7 README files documenting structure and purpose

## Impact Assessment

### ✅ No Breaking Changes
- All test files retain their original filenames
- File contents are unchanged
- Tests continue to discover files automatically via recursive scanning
- Invalid test files remain in `invalid/` subdirectory

### 🎯 Benefits
1. **Better Organization**: Files grouped by purpose and complexity
2. **Easier Navigation**: Clear hierarchy makes finding relevant tests easier
3. **Improved Maintainability**: Related tests are co-located
4. **Scalability**: Structure supports adding new test categories
5. **Documentation**: Each category has explanatory README

### 🔍 Migration Required For
If you have any custom scripts or tools that directly reference test file paths, you will need to update them to:
1. Use recursive globbing (`rglob` in Python, `SearchOption.AllDirectories` in .NET)
2. Filter out the `invalid/` subdirectory
3. Or update hardcoded paths to include the new directory structure

## Verification

Run these commands to verify the migration:

### Python
```bash
python3 -c "
from pathlib import Path
input_dir = Path('test-data/input/threads')
all_files = list(input_dir.rglob('*.xml'))
valid_files = [f for f in all_files if 'invalid' not in f.parts]
print(f'Total: {len(all_files)}, Valid: {len(valid_files)}, Invalid: {len(all_files) - len(valid_files)}')
"
# Expected: Total: 101, Valid: 84, Invalid: 17
```

### Test Suites
```bash
# Python
pytest python/microsoft-agents-protocol/tests/test_integration.py -v

# TypeScript
npm test -- integration.test.ts

# .NET
dotnet test --filter "Category=GoldenFileIntegration"
```

All tests should pass and discover all 84 valid test files.

## Questions?

- See `README.md` in each directory for detailed information
- See `../results/` for golden file test outputs
- See protocol documentation in `/docs/` for specification details
