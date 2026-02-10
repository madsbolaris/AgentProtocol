namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Context for SSE streaming operations.
/// Provides methods to emit streaming events with proper sequencing.
/// </summary>
/// <typeparam name="TContext">Type of custom context data</typeparam>
public interface IStreamContext<TContext> where TContext : class
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
    /// Custom context instance for this run
    /// </summary>
    TContext Context { get; }

    /// <summary>
    /// Next event sequence number (auto-increments on each emit)
    /// </summary>
    int NextEventSeq { get; }

    /// <summary>
    /// Emit a streaming event with automatic eventSeq assignment
    /// </summary>
    Task EmitAsync(string eventType, object data, CancellationToken cancellationToken = default);

    /// <summary>
    /// Emit multiple streaming events as a batch
    /// </summary>
    Task EmitBatchAsync(IEnumerable<(string eventType, object data)> events, CancellationToken cancellationToken = default);
}
