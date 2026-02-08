namespace Microsoft.Agents.Protocol.Client;

/// <summary>
/// Options for chat completion and streaming requests.
/// </summary>
public class ChatOptions
{
    /// <summary>
    /// Agent ID to use (optional if only one agent registered).
    /// </summary>
    public string? AgentId { get; set; }

    /// <summary>
    /// Tools available for the agent to call.
    /// </summary>
    public ToolCollection? Tools { get; set; }

    /// <summary>
    /// Additional metadata for the request.
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }

    /// <summary>
    /// Callback fired when a tool call starts (for monitoring).
    /// </summary>
    public Func<ToolCallInfo, Task>? OnToolCallStarted { get; set; }

    /// <summary>
    /// Callback fired when a tool call completes (for monitoring).
    /// </summary>
    public Func<ToolCallInfo, object, Task>? OnToolCallCompleted { get; set; }

    /// <summary>
    /// Callback fired when a tool call fails (for monitoring).
    /// </summary>
    public Func<ToolCallInfo, Exception, Task>? OnToolCallFailed { get; set; }
}

/// <summary>
/// Information about a tool call.
/// </summary>
public class ToolCallInfo
{
    public required string CallId { get; set; }
    public required string Name { get; set; }
    public required string Arguments { get; set; }
}
