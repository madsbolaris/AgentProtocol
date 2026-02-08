using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Protocol.Sdk.LLM;
using System.Runtime.CompilerServices;

namespace Microsoft.Agents.Protocol.Sdk.LLM.Testing;

/// <summary>
/// Mock implementation of IProtocolLLMClient for testing.
/// Allows pre-queueing responses without making real API calls.
/// </summary>
public class MockProtocolLLMClient : IProtocolLLMClient
{
    private readonly Queue<AgentMessage> _queuedResponses = new();
    private readonly Queue<List<AgentMessageDelta>> _queuedStreamingResponses = new();
    private readonly List<(List<ChatMessage> ConversationHistory, ToolDefinition[]? Tools)> _callHistory = new();

    /// <summary>
    /// Provider information for the mock client.
    /// </summary>
    public LLMProviderInfo ProviderInfo { get; set; } = new()
    {
        Provider = "Mock",
        Model = "mock-model",
        SupportsStreaming = true,
        SupportsFunctionCalling = true,
        SupportsVision = true,
        SupportsMultimodal = true
    };

    /// <summary>
    /// Gets the history of all generate calls made to this client.
    /// </summary>
    public IReadOnlyList<(List<ChatMessage> ConversationHistory, ToolDefinition[]? Tools)> CallHistory => _callHistory;

    /// <summary>
    /// Gets the number of generate calls made.
    /// </summary>
    public int CallCount => _callHistory.Count;

    /// <summary>
    /// Enqueues a response to be returned by the next GenerateAsync call.
    /// </summary>
    public void EnqueueResponse(AgentMessage message)
    {
        ArgumentNullException.ThrowIfNull(message);
        _queuedResponses.Enqueue(message);
    }

    /// <summary>
    /// Enqueues a text response to be returned by the next GenerateAsync call.
    /// </summary>
    public void EnqueueTextResponse(string text)
    {
        EnqueueResponse(new AgentMessage
        {
            MessageId = $"msg_{Guid.NewGuid():N}",
            Contents = new List<AIContent>
            {
                new TextContent { Text = text }
            }
        });
    }

    /// <summary>
    /// Enqueues a tool call response to be returned by the next GenerateAsync call.
    /// </summary>
    public void EnqueueToolCallResponse(string toolName, string arguments, string? callId = null)
    {
        EnqueueResponse(new AgentMessage
        {
            MessageId = $"msg_{Guid.NewGuid():N}",
            Contents = new List<AIContent>
            {
                new FunctionCallContent
                {
                    CallId = callId ?? $"call_{Guid.NewGuid():N}",
                    Name = toolName,
                    Arguments = arguments
                }
            }
        });
    }

    /// <summary>
    /// Enqueues a streaming response to be returned by the next StreamAsync call.
    /// </summary>
    public void EnqueueStreamingResponse(List<AgentMessageDelta> deltas)
    {
        ArgumentNullException.ThrowIfNull(deltas);
        _queuedStreamingResponses.Enqueue(deltas);
    }

    /// <summary>
    /// Enqueues a streaming text response.
    /// </summary>
    public void EnqueueStreamingTextResponse(string text, int chunkSize = 10)
    {
        var messageId = $"msg_{Guid.NewGuid():N}";
        var deltas = new List<AgentMessageDelta>
        {
            new AgentMessageDelta
            {
                MessageId = messageId,
                Type = DeltaType.MessageStart
            }
        };

        var textBuffer = "";
        for (int i = 0; i < text.Length; i += chunkSize)
        {
            var chunk = text.Substring(i, Math.Min(chunkSize, text.Length - i));
            textBuffer += chunk;

            deltas.Add(new AgentMessageDelta
            {
                MessageId = messageId,
                Type = DeltaType.TextDelta,
                Content = new TextContent { Text = textBuffer }
            });
        }

        deltas.Add(new AgentMessageDelta
        {
            MessageId = messageId,
            Type = DeltaType.MessageComplete,
            IsComplete = true
        });

        _queuedStreamingResponses.Enqueue(deltas);
    }

    /// <summary>
    /// Clears all queued responses and call history.
    /// </summary>
    public void Reset()
    {
        _queuedResponses.Clear();
        _queuedStreamingResponses.Clear();
        _callHistory.Clear();
    }

    public Task<AgentMessage> GenerateAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(conversationHistory);

        _callHistory.Add((conversationHistory, availableTools));

        if (_queuedResponses.Count == 0)
        {
            throw new InvalidOperationException(
                "No responses queued. Use EnqueueResponse() to add responses before calling GenerateAsync().");
        }

        var response = _queuedResponses.Dequeue();
        return Task.FromResult(response);
    }

    public async IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(conversationHistory);

        _callHistory.Add((conversationHistory, availableTools));

        if (_queuedStreamingResponses.Count == 0)
        {
            throw new InvalidOperationException(
                "No streaming responses queued. Use EnqueueStreamingResponse() to add responses before calling StreamAsync().");
        }

        var deltas = _queuedStreamingResponses.Dequeue();

        foreach (var delta in deltas)
        {
            cancellationToken.ThrowIfCancellationRequested();
            await Task.Delay(1, cancellationToken); // Simulate streaming delay
            yield return delta;
        }
    }
}
