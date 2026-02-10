using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Runtime;
using Microsoft.Agents;

namespace Microsoft.AspNetCore.Builder;

/// <summary>
/// Extension methods for mapping Agent Protocol endpoints.
/// </summary>
public static class AgentProtocolEndpointRouteBuilderExtensions
{
    /// <summary>
    /// Maps Agent Protocol endpoints to the application (non-generic version for simple agents).
    /// </summary>
    public static IEndpointRouteBuilder MapAgentProtocol(this IEndpointRouteBuilder endpoints)
    {
        // Root endpoint - returns basic agent info
        endpoints.MapGet("/", () => Results.Ok(new
        {
            name = "Agent",
            version = "1.0.0",
            description = "Agent built with Microsoft.Agents.Protocol.Hosting"
        }));

        // Health check endpoint - Agent Protocol compliant
        endpoints.MapGet("/health", () => Results.Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow
        }));

        // Agent card endpoint - Agent Protocol compliant
        endpoints.MapGet("/agent-card", () => Results.Ok(new
        {
            name = "Agent",
            version = "1.0.0",
            description = "Agent built with Microsoft.Agents.Protocol.Hosting"
        }));

        // Agent Protocol /runs/wait endpoint
        endpoints.MapPost("/runs/wait", async (
            Run request,
            CancellationToken cancellationToken) =>
        {
            // Simple implementation for agents without AgentProtocolRunner
            // This allows the new hosting package to work with AgentApplication
            await Task.CompletedTask; // Suppress async warning

            // Return properly typed Run model with correct field names
            return Results.Ok(new Run
            {
                RunId = Guid.NewGuid().ToString(),
                ThreadId = request.ThreadId ?? Guid.NewGuid().ToString(),
                AgentId = request.AgentId ?? "default-agent",
                Status = RunStatus.Completed,
                Output = new List<ChatMessage>(),
                Input = request.Input ?? new List<ChatMessage>(),
                Usage = new CompletionUsage(),
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow,
                CompletedAt = DateTime.UtcNow
            });
        });

        // Agent Protocol /runs/stream endpoint
        endpoints.MapPost("/runs/stream", async (HttpContext context, CancellationToken cancellationToken) =>
        {
            // Set headers for SSE streaming with CORS
            context.Response.Headers["Content-Type"] = "text/event-stream";
            context.Response.Headers["Cache-Control"] = "no-cache";
            context.Response.Headers["Connection"] = "keep-alive";
            context.Response.Headers["Access-Control-Allow-Origin"] = "*";
            context.Response.Headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
            context.Response.Headers["Access-Control-Allow-Headers"] = "Content-Type";
            context.Response.Headers["Access-Control-Expose-Headers"] = "*";

            // Read and parse request body
            using var reader = new StreamReader(context.Request.Body);
            var body = await reader.ReadToEndAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(body);

            var runId = $"run-{Guid.NewGuid()}";
            var threadId = data.TryGetProperty("threadId", out var tid) ? tid.GetString() : $"thread-{Guid.NewGuid()}";
            var messageId = $"msg-{Guid.NewGuid()}";
            var eventSeq = 0;

            // Extract text from input
            var text = "";
            if (data.TryGetProperty("input", out var input) && input.ValueKind == JsonValueKind.Array)
            {
                var inputArray = input.EnumerateArray();
                if (inputArray.Any())
                {
                    var firstMessage = inputArray.First();
                    if (firstMessage.TryGetProperty("contents", out var contents) && contents.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var content in contents.EnumerateArray())
                        {
                            if (content.TryGetProperty("kind", out var kind) && kind.GetString() == "text" &&
                                content.TryGetProperty("text", out var textProp))
                            {
                                text = textProp.GetString() ?? "";
                                break;
                            }
                        }
                    }
                }
            }

            // Helper to send SSE events (correct Agent Protocol format)
            async Task SendEvent(string eventName, object eventData)
            {
                eventSeq++;
                var dataDict = new Dictionary<string, object>();
                foreach (var prop in eventData.GetType().GetProperties())
                {
                    dataDict[prop.Name.Substring(0, 1).ToLower() + prop.Name.Substring(1)] = prop.GetValue(eventData);
                }
                dataDict["eventSeq"] = eventSeq;

                // SSE format: event type is in the "event:" line, data is sent directly
                var json = JsonSerializer.Serialize(dataDict);
                await context.Response.WriteAsync($"event: {eventName}\ndata: {json}\n\n", cancellationToken);
                await context.Response.Body.FlushAsync(cancellationToken);
            }

            // Send run.created event
            await SendEvent("run.created", new
            {
                RunId = runId,
                ThreadId = threadId,
                AgentId = "default-agent",
                Status = "queued",
                CreatedAt = DateTime.UtcNow.ToString("o")
            });

            // Send run.started event
            await SendEvent("run.started", new
            {
                RunId = runId,
                ThreadId = threadId,
                Status = "in_progress",
                StartedAt = DateTime.UtcNow.ToString("o")
            });

            // Send message.created event
            await SendEvent("message.created", new
            {
                RunId = runId,
                ThreadId = threadId,
                Message = new
                {
                    MessageId = messageId,
                    Role = "assistant",
                    Contents = new List<object>()
                },
                CreatedAt = DateTime.UtcNow.ToString("o")
            });

            // Process message and stream response in chunks
            var responseText = $"Echo: {text}";
            var chunkSize = 5;

            for (var i = 0; i < responseText.Length; i += chunkSize)
            {
                var chunk = responseText.Substring(i, Math.Min(chunkSize, responseText.Length - i));
                await SendEvent("message.delta", new
                {
                    RunId = runId,
                    ThreadId = threadId,
                    MessageId = messageId,
                    Delta = new
                    {
                        Role = "agent",
                        Contents = new[]
                        {
                            new { Kind = "text", Text = chunk }
                        }
                    }
                });
                // Small delay to simulate streaming
                await Task.Delay(50, cancellationToken);
            }

            // Send message.completed event
            await SendEvent("message.completed", new
            {
                RunId = runId,
                ThreadId = threadId,
                MessageId = messageId,
                Usage = new
                {
                    TotalTokens = responseText.Split(' ').Length
                },
                CompletedAt = DateTime.UtcNow.ToString("o")
            });

            // Send run.completed event
            await SendEvent("run.completed", new
            {
                RunId = runId,
                ThreadId = threadId,
                Status = "completed",
                Output = new[]
                {
                    new
                    {
                        MessageId = messageId,
                        Role = "assistant",
                        Contents = new[]
                        {
                            new { Kind = "text", Text = responseText }
                        }
                    }
                },
                CompletedAt = DateTime.UtcNow.ToString("o")
            });
        });

        return endpoints;
    }

    /// <summary>
    /// Maps Agent Protocol endpoints to the application (generic version with full context support).
    /// </summary>
    public static IEndpointRouteBuilder MapAgentProtocol<TContext>(
        this IEndpointRouteBuilder endpoints)
        where TContext : class
    {
        // Root endpoint - returns agent info
        endpoints.MapGet("/", async (HttpContext context, AgentProtocolApplication<TContext> agent) =>
        {
            var tools = agent.Tools.Values.Select(t => new
            {
                name = t.Name,
                description = t.Description
            }).ToList();

            return Results.Ok(new
            {
                name = agent.GetType().Name,
                version = "1.0.0",
                tools = tools
            });
        });

        // Health check endpoint - Agent Protocol compliant
        endpoints.MapGet("/health", () => Results.Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow
        }));

        // Agent card endpoint - Agent Protocol compliant
        endpoints.MapGet("/agent-card", (AgentProtocolApplication<TContext> agent) =>
        {
            var tools = agent.Tools.Values.Select(t => new
            {
                name = t.Name,
                description = t.Description
            }).ToList();

            return Results.Ok(new
            {
                name = agent.GetType().Name,
                version = "1.0.0",
                description = "Agent built with Microsoft.Agents.Protocol.Hosting",
                tools = tools
            });
        });

        // Agent Protocol /runs/wait endpoint
        endpoints.MapPost("/runs/wait", async (
            RunRequest request,
            AgentProtocolRunner<TContext> runner,
            CancellationToken cancellationToken) =>
        {
            var result = await runner.ExecuteRunAsync(request, cancellationToken);
            return Results.Ok(result);
        });

        // Agent Protocol /runs/stream endpoint
        endpoints.MapPost("/runs/stream", async (
            HttpContext httpContext,
            AgentProtocolRunner<TContext> runner,
            CancellationToken cancellationToken) =>
        {
            // Set headers for SSE streaming
            httpContext.Response.Headers["Content-Type"] = "text/event-stream";
            httpContext.Response.Headers["Cache-Control"] = "no-cache";
            httpContext.Response.Headers["Connection"] = "keep-alive";
            httpContext.Response.Headers["Access-Control-Allow-Origin"] = "*";
            httpContext.Response.Headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
            httpContext.Response.Headers["Access-Control-Allow-Headers"] = "Content-Type";
            httpContext.Response.Headers["Access-Control-Expose-Headers"] = "*";

            // Read request body
            using var reader = new StreamReader(httpContext.Request.Body);
            var body = await reader.ReadToEndAsync();
            var request = JsonSerializer.Deserialize<RunRequest>(body, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            if (request == null)
            {
                httpContext.Response.StatusCode = 400;
                return;
            }

            // Stream events
            await foreach (var streamEvent in runner.ExecuteRunStreamAsync(request, cancellationToken))
            {
                // Convert Data to JSON with camelCase
                var dataJson = JsonSerializer.Serialize(streamEvent.Data, new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });

                // Send SSE event
                await httpContext.Response.WriteAsync($"event: {streamEvent.EventName}\n", cancellationToken);
                await httpContext.Response.WriteAsync($"data: {dataJson}\n\n", cancellationToken);
                await httpContext.Response.Body.FlushAsync(cancellationToken);
            }
        });

        return endpoints;
    }
}
