namespace Microsoft.Agents.Protocol.Hosting.Hooks;

/// <summary>
/// Block hook that prevents execution based on conditions.
/// Used for guardrails, safety, policy enforcement.
/// </summary>
public class BlockHook : ProtocolHook
{
    /// <summary>
    /// Message to return when blocked
    /// </summary>
    public string Message { get; set; } = "This action is not allowed.";

    /// <summary>
    /// Error code to return when blocked
    /// </summary>
    public string? ErrorCode { get; set; }

    /// <summary>
    /// Whether to log the blocked attempt
    /// </summary>
    public bool LogBlocked { get; set; } = true;
}
