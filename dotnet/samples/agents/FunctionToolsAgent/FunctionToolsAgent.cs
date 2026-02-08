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
using System.Linq;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Threading;

#pragma warning disable OPENAI001

namespace FunctionToolsSample;

public class FunctionToolsAgent : AgentApplication
{
    private readonly HttpClient _httpClient;
    private readonly Random _random = new();
    private readonly ChatClient _chatClient;
    private readonly Dictionary<string, List<ChatMessage>> _conversationHistory = new();

    public FunctionToolsAgent(AgentApplicationOptions options, HttpClient httpClient) : base(options)
    {
        _httpClient = httpClient;

        // Load configuration from environment variables
        var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT")
            ?? throw new InvalidOperationException("FOUNDRY_ENDPOINT environment variable is required");
        var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY")
            ?? throw new InvalidOperationException("FOUNDRY_API_KEY environment variable is required");
        var model = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT") ?? "gpt-5-nano";

        // Create ChatClient for Foundry
        _chatClient = new ChatClient(
            credential: new ApiKeyCredential(apiKey),
            model: model,
            options: new OpenAIClientOptions()
            {
                Endpoint = new Uri($"{endpoint}/openai/v1/")
            });

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
                    MessageFactory.Text("Hello! I'm a Function Tools Agent. I can help you with weather and time information. Try asking: 'What's the weather in Seattle?' or 'What time is it?'"),
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

            // Get completion from LLM
            var completion = await _chatClient.CompleteChatAsync(_conversationHistory[conversationId], chatOptions, cancellationToken);

            // Check if the model wants to call functions
            if (completion.Value.FinishReason == ChatFinishReason.ToolCalls)
            {
                // Add assistant message with tool calls to history
                var assistantMessage = new AssistantChatMessage(completion.Value);
                _conversationHistory[conversationId].Add(assistantMessage);

                // Execute each tool call
                foreach (var toolCall in completion.Value.ToolCalls)
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
                foreach (var contentPart in completion.Value.Content)
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

        await turnContext.SendActivityAsync(response, cancellationToken: cancellationToken);
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
