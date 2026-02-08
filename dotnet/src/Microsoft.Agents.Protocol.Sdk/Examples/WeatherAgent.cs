using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Protocol.Sdk.Core;
using System.Text.Json;

namespace Microsoft.Agents.Protocol.Sdk.Examples;

/// <summary>
/// Weather agent example (Level 3 - Tool calling).
/// Demonstrates tool registration and execution.
/// </summary>
public class WeatherAgent : AgentProtocolApplication<WeatherContext>
{
    public WeatherAgent(AgentProtocolOptions options) : base(options)
    {
        // Register user message handler
        OnUserMessage(HandleUserMessageAsync);

        // Register tool handler with definition
        OnToolCall("get_weather", HandleGetWeatherAsync, new ToolDefinition
        {
            Name = "get_weather",
            Description = "Get current weather for a location",
            ParametersSchema = new
            {
                type = "object",
                properties = new
                {
                    location = new { type = "string", description = "City name or zip code" },
                    units = new { type = "string", @enum = new[] { "celsius", "fahrenheit" } }
                },
                required = new[] { "location" }
            }
        });
    }

    private async Task HandleUserMessageAsync(
        IMessageContext<WeatherContext> context,
        ChatMessage message,
        CancellationToken ct)
    {
        // The LLM client will automatically detect when to call get_weather tool
        // This handler is just for direct responses without tools
        await context.SendTextAsync("I can help you check the weather! What location are you interested in?", ct);
    }

    private async Task<object> HandleGetWeatherAsync(
        IToolCallContext<WeatherContext> context,
        FunctionCallContent toolCall,
        CancellationToken ct)
    {
        var args = JsonSerializer.Deserialize<WeatherArgs>(toolCall.Arguments);
        if (args == null)
        {
            return new { error = "Invalid arguments" };
        }

        // Simulate weather API call
        await Task.Delay(100, ct);

        return new
        {
            location = args.Location,
            temperature = 72,
            conditions = "sunny",
            humidity = 45,
            units = args.Units ?? "fahrenheit"
        };
    }

    public override Task<WeatherContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        var context = new WeatherContext
        {
            ApiKey = "simulated-api-key",
            CacheEnabled = true
        };
        return Task.FromResult(context);
    }
}

/// <summary>
/// Custom context for weather agent
/// </summary>
public class WeatherContext
{
    public string ApiKey { get; set; } = string.Empty;
    public bool CacheEnabled { get; set; }
}

/// <summary>
/// Arguments for get_weather tool
/// </summary>
public class WeatherArgs
{
    public string Location { get; set; } = string.Empty;
    public string? Units { get; set; }
}
