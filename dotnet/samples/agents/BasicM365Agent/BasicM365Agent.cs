// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using Microsoft.Agents.Builder;
using Microsoft.Agents.Builder.App;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;
using OpenAI;
using OpenAI.Chat;
using System;
using System.ClientModel;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Threading;

#pragma warning disable OPENAI001

namespace BasicM365Sample;

public class BasicM365Agent : AgentApplication
{
    private readonly HttpClient _httpClient;
    private readonly Random _random = new();
    private readonly ChatClient? _chatClient;
    private readonly Dictionary<string, List<ChatMessage>> _conversationHistory = new();
    private readonly LLMRecorder? _recorder;
    private readonly LLMPlayer? _player;
    private readonly string _model;
    private readonly bool _useRecordings;

    public BasicM365Agent(AgentApplicationOptions options, HttpClient httpClient) : base(options)
    {
        _httpClient = httpClient;

        // ============================================================================
        // ENVIRONMENT VARIABLES - Set automatically by scripts/ci/start_samples.py
        // ============================================================================
        // These environment variables are loaded from .env file at repo root:
        //   - FOUNDRY_ENDPOINT: LLM endpoint URL
        //   - FOUNDRY_API_KEY: API key for authentication
        //   - FOUNDRY_MODEL_DEPLOYMENT: Model name (default: gpt-5-nano)
        //   - USE_LLM_RECORDINGS: Set to "true" for test mode (replays recordings)
        //   - RECORD_LLM: Set to "true" to record LLM interactions
        //
        // Developers should NEVER manually set these variables.
        // Use: python3 scripts/ci/start_samples.py basic-m365 --lang dotnet --ui
        // ============================================================================

        // Check if we should use LLM recordings (test mode)
        var useRecordings = Environment.GetEnvironmentVariable("USE_LLM_RECORDINGS");
        _useRecordings = !string.IsNullOrEmpty(useRecordings) && useRecordings.Equals("true", StringComparison.OrdinalIgnoreCase);

        // Find recordings directory (navigate up to repo root)
        var repoRoot = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(),
            "..", "..", "..", ".."
        ));
        var recordingsDir = Path.Combine(repoRoot, "test-data", "llm-recordings", "basic-m365");

        if (_useRecordings)
        {
            // Test mode: Use recorded LLM responses
            _model = "gpt-5-nano"; // Default model for recordings
            _player = new LLMPlayer(recordingsDir);
            Console.WriteLine($"▶️  LLM Playback enabled: {recordingsDir}");
            Console.WriteLine("   Using recorded LLM responses (test mode)");
        }
        else
        {
            // Generation mode: Use real LLM and optionally record
            var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT")
                ?? throw new InvalidOperationException("FOUNDRY_ENDPOINT environment variable is required");
            var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY")
                ?? throw new InvalidOperationException("FOUNDRY_API_KEY environment variable is required");
            _model = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT") ?? "gpt-5-nano";

            // Create ChatClient for Foundry
            _chatClient = new ChatClient(
                credential: new ApiKeyCredential(apiKey),
                model: _model,
                options: new OpenAIClientOptions()
                {
                    Endpoint = new Uri($"{endpoint}/openai/v1/")
                });

            // Check if LLM recording is enabled
            var recordLlm = Environment.GetEnvironmentVariable("RECORD_LLM");
            if (!string.IsNullOrEmpty(recordLlm) && recordLlm.Equals("true", StringComparison.OrdinalIgnoreCase))
            {
                Directory.CreateDirectory(recordingsDir);
                _recorder = new LLMRecorder(recordingsDir);
                Console.WriteLine($"📹 LLM Recording enabled: {recordingsDir}");
            }
        }

        OnConversationUpdate(ConversationUpdateEvents.MembersAdded, WelcomeMessageAsync);
        OnActivity(ActivityTypes.Message, OnMessageAsync, rank: RouteRank.Last);
    }

    private async Task WelcomeMessageAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken cancellationToken)
    {
        foreach (ChannelAccount member in turnContext.Activity.MembersAdded)
        {
            if (member.Id != turnContext.Activity.Recipient.Id)
            {
                await turnContext.SendActivityAsync(
                    MessageFactory.Text("Hello! I'm a Basic M365 Agent. I can help you with weather and time information. Try asking: 'What's the weather in Seattle?' or 'What time is it?'"),
                    cancellationToken);
            }
        }
    }

    private async Task OnMessageAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken cancellationToken)
    {
        // Extract role from ChannelData (default to "user" if not present)
        var role = "user";
        if (turnContext.Activity.ChannelData != null)
        {
            try
            {
                var channelDataJson = JsonSerializer.Serialize(turnContext.Activity.ChannelData);
                using var doc = JsonDocument.Parse(channelDataJson);
                if (doc.RootElement.TryGetProperty("role", out var roleElement))
                {
                    role = roleElement.GetString() ?? "user";
                }
            }
            catch
            {
                // If parsing fails, default to "user"
            }
        }

        // Only respond to user messages
        if (role != "user")
        {
            return;
        }

        var userMessage = turnContext.Activity.Text ?? "";
        var conversationId = turnContext.Activity.Conversation.Id;

        // Initialize conversation history if needed
        if (!_conversationHistory.ContainsKey(conversationId))
        {
            _conversationHistory[conversationId] = new List<ChatMessage>
            {
                new SystemChatMessage("You are a helpful assistant that can check the weather and tell the time. Use the available functions to help users.")
            };
        }

        // Add user message to history
        _conversationHistory[conversationId].Add(new UserChatMessage(userMessage));

        // Track the starting index to capture new messages generated during this turn
        var startingHistoryCount = _conversationHistory[conversationId].Count;

        // Define available functions
        var tools = new List<ChatTool>
        {
            ChatTool.CreateFunctionTool(
                functionName: "GetWeatherAsync",
                functionDescription: "Get the weather for a given location.",
                functionParameters: BinaryData.FromString("""
                {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get the weather for."
                        }
                    },
                    "required": ["location"]
                }
                """)),
            ChatTool.CreateFunctionTool(
                functionName: "GetCurrentTime",
                functionDescription: "Get the current UTC time.",
                functionParameters: BinaryData.FromString("""
                {
                    "type": "object",
                    "properties": {}
                }
                """))
        };

        // Call LLM with function calling in a loop
        var chatOptions = new ChatCompletionOptions();
        foreach (var tool in tools)
        {
            chatOptions.Tools.Add(tool);
        }

        var response = "";
        var maxIterations = 5; // Prevent infinite loops
        var iteration = 0;

        while (iteration < maxIterations)
        {
            iteration++;

            // Get completion from LLM (either real or replayed)
            ChatCompletion completion;
            if (_useRecordings && _player != null)
            {
                // Test mode: Replay recorded response
                completion = await _player.ReplayAsync(_model, _conversationHistory[conversationId], chatOptions.Tools, cancellationToken);
            }
            else if (_chatClient != null)
            {
                // Generation mode: Use real LLM
                var completionResult = await _chatClient.CompleteChatAsync(_conversationHistory[conversationId], chatOptions, cancellationToken);
                completion = completionResult.Value;

                // Record LLM interaction if recorder is enabled
                if (_recorder != null)
                {
                    await _recorder.RecordAsync(_model, _conversationHistory[conversationId], chatOptions.Tools, completion, cancellationToken);
                }
            }
            else
            {
                throw new InvalidOperationException("Neither ChatClient nor LLMPlayer is available");
            }

            // Check if the model wants to call functions
            if (completion.FinishReason == ChatFinishReason.ToolCalls)
            {
                // Add assistant message with tool calls to history
                var assistantMessage = new AssistantChatMessage(completion);
                _conversationHistory[conversationId].Add(assistantMessage);

                // Execute each tool call
                foreach (var toolCall in completion.ToolCalls)
                {
                    var functionName = toolCall.FunctionName;
                    var functionArgs = JsonDocument.Parse(toolCall.FunctionArguments.ToString()).RootElement;

                    string functionResult;
                    if (functionName == "GetWeatherAsync")
                    {
                        var location = functionArgs.TryGetProperty("location", out var loc) ? loc.GetString() ?? "unknown" : "unknown";
                        functionResult = await GetWeatherAsync(location);
                    }
                    else if (functionName == "GetCurrentTime")
                    {
                        functionResult = GetCurrentTime();
                    }
                    else
                    {
                        functionResult = "Unknown function";
                    }

                    // Add function result to conversation history
                    _conversationHistory[conversationId].Add(new ToolChatMessage(toolCall.Id, functionResult));
                }
            }
            else
            {
                // Model provided a final response
                foreach (var contentPart in completion.Content)
                {
                    response += contentPart.Text;
                }
                _conversationHistory[conversationId].Add(new AssistantChatMessage(response));
                break;
            }
        }

        if (string.IsNullOrEmpty(response))
        {
            response = "I apologize, but I wasn't able to complete your request.";
        }

        // Send all messages generated during this turn as separate activities
        for (var i = startingHistoryCount; i < _conversationHistory[conversationId].Count; i++)
        {
            var chatMessage = _conversationHistory[conversationId][i];
            var agentMessage = ConvertChatMessageToAgentProtocol(chatMessage);

            // Create an activity with the Agent Protocol message in the Value field
            var activity = MessageFactory.Text("");
            activity.Value = agentMessage;
            await turnContext.SendActivityAsync(activity, cancellationToken);
        }
    }

    /// <summary>
    /// Converts an OpenAI ChatMessage to Agent Protocol message format
    /// </summary>
    private Dictionary<string, object> ConvertChatMessageToAgentProtocol(ChatMessage chatMessage)
    {
        var message = new Dictionary<string, object>();

        // Determine role
        // CRITICAL: Agent Protocol uses "agent" role, NOT "assistant" (see TypeSpec ChatRole enum)
        if (chatMessage is AssistantChatMessage)
        {
            message["role"] = "agent";
        }
        else if (chatMessage is ToolChatMessage)
        {
            message["role"] = "tool";
        }
        else
        {
            message["role"] = "assistant"; // Default
        }

        // Convert contents
        var contents = new List<object>();

        if (chatMessage is AssistantChatMessage assistantMsg)
        {
            // Check if this is a tool call message
            if (assistantMsg.ToolCalls != null && assistantMsg.ToolCalls.Count > 0)
            {
                foreach (var toolCall in assistantMsg.ToolCalls)
                {
                    contents.Add(new Dictionary<string, object>
                    {
                        ["kind"] = "functionCall",
                        ["callId"] = toolCall.Id,
                        ["name"] = toolCall.FunctionName,
                        ["arguments"] = toolCall.FunctionArguments.ToString()
                    });
                }
            }
            else
            {
                // Text response
                var text = "";
                foreach (var contentPart in assistantMsg.Content)
                {
                    text += contentPart.Text;
                }
                contents.Add(new Dictionary<string, object>
                {
                    ["kind"] = "text",
                    ["text"] = text
                });
            }
        }
        else if (chatMessage is ToolChatMessage toolMsg)
        {
            // Tool result
            contents.Add(new Dictionary<string, object>
            {
                ["kind"] = "functionResult",
                ["callId"] = toolMsg.ToolCallId,
                ["result"] = toolMsg.Content.FirstOrDefault()?.Text ?? ""
            });
        }
        else
        {
            // Fallback: treat as text
            var text = "";
            if (chatMessage.Content != null && chatMessage.Content.Count > 0)
            {
                foreach (var contentPart in chatMessage.Content)
                {
                    text += contentPart.Text;
                }
            }
            contents.Add(new Dictionary<string, object>
            {
                ["kind"] = "text",
                ["text"] = text
            });
        }

        message["contents"] = contents;
        return message;
    }

    /// <summary>
    /// Function tool: Get weather for a location
    /// </summary>
    [Description("Get the weather for a given location.")]
    private async Task<string> GetWeatherAsync(
        [Description("The location to get the weather for.")] string location)
    {
        // Simulate async API call
        await Task.Delay(100);

        var conditions = new[] { "sunny", "cloudy", "rainy", "partly cloudy", "stormy" };
        var condition = conditions[_random.Next(conditions.Length)];
        var temperature = _random.Next(10, 35);

        return $"🌤️ The weather in {location} is {condition} with a temperature of {temperature}°C.";
    }

    /// <summary>
    /// Function tool: Get current time
    /// </summary>
    [Description("Get the current UTC time.")]
    private string GetCurrentTime()
    {
        var now = DateTime.UtcNow;
        return $"🕐 The current UTC time is {now:yyyy-MM-dd HH:mm:ss}.";
    }
}
