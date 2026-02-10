namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Options for stopping the agent host.
/// </summary>
public class StopOptions
{
    /// <summary>
    /// Grace period in milliseconds to wait for active runs to complete.
    /// </summary>
    public int GracePeriodMs { get; set; } = 30000;

    /// <summary>
    /// Whether to finish queued tasks before stopping.
    /// </summary>
    public bool FinishQueued { get; set; } = false;
}
