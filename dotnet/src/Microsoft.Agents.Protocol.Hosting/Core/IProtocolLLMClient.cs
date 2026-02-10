using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// LLM client that returns Agent Protocol types directly.
/// Abstracts provider-specific APIs (OpenAI, Anthropic, etc.) and returns
/// AgentMessage and AgentMessageDelta (Protocol types) instead of provider types.
/// </summary>
public interface IProtocolLLMClient
{
    /// <summary>
    /// Generate a single response (non-streaming)
    /// </summary>
    /// <param name="conversationHistory">Full conversation history including system message</param>
    /// <param name="availableTools">Tools available for calling</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Complete agent message with Protocol types</returns>
    Task<AgentMessage> GenerateAsync(
        IReadOnlyList<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Stream response chunks (for SSE streaming)
    /// </summary>
    /// <param name="conversationHistory">Full conversation history including system message</param>
    /// <param name="availableTools">Tools available for calling</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Stream of message deltas with Protocol types</returns>
    IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        IReadOnlyList<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Represents a single delta/chunk in a streaming response.
/// Uses Agent Protocol types (AIContent, FunctionCallContent) directly.
/// </summary>
public class AgentMessageDelta
{
    /// <summary>
    /// Message ID (same across all deltas for one message)
    /// </summary>
    public string MessageId { get; set; } = string.Empty;

    /// <summary>
    /// Type of delta
    /// </summary>
    public DeltaType Type { get; set; }

    /// <summary>
    /// Content delta (for text, typically)
    /// </summary>
    public AIContent? Content { get; set; }

    /// <summary>
    /// Tool call information (for tool calls)
    /// </summary>
    public FunctionCallContent? ToolCall { get; set; }

    /// <summary>
    /// Whether this is the final delta
    /// </summary>
    public bool IsComplete { get; set; }

    /// <summary>
    /// Accumulated text so far (convenience property)
    /// </summary>
    public string? AccumulatedText { get; set; }
}

/// <summary>
/// Types of deltas in a streaming response
/// </summary>
public enum DeltaType
{
    /// <summary>
    /// Message started
    /// </summary>
    MessageStart,

    /// <summary>
    /// Text content delta
    /// </summary>
    TextDelta,

    /// <summary>
    /// Tool call started
    /// </summary>
    ToolCallStart,

    /// <summary>
    /// Tool call delta (streaming arguments)
    /// </summary>
    ToolCallDelta,

    /// <summary>
    /// Tool call completed
    /// </summary>
    ToolCallComplete,

    /// <summary>
    /// Message completed
    /// </summary>
    MessageComplete
}

/// <summary>
/// Tool definition for LLM providers
/// </summary>
public class ToolDefinition
{
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public object? ParametersSchema { get; set; }
}
