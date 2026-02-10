namespace Microsoft.Agents.Protocol.Hosting.Hooks;

/// <summary>
/// Telemetry hook for metrics, logging, and observability.
/// Used for monitoring, debugging, analytics.
/// </summary>
public class TelemetryHook : ProtocolHook
{
    /// <summary>
    /// Telemetry destination (e.g., "console", "applicationinsights", "datadog")
    /// </summary>
    public string Destination { get; set; } = "console";

    /// <summary>
    /// Configuration for the telemetry destination
    /// </summary>
    public Dictionary<string, object> Configuration { get; set; } = new();

    /// <summary>
    /// What to include in telemetry
    /// </summary>
    public TelemetryOptions Options { get; set; } = new();
}

/// <summary>
/// Options for what to include in telemetry
/// </summary>
public class TelemetryOptions
{
    /// <summary>
    /// Include message text
    /// </summary>
    public bool IncludeMessages { get; set; } = true;

    /// <summary>
    /// Include tool calls and results
    /// </summary>
    public bool IncludeTools { get; set; } = true;

    /// <summary>
    /// Include timing information
    /// </summary>
    public bool IncludeTiming { get; set; } = true;

    /// <summary>
    /// Include token usage
    /// </summary>
    public bool IncludeTokens { get; set; } = true;

    /// <summary>
    /// Include errors and failures
    /// </summary>
    public bool IncludeErrors { get; set; } = true;

    /// <summary>
    /// Include custom metadata
    /// </summary>
    public bool IncludeMetadata { get; set; } = true;
}
