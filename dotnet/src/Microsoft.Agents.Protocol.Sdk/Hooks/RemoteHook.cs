namespace Microsoft.Agents.Protocol.Sdk.Hooks;

/// <summary>
/// Remote hook that calls an external HTTP endpoint.
/// Used for content moderation, approval workflows, logging, etc.
/// </summary>
public class RemoteHook : ProtocolHook
{
    /// <summary>
    /// HTTP endpoint to call
    /// </summary>
    public string Endpoint { get; set; } = string.Empty;

    /// <summary>
    /// HTTP method (default: POST)
    /// </summary>
    public string Method { get; set; } = "POST";

    /// <summary>
    /// Authentication headers
    /// </summary>
    public Dictionary<string, string> Headers { get; set; } = new();

    /// <summary>
    /// Timeout for the HTTP call
    /// </summary>
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);

    /// <summary>
    /// Whether to block the run if the hook fails
    /// </summary>
    public bool BlockOnFailure { get; set; } = true;

    /// <summary>
    /// Maximum number of retry attempts
    /// </summary>
    public int MaxRetries { get; set; } = 3;
}
