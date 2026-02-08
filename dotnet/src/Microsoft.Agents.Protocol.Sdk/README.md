# Microsoft.Agents.Protocol.Sdk

Build agents using the Agent Protocol specification with M365-style ergonomics.

## Features

- ✅ **Simple API**: Echo agent in 5 lines of code
- ✅ **Strongly-typed**: Direct Protocol types (no conversions)
- ✅ **Handler-based**: Familiar M365 SDK-style registration
- ✅ **Protocol-complete**: 11-state lifecycle, 5 hook types, SSE streaming
- ✅ **LLM-agnostic**: Abstracts OpenAI, Anthropic, Azure, etc.
- ✅ **Type-safe context**: Generic `TContext` for custom state

## Installation

```bash
dotnet add package Microsoft.Agents.Protocol.Sdk
```

## Quick Start

### 1. Echo Agent (5 lines)

```csharp
using Microsoft.Agents.Protocol.Sdk;

public class EchoAgent : AgentProtocolApplication<EmptyContext>
{
    public EchoAgent(AgentProtocolOptions options) : base(options)
    {
        OnUserMessage((ctx, msg, ct) =>
            ctx.SendTextAsync($"You said: {((UserMessage)msg).Text}", ct));
    }
}

public class EmptyContext { }
```

### 2. Weather Agent (Tool Calling)

```csharp
using Microsoft.Agents.Protocol.Sdk;
using Microsoft.Agents.Abstractions.Models;

public class WeatherAgent : AgentProtocolApplication<WeatherContext>
{
    public WeatherAgent(AgentProtocolOptions options) : base(options)
    {
        OnUserMessage(HandleUserMessageAsync);

        OnToolCall("get_weather", HandleGetWeatherAsync, new ToolDefinition
        {
            Name = "get_weather",
            Description = "Get current weather for a location",
            ParametersSchema = new
            {
                type = "object",
                properties = new
                {
                    location = new { type = "string" }
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
        await context.SendTextAsync(
            "I can help you check the weather! What location?", ct);
    }

    private async Task<object> HandleGetWeatherAsync(
        IToolCallContext<WeatherContext> context,
        FunctionCallContent toolCall,
        CancellationToken ct)
    {
        var args = JsonSerializer.Deserialize<WeatherArgs>(toolCall.Arguments);

        // Call weather API
        var weather = await _weatherService.GetWeatherAsync(args.Location, ct);

        return new {
            location = args.Location,
            temperature = weather.Temperature,
            conditions = weather.Conditions
        };
    }

    public override Task<WeatherContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new WeatherContext
        {
            ApiKey = _configuration["WeatherApiKey"]
        });
    }
}

public class WeatherContext
{
    public string ApiKey { get; set; } = string.Empty;
}

public class WeatherArgs
{
    public string Location { get; set; } = string.Empty;
}
```

### 3. Setup (Program.cs)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Register agent
builder.Services.AddSingleton<AgentProtocolOptions>(new AgentProtocolOptions
{
    Name = "WeatherAgent",
    Instructions = "You are a helpful weather assistant.",
    Model = "gpt-4",
    LLMClient = new OpenAIProtocolClient(apiKey: "..."),
    EnableStreaming = true
});

builder.Services.AddSingleton<WeatherAgent>();

var app = builder.Build();

// Map Agent Protocol endpoints
app.MapAgentProtocolEndpoints<WeatherAgent, WeatherContext>();

app.Run();
```

## Core Concepts

### 1. Handler Registration

Register handlers for different message types and tools:

```csharp
public MyAgent(AgentProtocolOptions options) : base(options)
{
    // Message handlers
    OnUserMessage(HandleUserMessageAsync);
    OnSystemMessage(HandleSystemMessageAsync);
    OnAgentMessage(HandleAgentMessageAsync);

    // Tool handlers
    OnToolCall("get_weather", HandleWeatherAsync);
    OnToolCall("search", HandleSearchAsync);
}
```

### 2. Lifecycle Hooks

Hook into run lifecycle events:

```csharp
public MyAgent(AgentProtocolOptions options) : base(options)
{
    // Run lifecycle
    OnRunStarted(HandleRunStartedAsync);
    OnRunCompleted(HandleRunCompletedAsync);

    // Tool lifecycle
    OnToolStart(HandleToolStartAsync);
    OnToolComplete(HandleToolCompleteAsync);

    // Streaming
    OnStreamChunk(HandleStreamChunkAsync);
}
```

### 3. Protocol Hooks

Add declarative hooks for guardrails, safety, telemetry:

```csharp
public MyAgent(AgentProtocolOptions options) : base(options)
{
    // PII redaction
    AddHook(new ModifyHook
    {
        Name = "pii-redactor",
        PredefinedPatterns = new[] { "email", "phone", "ssn" },
        Replacement = "[REDACTED]",
        Lifecycle = HookLifecycle.BeforeRun
    });

    // Content moderation
    AddHook(new RemoteHook
    {
        Name = "content-moderator",
        Endpoint = "https://moderation.example.com/check",
        Lifecycle = HookLifecycle.AfterRun
    });

    // Keyword blocking
    AddHook(new BlockHook
    {
        Name = "keyword-blocker",
        Condition = new KeywordCondition { Keywords = new[] { "competitor" } },
        Message = "I cannot discuss that topic.",
        Lifecycle = HookLifecycle.BeforeRun
    });

    // Telemetry
    AddHook(new TelemetryHook
    {
        Name = "app-insights",
        Destination = "applicationinsights",
        Lifecycle = HookLifecycle.AfterRun
    });

    // Webhooks
    AddHook(new SendMessageHook
    {
        Name = "completion-webhook",
        Channel = "webhook",
        Destination = "https://example.com/webhook",
        Lifecycle = HookLifecycle.AfterRun
    });
}
```

### 4. Custom Context

Use generic context for type-safe dependency injection:

```csharp
public class MyContext
{
    public IDatabase Database { get; set; } = null!;
    public ILogger Logger { get; set; } = null!;
    public string UserId { get; set; } = string.Empty;
}

public class MyAgent : AgentProtocolApplication<MyContext>
{
    private readonly IDatabase _db;

    public MyAgent(AgentProtocolOptions options, IDatabase db) : base(options)
    {
        _db = db;
        OnUserMessage(HandleUserMessageAsync);
    }

    private async Task HandleUserMessageAsync(
        IMessageContext<MyContext> context,
        ChatMessage message,
        CancellationToken ct)
    {
        // Access custom context
        var user = await context.Context.Database.GetUserAsync(
            context.Context.UserId, ct);

        await context.SendTextAsync($"Hello, {user.Name}!", ct);
    }

    public override Task<MyContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new MyContext
        {
            Database = _db,
            Logger = _logger,
            UserId = ExtractUserIdFromThread(threadId)
        });
    }
}
```

### 5. Context Interfaces

Four context types provide different capabilities:

```csharp
// Message handling
public interface IMessageContext<TContext>
{
    ChatMessage Message { get; }
    TContext Context { get; }
    string RunId { get; }
    string ThreadId { get; }
    IReadOnlyList<ChatMessage> ConversationHistory { get; }

    Task SendTextAsync(string text, CancellationToken ct);
    Task SendMessageAsync(AgentMessage message, CancellationToken ct);
}

// Tool execution
public interface IToolCallContext<TContext>
{
    FunctionCallContent ToolCall { get; }
    TContext Context { get; }
    string RunId { get; }

    Task EmitToolEventAsync(string eventType, object data, CancellationToken ct);
}

// Run lifecycle
public interface IRunContext<TContext>
{
    string RunId { get; }
    RunStatus Status { get; }  // 11-state machine
    TContext Context { get; }

    Task<UserMessage> RequestInputAsync(string prompt, CancellationToken ct);
    Task<string> RequireAuthAsync(string scope, CancellationToken ct);
    Task CancelAsync(string reason, CancellationToken ct);
}

// Streaming
public interface IStreamContext<TContext>
{
    string RunId { get; }
    int NextEventSeq { get; }  // Auto-increments
    TContext Context { get; }

    Task EmitAsync(string eventType, object data, CancellationToken ct);
}
```

## LLM Integration

Use `IProtocolLLMClient` for provider abstraction:

```csharp
// OpenAI
var llmClient = new OpenAIProtocolClient(
    apiKey: "sk-...",
    model: "gpt-4"
);

// Anthropic
var llmClient = new AnthropicProtocolClient(
    apiKey: "sk-ant-...",
    model: "claude-3-5-sonnet-20241022"
);

// Azure OpenAI
var llmClient = new AzureOpenAIProtocolClient(
    endpoint: "https://your-resource.openai.azure.com",
    apiKey: "...",
    deploymentName: "gpt-4"
);

var options = new AgentProtocolOptions
{
    LLMClient = llmClient,
    // ...
};
```

The LLM client returns Agent Protocol types directly - no conversion needed!

```csharp
// Non-streaming
AgentMessage response = await llmClient.GenerateAsync(
    conversationHistory,
    tools,
    cancellationToken
);

// Streaming
await foreach (var delta in llmClient.StreamAsync(
    conversationHistory,
    tools,
    cancellationToken))
{
    if (delta.Type == DeltaType.TextDelta)
    {
        Console.Write(delta.AccumulatedText);
    }
    else if (delta.Type == DeltaType.ToolCallStart)
    {
        // Execute tool
    }
}
```

## Architecture

```
┌──────────────────────────────────────┐
│ AgentProtocolApplication<TContext>   │  ← Define agent
│ - OnUserMessage()                    │
│ - OnToolCall()                       │
│ - AddHook()                          │
│ - Lifecycle hooks                    │
└────────────┬─────────────────────────┘
             │
             ↓ executed by
┌──────────────────────────────────────┐
│ AgentRunner<TContext>                │  ← Execute agent
│ - 11-state machine                   │
│ - Message routing                    │
│ - Tool execution loop                │
│ - Hook pipeline                      │
│ - SSE streaming                      │
└────────────┬─────────────────────────┘
             │
             ↓ exposed via
┌──────────────────────────────────────┐
│ MapAgentProtocolEndpoints()          │  ← HTTP endpoints
│ - POST /runs/wait                    │
│ - POST /runs/stream                  │
│ - GET /runs/{id}/stream              │
└──────────────────────────────────────┘
```

## Run Lifecycle

The SDK manages an 11-state run lifecycle:

1. **queued** - Run created, waiting to start
2. **in_progress** - Currently executing
3. **requires_action** - Waiting for tool execution
4. **input_required** - Waiting for user input
5. **auth_required** - Waiting for authentication
6. **cancelling** - Cancellation requested
7. **cancelled** - Cancelled by user
8. **failed** - Error occurred
9. **completed** - Successfully completed
10. **incomplete** - Stopped without completion
11. **timeout** - Exceeded time limit

## Examples

See [Examples/](./Examples/) for complete examples:

- **EchoAgent.cs** - Simple echo (5 lines)
- **WeatherAgent.cs** - Tool calling with custom context
- More examples coming in Phase 5!

## Status

**Version**: 0.1.0-alpha
**Phase 1**: ✅ Core SDK Complete
**Phase 2**: 🔜 Execution Engine (Runner)
**Phase 3**: 📋 HTTP Integration
**Phase 4**: 📋 Advanced Features
**Phase 5**: 📋 Samples & Documentation

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../../LICENSE)

---

Built with ❤️ for the Agent Protocol community
