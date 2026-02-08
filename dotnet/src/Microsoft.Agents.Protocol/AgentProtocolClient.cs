using System;
using System.Net.Http;
using System.Net.Http.Headers;

namespace Microsoft.Agents.Protocol;

/// <summary>
/// Main client for interacting with Agent Protocol APIs
/// Provides access to Agents, Runs, and Threads operations
/// </summary>
public class AgentProtocolClient : IDisposable
{
    private readonly HttpClient _httpClient;
    private readonly bool _disposeHttpClient;
    private readonly AgentProtocolClientOptions _options;

    /// <summary>
    /// Gets the Runs API client
    /// </summary>
    public RunsClient Runs { get; }

    /// <summary>
    /// Gets the Threads API client
    /// </summary>
    public ThreadsClient Threads { get; }

    /// <summary>
    /// Gets the Agents API client
    /// </summary>
    public AgentsClient Agents { get; }

    /// <summary>
    /// Creates a new instance of the Agent Protocol client
    /// </summary>
    /// <param name="options">Client configuration options</param>
    public AgentProtocolClient(AgentProtocolClientOptions options)
    {
        _options = options ?? throw new ArgumentNullException(nameof(options));

        if (_options.HttpClient != null)
        {
            _httpClient = _options.HttpClient;
            _disposeHttpClient = false;
        }
        else
        {
            _httpClient = new HttpClient
            {
                BaseAddress = _options.BaseUrl,
                Timeout = TimeSpan.FromSeconds(_options.TimeoutSeconds)
            };
            _disposeHttpClient = true;
        }

        // Configure authentication if API key is provided
        if (!string.IsNullOrEmpty(_options.ApiKey))
        {
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", _options.ApiKey);
        }

        // Set default headers
        _httpClient.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));

        // Initialize API clients
        Runs = new RunsClient(_httpClient, _options);
        Threads = new ThreadsClient(_httpClient, _options);
        Agents = new AgentsClient(_httpClient, _options);
    }

    /// <summary>
    /// Creates a new instance with just a base URL
    /// </summary>
    /// <param name="baseUrl">Base URL for the Agent Protocol API</param>
    public AgentProtocolClient(string baseUrl)
        : this(new AgentProtocolClientOptions
        {
            BaseUrl = new Uri(baseUrl)
        })
    {
    }

    /// <summary>
    /// Creates a new instance with base URL and API key
    /// </summary>
    /// <param name="baseUrl">Base URL for the Agent Protocol API</param>
    /// <param name="apiKey">API key for authentication</param>
    public AgentProtocolClient(string baseUrl, string apiKey)
        : this(new AgentProtocolClientOptions
        {
            BaseUrl = new Uri(baseUrl),
            ApiKey = apiKey
        })
    {
    }

    /// <summary>
    /// Disposes the client and underlying HTTP client if owned
    /// </summary>
    public void Dispose()
    {
        if (_disposeHttpClient)
        {
            _httpClient?.Dispose();
        }
    }
}
