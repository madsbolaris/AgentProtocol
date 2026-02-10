using Microsoft.Agents;
using Microsoft.Extensions.Logging;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Default implementation of IOutOfBandPublisher.
/// Enqueues messages for processing by workers.
/// </summary>
internal class OutOfBandPublisher : IOutOfBandPublisher
{
    private readonly ILogger<OutOfBandPublisher> _logger;

    public OutOfBandPublisher(ILogger<OutOfBandPublisher> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task SendToThreadAsync(
        string threadId,
        AIContent content,
        string? runId = null,
        string? idempotencyKey = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId))
            throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (content == null)
            throw new ArgumentNullException(nameof(content));

        // TODO: Implement actual queueing mechanism
        _logger.LogInformation(
            "Out-of-band message queued for thread {ThreadId}, runId: {RunId}, idempotencyKey: {IdempotencyKey}",
            threadId, runId, idempotencyKey);

        await Task.CompletedTask;
    }

    public async Task SendToThreadAsync(
        string threadId,
        string text,
        string? runId = null,
        string? idempotencyKey = null,
        CancellationToken cancellationToken = default)
    {
        var content = new TextContent { Text = text };
        await SendToThreadAsync(threadId, content, runId, idempotencyKey, cancellationToken);
    }
}
