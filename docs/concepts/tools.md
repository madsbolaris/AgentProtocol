# Tools

**Tools** (also called functions) extend agent capabilities by allowing them to perform actions, access data, and interact with external systems.

## What are Tools?

Tools are functions that agents can call during execution. When an agent needs to:
- Get current information (weather, stock prices, etc.)
- Perform calculations
- Access databases
- Send messages
- Control systems

...it uses tools.

## How Tools Work

### 1. Define Tool
Specify what the tool does and its parameters:

```typescript
{
  name: "get_weather",
  description: "Get current weather for a location",
  parameters: {
    location: "string",
    units: "celsius | fahrenheit"
  }
}
```

### 2. Agent Decides to Use Tool
During execution, agent determines a tool is needed:

```
User: "What's the weather in Seattle?"
Agent thinks: "I need weather data, I'll use get_weather"
```

### 3. Tool Called
Agent invokes the tool with parameters:

```json
{
  "name": "get_weather",
  "arguments": {
    "location": "Seattle",
    "units": "fahrenheit"
  }
}
```

### 4. Tool Executes
Your code runs and returns result:

```javascript
function get_weather(location, units) {
  const data = fetch_weather_api(location);
  return convert_units(data, units);
}
// Returns: {temp: 72, condition: "sunny"}
```

### 5. Agent Uses Result
Agent incorporates tool output into response:

```
Agent: "The weather in Seattle is 72°F and sunny."
```

## Tool Definition

### Required Properties

**name** - Unique identifier
```
"get_weather"
```

**description** - What the tool does (used by agent to decide when to call)
```
"Get current weather conditions for any location worldwide"
```

**parameters** - JSON schema describing inputs
```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "string",
      "description": "City name or coordinates"
    },
    "units": {
      "type": "string",
      "enum": ["celsius", "fahrenheit"]
    }
  },
  "required": ["location"]
}
```

### Optional Properties

**strict** - Enforce parameter schema strictly
**response_format** - Expected output format

## Tool Patterns

### Information Retrieval
```
get_weather(location)
search_web(query)
lookup_database(id)
```

### Actions
```
send_email(to, subject, body)
create_ticket(title, description)
schedule_meeting(attendees, time)
```

### Calculations
```
calculate(expression)
convert_currency(amount, from, to)
analyze_data(dataset)
```

### External APIs
```
call_api(endpoint, params)
check_inventory(product_id)
get_user_info(user_id)
```

## Tool Execution Modes

### Automatic
Agent calls tools automatically during execution:

```
User: "What's the weather?"
→ Agent automatically calls get_weather()
→ Agent responds with result
```

### Requires Action
Agent requests permission before calling tools:

```
User: "Send email to boss"
→ Agent asks: "Call send_email(to='boss@company.com')?"
→ User approves
→ Tool executes
```

### Manual
You execute tools explicitly:

```
User: "Check weather"
→ You call get_weather()
→ You pass result to agent
→ Agent responds
```

## Tool Choice Strategies

### Auto (Default)
Agent decides whether and which tools to use:
```
tool_choice: "auto"
```

### Required
Agent must use at least one tool:
```
tool_choice: "required"
```

### Specific Tool
Agent must use a specific tool:
```
tool_choice: {name: "get_weather"}
```

### None
Agent cannot use any tools:
```
tool_choice: "none"
```

## Multiple Tool Calls

Agents can call multiple tools in one turn:

### Sequential
```
User: "Compare weather in Seattle and Portland"
→ get_weather("Seattle") → 72°F
→ get_weather("Portland") → 68°F
→ "Seattle is 72°F, Portland is 68°F. Seattle is warmer."
```

### Parallel
```
User: "What's the weather and stock price?"
→ [get_weather(), get_stock_price()] executed in parallel
→ Agent combines both results
```

## Tool Results

### Success
```json
{
  "result": {
    "temperature": 72,
    "condition": "sunny"
  }
}
```

### Error
```json
{
  "error": "Location not found",
  "code": "LOCATION_NOT_FOUND"
}
```

### Partial Success
```json
{
  "result": {...},
  "warnings": ["Using cached data"]
}
```

## Related Concepts

- **[Agents](agents.md)** - Use tools to extend capabilities
- **[Runs](runs.md)** - Tool calls happen during runs
- **[Messages](messages.md)** - Tool calls and results are messages

## Best Practices

✅ **Do:**
- Write clear tool descriptions
- Define precise parameter schemas
- Handle errors gracefully
- Return structured data
- Document expected behavior
- Validate inputs

❌ **Don't:**
- Make tools too complex
- Use vague descriptions
- Return unstructured text
- Ignore error cases
- Skip input validation
- Create too many similar tools

## Tool Security

### Validation
Always validate tool inputs:
```javascript
function send_email(to, subject, body) {
  if (!is_valid_email(to)) {
    throw new Error("Invalid email");
  }
  // ...
}
```

### Authorization
Check permissions before executing:
```javascript
function delete_file(path) {
  if (!user.can_delete(path)) {
    throw new Error("Unauthorized");
  }
  // ...
}
```

### Rate Limiting
Prevent abuse:
```javascript
function expensive_api_call(params) {
  if (rate_limit_exceeded()) {
    throw new Error("Too many requests");
  }
  // ...
}
```

## Tool Examples

See complete tool examples in:
- [Client SDK](../products/client-sdk/examples.md)
- [Hosting SDK](../products/hosting-sdk/examples.md)

## Next Steps

- Learn about [Agents](agents.md) that use tools
- Understand [Runs](runs.md) where tools execute
- Explore SDK examples for tool implementations
