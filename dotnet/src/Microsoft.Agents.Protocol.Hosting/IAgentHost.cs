using System.Threading;
using System.Threading.Tasks;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Interface for the agent host lifecycle and message processing.
/// </summary>
public interface IAgentHost
{
    /// <summary>
    /// Starts the agent host server.
    /// </summary>
    /// <param name="port">Optional port number (default: 3000).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task StartAsync(int port = 3000, CancellationToken cancellationToken = default);

    /// <summary>
    /// Stops the agent host server.
    /// </summary>
    /// <param name="options">Optional stop options.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task StopAsync(StopOptions? options = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Checks the health of the agent host and its subsystems.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Health check response.</returns>
    Task<HealthCheck> CheckHealthAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the out-of-band publisher for sending messages.
    /// </summary>
    /// <returns>The publisher instance.</returns>
    IOutOfBandPublisher GetPublisher();

    /// <summary>
    /// Processes a message directly (bypasses HTTP).
    /// </summary>
    /// <param name="message">The message text.</param>
    /// <param name="threadId">Optional thread ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The response.</returns>
    Task<MessageResponse> ProcessMessageAsync(
        string message,
        string? threadId = null,
        CancellationToken cancellationToken = default);
}
