# Function Tools Test Cases

Test input files for Basic M365 Agent with LLM function calling.

## Test Scenarios

### 50-weather-query.xml
**Purpose**: Test simple weather function call

**Input**: "What's the weather like in Seattle?"

**Expected Behavior**:
1. LLM recognizes need to call `get_weather` function
2. LLM extracts location parameter: "Seattle"
3. Agent executes `get_weather("Seattle")`
4. Returns formatted weather information

**Expected Function Calls**: 1 (get_weather)

**Expected Response**: Weather information for Seattle

---

### 51-time-query.xml
**Purpose**: Test simple time function call

**Input**: "What time is it?"

**Expected Behavior**:
1. LLM recognizes need to call `get_time` function
2. Agent executes `get_time()` (no parameters)
3. Returns current UTC time

**Expected Function Calls**: 1 (get_time)

**Expected Response**: Current UTC timestamp

---

### 52-multi-function.xml
**Purpose**: Test multiple function calls in sequence

**Input**: "What's the weather in Paris and what time is it?"

**Expected Behavior**:
1. LLM recognizes need for two functions
2. First LLM call → `get_weather("Paris")`
3. Agent executes weather function
4. Second LLM call → `get_time()`
5. Agent executes time function
6. LLM synthesizes combined response

**Expected Function Calls**: 2 (get_weather, get_time)

**Expected Response**: Both weather and time information

---

### 53-no-function.xml
**Purpose**: Test LLM direct response without function calls

**Input**: "Hello! How are you today?"

**Expected Behavior**:
1. LLM determines no function needed
2. LLM provides direct conversational response
3. No function calls made

**Expected Function Calls**: 0

**Expected Response**: Conversational greeting response

---

## Testing Strategy

### Generation Mode
Run once to create golden files and LLM recordings using the .NET bot (canonical source):

```bash
# Set Foundry credentials
export FOUNDRY_ENDPOINT=https://...
export FOUNDRY_API_KEY=...
export FOUNDRY_MODEL_DEPLOYMENT=gpt-5-nano

# Generate golden files and LLM recordings from .NET
python scripts/generate_golden_datasets.py --sample basic-m365 --record-llm
```

### Test Mode
Run frequently for fast, deterministic validation:

```bash
# No credentials needed - uses recorded LLM interactions!
SAMPLE_NAME=basic-m365 pytest python/microsoft-agents-protocol/tests/integration/test_basic_m365_integration.py -v
```

## Determinism

All test cases are designed for deterministic results:

1. **LLM Settings**:
   - temperature=0.0 (most deterministic)
   - seed=42 (additional determinism)

2. **Function Results**:
   - Weather: Seeded random based on location
   - Time: Mocked in tests or use fixed timestamp

3. **Input Messages**:
   - Clear, unambiguous requests
   - Simple language for consistent LLM interpretation

## Coverage

Test coverage matrix:

| Scenario | Function Calling | Parameters | Multi-turn | Direct Response |
|----------|-----------------|------------|------------|-----------------|
| 50-weather-query | ✅ | ✅ (location) | ❌ | ❌ |
| 51-time-query | ✅ | ❌ (none) | ❌ | ❌ |
| 52-multi-function | ✅ | ✅ (location) | ✅ | ❌ |
| 53-no-function | ❌ | ❌ | ❌ | ✅ |

## Related Files

- **Recordings**: `test-data/llm-recordings/basic-m365/`
- **Golden Files (json)**: `test-data/results/basic-m365/json/`
- **Golden Files (xml)**: `test-data/results/basic-m365/xml/`
- **Tests**: `python/microsoft-agents-protocol/tests/integration/`
