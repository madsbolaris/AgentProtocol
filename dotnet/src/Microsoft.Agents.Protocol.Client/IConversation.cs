using Microsoft.Agents;
using Microsoft.Agents.Protocol.Xml;

namespace Microsoft.Agents.Protocol.Client;

/// <summary>
/// Represents a conversation with state maintained across multiple messages.
/// </summary>
public interface IConversation
{
    /// <summary>
    /// Gets the thread ID for this conversation (null until first message sent).
    /// </summary>
    string? ThreadId { get; }

    /// <summary>
    /// Gets all messages in this conversation (cached locally).
    /// Messages are automatically added as the conversation progresses.
    /// </summary>
    IReadOnlyList<ChatMessage> Messages { get; }

    /// <summary>
    /// Sends a message and returns the complete response as text.
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent's text response</returns>
    Task<string> SendAsync(string message, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a structured message and returns the complete response.
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent's response message</returns>
    Task<ChatMessage> SendAsync(ChatMessage message, CancellationToken cancellationToken = default);

    /// <summary>
    /// Streams message responses as structured messages (Mode 2: Messages).
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Async enumerable of messages</returns>
    IAsyncEnumerable<ChatMessage> StreamMessagesAsync(
        string message,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Streams raw events (Mode 3: Events).
    /// </summary>
    /// <param name="message">The message to send</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Async enumerable of stream events</returns>
    IAsyncEnumerable<StreamEvent> StreamEventsAsync(
        string message,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets all messages from this conversation's thread.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of messages in chronological order</returns>
    /// <exception cref="InvalidOperationException">
    /// Thrown when no thread ID is available. Send a message first to create a thread.
    /// </exception>
    /// <remarks>
    /// This is a convenience method that retrieves the full message history for this conversation's thread.
    /// It delegates to <see cref="AgentProtocolClient.GetThreadMessagesAsync(string, CancellationToken)"/>.
    /// </remarks>
    Task<List<ChatMessage>> GetMessagesAsync(CancellationToken cancellationToken = default);
}

/// <summary>
/// Internal implementation of IConversation.
/// </summary>
internal class Conversation : IConversation
{
    private readonly AgentProtocolClient _client;
    private string? _threadId;
    private readonly List<ChatMessage> _messages = new();
    private readonly bool _enableLogging;
    private readonly string _logDirectory;

    public Conversation(AgentProtocolClient client, string? threadId, bool enableLogging, string logDirectory)
    {
        _client = client;
        _threadId = threadId;
        _enableLogging = enableLogging;
        _logDirectory = logDirectory;
    }

    public string? ThreadId => _threadId;

    public IReadOnlyList<ChatMessage> Messages => _messages.AsReadOnly();

    public async Task<string> SendAsync(string message, CancellationToken cancellationToken = default)
    {
        var userMessage = new UserMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = message }
            }
        };

        var request = new RunRequest
        {
            ThreadId = _threadId,
            Input = new List<ChatMessage> { userMessage }
        };

        var response = await _client.RunAsync(request, cancellationToken);

        // Update thread ID if this was the first message
        if (_threadId == null)
        {
            _threadId = response.ThreadId;
        }

        // Add user message to cache
        _messages.Add(userMessage);

        // Add agent response to cache
        if (response.Output != null && response.Output.Count > 0)
        {
            foreach (var outputMessage in response.Output)
            {
                _messages.Add(outputMessage);
            }
        }

        // Auto-save if logging is enabled
        AutoSaveConversation();

        if (response.Output == null || response.Output.Count == 0)
            return string.Empty;

        // Extract text from first assistant message
        var assistantMessage = response.Output.FirstOrDefault(m => m.Role == ChatRole.Agent);
        if (assistantMessage == null)
            return string.Empty;

        var textContent = assistantMessage.Contents?.OfType<TextContent>().FirstOrDefault();
        return textContent?.Text ?? string.Empty;
    }

    public async Task<ChatMessage> SendAsync(ChatMessage message, CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            ThreadId = _threadId,
            Input = new List<ChatMessage> { message }
        };

        var response = await _client.RunAsync(request, cancellationToken);

        // Update thread ID if this was the first message
        if (_threadId == null)
        {
            _threadId = response.ThreadId;
        }

        // Add user message to cache
        _messages.Add(message);

        // Add agent response to cache
        if (response.Output != null && response.Output.Count > 0)
        {
            foreach (var outputMessage in response.Output)
            {
                _messages.Add(outputMessage);
            }
        }

        // Auto-save if logging is enabled
        AutoSaveConversation();

        if (response.Output == null || response.Output.Count == 0)
            return new AgentMessage { Contents = new List<AIContent>() };

        return response.Output.FirstOrDefault(m => m.Role == ChatRole.Agent)
            ?? new AgentMessage { Contents = new List<AIContent>() };
    }

    public async IAsyncEnumerable<ChatMessage> StreamMessagesAsync(
        string message,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            ThreadId = _threadId,
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

        // Track messages by ID
        var messageMap = new Dictionary<string, ChatMessage>();

        await foreach (var evt in _client.StreamAsync(request, cancellationToken))
        {
            // Update thread ID from first event
            if (_threadId == null && evt.EventType == "run.started")
            {
                var runData = evt.GetData<RunResponse>();
                if (runData != null)
                {
                    _threadId = runData.ThreadId;
                }
            }

            // Handle message events
            if (evt.EventType == "message.created")
            {
                var messageData = evt.GetData<ChatMessage>();
                if (messageData != null && !string.IsNullOrEmpty(messageData.MessageId))
                {
                    messageMap[messageData.MessageId] = messageData;
                    yield return messageData;
                }
            }
            else if (evt.EventType == "message.updated" || evt.EventType == "message.delta")
            {
                var messageData = evt.GetData<ChatMessage>();
                if (messageData != null && !string.IsNullOrEmpty(messageData.MessageId))
                {
                    messageMap[messageData.MessageId] = messageData;
                    yield return messageData;
                }
            }
        }
    }

    public async IAsyncEnumerable<StreamEvent> StreamEventsAsync(
        string message,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            ThreadId = _threadId,
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

        await foreach (var evt in _client.StreamAsync(request, cancellationToken))
        {
            // Update thread ID from first event
            if (_threadId == null && evt.EventType == "run.started")
            {
                var runData = evt.GetData<RunResponse>();
                if (runData != null)
                {
                    _threadId = runData.ThreadId;
                }
            }

            yield return evt;
        }
    }

    public async Task<List<ChatMessage>> GetMessagesAsync(CancellationToken cancellationToken = default)
    {
        if (ThreadId == null)
        {
            throw new InvalidOperationException(
                "No thread ID available. Send a message to this conversation first to create a thread.");
        }

        return await _client.GetThreadMessagesAsync(ThreadId, cancellationToken)
            .ConfigureAwait(false);
    }

    /// <summary>
    /// Automatically saves the conversation to XML if logging is enabled.
    /// </summary>
    private void AutoSaveConversation()
    {
        if (!_enableLogging || _threadId == null)
            return;

        try
        {
            // Ensure log directory exists
            if (!Directory.Exists(_logDirectory))
            {
                Directory.CreateDirectory(_logDirectory);
            }

            // Save conversation to file
            var filePath = Path.Combine(_logDirectory, $"{_threadId}.xml");
            File.WriteAllText(filePath, ToString());
        }
        catch
        {
            // Silently ignore logging errors to avoid breaking the main flow
        }
    }

    /// <summary>
    /// Returns the XML representation of all messages in this conversation.
    /// </summary>
    /// <returns>XML string with all messages wrapped in a thread element</returns>
    public override string ToString()
    {
        if (_messages.Count == 0)
        {
            return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<thread />";
        }

        var serializer = new MessageSerializer();
        return serializer.SerializeMany(_messages, rootElement: "thread");
    }
}
