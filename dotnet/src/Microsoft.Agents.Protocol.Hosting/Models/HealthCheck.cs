using System.Collections.Generic;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Health check response for the agent host.
/// </summary>
public class HealthCheck
{
    /// <summary>
    /// Overall status (healthy, degraded, unhealthy).
    /// </summary>
    public string Status { get; set; } = "unknown";

    /// <summary>
    /// Individual health checks for different subsystems.
    /// </summary>
    public Dictionary<string, bool> Checks { get; set; } = new();

    /// <summary>
    /// Uptime in milliseconds.
    /// </summary>
    public long UptimeMs { get; set; }
}
