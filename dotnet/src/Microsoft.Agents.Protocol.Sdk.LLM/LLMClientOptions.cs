namespace Microsoft.Agents.Protocol.Sdk.LLM;

/// <summary>
/// Base options for LLM clients.
/// </summary>
public class LLMClientOptions
{
    /// <summary>
    /// Temperature for generation (0.0 = deterministic, 2.0 = very random).
    /// Default: 1.0
    /// </summary>
    public double Temperature { get; set; } = 1.0;

    /// <summary>
    /// Maximum number of tokens to generate.
    /// </summary>
    public int? MaxTokens { get; set; }

    /// <summary>
    /// Random seed for deterministic generation (when supported).
    /// </summary>
    public int? Seed { get; set; }

    /// <summary>
    /// Top-p sampling parameter (when supported).
    /// </summary>
    public double? TopP { get; set; }

    /// <summary>
    /// Frequency penalty (when supported).
    /// </summary>
    public double? FrequencyPenalty { get; set; }

    /// <summary>
    /// Presence penalty (when supported).
    /// </summary>
    public double? PresencePenalty { get; set; }

    /// <summary>
    /// Additional provider-specific options.
    /// </summary>
    public Dictionary<string, object>? AdditionalOptions { get; set; }
}
