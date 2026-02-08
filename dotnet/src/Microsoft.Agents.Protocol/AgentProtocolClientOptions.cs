using System;
using System.Net.Http;

namespace Microsoft.Agents.Protocol;

/// <summary>
/// Configuration options for Agent Protocol client
/// </summary>
public class AgentProtocolClientOptions
{
    /// <summary>
    /// Base URL for the Agent Protocol API
    /// </summary>
    public required Uri BaseUrl { get; set; }

    /// <summary>
    /// Optional API key for authentication
    /// </summary>
    public string? ApiKey { get; set; }

    /// <summary>
    /// Optional HTTP client to use for requests
    /// If not provided, a new HttpClient will be created
    /// </summary>
    public HttpClient? HttpClient { get; set; }

    /// <summary>
    /// Request timeout in seconds (default: 30)
    /// </summary>
    public int TimeoutSeconds { get; set; } = 30;

    /// <summary>
    /// Maximum number of retry attempts for failed requests (default: 3)
    /// </summary>
    public int MaxRetries { get; set; } = 3;
}
