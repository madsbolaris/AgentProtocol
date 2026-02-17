using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Model;

namespace Microsoft.Agents.Protocol.Hosting.Tests.Recording;

/// <summary>
/// Replays recorded LLM interactions for deterministic testing.
/// Reads recordings created by RecordingProtocolLLMClient.
/// </summary>
public class ReplayProtocolLlmClient : IProtocolLLMClient
{
    private readonly string _recordingsDir;
    private int _callCount = 0;

    public ReplayProtocolLlmClient(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));
        if (!Directory.Exists(_recordingsDir))
        {
            throw new DirectoryNotFoundException(
                $"Recordings directory not found: {_recordingsDir}\n\n" +
                $"Please run tests in RECORD_LLM=true mode first to create recordings.");
        }
    }

    public LLMProviderInfo ProviderInfo => new LLMProviderInfo
    {
        Name = "ReplayClient",
        Model = "recorded-responses"
    };

    public async Task<AgentMessage> GenerateAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);

        // Find the recording file for this call
        var responseFile = Path.Combine(_recordingsDir, $"call-{callId:D4}.response.json");

        if (!File.Exists(responseFile))
        {
            throw new FileNotFoundException(
                $"No recorded LLM response found for call #{callId}\n" +
                $"Expected file: {responseFile}\n\n" +
                $"This usually means:\n" +
                $"1. Tests need to be run in RECORD_LLM=true mode first\n" +
                $"2. The number of LLM calls has changed\n" +
                $"3. The recording file was deleted\n",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying LLM call #{callId}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseDoc = JsonDocument.Parse(responseJson);
        var response = responseDoc.RootElement.GetProperty("response");

        // Reconstruct AgentMessage from recording
        var message = new AgentMessage
        {
            MessageId = response.TryGetProperty("messageId", out var msgId)
                ? msgId.GetString()
                : $"replay-msg-{callId}",
            Contents = new List<AIContent>()
        };

        // Parse contents
        if (response.TryGetProperty("contents", out var contents) &&
            contents.ValueKind == JsonValueKind.Array)
        {
            foreach (var content in contents.EnumerateArray())
            {
                var type = content.GetProperty("type").GetString();

                switch (type)
                {
                    case "text":
                        message.Contents.Add(new TextContent
                        {
                            Text = content.GetProperty("text").GetString() ?? ""
                        });
                        break;

                    case "function_call":
                        message.Contents.Add(new FunctionCallContent
                        {
                            CallId = content.GetProperty("callId").GetString() ?? "",
                            Name = content.GetProperty("name").GetString() ?? "",
                            Arguments = content.GetProperty("arguments").GetString() ?? "{}"
                        });
                        break;

                    case "function_result":
                        message.Contents.Add(new FunctionResultContent
                        {
                            CallId = content.GetProperty("callId").GetString() ?? "",
                            Result = content.GetProperty("result").GetString() ?? ""
                        });
                        break;

                    case "image":
                        message.Contents.Add(new ImageContent
                        {
                            Uri = content.GetProperty("uri").GetString() ?? ""
                        });
                        break;
                }
            }
        }

        return message;
    }

    public async IAsyncEnumerable<AgentMessageDelta> StreamAsync(
        List<ChatMessage> conversationHistory,
        ToolDefinition[]? availableTools = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);

        // Find the recording file for this call
        var responseFile = Path.Combine(_recordingsDir, $"call-{callId:D4}.response.json");

        if (!File.Exists(responseFile))
        {
            throw new FileNotFoundException(
                $"No recorded LLM streaming response found for call #{callId}\n" +
                $"Expected file: {responseFile}",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying LLM streaming call #{callId}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseDoc = JsonDocument.Parse(responseJson);

        // Check if this is a streaming response
        if (!responseDoc.RootElement.TryGetProperty("streaming", out var streaming) ||
            !streaming.GetBoolean())
        {
            throw new InvalidOperationException(
                $"Recording for call #{callId} is not a streaming response");
        }

        // Replay deltas
        var deltas = responseDoc.RootElement.GetProperty("deltas");
        foreach (var delta in deltas.EnumerateArray())
        {
            var messageId = delta.TryGetProperty("messageId", out var msgId)
                ? msgId.GetString() ?? ""
                : "";

            var typeStr = delta.GetProperty("type").GetString() ?? "";
            var deltaType = Enum.Parse<AgentMessageDeltaType>(typeStr);

            AIContent? content = null;
            if (delta.TryGetProperty("content", out var contentElement) &&
                contentElement.ValueKind != JsonValueKind.Null)
            {
                var contentType = contentElement.GetProperty("type").GetString();
                content = contentType switch
                {
                    "text" => new TextContent { Text = contentElement.GetProperty("text").GetString() ?? "" },
                    "image" => new ImageContent { Uri = contentElement.GetProperty("uri").GetString() ?? "" },
                    _ => null
                };
            }

            FunctionCallContent? toolCall = null;
            if (delta.TryGetProperty("toolCall", out var toolCallElement) &&
                toolCallElement.ValueKind != JsonValueKind.Null)
            {
                toolCall = new FunctionCallContent
                {
                    CallId = toolCallElement.GetProperty("callId").GetString() ?? "",
                    Name = toolCallElement.GetProperty("name").GetString() ?? "",
                    Arguments = toolCallElement.GetProperty("arguments").GetString() ?? "{}"
                };
            }

            var isComplete = delta.TryGetProperty("isComplete", out var complete) && complete.GetBoolean();

            yield return new AgentMessageDelta
            {
                MessageId = messageId,
                Type = deltaType,
                Content = content,
                ToolCall = toolCall,
                IsComplete = isComplete
            };
        }
    }
}
