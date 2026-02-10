# Tool Execution

Tools allow agents to take actions and retrieve information by calling functions you define. The SDK handles registration, parameter validation, and result formatting.

## What Are Tools?

**Tools** are functions that extend an agent's capabilities beyond text generation:

- **Retrieval**: Search databases, APIs, or documents
- **Actions**: Send emails, create tickets, update records
- **Computation**: Perform calculations, data analysis
- **Integration**: Connect to external services

## Basic Tool Usage

=== "Python"
    ```python
    from microsoft.agents.protocol import AgentProtocolClient, ToolCollection

    # Define a tool function
    def get_weather(location: str) -> str:
        """Get current weather for a location."""
        # In production, call a real weather API
        return f"Weather in {location}: 72°F, sunny"

    # Register tools
    tools = ToolCollection()
    tools.add("get_weather", get_weather)

    # Use tools with client
    client = AgentProtocolClient("http://localhost:3978")
    response = await client.complete_chat(
        "What's the weather in Seattle?",
        tools=tools
    )
    print(response)
    ```

=== "TypeScript"
    ```typescript
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol';

    // Define a tool function
    function getWeather(location: string): string {
        // In production, call a real weather API
        return `Weather in ${location}: 72°F, sunny`;
    }

    // Register tools
    const tools = new ToolCollection();
    tools.add("get_weather", getWeather);

    // Use tools with client
    const client = new AgentProtocolClient("http://localhost:3978");
    const response = await client.completeChat(
        "What's the weather in Seattle?",
        { tools }
    );
    console.log(response);
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol.Client;

    // Define a tool function
    string GetWeather(string location)
    {
        // In production, call a real weather API
        return $"Weather in {location}: 72°F, sunny";
    }

    // Register tools
    var tools = new ToolCollection
    {
        ["get_weather"] = (string location) => GetWeather(location)
    };

    // Use tools with client
    using var client = new AgentProtocolClient("http://localhost:3978");
    var response = await client.CompleteChatAsync(
        "What's the weather in Seattle?",
        tools: tools
    );
    Console.WriteLine(response);
    ```

## Tool Registration

### Method 1: ToolCollection (Recommended)

=== "Python"
    ```python
    tools = ToolCollection()

    # Simple function
    tools.add("get_time", lambda: datetime.now().isoformat())

    # Function with parameters
    tools.add("calculate", lambda x, y, op: eval(f"{x}{op}{y}"))

    # Async function
    async def search_docs(query: str) -> list:
        results = await search_api(query)
        return results

    tools.add("search_docs", search_docs)
    ```

=== "TypeScript"
    ```typescript
    const tools = new ToolCollection();

    // Simple function
    tools.add("get_time", () => new Date().toISOString());

    // Function with parameters
    tools.add("calculate", (x: number, y: number, op: string) => {
        return eval(`${x}${op}${y}`);
    });

    // Async function
    tools.add("search_docs", async (query: string) => {
        const results = await searchApi(query);
        return results;
    });
    ```

=== "C#"
    ```csharp
    var tools = new ToolCollection
    {
        // Simple function
        ["get_time"] = () => DateTime.Now.ToString("O"),

        // Function with parameters
        ["calculate"] = (int x, int y, string op) => op switch
        {
            "+" => x + y,
            "-" => x - y,
            "*" => x * y,
            "/" => x / y,
            _ => throw new ArgumentException("Invalid operator")
        },

        // Async function
        ["search_docs"] = async (string query) =>
        {
            var results = await SearchApiAsync(query);
            return results;
        }
    };
    ```

## Secure Tool Implementation

### Input Validation

**Always validate tool parameters:**

=== "Python"
    ```python
    import re

    def get_weather(location: str) -> str:
        # Validate input format
        if not re.match(r'^[a-zA-Z\s,]+$', location):
            raise ValueError("Invalid location format")

        # Validate length
        if len(location) > 100:
            raise ValueError("Location name too long")

        # Validate against allowlist (if applicable)
        allowed_cities = ["Seattle", "Portland", "San Francisco"]
        if location not in allowed_cities:
            raise ValueError(f"Weather unavailable for {location}")

        return f"Weather in {location}: 72°F, sunny"
    ```

=== "TypeScript"
    ```typescript
    function getWeather(location: string): string {
        // Validate input format
        if (!/^[a-zA-Z\s,]+$/.test(location)) {
            throw new Error("Invalid location format");
        }

        // Validate length
        if (location.length > 100) {
            throw new Error("Location name too long");
        }

        // Validate against allowlist
        const allowedCities = ["Seattle", "Portland", "San Francisco"];
        if (!allowedCities.includes(location)) {
            throw new Error(`Weather unavailable for ${location}`);
        }

        return `Weather in ${location}: 72°F, sunny`;
    }
    ```

=== "C#"
    ```csharp
    string GetWeather(string location)
    {
        // Validate input format
        if (!Regex.IsMatch(location, @"^[a-zA-Z\s,]+$"))
            throw new ArgumentException("Invalid location format");

        // Validate length
        if (location.Length > 100)
            throw new ArgumentException("Location name too long");

        // Validate against allowlist
        var allowedCities = new[] { "Seattle", "Portland", "San Francisco" };
        if (!allowedCities.Contains(location))
            throw new ArgumentException($"Weather unavailable for {location}");

        return $"Weather in {location}: 72°F, sunny";
    }
    ```

### Parameter Sanitization

=== "Python"
    ```python
    from html import escape
    from pathlib import Path

    def safe_tool(user_input: str, file_path: str) -> str:
        # Sanitize text input
        safe_text = escape(user_input)

        # Sanitize file paths
        safe_path = Path(file_path).resolve()
        allowed_dir = Path("/allowed/directory").resolve()

        if not safe_path.is_relative_to(allowed_dir):
            raise ValueError("Path outside allowed directory")

        return f"Processed: {safe_text}"
    ```

## Tool Error Handling

Handle tool errors gracefully:

=== "Python"
    ```python
    def robust_tool(query: str) -> str:
        try:
            result = call_external_api(query)
            return result
        except ConnectionError:
            return "Error: Unable to connect to service"
        except TimeoutError:
            return "Error: Request timed out"
        except Exception as e:
            # Log error but don't expose internals
            logger.error(f"Tool error: {e}")
            return "Error: Unable to process request"
    ```

## Advanced Patterns

### Tool Chaining

Tools can call other tools:

=== "Python"
    ```python
    async def weather_advice(location: str) -> str:
        # Call weather tool
        weather = await tools.execute("get_weather", location=location)

        # Call advice tool based on weather
        advice = await tools.execute("get_clothing_advice", weather=weather)

        return f"{weather}. {advice}"

    tools.add("weather_advice", weather_advice)
    ```

### Conditional Tools

Enable tools based on context:

=== "Python"
    ```python
    def get_tools_for_user(user_role: str) -> ToolCollection:
        tools = ToolCollection()

        # Everyone gets basic tools
        tools.add("search", search_function)

        # Admins get additional tools
        if user_role == "admin":
            tools.add("delete", delete_function)
            tools.add("modify", modify_function)

        return tools
    ```

## Best Practices

### Do:
- ✅ Validate all tool inputs
- ✅ Use allowlists instead of denylists
- ✅ Implement timeouts for external calls
- ✅ Log tool executions for debugging
- ✅ Return structured data when possible
- ✅ Handle errors gracefully

### Don't:
- ❌ Execute arbitrary code from tool parameters
- ❌ Expose internal errors to users
- ❌ Allow file system access without validation
- ❌ Skip input validation "just this once"
- ❌ Return sensitive data (passwords, keys)

## Testing Tools

Test tools independently:

=== "Python"
    ```python
    import pytest

    def test_get_weather():
        result = get_weather("Seattle")
        assert "Seattle" in result
        assert "°F" in result

    def test_get_weather_invalid_input():
        with pytest.raises(ValueError):
            get_weather("'; DROP TABLE users;--")

    def test_get_weather_long_input():
        with pytest.raises(ValueError):
            get_weather("x" * 1000)
    ```

## Next Steps

- [Streaming](streaming.md) - Stream responses with tool calls
- [Error Handling](error-handling.md) - Handle tool errors
- [Security Best Practices](../security/index.md) - Comprehensive security guide
