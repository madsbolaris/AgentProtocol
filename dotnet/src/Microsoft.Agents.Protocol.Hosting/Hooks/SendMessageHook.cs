namespace Microsoft.Agents.Protocol.Hosting.Hooks;

/// <summary>
/// Send message hook that delivers notifications.
/// Used for alerts, webhooks, integrations.
/// </summary>
public class SendMessageHook : ProtocolHook
{
    /// <summary>
    /// Delivery channel (e.g., "webhook", "email", "slack", "teams")
    /// </summary>
    public string Channel { get; set; } = "webhook";

    /// <summary>
    /// Destination address (URL, email, channel ID, etc.)
    /// </summary>
    public string Destination { get; set; } = string.Empty;

    /// <summary>
    /// Message template
    /// </summary>
    public string Template { get; set; } = string.Empty;

    /// <summary>
    /// Configuration for the channel
    /// </summary>
    public Dictionary<string, object> Configuration { get; set; } = new();

    /// <summary>
    /// Whether to block the run if sending fails
    /// </summary>
    public bool BlockOnFailure { get; set; } = false;
}
