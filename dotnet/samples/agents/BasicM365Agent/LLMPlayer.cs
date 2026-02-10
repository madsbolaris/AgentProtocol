// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.ClientModel;
using System.ClientModel.Primitives;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using OpenAI.Chat;

namespace BasicM365Sample;

/// <summary>
/// Replays recorded LLM responses for deterministic testing.
/// Based on Python's MockLLMClient implementation.
/// </summary>
public class LLMPlayer
{
    private readonly string _recordingsDir;
    private readonly LLMRecorder _recorder;
    private int _callCount = 0;

    public LLMPlayer(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));
        if (!Directory.Exists(_recordingsDir))
        {
            throw new DirectoryNotFoundException($"Recordings directory not found: {_recordingsDir}");
        }
        _recorder = new LLMRecorder(_recordingsDir);
    }

    /// <summary>
    /// Replay a recorded LLM response.
    /// </summary>
    public async Task<ChatCompletion> ReplayAsync(
        string model,
        IEnumerable<ChatMessage> messages,
        IEnumerable<ChatTool>? tools = null,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);

        // Generate hash to find recording
        var hashKey = _recorder.HashRequest(model, messages, tools);

        // Load recorded response
        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        if (!File.Exists(responseFile))
        {
            throw new FileNotFoundException(
                $"No recorded LLM response found for request hash: {hashKey}\n" +
                $"Expected file: {responseFile}\n\n" +
                $"This usually means:\n" +
                $"1. Tests need to be run in generation mode first: RECORD_LLM=true\n" +
                $"2. The request parameters have changed (different hash)\n" +
                $"3. The recording file was deleted\n\n" +
                $"Request details:\n" +
                $"  Model: {model}\n" +
                $"  Messages: {messages.Count()} messages\n" +
                $"  Tools: {tools?.Count() ?? 0} tools\n",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying LLM call #{callId}: {hashKey}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseData = JsonDocument.Parse(responseJson);

        // Convert recorded response to ChatCompletion
        return ConvertToChatCompletion(responseData.RootElement);
    }

    private ChatCompletion ConvertToChatCompletion(JsonElement responseElement)
    {
        // The recorded response has structure:
        // {
        //   "callId": 1,
        //   "timestamp": "...",
        //   "hash": "...",
        //   "response": {
        //     "id": "...",
        //     "model": "...",
        //     "created": "...",
        //     "finishReason": "Stop|ToolCalls",
        //     "content": [{ "text": "..." }],
        //     "toolCalls": [...]
        //   }
        // }

        var response = responseElement.GetProperty("response");

        var id = response.GetProperty("id").GetString() ?? "mock-completion";
        var model = response.GetProperty("model").GetString() ?? "unknown";
        var finishReasonStr = response.GetProperty("finishReason").GetString() ?? "Stop";

        // Parse finish reason
        ChatFinishReason finishReason = finishReasonStr switch
        {
            "ToolCalls" => ChatFinishReason.ToolCalls,
            "Stop" => ChatFinishReason.Stop,
            "Length" => ChatFinishReason.Length,
            _ => ChatFinishReason.Stop
        };

        // Parse content
        var contentList = new List<ChatMessageContentPart>();
        if (response.TryGetProperty("content", out var contentArray) && contentArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var contentItem in contentArray.EnumerateArray())
            {
                if (contentItem.TryGetProperty("text", out var textElement))
                {
                    var text = textElement.GetString();
                    if (!string.IsNullOrEmpty(text))
                    {
                        contentList.Add(ChatMessageContentPart.CreateTextPart(text));
                    }
                }
            }
        }

        // Parse tool calls
        var toolCallsList = new List<ChatToolCall>();
        if (response.TryGetProperty("toolCalls", out var toolCallsArray) && toolCallsArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var toolCallItem in toolCallsArray.EnumerateArray())
            {
                var toolCallId = toolCallItem.GetProperty("id").GetString() ?? "mock-tool-call";
                var function = toolCallItem.GetProperty("function");
                var functionName = function.GetProperty("name").GetString() ?? "unknown";
                var functionArgs = function.GetProperty("arguments").GetString() ?? "{}";

                toolCallsList.Add(ChatToolCall.CreateFunctionToolCall(
                    toolCallId,
                    functionName,
                    BinaryData.FromString(functionArgs)
                ));
            }
        }

        // Create a mock ChatCompletion
        // Note: We need to use reflection or create a mock because ChatCompletion constructor is internal
        return ChatModelFactory.CreateChatCompletion(
            id: id,
            model: model,
            createdAt: DateTimeOffset.UtcNow,
            fingerprint: null,
            finishReason: finishReason,
            contentTokenLogProbabilities: Array.Empty<ChatTokenLogProbabilityDetails>(),
            refusalTokenLogProbabilities: Array.Empty<ChatTokenLogProbabilityDetails>(),
            content: contentList,
            toolCalls: toolCallsList,
            refusal: null,
            usage: null
        );
    }
}

/// <summary>
/// Factory for creating ChatCompletion instances (for testing).
/// </summary>
internal static class ChatModelFactory
{
    public static ChatCompletion CreateChatCompletion(
        string id,
        string model,
        DateTimeOffset createdAt,
        string? fingerprint,
        ChatFinishReason finishReason,
        IEnumerable<ChatTokenLogProbabilityDetails> contentTokenLogProbabilities,
        IEnumerable<ChatTokenLogProbabilityDetails> refusalTokenLogProbabilities,
        IEnumerable<ChatMessageContentPart> content,
        IEnumerable<ChatToolCall> toolCalls,
        string? refusal,
        ChatTokenUsage? usage)
    {
        // Construct OpenAI-compatible response JSON and deserialize using SDK
        var toolCallsArray = toolCalls.Any() ? toolCalls.Select(tc => new
        {
            id = tc.Id,
            type = "function",
            function = new
            {
                name = tc.FunctionName,
                arguments = tc.FunctionArguments.ToString()
            }
        }).ToArray() : null;

        // Convert finish reason to OpenAI API format
        string finishReasonString = finishReason switch
        {
            ChatFinishReason.ToolCalls => "tool_calls",
            ChatFinishReason.Stop => "stop",
            ChatFinishReason.Length => "length",
            _ => "stop"
        };

        // When there are tool calls, content should be null, not empty string
        object? contentValue = toolCallsArray != null ? null : (content.FirstOrDefault()?.Text ?? "");

        var responseObj = new
        {
            id = id,
            @object = "chat.completion",
            created = createdAt.ToUnixTimeSeconds(),
            model = model,
            choices = new[]
            {
                new
                {
                    index = 0,
                    message = new
                    {
                        role = "assistant",
                        content = contentValue,
                        tool_calls = toolCallsArray
                    },
                    finish_reason = finishReasonString
                }
            },
            usage = new
            {
                prompt_tokens = 0,
                completion_tokens = 0,
                total_tokens = 0
            }
        };

        var responseJson = JsonSerializer.Serialize(responseObj);

        try
        {
            // Use ModelReaderWriter to deserialize - this is the proper way for SDK types
            var jsonData = BinaryData.FromString(responseJson);
            var result = ModelReaderWriter.Read<ChatCompletion>(jsonData);
            if (result != null)
            {
                return result;
            }

            throw new InvalidOperationException("ModelReaderWriter returned null");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  Failed to deserialize ChatCompletion: {ex.Message}");
            Console.WriteLine($"   JSON: {responseJson}");
            throw new InvalidOperationException(
                $"Failed to create ChatCompletion from recorded data. Content: {string.Join(" ", content.Select(c => c.Text))}",
                ex);
        }
    }
}
