using Microsoft.Agents.Abstractions.Models;

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
}

/// <summary>
/// Internal implementation of IConversation.
/// </summary>
internal class Conversation : IConversation
{
    private readonly AgentProtocolClient _client;
    private string? _threadId;

    public Conversation(AgentProtocolClient client, string? threadId)
    {
        _client = client;
        _threadId = threadId;
    }

    public string? ThreadId => _threadId;

    public async Task<string> SendAsync(string message, CancellationToken cancellationToken = default)
    {
        var request = new RunRequest
        {
            ThreadId = _threadId,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = message }
                    }
                }
            }
        };

        var response = await _client.RunAsync(request, cancellationToken);

        // Update thread ID if this was the first message
        if (_threadId == null)
        {
            _threadId = response.ThreadId;
        }

        if (response.Output == null || response.Output.Count == 0)
            return string.Empty;

        // Extract text from first assistant message
        var assistantMessage = response.Output.FirstOrDefault(m => m.Role == "assistant");
        if (assistantMessage == null)
            return string.Empty;

        var textContent = assistantMessage.Contents.OfType<TextContent>().FirstOrDefault();
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

        if (response.Output == null || response.Output.Count == 0)
            return new ChatMessage { Role = "assistant", Contents = new List<Content>() };

        return response.Output.FirstOrDefault(m => m.Role == "assistant")
            ?? new ChatMessage { Role = "assistant", Contents = new List<Content>() };
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
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
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
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
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
}
