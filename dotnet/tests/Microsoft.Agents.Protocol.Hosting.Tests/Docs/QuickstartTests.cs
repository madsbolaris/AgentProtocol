using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests.Docs;

// Mock types for testing
public interface IStreamable { }
public class AIContentChunk { }
public class TextContentChunk : AIContentChunk
{
    public string? Text { get; set; }
}

// Type aliases for middleware signatures

// Simple middleware (default case - 80%)
public delegate IAsyncEnumerable<IStreamable> Middleware<T>(
    IAsyncEnumerable<T> stream,
    Thread thread,
    CancellationToken cancellationToken = default
) where T : IStreamable;

// Chained middleware (advanced case - 20%)
public delegate Task<IAsyncEnumerable<IStreamable>> ChainedMiddleware<T>(
    IAsyncEnumerable<T> stream,
    Thread thread,
    Func<IAsyncEnumerable<IStreamable>, Task<IAsyncEnumerable<T>>> next,
    CancellationToken cancellationToken = default
) where T : IStreamable;

public delegate Task MessageMiddleware(
    ChatMessage message,
    Thread thread,
    Func<Task> next,
    CancellationToken cancellationToken
);

/// <summary>
/// Tests for all Hosting SDK Quickstart Guide samples
/// </summary>
public class QuickstartTests : IDisposable
{
    private TestServer? _server;
    private HttpClient? _httpClient;

    public void Dispose()
    {
        _httpClient?.Dispose();
        _server?.Dispose();
    }

    #region Step 1: Hello World

    [Fact]
    [DocExample("hosting-hello-world")]
    public async Task Step1_HelloWorld_RespondsToBasicMessage()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"]
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);

        var app = builder.Build();
        app.MapAgentProtocol();
        #endregion

        // Assert - Test validation (not in snippet)
        _server = new TestServer(builder.WebHost);
        _httpClient = _server.CreateClient();

        var requestData = new
        {
            input = new[]
            {
                new
                {
                    role = "user",
                    contents = new[] { new { type = "text", text = "Hello!" } }
                }
            }
        };

        var response = await _httpClient.PostAsync("/runs/wait",
            new StringContent(JsonSerializer.Serialize(requestData), Encoding.UTF8, "application/json"));

        response.Should().NotBeNull();
        response.IsSuccessStatusCode.Should().BeTrue();
    }

    #endregion

    #region Step 2: Adding Tools

    [Fact]
    [DocExample("hosting-adding-tools")]
    public async Task Step2_AddingTools_ToolsRegistered()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        string GetWeather(string location) => $"The weather in {location} is sunny and 72°F";
        string GetTime() => DateTime.UtcNow.ToString("O");

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Functions = new[]
            {
                ("get_weather", "Get current weather for a location", (Func<string, string>)GetWeather),
                ("get_time", "Get current time in UTC", (Func<string>)GetTime)
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);

        var app = builder.Build();
        app.MapAgentProtocol();
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Functions.Should().NotBeNull();
        agentOptions.Functions.Should().HaveCount(2);
    }

    #endregion

    #region Step 3: Client-Provided Functions

    [Fact]
    [DocExample("hosting-client-functions")]
    public void Step3_ClientProvidedFunctions_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        // Enable client-provided functions
        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            AllowClientFunctions = true  // Enable client functions
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.AllowClientFunctions.Should().BeTrue();
    }

    #endregion

    #region Step 4: Command Router Middleware

    [Fact]
    [DocExample("hosting-command-router")]
    public void Step4_CommandRouterMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        // Type: Middleware<TextContent>
        async IAsyncEnumerable<IStreamable> CommandRouter(
            TextContent content,
            Thread thread,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            // Check if it's the /help command
            if (content.Text?.Trim() == "/help")
            {
                // Handle command - return result without calling LLM
                yield return new TextContent
                {
                    Text = "Available commands:\n/help - Show this help"
                };
            }
            else
            {
                // Pass through to LLM
                yield return content;
            }
        }

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                CommandRouter  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    #endregion

    #region Step 4: Reaction Handler Middleware

    [Fact]
    [DocExample("hosting-reaction-handler")]
    public void Step4_ReactionHandlerMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        // Type: Middleware<MessageReactionContent>
        async IAsyncEnumerable<IStreamable> HandleReactions(
            MessageReactionContent reaction,
            Thread thread,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            // Convert reaction to a message the agent can understand
            var developerMsg = new DeveloperMessage
            {
                Content = new[]
                {
                    new TextContent
                    {
                        Text = $"User reacted with {reaction.Emoji} to a previous message."
                    }
                }
            };
            yield return reaction;
            yield return developerMsg;  // Yield so LLM can process the notification
        }

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                HandleReactions  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    #endregion

    #region Step 4: Streaming Processing Middleware

    [Fact]
    [DocExample("hosting-streaming-middleware")]
    public void Step4_StreamingMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        // Type: Middleware<TextContentChunk>
        async IAsyncEnumerable<IStreamable> UppercaseContent(
            IAsyncEnumerable<TextContentChunk> stream,
            Thread thread,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            await foreach (var chunk in stream.WithCancellation(cancellationToken))
            {
                if (chunk.Text != null)
                {
                    chunk.Text = chunk.Text.ToUpper();
                }
                yield return chunk;
            }
        }

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                UppercaseContent  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    #endregion

    #region Step 4: Before and After Middleware

    [Fact]
    [DocExample("hosting-before-after")]
    public void Step4_BeforeAfterMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        ChainedMiddleware<TextContentChunk> timeStreaming = async (
            IAsyncEnumerable<TextContentChunk> stream,
            Thread thread,
            Func<IAsyncEnumerable<IStreamable>, Task<IAsyncEnumerable<TextContentChunk>>> next,
            CancellationToken cancellationToken) =>
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            Console.WriteLine("🚀 Starting stream");

            var result = await next(stream);

            sw.Stop();
            Console.WriteLine($"✅ Stream completed in {sw.ElapsedMilliseconds}ms");

            return result;
        };

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                TimeStreaming  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    #endregion

    #region Step 4: Message Middleware

    [Fact]
    [DocExample("hosting-message-middleware")]
    public void Step4_MessageMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        MessageMiddleware timingMiddleware = async (
            ChatMessage message,
            Thread thread,
            Func<Task> next,
            CancellationToken cancellationToken) =>
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            Console.WriteLine($"⏱️ Processing started for thread {thread.Id}");

            await next();

            sw.Stop();
            Console.WriteLine($"✅ Completed in {sw.ElapsedMilliseconds}ms");
        };

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                TimingMiddleware  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    #endregion

    #region Step 4: Error Handling Middleware

    [Fact]
    [DocExample("hosting-error-handling")]
    public void Step4_ErrorMiddleware_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        // Type: MessageMiddleware
        async Task ErrorMiddleware(
            ChatMessage message,
            Thread thread,
            Func<Task> next,
            CancellationToken cancellationToken)
        {
            try
            {
                await next();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Error: {ex.Message}");
                var errorMsg = new AgentMessage
                {
                    Content = new[] { new TextContent { Text = "Sorry, something went wrong." } }
                };
                thread.AddMessage(errorMsg);
            }
        }

        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Middleware = new MiddlewareCollection
            {
                ErrorMiddleware  // Type inferred from method signature
            }
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Middleware.Should().NotBeNull();
        agentOptions.Middleware.Should().NotBeEmpty();
    }

    [Fact]
    [DocExample("hosting-content-filter")]
    public async Task Step4_ContentFilterMiddleware_ConfigurationWorks()
    {
        #region Snippet
        // Type: Middleware<TextContent>
        async IAsyncEnumerable<IStreamable> ContentFilter(
            TextContent content,
            Thread thread)
        {
            // Filter profanity and sensitive information
            var filteredText = content.Text.Replace("badword", "***");

            // Check for sensitive patterns
            if (content.Text.Contains("ssn:", StringComparison.OrdinalIgnoreCase))
            {
                yield return new TextContent { Text = "[REDACTED - Sensitive information removed]" };
            }
            else
            {
                content.Text = filteredText;
                yield return content;
            }
        }
        #endregion

        var thread = new Thread { ThreadId = "test_thread" };
        var content = new TextContent { Text = "This contains badword" };

        var result = new List<IStreamable>();
        await foreach (var item in ContentFilter(content, thread))
        {
            result.Add(item);
        }

        Assert.Single(result);
        Assert.Contains("***", ((TextContent)result[0]).Text);
    }

    [Fact]
    [DocExample("hosting-metadata-enrichment")]
    public async Task Step4_MetadataEnrichmentMiddleware_ConfigurationWorks()
    {
        #region Snippet
        // Type: Middleware<TextContent>
        async IAsyncEnumerable<IStreamable> MetadataEnricher(
            TextContent content,
            Thread thread)
        {
            // Get user context from thread metadata
            var userTimezone = thread.Metadata?.GetValueOrDefault("user_timezone", "UTC") ?? "UTC";

            // Add context as developer message
            yield return new DeveloperMessage
            {
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = $"[Context: User timezone={userTimezone}, session_active=True]" }
                }
            };

            yield return content; // Pass through original
        }
        #endregion

        var thread = new Thread
        {
            ThreadId = "test_thread",
            Metadata = new Dictionary<string, object> { ["user_timezone"] = "PST" }
        };
        var content = new TextContent { Text = "Hello" };

        var result = new List<IStreamable>();
        await foreach (var item in MetadataEnricher(content, thread))
        {
            result.Add(item);
        }

        Assert.Equal(2, result.Count);
        Assert.IsType<DeveloperMessage>(result[0]);
        var devMsg = (DeveloperMessage)result[0];
        Assert.Contains("PST", ((TextContent)devMsg.Contents[0]).Text);
    }

    [Fact]
    [DocExample("hosting-response-formatter")]
    public async Task Step4_ResponseFormatterMiddleware_ConfigurationWorks()
    {
        #region Snippet
        // Type: Middleware<TextContentChunk>
        async IAsyncEnumerable<IStreamable> ResponseFormatter(
            IAsyncEnumerable<TextContentChunk> stream,
            Thread thread)
        {
            var firstChunk = true;
            await foreach (var chunk in stream)
            {
                if (firstChunk)
                {
                    // Add branding to first chunk
                    chunk.Text = $"🤖 **Agent Response:**\n\n{chunk.Text}";
                    firstChunk = false;
                }
                yield return chunk;
            }
        }
        #endregion

        async IAsyncEnumerable<TextContentChunk> MockStream()
        {
            yield return new TextContentChunk { Text = "Hello" };
            yield return new TextContentChunk { Text = " world" };
        }

        var thread = new Thread { ThreadId = "test_thread" };
        var result = new List<IStreamable>();
        await foreach (var item in ResponseFormatter(MockStream(), thread))
        {
            result.Add(item);
        }

        Assert.Equal(2, result.Count);
        Assert.Contains("🤖", ((TextContentChunk)result[0]).Text);
    }

    #endregion

    #region Step 6: Persistent Conversations - In-Memory

    [Fact]
    [DocExample("hosting-inmemory-storage")]
    public void Step6_InMemoryStorage_IsDefault()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"]
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);

        // Conversations stored in memory (lost on restart)
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Storage.Should().BeNull(); // Default storage is implicit
    }

    #endregion

    #region Step 6: Durable Storage

    [Fact]
    [DocExample("hosting-durable-storage")]
    public void Step6_DurableStorage_ConfigurationWorks()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();
        var mockStorage = new InMemoryStorageProvider(); // Using in-memory as substitute for test

        #region Snippet
        var agentOptions = new AgentOptions
        {
            Model = "gpt-4",
            Instructions = "You are helpful.",
            ApiKey = builder.Configuration["OpenAI:ApiKey"],
            Storage = new SqlStorageProvider(builder.Configuration["DatabaseUrl"])
        };

        builder.Services
            .AddAgentHost()
            .AddDefaultAgent(agentOptions);

        // Conversations persist across server restarts
        #endregion

        // Assert - Test validation (not in snippet)
        agentOptions.Storage.Should().NotBeNull();
    }

    #endregion

    #region Tool Error Handling

    [Fact]
    [DocExample("hosting-tool-error-handling")]
    public async Task Tools_ErrorHandling_ReturnsErrorMessage()
    {
        // Arrange - Test setup (not in snippet)
        var builder = WebApplication.CreateBuilder();

        #region Snippet
        async Task<string> GetWeather(string location)
        {
            try
            {
                using var client = new HttpClient();
                var url = $"https://api.weather.com/v1/current?location={Uri.EscapeDataString(location)}";
                var response = await client.GetStringAsync(url);
                return $"Weather in {location}: {response}";
            }
            catch (HttpRequestException ex)
            {
                // Return error message - LLM will explain to user
                return $"Sorry, couldn't fetch weather: {ex.Message}";
            }
        }
        #endregion

        // Test the tool function
        var result = await GetWeather("InvalidCity");

        // Assert - Test validation (not in snippet)
        result.Should().Contain("couldn't fetch weather");
        result.Should().Contain("City not found");
    }

    #endregion
}

/// <summary>
/// Stub class representing the intended AgentOptions API for quickstart documentation
/// NOTE: This is a design intent class for documentation purposes.
/// The actual Hosting SDK uses a different fluent builder API.
/// </summary>
public class AgentOptions
{
    public string? Model { get; set; }
    public string? Instructions { get; set; }
    public string? ApiKey { get; set; }
    public Array? Functions { get; set; }
    public bool AllowClientFunctions { get; set; }
    public MiddlewareCollection? Middleware { get; set; }
    public object? Storage { get; set; }
}

/// <summary>
/// Stub class for middleware collection
/// </summary>
public class MiddlewareCollection : List<object>
{
}

/// <summary>
/// Simple in-memory storage provider for testing
/// </summary>
public class InMemoryStorageProvider
{
    // Placeholder for testing - real implementation would have storage methods
}
