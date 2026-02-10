using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Context for the overall run lifecycle.
/// Provides access to run state and methods to control the run.
/// </summary>
/// <typeparam name="TContext">Type of custom context data</typeparam>
public interface IRunContext<TContext> where TContext : class
{
    /// <summary>
    /// Current run ID
    /// </summary>
    string RunId { get; }

    /// <summary>
    /// Thread ID for conversation history
    /// </summary>
    string ThreadId { get; }

    /// <summary>
    /// Optional journal ID for cross-conversation memory
    /// </summary>
    string? JournalId { get; }

    /// <summary>
    /// Current run status (queued, in_progress, requires_action, etc.)
    /// </summary>
    RunStatus Status { get; }

    /// <summary>
    /// Custom context instance for this run
    /// </summary>
    TContext Context { get; }

    /// <summary>
    /// Full conversation history
    /// </summary>
    IReadOnlyList<ChatMessage> ConversationHistory { get; }

    /// <summary>
    /// Request user input (transitions to input_required state)
    /// </summary>
    Task<UserMessage> RequestInputAsync(string prompt, CancellationToken cancellationToken = default);

    /// <summary>
    /// Request authentication (transitions to auth_required state)
    /// </summary>
    Task<string> RequireAuthAsync(string scope, string? message = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Cancel the run (transitions to cancelling state)
    /// </summary>
    Task CancelAsync(string reason, CancellationToken cancellationToken = default);

    /// <summary>
    /// Add metadata to the run
    /// </summary>
    void SetMetadata(string key, object value);

    /// <summary>
    /// Get metadata from the run
    /// </summary>
    object? GetMetadata(string key);
}

/// <summary>
/// Run status matching the 11-state Protocol lifecycle
/// </summary>
public enum RunStatus
{
    Queued,
    InProgress,
    RequiresAction,
    InputRequired,
    AuthRequired,
    Cancelling,
    Cancelled,
    Failed,
    Completed,
    Incomplete,
    Timeout
}
