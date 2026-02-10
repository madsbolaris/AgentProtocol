using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Publishes out-of-band messages to threads from background services, webhooks, or scheduled tasks.
/// Messages are enqueued for processing, ensuring horizontal scalability.
/// </summary>
public interface IOutOfBandPublisher
{
    /// <summary>
    /// Sends a message to a thread from outside the normal request/response flow.
    /// </summary>
    /// <param name="threadId">The thread ID to send to.</param>
    /// <param name="content">The content to send.</param>
    /// <param name="runId">Optional run ID if associated with a specific run.</param>
    /// <param name="idempotencyKey">Idempotency key to prevent duplicate sends.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>A task representing the async operation.</returns>
    Task SendToThreadAsync(
        string threadId,
        AIContent content,
        string? runId = null,
        string? idempotencyKey = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a text message to a thread from outside the normal request/response flow.
    /// </summary>
    /// <param name="threadId">The thread ID to send to.</param>
    /// <param name="text">The text to send.</param>
    /// <param name="runId">Optional run ID if associated with a specific run.</param>
    /// <param name="idempotencyKey">Idempotency key to prevent duplicate sends.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>A task representing the async operation.</returns>
    Task SendToThreadAsync(
        string threadId,
        string text,
        string? runId = null,
        string? idempotencyKey = null,
        CancellationToken cancellationToken = default);
}
