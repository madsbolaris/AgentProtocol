// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.ClientModel;
using System.ClientModel.Primitives;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using OpenAI.Chat;

namespace BasicM365Sample;

/// <summary>
/// Testing wrapper for ChatClient that supports recording and playback of LLM interactions.
/// This enables deterministic testing by recording real LLM responses and playing them back.
/// </summary>
public class TestingChatClient
{
    private readonly ChatClient? _realClient;
    private readonly string _recordingsDir;
    private readonly string _modelId;
    private readonly bool _recordMode;
    private readonly bool _playbackMode;
    private int _callCount = 0;

    public TestingChatClient(
        ChatClient? realClient,
        string recordingsDir,
        string modelId,
        bool recordMode = false,
        bool playbackMode = false)
    {
        if (recordMode && playbackMode)
        {
            throw new InvalidOperationException("Cannot enable both record and playback mode simultaneously");
        }

        if (recordMode && realClient == null)
        {
            throw new ArgumentNullException(nameof(realClient), "Real client required for recording mode");
        }

        if (playbackMode && !Directory.Exists(recordingsDir))
        {
            throw new DirectoryNotFoundException($"Recordings directory not found: {recordingsDir}");
        }

        _realClient = realClient;
        _recordingsDir = recordingsDir;
        _modelId = modelId;
        _recordMode = recordMode;
        _playbackMode = playbackMode;

        if (_recordMode)
        {
            Directory.CreateDirectory(_recordingsDir);
            Console.WriteLine($"📹 LLM Recording enabled: {_recordingsDir}");
        }
        else if (_playbackMode)
        {
            Console.WriteLine($"▶️  LLM Playback enabled: {_recordingsDir}");
            Console.WriteLine("   Using recorded LLM responses (test mode)");
        }
    }

    public async Task<ChatCompletion> CompleteChatAsync(
        IEnumerable<ChatMessage> messages,
        ChatCompletionOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);
        var hashKey = ComputeRequestHash(messages, options);

        if (_playbackMode)
        {
            return await PlaybackResponseAsync(callId, hashKey, messages, options, cancellationToken);
        }

        // Call real LLM (works in both normal and recording mode)
        if (_realClient == null)
        {
            throw new InvalidOperationException("Real client not available. Use recording mode with a valid ChatClient.");
        }

        var response = await _realClient.CompleteChatAsync(messages, options, cancellationToken);

        if (_recordMode)
        {
            await RecordInteractionAsync(callId, hashKey, messages, options, response);
        }

        return response;
    }

    private async Task<ChatCompletion> PlaybackResponseAsync(
        int callId,
        string hashKey,
        IEnumerable<ChatMessage> messages,
        ChatCompletionOptions? options,
        CancellationToken cancellationToken)
    {
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
                $"  Messages: {messages.Count()} messages\n" +
                $"  Options: {(options != null ? "provided" : "null")}\n",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying LLM call #{callId}: {hashKey}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseData = JsonDocument.Parse(responseJson);

        return DeserializeChatCompletion(responseData.RootElement.GetProperty("response"));
    }

    private async Task RecordInteractionAsync(
        int callId,
        string hashKey,
        IEnumerable<ChatMessage> messages,
        ChatCompletionOptions? options,
        ChatCompletion response)
    {
        Console.WriteLine($"  📹 Recording LLM call #{callId}: {hashKey}");

        // Save request
        var requestFile = Path.Combine(_recordingsDir, $"{hashKey}.request.json");
        var requestData = new
        {
            callId,
            timestamp = DateTime.UtcNow,
            hash = hashKey,
            model = _modelId,
            messages = NormalizeMessages(messages),
            tools = options?.Tools?.Select(t => new
            {
                type = "function",
                function = new
                {
                    name = t.FunctionName,
                    description = t.FunctionDescription,
                    parameters = JsonSerializer.Deserialize<JsonElement>(t.FunctionParameters?.ToString() ?? "{}")
                }
            }).ToArray()
        };

        await File.WriteAllTextAsync(requestFile,
            JsonSerializer.Serialize(requestData, new JsonSerializerOptions { WriteIndented = true }));

        // Save response
        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        var responseData = new
        {
            callId,
            timestamp = DateTime.UtcNow,
            hash = hashKey,
            response = new
            {
                id = response.Id,
                model = response.Model,
                created = response.CreatedAt,
                finishReason = response.FinishReason.ToString(),
                content = response.Content.Select(c => new { text = c.Text }).ToArray(),
                toolCalls = response.ToolCalls.Select(tc => new
                {
                    id = tc.Id,
                    type = "Function",
                    function = new
                    {
                        name = tc.FunctionName,
                        arguments = tc.FunctionArguments.ToString()
                    }
                }).ToArray()
            }
        };

        await File.WriteAllTextAsync(responseFile,
            JsonSerializer.Serialize(responseData, new JsonSerializerOptions { WriteIndented = true }));
    }

    private string ComputeRequestHash(IEnumerable<ChatMessage> messages, ChatCompletionOptions? options)
    {
        // Use exact same hash algorithm as old LLMRecorder for compatibility
        var requestDict = new Dictionary<string, object>
        {
            ["model"] = _modelId,
            ["messages"] = NormalizeMessages(messages),
            ["temperature"] = 0.0f
        };

        if (options?.Tools != null && options.Tools.Any())
        {
            requestDict["tools"] = options.Tools.Select(t =>
            {
                // Parse and re-serialize parameters as compact JSON for consistent hashing
                string compactParams = "{}";
                if (t.FunctionParameters != null)
                {
                    using var doc = JsonDocument.Parse(t.FunctionParameters.ToString());
                    compactParams = JsonSerializer.Serialize(doc.RootElement, new JsonSerializerOptions
                    {
                        WriteIndented = false
                    });
                }

                return new
                {
                    type = "function",
                    function = new
                    {
                        name = t.FunctionName,
                        description = t.FunctionDescription,
                        parameters = compactParams
                    }
                };
            }).ToArray();
        }

        // Serialize to stable JSON (sorted keys, no whitespace)
        var serializerOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };
        var json = JsonSerializer.Serialize(requestDict, serializerOptions);

        // Sort keys by converting to sorted dictionary
        using var doc = JsonDocument.Parse(json);
        var sortedJson = SortJsonKeys(doc.RootElement);

        // Fix temperature formatting: ensure "temperature":0 becomes "temperature":0.0
        // This ensures consistency with Python's json.dumps() behavior
        sortedJson = System.Text.RegularExpressions.Regex.Replace(
            sortedJson,
            @"""temperature"":0(?![.0-9])",
            @"""temperature"":0.0"
        );

        // Log the JSON being hashed for debugging
        Console.WriteLine($"🔍 [C#] Computing hash for:");
        Console.WriteLine($"   JSON length: {sortedJson.Length} chars");
        Console.WriteLine($"   FULL JSON: {sortedJson}");
        System.IO.File.WriteAllText("/tmp/csharp_json.txt", sortedJson);

        // Hash and truncate (SHA256, first 16 chars)
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(sortedJson));
        var hashStr = Convert.ToHexString(hash)[..16].ToLowerInvariant();
        Console.WriteLine($"   Hash: {hashStr}");
        return hashStr;
    }

    private List<object> NormalizeMessages(IEnumerable<ChatMessage> messages)
    {
        return messages.Select(msg =>
        {
            var normalized = new Dictionary<string, object>
            {
                ["role"] = msg switch
                {
                    SystemChatMessage => "system",
                    UserChatMessage => "user",
                    AssistantChatMessage => "assistant",
                    ToolChatMessage => "tool",
                    _ => "unknown"
                }
            };

            // Extract content based on message type
            if (msg is SystemChatMessage systemMsg)
            {
                normalized["content"] = systemMsg.Content[0].Text;
            }
            else if (msg is UserChatMessage userMsg)
            {
                normalized["content"] = userMsg.Content[0].Text;
            }
            else if (msg is AssistantChatMessage assistantMsg)
            {
                if (assistantMsg.Content.Any())
                {
                    normalized["content"] = string.Join("", assistantMsg.Content.Select(c => c.Text));
                }
                if (assistantMsg.ToolCalls.Any())
                {
                    normalized["tool_calls"] = assistantMsg.ToolCalls.Select(tc => new
                    {
                        id = tc.Id,
                        type = tc.Kind.ToString(),
                        function = new
                        {
                            name = tc.FunctionName,
                            arguments = tc.FunctionArguments.ToString()
                        }
                    }).ToArray();
                }
            }
            else if (msg is ToolChatMessage toolMsg)
            {
                normalized["tool_call_id"] = toolMsg.ToolCallId;
                normalized["content"] = toolMsg.Content[0].Text;
            }

            return (object)normalized;
        }).ToList();
    }

    private string SortJsonKeys(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var sorted = new SortedDictionary<string, object>();
            foreach (var prop in element.EnumerateObject())
            {
                if (prop.Value.ValueKind == JsonValueKind.Object || prop.Value.ValueKind == JsonValueKind.Array)
                {
                    sorted[prop.Name] = JsonSerializer.Deserialize<object>(SortJsonKeys(prop.Value))!;
                }
                else
                {
                    sorted[prop.Name] = JsonSerializer.Deserialize<object>(prop.Value.GetRawText())!;
                }
            }
            return JsonSerializer.Serialize(sorted);
        }
        else if (element.ValueKind == JsonValueKind.Array)
        {
            var array = element.EnumerateArray()
                .Select(item => item.ValueKind == JsonValueKind.Object || item.ValueKind == JsonValueKind.Array
                    ? JsonSerializer.Deserialize<object>(SortJsonKeys(item))!
                    : JsonSerializer.Deserialize<object>(item.GetRawText())!)
                .ToArray();
            return JsonSerializer.Serialize(array);
        }
        else
        {
            return element.GetRawText();
        }
    }

    private ChatCompletion DeserializeChatCompletion(JsonElement responseElement)
    {
        var id = responseElement.GetProperty("id").GetString() ?? "mock-completion";
        var model = responseElement.GetProperty("model").GetString() ?? "unknown";
        var finishReasonStr = responseElement.GetProperty("finishReason").GetString() ?? "Stop";

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
        if (responseElement.TryGetProperty("content", out var contentArray) &&
            contentArray.ValueKind == JsonValueKind.Array)
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
        if (responseElement.TryGetProperty("toolCalls", out var toolCallsArray) &&
            toolCallsArray.ValueKind == JsonValueKind.Array)
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

        // Create ChatCompletion using OpenAI SDK deserialization
        var toolCallsForSerialization = toolCallsList.Any() ? toolCallsList.Select(tc => new
        {
            id = tc.Id,
            type = "function",
            function = new
            {
                name = tc.FunctionName,
                arguments = tc.FunctionArguments.ToString()
            }
        }).ToArray() : null;

        // Map finish reason to OpenAI format (with underscores)
        var finishReasonFormatted = finishReason switch
        {
            ChatFinishReason.ToolCalls => "tool_calls",
            ChatFinishReason.Stop => "stop",
            ChatFinishReason.Length => "length",
            ChatFinishReason.ContentFilter => "content_filter",
            _ => "stop"
        };

        var responseObj = new
        {
            id,
            @object = "chat.completion",
            created = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            model,
            choices = new[]
            {
                new
                {
                    index = 0,
                    message = new
                    {
                        role = "assistant",
                        content = contentList.FirstOrDefault()?.Text ?? "",
                        tool_calls = toolCallsForSerialization
                    },
                    finish_reason = finishReasonFormatted
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
                $"Failed to create ChatCompletion from recorded data.",
                ex);
        }
    }
}
