using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Model;

/// <summary>
/// LLM client that speaks Agent Protocol types natively.
/// Eliminates the need for conversion layers between provider-specific types
/// and Agent Protocol types.
/// </summary>
public interface IProtocolLLMClient
{
    /// <summary>
    /// Generate a response using Agent Protocol message types.
    /// </summary>
    /// <param name="conversationHistory">The conversation history using Protocol message types</param>
    /// <param name="availableTools">Optional tool definitions in Protocol format</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Agent message with Protocol content types</returns>
    Task<AgentMessage> GenerateAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Stream a response using Agent Protocol message types.
    /// </summary>
    /// <param name="conversationHistory">The conversation history using Protocol message types</param>
    /// <param name="availableTools">Optional tool definitions in Protocol format</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Async stream of deltas with Protocol content types</returns>
    IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Provider-specific metadata and capabilities.
    /// </summary>
    LLMProviderInfo ProviderInfo { get; }
}
