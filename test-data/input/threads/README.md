# Thread Test Data

This directory contains XML test data files for validating the Agent Protocol implementation across three languages (Python, TypeScript, and .NET).

## Directory Structure

The test files are organized into a multi-layer hierarchy based on their purpose and complexity:

```
threads/
├── basic/                      # Basic message types and simple content
│   ├── messages/              # Individual message types (system, developer, user, agent, tool, channel)
│   └── simple-content/        # Simple content types (text, refusal, function-call, etc.)
├── content-types/             # Specialized content types
│   ├── media/                # Audio, video, image, file, transcript content
│   ├── documents/            # Document content types
│   ├── ui/                   # UI-related content (adaptive cards, suggested actions, typing indicators)
│   ├── system/               # System content (content filters, events)
│   ├── functions/            # Function call and result flows
│   ├── messages/             # Message-related content (reactions, deletes, updates)
│   └── specialized/          # Specialized content (search results, hosted files, traces, etc.)
├── conversations/             # Multi-message conversation flows
│   ├── single-turn/          # Single message conversations
│   ├── multi-turn/           # Multi-turn conversations
│   ├── multi-user/           # Conversations with multiple users
│   └── tool-use/             # Conversations involving tool use
├── roles/                     # Role-based message organization
│   ├── agent-only/           # Agent-only threads
│   ├── tool-only/            # Tool-only threads
│   ├── interleaved/          # Mixed role threads
│   └── all-roles/            # Threads with all role types
├── scenarios/                 # Real-world usage scenarios
│   ├── queries/              # Query scenarios (weather, time, etc.)
│   ├── functions/            # Function calling scenarios
│   └── events/               # Event-based scenarios (user joined, emoji reactions, etc.)
├── edge-cases/                # Edge case testing
│   ├── empty/                # Empty thread handling
│   ├── duplicates/           # Duplicate message handling
│   ├── long/                 # Long conversation handling
│   └── special/              # Special edge cases
└── invalid/                   # Invalid XML for negative testing (17 files)
```

## Test Organization

Each subdirectory contains related test files that validate specific aspects of the protocol:

- **basic/** - Tests fundamental message types and simple content
- **content-types/** - Tests specialized content types and their serialization
- **conversations/** - Tests multi-message interactions and thread management
- **roles/** - Tests role-based access and message filtering
- **scenarios/** - Tests real-world usage patterns
- **edge-cases/** - Tests boundary conditions and error handling

## File Naming Convention

Files follow the pattern: `{number}-{descriptive-name}.xml`

- Numbers indicate original test order (preserved for backward compatibility)
- Descriptive names clarify the test purpose
- Examples: `01-system-message.xml`, `29-thread-with-tool-use.xml`, `80-emoji-reaction-added.xml`

## Usage

These test files are used by:

1. **Integration Tests** - Three language implementations process all valid XML files
2. **Validation Tests** - Tests verify XML structure and protocol compliance
3. **Golden File Tests** - Compares output against expected results

### Running Tests

**Python:**
```bash
pytest python/microsoft-agents-protocol/tests/test_integration.py -v
```

**TypeScript:**
```bash
npm test -- integration.test.ts
```

**.NET:**
```bash
dotnet test --filter "Category=GoldenFileIntegration"
```

## Adding New Tests

When adding new test files:

1. Place the file in the appropriate subdirectory based on its purpose
2. Follow the existing naming convention
3. Update the corresponding README in that subdirectory
4. Ensure the XML is valid and follows the Agent Protocol schema
5. Run all three language test suites to verify compatibility

## Total Files

- **Valid test files**: 84 XML files across all subdirectories
- **Invalid test files**: 17 XML files in `invalid/` subdirectory
- **Total**: 101 test files

## See Also

- Each subdirectory contains its own README.md with detailed file listings
- `/test-data/results/` contains expected output for golden file tests
- Protocol documentation: [Agent Protocol Specification](../../../docs/)
