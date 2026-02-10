using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Context provided when handling user messages, system messages, or agent responses.
/// Provides methods to send responses and access the conversation state.
/// </summary>
/// <typeparam name="TContext">Type of custom context data</typeparam>
public interface IMessageContext<TContext> where TContext : class
{
    /// <summary>
    /// The message being handled
    /// </summary>
    ChatMessage Message { get; }

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
    /// Optional journal ID for cross-conversation memory
    /// </summary>
    string? JournalId { get; }

    /// <summary>
    /// Full conversation history including this message
    /// </summary>
    IReadOnlyList<ChatMessage> ConversationHistory { get; }

    /// <summary>
    /// Next event sequence number (auto-increments)
    /// </summary>
    int NextEventSeq { get; }

    /// <summary>
    /// Send a text response
    /// </summary>
    Task SendTextAsync(string text, CancellationToken cancellationToken = default);

    /// <summary>
    /// Send a response with arbitrary content
    /// </summary>
    Task SendContentAsync(AIContent content, CancellationToken cancellationToken = default);

    /// <summary>
    /// Send a complete agent message
    /// </summary>
    Task SendMessageAsync(AgentMessage message, CancellationToken cancellationToken = default);

    /// <summary>
    /// Stream response chunks (for SSE streaming)
    /// </summary>
    IAsyncEnumerable<AgentMessageDelta> StreamResponseAsync(
        Func<IAsyncEnumerable<AgentMessageDelta>> streamProvider,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Emit a streaming chunk without adding to response list.
    /// Used for real-time token streaming where each token should trigger
    /// an event but not create a separate message.
    /// </summary>
    Task EmitStreamChunkAsync(string text, CancellationToken cancellationToken = default);
}
