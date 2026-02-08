// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
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
/// Records LLM request/response pairs for test replay.
/// Based on Python's LLMRecorder implementation.
/// </summary>
public class LLMRecorder
{
    private readonly string _recordingsDir;
    private int _callCount = 0;
    private readonly JsonSerializerOptions _jsonOptions;

    public LLMRecorder(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));
        Directory.CreateDirectory(_recordingsDir);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };
    }

    /// <summary>
    /// Generate deterministic hash from request parameters.
    /// </summary>
    public string HashRequest(
        string model,
        IEnumerable<ChatMessage> messages,
        IEnumerable<ChatTool>? tools = null,
        float temperature = 0.0f)
    {
        // Build canonical request representation
        var requestDict = new Dictionary<string, object>
        {
            ["model"] = model,
            ["messages"] = NormalizeMessages(messages),
            ["temperature"] = temperature
        };

        if (tools != null && tools.Any())
        {
            requestDict["tools"] = tools.Select(t => new
            {
                type = "function",
                function = new
                {
                    name = t.FunctionName,
                    description = t.FunctionDescription,
                    parameters = t.FunctionParameters?.ToString() ?? "{}"
                }
            }).ToArray();
        }

        // Serialize to stable JSON (sorted keys, no whitespace)
        var json = JsonSerializer.Serialize(requestDict, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        });

        // Sort keys by converting to sorted dictionary
        using var doc = JsonDocument.Parse(json);
        var sortedJson = SortJsonKeys(doc.RootElement);

        // Hash and truncate
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(sortedJson));
        return Convert.ToHexString(hash)[..16].ToLowerInvariant();
    }

    /// <summary>
    /// Record an LLM request/response pair.
    /// </summary>
    public async Task RecordAsync(
        string model,
        IEnumerable<ChatMessage> messages,
        IEnumerable<ChatTool>? tools,
        ChatCompletion response,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);
        var timestamp = DateTime.UtcNow;

        var hashKey = HashRequest(model, messages, tools);

        // Record request
        var requestData = new
        {
            callId,
            timestamp,
            hash = hashKey,
            model,
            messages = NormalizeMessages(messages),
            tools = tools?.Select(t => new
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

        var requestFile = Path.Combine(_recordingsDir, $"{hashKey}.request.json");
        await File.WriteAllTextAsync(
            requestFile,
            JsonSerializer.Serialize(requestData, _jsonOptions),
            cancellationToken);

        // Record response
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
                    type = tc.Kind.ToString(),
                    function = new
                    {
                        name = tc.FunctionName,
                        arguments = tc.FunctionArguments.ToString()
                    }
                }).ToArray()
            }
        };

        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        await File.WriteAllTextAsync(
            responseFile,
            JsonSerializer.Serialize(responseData, _jsonOptions),
            cancellationToken);
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
                .Select(item => JsonSerializer.Deserialize<object>(
                    item.ValueKind == JsonValueKind.Object || item.ValueKind == JsonValueKind.Array
                        ? SortJsonKeys(item)
                        : item.GetRawText())!)
                .ToArray();
            return JsonSerializer.Serialize(array);
        }

        return element.GetRawText();
    }
}
