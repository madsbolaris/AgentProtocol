using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Model;

/// <summary>
/// Delta update for streaming responses, using Agent Protocol native types.
/// </summary>
public class AgentMessageDelta
{
    /// <summary>
    /// Unique identifier for the message being streamed.
    /// </summary>
    public required string MessageId { get; set; }

    /// <summary>
    /// The type of delta update.
    /// </summary>
    public required DeltaType Type { get; set; }

    /// <summary>
    /// Content delta (Agent Protocol native type).
    /// </summary>
    public AIContent? Content { get; set; }

    /// <summary>
    /// Tool call delta (Agent Protocol native type).
    /// </summary>
    public FunctionCallContent? ToolCall { get; set; }

    /// <summary>
    /// Indicates if this is the final delta for the message.
    /// </summary>
    public bool IsComplete { get; set; }

    /// <summary>
    /// Optional metadata from the provider.
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
}
