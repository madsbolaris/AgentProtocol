using Microsoft.Agents;
using Microsoft.Extensions.Logging;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Context for agent turn processing with simplified API.
/// </summary>
public interface IAgentContext
{
    /// <summary>
    /// Gets the current run ID.
    /// </summary>
    string RunId { get; }

    /// <summary>
    /// Gets the current thread ID.
    /// </summary>
    string ThreadId { get; }

    /// <summary>
    /// Gets the logger for this context.
    /// </summary>
    ILogger Logger { get; }

    /// <summary>
    /// Sends a response message to the user.
    /// </summary>
    /// <param name="content">The content to send.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task RespondAsync(AIContent content, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a text response to the user.
    /// </summary>
    /// <param name="text">The text to send.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task RespondAsync(string text, CancellationToken cancellationToken = default);

    /// <summary>
    /// Logs a message (visible to debugging/observability, not sent to user).
    /// </summary>
    /// <param name="message">The message to log.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task LogAsync(string message, CancellationToken cancellationToken = default);

    /// <summary>
    /// Pauses the run and waits for approval before continuing.
    /// </summary>
    /// <param name="summary">Summary of what needs approval.</param>
    /// <param name="metadata">Optional metadata.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task PauseForApprovalAsync(
        string summary,
        object? metadata = null,
        CancellationToken cancellationToken = default);
}
