using System.Reflection;
using System.Text.Json;

namespace Microsoft.Agents.Protocol.Client;

/// <summary>
/// Collection of tools (functions) that can be called by the agent.
/// Supports lambda functions with automatic schema generation.
/// </summary>
public class ToolCollection : IEnumerable<ToolDefinition>
{
    private readonly Dictionary<string, ToolDefinition> _tools = new();

    /// <summary>
    /// Adds a tool using collection initializer syntax.
    /// </summary>
    public void Add(string name, Func<string, string> handler)
    {
        Add(name, (Delegate)handler);
    }

    public void Add(string name, Func<string, Task<string>> handler)
    {
        Add(name, (Delegate)handler);
    }

    public void Add(string name, Func<string, string, string> handler)
    {
        Add(name, (Delegate)handler);
    }

    public void Add(string name, Func<double, double, string, double> handler)
    {
        Add(name, (Delegate)handler);
    }

    // Add more overloads as needed for common signatures

    public IEnumerator<ToolDefinition> GetEnumerator()
    {
        return _tools.Values.GetEnumerator();
    }

    System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator()
    {
        return GetEnumerator();
    }

    /// <summary>
    /// Adds a tool with a synchronous function.
    /// </summary>
    public void Add(string name, Delegate handler, string? description = null)
    {
        var tool = new ToolDefinition
        {
            Name = name,
            Description = description ?? $"Executes {name}",
            Handler = handler,
            Schema = GenerateSchema(handler)
        };
        _tools[name] = tool;
    }

    /// <summary>
    /// Gets a tool by name.
    /// </summary>
    public ToolDefinition? Get(string name)
    {
        return _tools.TryGetValue(name, out var tool) ? tool : null;
    }

    /// <summary>
    /// Gets all tool definitions.
    /// </summary>
    public IEnumerable<ToolDefinition> GetAll()
    {
        return _tools.Values;
    }

    /// <summary>
    /// Executes a tool by name with JSON arguments.
    /// </summary>
    public async Task<object> ExecuteAsync(string toolName, string argumentsJson)
    {
        var tool = Get(toolName);
        if (tool == null)
            throw new InvalidOperationException($"Tool '{toolName}' not found");

        return await tool.ExecuteAsync(argumentsJson);
    }

    /// <summary>
    /// Generates JSON schema from delegate parameters.
    /// </summary>
    private static object GenerateSchema(Delegate handler)
    {
        var method = handler.Method;
        var parameters = method.GetParameters();

        var properties = new Dictionary<string, object>();
        var required = new List<string>();

        foreach (var param in parameters)
        {
            properties[param.Name!] = new
            {
                type = GetJsonType(param.ParameterType),
                description = $"Parameter {param.Name}"
            };

            if (!param.IsOptional)
            {
                required.Add(param.Name!);
            }
        }

        return new
        {
            type = "object",
            properties,
            required
        };
    }

    private static string GetJsonType(Type type)
    {
        if (type == typeof(string)) return "string";
        if (type == typeof(int) || type == typeof(long)) return "integer";
        if (type == typeof(double) || type == typeof(float)) return "number";
        if (type == typeof(bool)) return "boolean";
        return "string"; // Default
    }
}

/// <summary>
/// Represents a single tool definition.
/// </summary>
public class ToolDefinition
{
    public required string Name { get; set; }
    public required string Description { get; set; }
    public required object Schema { get; set; }
    public required Delegate Handler { get; set; }

    /// <summary>
    /// Executes the tool with JSON arguments.
    /// </summary>
    public async Task<object> ExecuteAsync(string argumentsJson)
    {
        var method = Handler.Method;
        var parameters = method.GetParameters();

        // Parse JSON to extract arguments
        var jsonDoc = JsonDocument.Parse(argumentsJson);
        var args = new object?[parameters.Length];

        for (int i = 0; i < parameters.Length; i++)
        {
            var param = parameters[i];
            if (jsonDoc.RootElement.TryGetProperty(param.Name!, out var value))
            {
                args[i] = JsonSerializer.Deserialize(value.GetRawText(), param.ParameterType);
            }
            else if (param.IsOptional)
            {
                args[i] = param.DefaultValue;
            }
            else
            {
                throw new ArgumentException($"Missing required parameter: {param.Name}");
            }
        }

        // Invoke the handler
        var result = Handler.DynamicInvoke(args);

        // Handle async results
        if (result is Task task)
        {
            await task;
            var resultProperty = task.GetType().GetProperty("Result");
            return resultProperty?.GetValue(task) ?? string.Empty;
        }

        return result ?? string.Empty;
    }
}
