# LLM Recordings

This directory contains recorded LLM request/response pairs for test replay.

## Purpose

Recordings enable **fast, deterministic, cost-free** testing of LLM-powered agents:

- **Generation Mode**: Records real LLM interactions during test generation
- **Test Mode**: Replays recorded interactions without calling real LLM

## Directory Structure

```
llm-recordings/
└── function-tools/              # Function Tools Agent recordings
    ├── a1b2c3d4.request.json   # Request with hash a1b2c3d4
    ├── a1b2c3d4.response.json  # Corresponding response
    ├── e5f6g7h8.request.json   # Another request
    └── e5f6g7h8.response.json  # Another response
```

## File Format

### Request File (`{hash}.request.json`)

```json
{
  "timestamp": "2026-02-07T12:00:00Z",
  "hash": "a1b2c3d4",
  "request": {
    "model": "gpt-5-nano",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant..."
      },
      {
        "role": "user",
        "content": "What's the weather in Seattle?"
      }
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get the weather for a given location.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The location to get the weather for."
              }
            },
            "required": ["location"]
          }
        }
      }
    ],
    "temperature": 0.0,
    "seed": 42
  }
}
```

### Response File (`{hash}.response.json`)

```json
{
  "timestamp": "2026-02-07T12:00:01Z",
  "hash": "a1b2c3d4",
  "response": {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1707307201,
    "model": "gpt-5-nano",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": null,
          "tool_calls": [
            {
              "id": "call_abc123",
              "type": "function",
              "function": {
                "name": "get_weather",
                "arguments": "{\"location\": \"Seattle\"}"
              }
            }
          ]
        },
        "finish_reason": "tool_calls"
      }
    ],
    "usage": {
      "prompt_tokens": 50,
      "completion_tokens": 20,
      "total_tokens": 70
    }
  }
}
```

## Hash Algorithm

Recordings are identified by a deterministic hash of the request:

1. **Normalize Request**: Create canonical representation with sorted keys
2. **Serialize**: Convert to stable JSON (no whitespace)
3. **Hash**: Apply SHA256
4. **Truncate**: Take first 16 characters

```python
request_dict = {
    "model": "gpt-5-nano",
    "messages": [...],
    "tools": [...],
    "temperature": 0.0,
    "seed": 42
}

json_str = json.dumps(request_dict, sort_keys=True, separators=(',', ':'))
hash_full = hashlib.sha256(json_str.encode()).hexdigest()
hash_key = hash_full[:16]  # "a1b2c3d4e5f6g7h8"
```

**Properties**:
- Same request → Same hash (deterministic)
- Different request → Different hash (collision-resistant)
- Includes all parameters that affect response

## Generating Recordings

Run tests in generation mode to create recordings:

```bash
# Set environment
export TEST_MODE=generate
export FOUNDRY_ENDPOINT=https://...
export FOUNDRY_API_KEY=...
export FOUNDRY_MODEL_DEPLOYMENT=gpt-5-nano

# Run generation tests
cd python/microsoft-agents-protocol
pytest tests/integration/test_function_tools_generation.py -v
```

**What happens**:
1. Tests call real Foundry LLM
2. Requests and responses are recorded to this directory
3. Golden files are created in `test-data/results/`

**When to regenerate**:
- First time setup
- When test inputs change
- When LLM model updates
- When function definitions change

## Using Recordings in Tests

Normal tests use recordings automatically:

```bash
# No Foundry credentials needed!
cd python/microsoft-agents-protocol
pytest tests/integration/test_function_tools_integration.py -v
```

**What happens**:
1. Tests use MockLLMClient
2. MockLLMClient loads recordings from this directory
3. Tests run fast (~1 second vs ~5 seconds)
4. Tests cost $0 (vs ~$0.01 per run)

## Determinism

To ensure recordings are reproducible:

1. **Temperature = 0.0**: Most deterministic LLM setting
2. **Seed = 42**: Additional determinism (if supported)
3. **Fixed Function Results**: Functions use seeded random for consistency

```python
# In test setup
random.seed(42)

# LLM call
completion = await client.chat.completions.create(
    model="gpt-5-nano",
    messages=[...],
    tools=[...],
    temperature=0.0,
    seed=42
)
```

## File Management

### Storage

- Each test case generates 2-10 recordings (depending on function calls)
- Average size: ~1-2 KB per recording
- Total for 10 test cases: ~20-40 KB

### Version Control

- ✅ **Commit recordings** to git
- ✅ Part of repository, ensures tests work everywhere
- ✅ Small file sizes (KB, not MB)

### Cleanup

If recordings accumulate, clean up old ones:

```bash
# Remove recordings for specific hash
rm test-data/llm-recordings/function-tools/a1b2c3d4.*

# Remove all recordings (will need to regenerate)
rm test-data/llm-recordings/function-tools/*.json
```

## Troubleshooting

### Error: "No recorded LLM response found"

**Problem**: Test is looking for a recording that doesn't exist

**Solutions**:
1. Run tests in generation mode first: `TEST_MODE=generate pytest ...`
2. Check if request parameters changed (different hash)
3. Verify recordings directory exists and has files

### Different Results Each Time

**Problem**: Same input produces different hashes

**Solutions**:
1. Ensure temperature=0.0 in all LLM calls
2. Set seed=42 for additional determinism
3. Check that messages array order is consistent

### Recordings Too Large

**Problem**: Recording files are unexpectedly large

**Solutions**:
1. Check if verbose content is being recorded
2. Limit message history in recordings
3. Consider compressing old recordings

## Model Version

Current recordings are for:
- **Model**: gpt-5-nano
- **Endpoint**: Microsoft Foundry (Azure OpenAI)
- **Date**: 2026-02-07
- **Version**: Initial generation

When regenerating, update this section with new model information.

## Related Documentation

- [LLM Testing Strategy](../../.workspace/llm-testing-strategy.md)
- [Implementation Plan](../../.workspace/llm-testing-implementation-plan.md)
- [Test Input Files](../input/function-tools-README.md)
- [Golden Files](../results/function-tools/README.md)
