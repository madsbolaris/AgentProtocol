using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Extensions.Logging;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Implementation of IAgentContext for agent turn processing.
/// </summary>
public class AgentContext : IAgentContext
{
    private readonly ILogger _logger;
    private readonly Func<string, Task>? _responseCallback;

    /// <summary>
    /// Creates a new AgentContext instance.
    /// </summary>
    /// <param name="runId">The run ID.</param>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="storage">The storage implementation.</param>
    /// <param name="logger">The logger.</param>
    /// <param name="responseCallback">Optional callback for responses.</param>
    public AgentContext(
        string runId,
        string threadId,
        IStorage storage,
        ILogger logger,
        Func<string, Task>? responseCallback = null)
    {
        RunId = runId ?? throw new ArgumentNullException(nameof(runId));
        ThreadId = threadId ?? throw new ArgumentNullException(nameof(threadId));
        State = new AgentState(threadId, storage ?? throw new ArgumentNullException(nameof(storage)));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _responseCallback = responseCallback;
    }

    /// <inheritdoc/>
    public string RunId { get; }

    /// <inheritdoc/>
    public string ThreadId { get; }

    /// <inheritdoc/>
    public ILogger Logger => _logger;

    /// <summary>
    /// Gets the state storage for this context.
    /// </summary>
    public AgentState State { get; }

    /// <inheritdoc/>
    public async Task RespondAsync(AIContent content, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return;
        }

        if (_responseCallback != null)
        {
            // Convert AIContent to text representation
            var text = content switch
            {
                TextContent textContent => textContent.Text ?? string.Empty,
                _ => content?.ToString() ?? string.Empty
            };
            await _responseCallback(text);
        }
    }

    /// <inheritdoc/>
    public async Task RespondAsync(string text, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return;
        }

        if (_responseCallback != null)
        {
            await _responseCallback(text);
        }
    }

    /// <inheritdoc/>
    public Task LogAsync(string message, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.CompletedTask;
        }

        _logger.LogInformation("[Run {RunId}] {Message}", RunId, message);
        return Task.CompletedTask;
    }

    /// <summary>
    /// Logs a message with a specific level.
    /// </summary>
    /// <param name="message">The message to log.</param>
    /// <param name="level">The log level (DEBUG, INFO, WARNING, ERROR).</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public Task LogAsync(string message, string level, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.CompletedTask;
        }

        var logLevel = level?.ToUpperInvariant() switch
        {
            "DEBUG" => LogLevel.Debug,
            "WARNING" => LogLevel.Warning,
            "ERROR" => LogLevel.Error,
            _ => LogLevel.Information
        };

        _logger.Log(logLevel, "[Run {RunId}] {Message}", RunId, message);
        return Task.CompletedTask;
    }

    /// <inheritdoc/>
    public Task PauseForApprovalAsync(
        string summary,
        object? metadata = null,
        CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.CompletedTask;
        }

        _logger.LogInformation("[Run {RunId}] Pause for approval requested: {Summary}", RunId, summary);

        // In a real implementation, this would pause the run and wait for external approval
        // For now, we just log it

        return Task.CompletedTask;
    }
}
