using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Protocol.Sdk.LLM;
using System.Runtime.CompilerServices;
using System.Text.Json;

namespace Microsoft.Agents.Protocol.Sdk.LLM.Testing;

/// <summary>
/// Wraps another IProtocolLLMClient and records all interactions to disk.
/// Useful for creating golden files and test recordings.
/// </summary>
public class RecordingProtocolLLMClient : IProtocolLLMClient
{
    private readonly IProtocolLLMClient _innerClient;
    private readonly string _recordingsDirectory;
    private readonly JsonSerializerOptions _jsonOptions;
    private int _callCount = 0;

    /// <summary>
    /// Creates a new recording client that wraps another client.
    /// </summary>
    /// <param name="innerClient">The actual LLM client to wrap</param>
    /// <param name="recordingsDirectory">Directory to save recordings</param>
    public RecordingProtocolLLMClient(
        IProtocolLLMClient innerClient,
        string recordingsDirectory)
    {
        _innerClient = innerClient ?? throw new ArgumentNullException(nameof(innerClient));
        _recordingsDirectory = recordingsDirectory ?? throw new ArgumentNullException(nameof(recordingsDirectory));

        Directory.CreateDirectory(_recordingsDirectory);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public LLMProviderInfo ProviderInfo => _innerClient.ProviderInfo;

    public async Task<AgentMessage> GenerateAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default)
    {
        var callId = ++_callCount;
        var timestamp = DateTime.UtcNow;

        // Record request
        var requestData = new
        {
            callId,
            timestamp,
            conversationHistory = SerializeMessages(conversationHistory),
            availableTools = availableTools?.Select(t => new
            {
                t.Type,
                function = new
                {
                    t.Function.Name,
                    t.Function.Description,
                    parameters = t.Function.Parameters
                }
            }).ToArray(),
            providerInfo = ProviderInfo
        };

        var requestFile = Path.Combine(_recordingsDirectory, $"call-{callId:D4}.request.json");
        await File.WriteAllTextAsync(requestFile, JsonSerializer.Serialize(requestData, _jsonOptions), cancellationToken);

        // Make actual call
        var response = await _innerClient.GenerateAsync(conversationHistory, availableTools, cancellationToken);

        // Record response
        var responseData = new
        {
            callId,
            timestamp = DateTime.UtcNow,
            durationMs = (DateTime.UtcNow - timestamp).TotalMilliseconds,
            response = SerializeAgentMessage(response)
        };

        var responseFile = Path.Combine(_recordingsDirectory, $"call-{callId:D4}.response.json");
        await File.WriteAllTextAsync(responseFile, JsonSerializer.Serialize(responseData, _jsonOptions), cancellationToken);

        return response;
    }

    public async IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var callId = ++_callCount;
        var timestamp = DateTime.UtcNow;
        var deltas = new List<object>();

        // Record request
        var requestData = new
        {
            callId,
            timestamp,
            streaming = true,
            conversationHistory = SerializeMessages(conversationHistory),
            availableTools = availableTools?.Select(t => new
            {
                t.Type,
                function = new
                {
                    t.Function.Name,
                    t.Function.Description,
                    parameters = t.Function.Parameters
                }
            }).ToArray(),
            providerInfo = ProviderInfo
        };

        var requestFile = Path.Combine(_recordingsDirectory, $"call-{callId:D4}.request.json");
        await File.WriteAllTextAsync(requestFile, JsonSerializer.Serialize(requestData, _jsonOptions), cancellationToken);

        // Stream and record deltas
        await foreach (var delta in _innerClient.StreamAsync(conversationHistory, availableTools, cancellationToken))
        {
            deltas.Add(new
            {
                delta.MessageId,
                type = delta.Type.ToString(),
                content = delta.Content != null ? SerializeContent(delta.Content) : null,
                toolCall = delta.ToolCall != null ? new
                {
                    delta.ToolCall.CallId,
                    delta.ToolCall.Name,
                    delta.ToolCall.Arguments
                } : null,
                delta.IsComplete
            });

            yield return delta;
        }

        // Record streaming response
        var responseData = new
        {
            callId,
            timestamp = DateTime.UtcNow,
            durationMs = (DateTime.UtcNow - timestamp).TotalMilliseconds,
            streaming = true,
            deltas
        };

        var responseFile = Path.Combine(_recordingsDirectory, $"call-{callId:D4}.response.json");
        await File.WriteAllTextAsync(responseFile, JsonSerializer.Serialize(responseData, _jsonOptions), cancellationToken);
    }

    private object SerializeMessages(List<ChatMessage> messages)
    {
        return messages.Select(m => new
        {
            type = m.GetType().Name,
            role = m switch
            {
                SystemMessage => "system",
                UserMessage => "user",
                AgentMessage => "agent",
                ToolMessage => "tool",
                _ => "unknown"
            },
            contents = m.Contents.Select(SerializeContent).ToArray()
        }).ToArray();
    }

    private object SerializeAgentMessage(AgentMessage message)
    {
        return new
        {
            message.MessageId,
            contents = message.Contents.Select(SerializeContent).ToArray()
        };
    }

    private object SerializeContent(AIContent content)
    {
        return content switch
        {
            TextContent text => new { type = "text", text.Text },
            FunctionCallContent func => new { type = "function_call", func.CallId, func.Name, func.Arguments },
            FunctionResultContent result => new { type = "function_result", result.CallId, result.Result },
            ImageContent image => new { type = "image", image.Uri },
            _ => new { type = content.GetType().Name }
        };
    }
}
