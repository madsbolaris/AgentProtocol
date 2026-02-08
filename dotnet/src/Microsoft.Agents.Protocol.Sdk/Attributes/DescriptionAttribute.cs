namespace Microsoft.Agents.Protocol.Sdk.Attributes;

/// <summary>
/// Provides a description for a tool parameter or property.
/// Used to generate JSON schema and help the LLM understand what the parameter is for.
/// </summary>
/// <example>
/// <code>
/// [Tool("Get weather")]
/// public async Task&lt;WeatherResult&gt; GetWeather(
///     [Description("City name or zip code")] string location,
///     [Description("Temperature units: celsius or fahrenheit")] string units = "fahrenheit")
/// {
///     // ...
/// }
/// </code>
/// </example>
[AttributeUsage(AttributeTargets.Parameter | AttributeTargets.Property, AllowMultiple = false, Inherited = true)]
public class DescriptionAttribute : Attribute
{
    /// <summary>
    /// Description of what this parameter or property represents
    /// </summary>
    public string Description { get; }

    /// <summary>
    /// Provides a description for a parameter or property.
    /// </summary>
    /// <param name="description">Clear description of what this represents</param>
    public DescriptionAttribute(string description)
    {
        if (string.IsNullOrWhiteSpace(description))
        {
            throw new ArgumentException("Description cannot be empty", nameof(description));
        }

        Description = description;
    }
}
