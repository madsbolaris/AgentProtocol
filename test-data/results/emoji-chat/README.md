# Emoji Chat Test Results

This directory contains golden datasets and test results for the EmojiChatBot sample agent.

## Sample Information

- **Name**: EmojiChatBot
- **Purpose**: Demonstrates emoji reaction handling and sentiment-based emoji suggestions
- **Languages**: .NET, Python, TypeScript
- **Ports**:
  - .NET: 3984
  - Python: 3985
  - TypeScript: 3986

## Directory Structure

```
emoji-chat/
├── json/               # JSON format outputs
├── xml/                # XML format outputs
└── README.md          # This file
```

## Test Inputs

Emoji-chat uses specific test inputs from `test-data/input/threads/`:

- `78-user-joined-event.xml` - User join events
- `79-user-left-event.xml` - User leave events
- `80-emoji-reaction-added.xml` - Emoji reaction added
- `81-emoji-reaction-removed.xml` - Emoji reaction removed
- `82-user-request-add-emoji.xml` - User requests emoji addition
- `83-user-request-suggest-emoji.xml` - User requests emoji suggestions
- `84-multiple-emoji-reactions.xml` - Multiple emoji reactions

## Generating Results

Generate golden files for emoji-chat:

```bash
# Start the .NET emoji-chat bot (if not already running)
cd dotnet/samples/agents/EmojiChatBot
dotnet run

# In another terminal, generate golden files
python scripts/testgen/generate_golden_datasets.py --sample emoji-chat

# With LLM recording (for agents that use LLMs)
python scripts/testgen/generate_golden_datasets.py --sample emoji-chat --record-llm
```

The script will automatically:
1. Start the .NET bot (if not running)
2. Send emoji-related test inputs
3. Capture outputs in JSON and XML formats
4. Optionally record LLM interactions
5. Stop the bot when complete

## Important: LLM Integration

⚠️ **Emoji-chat uses an LLM (GPT-4)** - it's not just a rule-based bot! The LLM decides when and how to use the emoji tools. This means:
- LLM recordings should be generated for deterministic testing
- The bot requires OpenAI API access (or mock recordings for tests)
- Responses may vary without recordings

## Agent Features

The EmojiChatBot demonstrates:

1. **Emoji Tools**:
   - `AddEmojiToMessage(messageId, emoji)` - Adds an emoji reaction to a message
   - `SuggestEmoji(messageText)` - Suggests emojis based on sentiment

2. **Event Handlers**:
   - User join/leave events
   - Emoji reaction added/removed events

3. **State Management**:
   - Message count tracking
   - Last emoji used tracking

## Cross-Language Validation

All three language implementations should produce identical outputs for the same inputs:
- .NET output is the canonical reference
- Python and TypeScript implementations validate against .NET golden files

## LLM Usage

**Emoji-chat uses an LLM!** The bot is configured with GPT-4 to intelligently decide when to call the emoji tools:

- `add_emoji_to_message` - Called when user wants to add emoji reactions
- `suggest_emoji` - Called to suggest appropriate emojis based on sentiment

### Why No Recordings Yet?

The `test-data/llm-recordings/emoji-chat/` directory is empty because recordings are only created when you run:

```bash
python scripts/testgen/generate_golden_datasets.py --sample emoji-chat --record-llm
```

### What Are LLM Recordings?

LLM recordings capture the exact request/response pairs between the agent and the LLM. This allows tests to:
- Run deterministically without calling real LLMs
- Replay the exact same LLM responses
- Avoid API costs during testing
- Ensure consistent test results

### Current Status

| Sample      | Uses LLM? | Has Recordings? | Count |
|-------------|-----------|-----------------|-------|
| basic-m365  | ✅ Yes    | ✅ Yes          | 38    |
| emoji-chat  | ✅ Yes    | ❌ No (needs generation) | 0 |
| echo-m365   | ❌ No     | N/A             | N/A   |
| evals       | ✅ Yes    | ✅ Yes          | 122   |

### To Generate Recordings

Run the emoji-chat bot with LLM recording enabled:

```bash
# Start the .NET bot with recording enabled
cd dotnet/samples/agents/EmojiChatBot
RECORD_LLM=true dotnet run

# Or use the automated script
python scripts/testgen/generate_golden_datasets.py --sample emoji-chat --record-llm
```

This will populate `test-data/llm-recordings/emoji-chat/` with request/response JSON files.
