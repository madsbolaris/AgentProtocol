using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Protocol.Sdk.Core;

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
}
