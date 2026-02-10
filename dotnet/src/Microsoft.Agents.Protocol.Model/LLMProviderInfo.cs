namespace Microsoft.Agents.Protocol.Model;

/// <summary>
/// Information about the LLM provider and its capabilities.
/// </summary>
public class LLMProviderInfo
{
    /// <summary>
    /// Provider name (e.g., "OpenAI", "Anthropic", "Azure").
    /// </summary>
    public required string Provider { get; set; }

    /// <summary>
    /// Model identifier (e.g., "gpt-4o", "claude-3-5-sonnet-20241022").
    /// </summary>
    public required string Model { get; set; }

    /// <summary>
    /// Indicates if the provider supports streaming responses.
    /// </summary>
    public bool SupportsStreaming { get; set; }

    /// <summary>
    /// Indicates if the provider supports function/tool calling.
    /// </summary>
    public bool SupportsFunctionCalling { get; set; }

    /// <summary>
    /// Indicates if the provider supports vision/image inputs.
    /// </summary>
    public bool SupportsVision { get; set; }

    /// <summary>
    /// Indicates if the provider supports multimodal inputs (audio, video, etc.).
    /// </summary>
    public bool SupportsMultimodal { get; set; }

    /// <summary>
    /// Additional provider-specific capabilities.
    /// </summary>
    public Dictionary<string, bool>? AdditionalCapabilities { get; set; }
}
