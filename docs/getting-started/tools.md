# Tool Execution Guide

**Learn how agents can call your functions to gather information and complete tasks.**

This guide shows you how to equip agents with tools (like weather APIs, databases, calculators, etc.) and handle their execution in a request-response loop.

---

!!! example "Real-World Example: Tools in Action"

    Tools enable agents to interact with external systems. When an agent needs information it doesn't have (like current weather, database records, or API data), it can call tools you provide. You execute those tools and return the results, allowing the agent to complete its task.

---

## Quick Overview

The tool execution flow works like this:

1. **Define Tools**: Specify available functions with schemas
2. **Agent Requests**: Agent returns `requires_action` status with tool calls
3. **Execute Tools**: Run the requested functions in your code
4. **Submit Results**: Send outputs back to continue the run
5. **Agent Completes**: Agent uses results to formulate final response

---

## Creating an Agent with Tools

Define tools using JSON Schema to describe their parameters.

**Python:**
```python
import json
from datetime import datetime
from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

client = AgentProtocolClient(AgentProtocolClientOptions(
    base_url="https://agents.example.com/v1",
    api_key="your-api-key"
))

def create_agent_with_tools():
    """Create agent with weather and time tools"""
    return {
        "name": "ToolAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant with access to weather and time information.",
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_current_time",
                "description": "Get current time in a timezone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., America/New_York)"
                        }
                    },
                    "required": ["timezone"]
                }
            }
        ]
    }
```

---

## Implementing Tool Functions

Create the actual implementations that will be called when the agent requests them.

**Python:**
```python
# Mock tool implementations
def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute tool and return result"""
    if tool_name == "get_weather":
        location = arguments['location']
        unit = arguments.get('unit', 'celsius')
        # Mock response (replace with real API call)
        return f"The weather in {location} is 22°{unit[0].upper()}, partly cloudy."

    elif tool_name == "get_current_time":
        timezone = arguments['timezone']
        # Mock response (replace with real time lookup)
        return f"Current time in {timezone}: {datetime.now().strftime('%H:%M:%S')}"

    return "Tool not found"
```

!!! tip "Real-World Implementation"

    In production, replace the mock responses with actual API calls, database queries, or other operations. The agent doesn't care how you implement the tools - it just needs the string results.

---

## Running with Tools

Execute a run and handle the tool calling loop.

**Python:**
```python
async def run_with_tools(prompt: str):
    """Execute run with tool calling"""
    agent = create_agent_with_tools()

    async with client:
        # Initial run
        result = await client.runs.create({
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "threadCleanup": "delete"
        })

        run_id = result['runId']

        # Handle tool calls
        while result['status'] == 'requires_action':
            print(f"Status: {result['status']}")

            # Extract tool calls
            tool_calls = [
                content for content in result['output'][0]['contents']
                if content['kind'] == 'functionCall'
            ]

            print(f"Agent requested {len(tool_calls)} tool(s):")
            for call in tool_calls:
                print(f"  - {call['name']}({call['arguments']})")

            # Execute tools
            tool_outputs = []
            for call in tool_calls:
                arguments = json.loads(call['arguments']) if isinstance(call['arguments'], str) else call['arguments']
                result_text = execute_tool(call['name'], arguments)
                print(f"  → Result: {result_text}")

                tool_outputs.append({
                    "tool_call_id": call['callId'],
                    "output": result_text
                })

            # Submit tool results
            result = await client.runs.submit_tool_outputs(
                run_id,
                {"tool_outputs": tool_outputs}
            )

        # Final response
        if result['status'] == 'completed':
            final_text = result['output'][-1]['contents'][0]['text']
            print(f"\nFinal response: {final_text}")
            return final_text
        else:
            raise Exception(f"Run failed: {result.get('error')}")
```

---

## Example Usage

### Single Tool Call

**Python:**
```python
print("=== Example 1: Single Tool ===")
await run_with_tools("What's the weather in Paris?")
```

**Output:**
```
=== Example 1: Single Tool ===
Status: requires_action
Agent requested 1 tool(s):
  - get_weather({"location": "Paris", "unit": "celsius"})
  → Result: The weather in Paris is 22°C, partly cloudy.

Final response: The weather in Paris is currently 22°C and partly cloudy.
```

### Multiple Tool Calls

**Python:**
```python
print("\n=== Example 2: Multiple Tools ===")
await run_with_tools("What's the weather in Tokyo and what time is it there?")
```

**Output:**
```
=== Example 2: Multiple Tools ===
Status: requires_action
Agent requested 2 tool(s):
  - get_weather({"location": "Tokyo", "unit": "celsius"})
  → Result: The weather in Tokyo is 22°C, partly cloudy.
  - get_current_time({"timezone": "Asia/Tokyo"})
  → Result: Current time in Asia/Tokyo: 14:30:00

Final response: In Tokyo, it's currently 22°C and partly cloudy. The local time is 14:30.
```

---

## Key Concepts

### Tool Call Structure

When an agent wants to call a tool, the response contains:

```python
{
    "status": "requires_action",
    "output": [{
        "role": "assistant",
        "contents": [
            {
                "kind": "functionCall",
                "name": "get_weather",
                "callId": "call_abc123",
                "arguments": {"location": "Paris", "unit": "celsius"}
            }
        ]
    }]
}
```

### Tool Output Structure

You must provide results that match the `callId`:

```python
{
    "tool_outputs": [
        {
            "tool_call_id": "call_abc123",  # Must match callId from tool call
            "output": "The weather in Paris is 22°C, partly cloudy."
        }
    ]
}
```

!!! danger "Critical: Match Tool Call IDs"

    The `tool_call_id` in your response **must exactly match** the `callId` from the agent's tool call. Mismatched IDs will cause the run to fail.

---

## Best Practices

### 1. Handle All Tool Calls

Always execute and return results for **every** tool call:

```python
# Ensure all tool calls have results
tool_calls = [c for c in output['contents'] if c['kind'] == 'functionCall']
tool_outputs = []

for call in tool_calls:
    tool_outputs.append({
        "tool_call_id": call['callId'],
        "output": execute_tool(call['name'], call['arguments'])
    })

# Verify all IDs are provided
call_ids = {c['callId'] for c in tool_calls}
output_ids = {o['tool_call_id'] for o in tool_outputs}
assert call_ids == output_ids, f"Missing results for: {call_ids - output_ids}"
```

### 2. Handle Errors Gracefully

Return error messages as strings when tools fail:

```python
def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute tool with error handling"""
    try:
        if tool_name == "get_weather":
            location = arguments['location']
            # Call weather API
            weather_data = fetch_weather_api(location)
            return f"Weather in {location}: {weather_data['temp']}°C, {weather_data['conditions']}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
```

### 3. Validate Arguments

Check required parameters before execution:

```python
def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute tool with validation"""
    if tool_name == "get_weather":
        if 'location' not in arguments:
            return "Error: location parameter is required"

        location = arguments['location']
        unit = arguments.get('unit', 'celsius')

        # Execute tool
        return fetch_weather(location, unit)
```

### 4. Keep Tool Descriptions Clear

Write descriptions that help the agent understand when and how to use each tool:

```python
{
    "name": "search_database",
    "description": "Search the customer database by email, phone, or customer ID. Returns customer record with order history.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Email address, phone number, or customer ID to search for"
            },
            "include_orders": {
                "type": "boolean",
                "description": "Whether to include order history (default: true)",
                "default": True
            }
        },
        "required": ["query"]
    }
}
```

---

## Common Patterns

### Pattern 1: Database Tools

```python
def create_database_agent():
    """Agent with database query tools"""
    return {
        "name": "DatabaseAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You help users query and analyze database records.",
        "tools": [
            {
                "name": "query_customers",
                "description": "Search customers by email, name, or ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {"type": "string"},
                        "limit": {"type": "number", "default": 10}
                    },
                    "required": ["search_term"]
                }
            },
            {
                "name": "get_order_history",
                "description": "Get order history for a customer ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"}
                    },
                    "required": ["customer_id"]
                }
            }
        ]
    }
```

### Pattern 2: API Integration Tools

```python
def create_api_agent():
    """Agent with external API tools"""
    return {
        "name": "APIAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You help users interact with external services.",
        "tools": [
            {
                "name": "send_email",
                "description": "Send an email via SendGrid API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "create_ticket",
                "description": "Create a support ticket in Zendesk",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"]
                        }
                    },
                    "required": ["title", "description"]
                }
            }
        ]
    }
```

### Pattern 3: Calculation Tools

```python
def create_calculator_agent():
    """Agent with computation tools"""
    return {
        "name": "CalculatorAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You help with mathematical calculations and data analysis.",
        "tools": [
            {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Math expression to evaluate (e.g., '2 + 2', 'sqrt(16)')"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "statistics",
                "description": "Calculate statistics (mean, median, std dev) for a dataset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numbers": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Array of numbers to analyze"
                        }
                    },
                    "required": ["numbers"]
                }
            }
        ]
    }
```

---

## Troubleshooting

### Issue: Tool Results Not Accepted

**Problem**: `submit_tool_outputs` returns an error

**Solution**: Ensure `tool_call_id` exactly matches the `callId` from the tool call:

```python
# Extract tool calls
tool_calls = [c for c in output['contents'] if c['kind'] == 'functionCall']

# Build outputs with matching IDs
tool_outputs = []
for call in tool_calls:
    tool_outputs.append({
        "tool_call_id": call['callId'],  # Must match exactly
        "output": execute_tool(call['name'], call['arguments'])
    })

# Verify
call_ids = {c['callId'] for c in tool_calls}
output_ids = {o['tool_call_id'] for o in tool_outputs}
if call_ids != output_ids:
    raise ValueError(f"Missing results for: {call_ids - output_ids}")
```

### Issue: Infinite Tool Loop

**Problem**: Agent keeps requesting the same tool

**Solution**: Ensure your tool returns useful information:

```python
# Bad: Too vague
return "Success"

# Good: Specific result
return "Weather in Paris: 22°C, partly cloudy with 60% humidity"

# Best: Structured result
return json.dumps({
    "temperature": 22,
    "unit": "celsius",
    "conditions": "partly cloudy",
    "humidity": 60,
    "wind_speed": 15
})
```

### Issue: Tool Argument Parsing Fails

**Problem**: Agent sends invalid arguments

**Solution**: Validate and provide clear error messages:

```python
def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute tool with argument validation"""
    if tool_name == "get_weather":
        # Validate required fields
        if 'location' not in arguments:
            return "Error: 'location' parameter is required"

        location = arguments['location']

        # Validate optional fields
        unit = arguments.get('unit', 'celsius')
        if unit not in ['celsius', 'fahrenheit']:
            return f"Error: 'unit' must be 'celsius' or 'fahrenheit', got '{unit}'"

        # Execute
        return fetch_weather(location, unit)
```

---

## Next Steps

Now that you understand tool execution, explore these advanced topics:

<div class="grid cards" markdown>

-   :material-speedometer:{ .lg .middle } **5-Minute Quickstart**

    Get your first agent running quickly with basic operations.

    [:octicons-arrow-right-24: Quickstart](quickstart.md)

-   :material-flask:{ .lg .middle } **Practical Examples**

    See real-world examples including image analysis and batch processing.

    [:octicons-arrow-right-24: Examples](examples.md)

-   :material-rocket-launch:{ .lg .middle } **Advanced Patterns**

    Master ephemeral runs, background execution, and stream reconnection.

    [:octicons-arrow-right-24: Advanced Patterns](advanced-patterns.md)

</div>

---

## Related Documentation

- **[Tool Execution Specification](../specifications/tool-execution.md)** - Technical details of tool execution flow
- **[API Reference: Runs](../api-reference/runs.md)** - Complete runs endpoint documentation
- **[Getting Started Guide](index.md)** - Full getting started walkthrough
- **[Human-in-Loop Guide](human-in-loop.md)** - Add approval workflows for tool execution

---

**Need Help?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/madsbolaris/AgentProtocol/issues).
