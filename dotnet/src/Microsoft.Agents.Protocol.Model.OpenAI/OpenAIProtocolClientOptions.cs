using System;
using Microsoft.Agents.Protocol.Model;

namespace Microsoft.Agents.Protocol.Model.OpenAI;

/// <summary>
/// Configuration options for OpenAI protocol client.
/// </summary>
public class OpenAIProtocolClientOptions : LLMClientOptions
{
    /// <summary>
    /// Custom endpoint URL (for Azure OpenAI, Foundry, etc.).
    /// </summary>
    public Uri? Endpoint { get; set; }

    /// <summary>
    /// Organization ID for OpenAI requests.
    /// </summary>
    public string? Organization { get; set; }

    /// <summary>
    /// Optional user identifier for tracking.
    /// </summary>
    public string? User { get; set; }
}
