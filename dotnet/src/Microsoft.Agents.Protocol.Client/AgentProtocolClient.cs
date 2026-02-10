using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using Microsoft.Agents;
using System.Linq;

namespace Microsoft.Agents.Protocol.Client;

/// <summary>
/// Client for interacting with Agent Protocol endpoints.
/// Provides methods for creating runs, streaming responses, and managing threads.
/// </summary>
public class AgentProtocolClient : IDisposable
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly bool _enableLogging;
    private readonly string _logDirectory;

    /// <summary>
    /// Creates a new Agent Protocol client.
    /// </summary>
    /// <param name="baseUrl">Base URL of the agent service (e.g., "http://localhost:5000")</param>
    /// <param name="httpClient">Optional HttpClient to use (will create one if not provided)</param>
    /// <param name="enableLogging">Enable automatic conversation logging to XML files</param>
    /// <param name="logDirectory">Directory path for saving conversation logs</param>
    public AgentProtocolClient(string baseUrl, HttpClient? httpClient = null, bool enableLogging = false, string logDirectory = "logs/conversations")
    {
        _baseUrl = baseUrl.TrimEnd('/');
        _httpClient = httpClient ?? new HttpClient();
        _enableLogging = enableLogging;
        _logDirectory = logDirectory;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };
    }

    /// <summary>
    /// Creates and waits for a run to complete synchronously.
    /// </summary>
    /// <param name="request">Run request containing agent ID, input messages, and options</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Completed run with output messages</returns>
    public async Task<RunResponse> RunAsync(
        RunRequest request,
        CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.PostAsJsonAsync(
            $"{_baseUrl}/runs/wait",
            request,
            _jsonOptions,
            cancellationToken);

        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<RunResponse>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Empty response from server");
    }

    /// <summary>
    /// Creates a run and streams the response using Server-Sent Events.
    /// </summary>
    /// <param name="request">Run request containing agent ID, input messages, and options</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Async enumerable of streaming events</returns>
    public async IAsyncEnumerable<StreamEvent> StreamAsync(
        RunRequest request,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.PostAsJsonAsync(
            $"{_baseUrl}/runs/stream",
            request,
            _jsonOptions,
            cancellationToken);

        response.EnsureSuccessStatusCode();

        using var stream = await response.Content.ReadAsStreamAsync(cancellationToken);
        using var reader = new StreamReader(stream);

        string? line;
        StreamEvent? currentEvent = null;

        while ((line = await reader.ReadLineAsync(cancellationToken)) != null)
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                // Empty line signals end of event
                if (currentEvent != null)
                {
                    yield return currentEvent;
                    currentEvent = null;
                }
                continue;
            }

            if (line.StartsWith("event:"))
            {
                currentEvent = new StreamEvent
                {
                    EventType = line.Substring(6).Trim(),
                    JsonOptions = _jsonOptions
                };
            }
            else if (line.StartsWith("data:"))
            {
                var data = line.Substring(5).Trim();
                if (currentEvent != null && !string.IsNullOrEmpty(data))
                {
                    currentEvent.Data = JsonSerializer.Deserialize<JsonElement>(data, _jsonOptions);
                }
            }
        }

        // Yield last event if exists
        if (currentEvent != null)
        {
            yield return currentEvent;
        }
    }

    /// <summary>
    /// Gets the current status of a run.
    /// </summary>
    /// <param name="runId">Run ID to check</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Run status information</returns>
    public async Task<RunResponse> GetRunStatusAsync(
        string runId,
        CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.GetAsync(
            $"{_baseUrl}/runs/{runId}",
            cancellationToken);

        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<RunResponse>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Empty response from server");
    }

    /// <summary>
    /// Cancels a running operation.
    /// </summary>
    /// <param name="runId">Run ID to cancel</param>
    /// <param name="cancellationToken">Cancellation token</param>
    public async Task CancelRunAsync(
        string runId,
        CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.PostAsync(
            $"{_baseUrl}/runs/{runId}/cancel",
            null,
            cancellationToken);

        response.EnsureSuccessStatusCode();
    }

    /// <summary>
    /// Gets messages from a thread.
    /// </summary>
    /// <param name="threadId">Thread ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of messages in the thread</returns>
    public async Task<List<ChatMessage>> GetThreadMessagesAsync(
        string threadId,
        CancellationToken cancellationToken = default)
    {
        var response = await _httpClient.GetAsync(
            $"{_baseUrl}/threads/{threadId}/messages",
            cancellationToken);

        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<ChatMessage>>(_jsonOptions, cancellationToken)
            ?? new List<ChatMessage>();
    }

    /// <summary>
    /// Sends a message and returns the complete response as text (simple API).
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent's text response</returns>
    public Task<string> CompleteChatAsync(
        string message,
        CancellationToken cancellationToken = default)
    {
        return CompleteChatAsync(message, options: null, cancellationToken);
    }

    /// <summary>
    /// Sends a message with options (including tools) and returns the complete response as text.
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="options">Chat options including tools</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent's text response</returns>
    public async Task<string> CompleteChatAsync(
        string message,
        ChatOptions? options,
        CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            AgentId = options?.AgentId,
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = message }
                    }
                }
            },
            Metadata = options?.Metadata
        };

        // If tools are provided, handle tool execution automatically
        if (options?.Tools != null)
        {
            return await CompleteChatWithToolsAsync(request, options, cancellationToken);
        }

        var response = await RunAsync(request, cancellationToken);

        if (response.Output == null || response.Output.Count == 0)
            return string.Empty;

        // Extract text from first assistant message
        var assistantMessage = response.Output.FirstOrDefault(m => m.Role == ChatRole.Agent);
        if (assistantMessage == null)
            return string.Empty;

        var textContent = assistantMessage.Contents?.OfType<TextContent>().FirstOrDefault();
        return textContent?.Text ?? string.Empty;
    }

    /// <summary>
    /// Handles tool execution automatically during streaming.
    /// </summary>
    private async Task<string> CompleteChatWithToolsAsync(
        RunRequest request,
        ChatOptions options,
        CancellationToken cancellationToken)
    {
        var resultText = new StringBuilder();

        await foreach (var evt in StreamAsync(request, cancellationToken))
        {
            if (evt.EventType == "message.delta" || evt.EventType == "message.updated")
            {
                var messageData = evt.GetData<ChatMessage>();
                if (messageData != null)
                {
                    var textContent = messageData.Contents?.OfType<TextContent>().FirstOrDefault();
                    if (textContent != null)
                    {
                        resultText.Clear();
                        resultText.Append(textContent.Text);
                    }
                }
            }
            else if (evt.EventType == "run.requires_action")
            {
                // Extract run ID and tool calls
                var runData = evt.GetData<RunResponse>();
                if (runData != null)
                {
                    // TODO: Handle tool execution
                    // This requires protocol-level support for submitting tool outputs
                    // For now, tools will need to be handled at a lower level
                }
            }
        }

        return resultText.ToString();
    }

    /// <summary>
    /// Sends a multi-modal message and returns the complete response message.
    /// </summary>
    /// <param name="message">The message to send (can include images, audio, etc.)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent's response message</returns>
    public async Task<ChatMessage> CompleteChatAsync(
        ChatMessage message,
        CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            Input = new List<ChatMessage> { message }
        };

        var response = await RunAsync(request, cancellationToken);

        if (response.Output == null || response.Output.Count == 0)
            return new AgentMessage { Contents = new List<AIContent>() };

        return response.Output.FirstOrDefault(m => m.Role == ChatRole.Agent)
            ?? new AgentMessage { Contents = new List<AIContent>() };
    }

    /// <summary>
    /// Streams a message response with text chunks delivered via callback (simple streaming API).
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="onTextChunk">Callback fired for each text chunk</param>
    /// <param name="cancellationToken">Cancellation token</param>
    public async Task StreamChatAsync(
        string message,
        Action<string> onTextChunk,
        CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = message }
                    }
                }
            }
        };

        var accumulatedText = string.Empty;

        await foreach (var evt in StreamAsync(request, cancellationToken))
        {
            // Handle different event types for text streaming
            if (evt.EventType == "message.delta" || evt.EventType == "message.updated")
            {
                var messageData = evt.GetData<ChatMessage>();
                if (messageData != null)
                {
                    var textContent = messageData.Contents?.OfType<TextContent>().FirstOrDefault();
                    if (textContent != null)
                    {
                        // Calculate new text since last update
                        var newText = textContent.Text.Substring(accumulatedText.Length);
                        if (!string.IsNullOrEmpty(newText))
                        {
                            onTextChunk(newText);
                            accumulatedText = textContent.Text;
                        }
                    }
                }
            }
        }
    }

    /// <summary>
    /// Creates a new conversation for maintaining state across multiple messages.
    /// </summary>
    /// <returns>A conversation instance</returns>
    public IConversation CreateConversation()
    {
        return new Conversation(this, null, _enableLogging, _logDirectory);
    }

    /// <summary>
    /// Resumes an existing conversation using a thread ID.
    /// </summary>
    /// <param name="threadId">The thread ID to resume</param>
    /// <returns>A conversation instance</returns>
    public IConversation ResumeConversation(string threadId)
    {
        return new Conversation(this, threadId, _enableLogging, _logDirectory);
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

/// <summary>
/// Request for creating a new run.
/// </summary>
public class RunRequest
{
    /// <summary>
    /// Agent ID to run (optional if only one agent is registered)
    /// </summary>
    public string? AgentId { get; set; }

    /// <summary>
    /// Thread ID for conversation continuity (optional, will be created if not provided)
    /// </summary>
    public string? ThreadId { get; set; }

    /// <summary>
    /// Journal ID for cross-conversation memory (optional)
    /// </summary>
    public string? JournalId { get; set; }

    /// <summary>
    /// Input messages to process
    /// </summary>
    public required List<ChatMessage> Input { get; set; }

    /// <summary>
    /// Additional metadata for this run
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }

    /// <summary>
    /// Webhook URL for run completion notification
    /// </summary>
    public string? Webhook { get; set; }
}

/// <summary>
/// Response from a run operation.
/// </summary>
public class RunResponse
{
    /// <summary>
    /// Unique run ID
    /// </summary>
    public required string RunId { get; set; }

    /// <summary>
    /// Thread ID (for conversation continuity)
    /// </summary>
    public required string ThreadId { get; set; }

    /// <summary>
    /// Run status (queued, in_progress, completed, failed, etc.)
    /// </summary>
    public required string Status { get; set; }

    /// <summary>
    /// Output messages from the agent
    /// </summary>
    public List<ChatMessage>? Output { get; set; }

    /// <summary>
    /// Error information if run failed
    /// </summary>
    public ErrorInfo? Error { get; set; }
}

/// <summary>
/// Error information for failed runs.
/// </summary>
public class ErrorInfo
{
    public required string Code { get; set; }
    public required string Message { get; set; }
    public Dictionary<string, object>? Details { get; set; }
}

/// <summary>
/// Server-Sent Event from a streaming run.
/// </summary>
public class StreamEvent
{
    /// <summary>
    /// Event type (e.g., "message.start", "message.delta", "tool_call.start")
    /// </summary>
    public required string EventType { get; set; }

    /// <summary>
    /// Event data as JSON
    /// </summary>
    public JsonElement Data { get; set; }

    /// <summary>
    /// JSON serializer options to use for deserialization
    /// </summary>
    internal JsonSerializerOptions? JsonOptions { get; set; }

    /// <summary>
    /// Extracts typed data from the event.
    /// </summary>
    public T? GetData<T>()
    {
        // Try deserializing with custom options first, fall back to default if it fails
        // The default serializer should pick up JsonPolymorphic attributes automatically
        try
        {
            return JsonSerializer.Deserialize<T>(Data.GetRawText(), JsonOptions);
        }
        catch (NotSupportedException)
        {
            // Fall back to default options which should handle polymorphic types
            return JsonSerializer.Deserialize<T>(Data.GetRawText());
        }
    }
}
