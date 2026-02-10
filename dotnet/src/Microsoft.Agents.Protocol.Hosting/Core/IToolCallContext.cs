using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Context provided when handling tool/function calls.
/// Provides access to the tool call details and methods to return results.
/// </summary>
/// <typeparam name="TContext">Type of custom context data</typeparam>
public interface IToolCallContext<TContext> where TContext : class
{
    /// <summary>
    /// The tool call being executed
    /// </summary>
    FunctionCallContent ToolCall { get; }

    /// <summary>
    /// Custom context instance for this run
    /// </summary>
    TContext Context { get; }

    /// <summary>
    /// Current run ID
    /// </summary>
    string RunId { get; }

    /// <summary>
    /// Thread ID for conversation history
    /// </summary>
    string ThreadId { get; }

    /// <summary>
    /// Full conversation history
    /// </summary>
    IReadOnlyList<ChatMessage> ConversationHistory { get; }

    /// <summary>
    /// Next event sequence number (auto-increments)
    /// </summary>
    int NextEventSeq { get; }

    /// <summary>
    /// Emit a streaming event for this tool execution
    /// </summary>
    Task EmitToolEventAsync(string eventType, object data, CancellationToken cancellationToken = default);
}
