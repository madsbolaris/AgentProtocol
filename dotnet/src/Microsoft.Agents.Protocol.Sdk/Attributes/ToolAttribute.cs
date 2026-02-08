namespace Microsoft.Agents.Protocol.Sdk.Attributes;

/// <summary>
/// Marks a method as an agent tool that can be called by the LLM.
/// The SDK automatically discovers these methods via reflection and registers them.
/// </summary>
/// <example>
/// <code>
/// [Tool("Get current weather for a location")]
/// public async Task&lt;WeatherResult&gt; GetWeather(string location)
/// {
///     return await _weatherService.GetWeatherAsync(location);
/// }
/// </code>
/// </example>
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = true)]
public class ToolAttribute : Attribute
{
    /// <summary>
    /// Description of what this tool does. This is shown to the LLM to help it decide when to use the tool.
    /// </summary>
    public string Description { get; }

    /// <summary>
    /// Optional: Override the tool name (defaults to method name in snake_case)
    /// </summary>
    public string? Name { get; set; }

    /// <summary>
    /// Marks a method as an agent tool.
    /// </summary>
    /// <param name="description">Clear description of what this tool does</param>
    public ToolAttribute(string description)
    {
        if (string.IsNullOrWhiteSpace(description))
        {
            throw new ArgumentException("Tool description cannot be empty", nameof(description));
        }

        Description = description;
    }
}
