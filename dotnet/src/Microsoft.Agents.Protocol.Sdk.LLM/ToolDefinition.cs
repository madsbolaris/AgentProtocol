using System.Text.Json;

namespace Microsoft.Agents.Protocol.Sdk.LLM;

/// <summary>
/// Defines a tool/function that can be called by the LLM.
/// Uses Agent Protocol native format.
/// </summary>
public class ToolDefinition
{
    /// <summary>
    /// The type of tool (default: "function").
    /// </summary>
    public string Type { get; set; } = "function";

    /// <summary>
    /// The function definition.
    /// </summary>
    public required FunctionDefinition Function { get; set; }
}

/// <summary>
/// Definition of a function that can be called.
/// </summary>
public class FunctionDefinition
{
    /// <summary>
    /// The name of the function.
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// Description of what the function does.
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// JSON Schema describing the function parameters.
    /// </summary>
    public JsonElement? Parameters { get; set; }
}
