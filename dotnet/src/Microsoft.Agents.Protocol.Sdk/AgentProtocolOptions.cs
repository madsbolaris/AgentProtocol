using Microsoft.Agents.Protocol.Sdk.Core;

namespace Microsoft.Agents.Protocol.Sdk;

/// <summary>
/// Configuration options for an Agent Protocol agent
/// </summary>
public class AgentProtocolOptions
{
    /// <summary>
    /// Agent name
    /// </summary>
    public string Name { get; set; } = "Agent";

    /// <summary>
    /// Agent description
    /// </summary>
    public string? Description { get; set; }

    /// <summary>
    /// System instructions/prompt
    /// </summary>
    public string? Instructions { get; set; }

    /// <summary>
    /// Model to use (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
    /// </summary>
    public string? Model { get; set; }

    /// <summary>
    /// LLM client for generating responses
    /// </summary>
    public IProtocolLLMClient? LLMClient { get; set; }

    /// <summary>
    /// Whether to enable streaming by default
    /// </summary>
    public bool EnableStreaming { get; set; } = true;

    /// <summary>
    /// Maximum number of tool execution iterations before stopping
    /// </summary>
    public int MaxToolIterations { get; set; } = 10;

    /// <summary>
    /// Default timeout for runs (null = no timeout)
    /// </summary>
    public TimeSpan? RunTimeout { get; set; }

    /// <summary>
    /// Whether to automatically add conversation history to LLM calls
    /// </summary>
    public bool IncludeConversationHistory { get; set; } = true;

    /// <summary>
    /// Maximum conversation history length (0 = unlimited)
    /// </summary>
    public int MaxHistoryLength { get; set; } = 100;

    /// <summary>
    /// Custom metadata to include in all runs
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}
