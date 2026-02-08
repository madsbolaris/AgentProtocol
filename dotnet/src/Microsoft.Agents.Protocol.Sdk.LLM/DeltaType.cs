namespace Microsoft.Agents.Protocol.Sdk.LLM;

/// <summary>
/// Types of delta updates during streaming.
/// </summary>
public enum DeltaType
{
    /// <summary>
    /// Message stream has started.
    /// </summary>
    MessageStart,

    /// <summary>
    /// Text content chunk received.
    /// </summary>
    TextDelta,

    /// <summary>
    /// Tool call has been initiated.
    /// </summary>
    ToolCallStart,

    /// <summary>
    /// Tool call arguments are streaming in.
    /// </summary>
    ToolCallDelta,

    /// <summary>
    /// Tool call has finished.
    /// </summary>
    ToolCallComplete,

    /// <summary>
    /// Message stream has completed.
    /// </summary>
    MessageComplete
}
