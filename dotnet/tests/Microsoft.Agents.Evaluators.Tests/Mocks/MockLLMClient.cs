// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace Microsoft.Agents.Evaluators.Tests.Mocks;

/// <summary>
/// Mock LLM client that replays recorded responses for deterministic testing.
/// Based on Python's MockLLMClient and the pattern from BasicM365Agent's LLMPlayer.
/// </summary>
public class MockLLMClient
{
    private readonly string _recordingsDir;
    private int _callCount = 0;

    public int CallCount => _callCount;

    public MockLLMClient(string recordingsDir)
    {
        _recordingsDir = recordingsDir ?? throw new ArgumentNullException(nameof(recordingsDir));

        if (!Directory.Exists(_recordingsDir))
        {
            throw new DirectoryNotFoundException(
                $"Recordings directory not found: {_recordingsDir}\n\n" +
                $"Please ensure LLM recordings exist for eval tests.\n" +
                $"Run generation mode first to create recordings.");
        }
    }

    /// <summary>
    /// Create a chat completion using recorded response.
    /// </summary>
    public async Task<MockChatCompletion> CreateChatCompletionAsync(
        string model,
        List<MockChatMessage> messages,
        List<MockTool>? tools = null,
        float temperature = 0.0f,
        int? seed = null,
        CancellationToken cancellationToken = default)
    {
        var callId = Interlocked.Increment(ref _callCount);

        // Generate hash to find recording
        var hashKey = HashRequest(model, messages, tools, temperature, seed);

        // Load recorded response
        var responseFile = Path.Combine(_recordingsDir, $"{hashKey}.response.json");
        if (!File.Exists(responseFile))
        {
            throw new FileNotFoundException(
                $"No recorded LLM response found for request hash: {hashKey}\n" +
                $"Expected file: {responseFile}\n\n" +
                $"This usually means:\n" +
                $"1. Tests need to be run in generation mode first\n" +
                $"2. The request parameters have changed (different hash)\n" +
                $"3. The recording file was deleted\n\n" +
                $"Request details:\n" +
                $"  Model: {model}\n" +
                $"  Messages: {messages.Count} messages\n" +
                $"  Tools: {tools?.Count ?? 0} tools\n" +
                $"  Temperature: {temperature}\n" +
                $"  Seed: {seed}\n",
                responseFile);
        }

        Console.WriteLine($"  ▶️  Replaying LLM call #{callId}: {hashKey}");

        var responseJson = await File.ReadAllTextAsync(responseFile, cancellationToken);
        var responseDoc = JsonDocument.Parse(responseJson);

        return MockChatCompletion.FromJson(responseDoc.RootElement);
    }

    /// <summary>
    /// Generate deterministic hash for LLM request.
    /// Matches the algorithm used in Python's LLMRecorder.
    /// </summary>
    public string HashRequest(
        string model,
        List<MockChatMessage> messages,
        List<MockTool>? tools = null,
        float temperature = 0.0f,
        int? seed = null)
    {
        // Normalize request for hashing
        var normalized = new Dictionary<string, object>
        {
            ["model"] = model,
            ["messages"] = NormalizeMessages(messages),
            ["temperature"] = temperature,
            ["seed"] = seed ?? (object)"null"
        };

        if (tools != null && tools.Any())
        {
            normalized["tools"] = NormalizeTools(tools);
        }

        // Convert to JSON string with sorted keys
        var json = JsonSerializer.Serialize(normalized, new JsonSerializerOptions
        {
            WriteIndented = false,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        // Sort keys for determinism
        using var doc = JsonDocument.Parse(json);
        var sortedJson = SortJsonKeys(doc.RootElement);

        // Generate SHA256 hash and take first 16 chars
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(sortedJson));
        return Convert.ToHexString(hash)[..16].ToLowerInvariant();
    }

    private List<Dictionary<string, object>> NormalizeMessages(List<MockChatMessage> messages)
    {
        return messages.Select(msg =>
        {
            var normalized = new Dictionary<string, object>
            {
                ["role"] = msg.Role,
                ["content"] = msg.Content ?? ""
            };

            if (msg.ToolCalls != null && msg.ToolCalls.Any())
            {
                normalized["tool_calls"] = msg.ToolCalls.Select(tc => new Dictionary<string, object>
                {
                    ["id"] = tc.Id,
                    ["type"] = tc.Type,
                    ["function"] = new Dictionary<string, object>
                    {
                        ["name"] = tc.Function.Name,
                        ["arguments"] = tc.Function.Arguments
                    }
                }).ToList();
            }

            if (!string.IsNullOrEmpty(msg.ToolCallId))
            {
                normalized["tool_call_id"] = msg.ToolCallId;
            }

            if (!string.IsNullOrEmpty(msg.Name))
            {
                normalized["name"] = msg.Name;
            }

            return normalized;
        }).ToList();
    }

    private List<Dictionary<string, object>> NormalizeTools(List<MockTool> tools)
    {
        return tools.Select(tool => new Dictionary<string, object>
        {
            ["type"] = "function",
            ["function"] = new Dictionary<string, object>
            {
                ["name"] = tool.Function.Name,
                ["description"] = tool.Function.Description ?? "",
                ["parameters"] = string.IsNullOrEmpty(tool.Function.Parameters)
                    ? new Dictionary<string, object>()
                    : JsonSerializer.Deserialize<Dictionary<string, object>>(tool.Function.Parameters)!
            }
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

/// <summary>
/// Mock chat completion response.
/// </summary>
public class MockChatCompletion
{
    public string Id { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public string FinishReason { get; set; } = "stop";
    public List<MockContentPart> Content { get; set; } = new();
    public List<MockToolCall> ToolCalls { get; set; } = new();

    public static MockChatCompletion FromJson(JsonElement responseElement)
    {
        // Response structure: { callId, timestamp, hash, response: { ... } }
        var response = responseElement.GetProperty("response");

        var completion = new MockChatCompletion
        {
            Id = response.GetProperty("id").GetString() ?? "mock-completion",
            Model = response.GetProperty("model").GetString() ?? "unknown",
            FinishReason = response.GetProperty("finishReason").GetString() ?? "stop"
        };

        // Parse content
        if (response.TryGetProperty("content", out var contentArray) &&
            contentArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var contentItem in contentArray.EnumerateArray())
            {
                if (contentItem.TryGetProperty("text", out var textElement))
                {
                    var text = textElement.GetString();
                    if (!string.IsNullOrEmpty(text))
                    {
                        completion.Content.Add(new MockContentPart { Text = text });
                    }
                }
            }
        }

        // Parse tool calls
        if (response.TryGetProperty("toolCalls", out var toolCallsArray) &&
            toolCallsArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var toolCallItem in toolCallsArray.EnumerateArray())
            {
                var toolCall = new MockToolCall
                {
                    Id = toolCallItem.GetProperty("id").GetString() ?? "mock-tool-call",
                    Type = toolCallItem.GetProperty("type").GetString() ?? "function"
                };

                var function = toolCallItem.GetProperty("function");
                toolCall.Function = new MockFunction
                {
                    Name = function.GetProperty("name").GetString() ?? "unknown",
                    Arguments = function.GetProperty("arguments").GetString() ?? "{}"
                };

                completion.ToolCalls.Add(toolCall);
            }
        }

        return completion;
    }
}

/// <summary>
/// Mock content part.
/// </summary>
public class MockContentPart
{
    public string Text { get; set; } = string.Empty;
}

/// <summary>
/// Mock tool call.
/// </summary>
public class MockToolCall
{
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = "function";
    public MockFunction Function { get; set; } = new();
}

/// <summary>
/// Mock function.
/// </summary>
public class MockFunction
{
    public string Name { get; set; } = string.Empty;
    public string Arguments { get; set; } = "{}";
}

/// <summary>
/// Mock chat message.
/// </summary>
public class MockChatMessage
{
    public string Role { get; set; } = string.Empty;
    public string? Content { get; set; }
    public List<MockToolCall>? ToolCalls { get; set; }
    public string? ToolCallId { get; set; }
    public string? Name { get; set; }
}

/// <summary>
/// Mock tool definition.
/// </summary>
public class MockTool
{
    public string Type { get; set; } = "function";
    public MockFunctionDefinition Function { get; set; } = new();
}

/// <summary>
/// Mock function definition.
/// </summary>
public class MockFunctionDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Parameters { get; set; }
}
