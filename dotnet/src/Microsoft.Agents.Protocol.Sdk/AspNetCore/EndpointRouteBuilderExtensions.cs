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
using Microsoft.Agents.Protocol.Sdk;
using Microsoft.Agents.Protocol.Sdk.Runtime;
using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.AspNetCore.Builder;

/// <summary>
/// Extension methods for mapping Agent Protocol endpoints.
/// </summary>
public static class AgentProtocolEndpointRouteBuilderExtensions
{
    /// <summary>
    /// Maps Agent Protocol endpoints to the application.
    /// </summary>
    public static IEndpointRouteBuilder MapAgentProtocol<TContext>(
        this IEndpointRouteBuilder endpoints)
        where TContext : class
    {
        // Enable CORS
        endpoints.ServiceProvider.GetRequiredService<IApplicationBuilder>()
            .UseCors("AgentProtocol");

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

        // Health check endpoint
        endpoints.MapGet("/health", () => Results.Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow
        }));

        // Agent Protocol /api/messages endpoint (Bot Framework compatible)
        endpoints.MapPost("/api/messages", async (
            HttpContext context,
            AgentProtocolRunner<TContext> runner,
            CancellationToken cancellationToken) =>
        {
            try
            {
                // Read request body
                using var reader = new StreamReader(context.Request.Body);
                var body = await reader.ReadToEndAsync(cancellationToken);

                // Try to parse as Bot Framework Activity
                var activity = JsonSerializer.Deserialize<JsonElement>(body);

                // Extract message text
                var text = activity.TryGetProperty("text", out var textProp)
                    ? textProp.GetString() ?? ""
                    : "";

                // Extract from/conversation for response
                var from = activity.TryGetProperty("from", out var fromProp)
                    ? fromProp
                    : default;

                var conversation = activity.TryGetProperty("conversation", out var convProp)
                    ? convProp
                    : default;

                // Check for message type
                var type = activity.TryGetProperty("type", out var typeProp)
                    ? typeProp.GetString()
                    : "message";

                // Create chat message
                ChatMessage message;
                if (type == "messageReaction")
                {
                    // Handle emoji reaction
                    var replyToId = activity.TryGetProperty("replyToId", out var replyToProp)
                        ? replyToProp.GetString()
                        : null;

                    var reactionsAdded = activity.TryGetProperty("reactionsAdded", out var reactionsProp)
                        ? reactionsProp.EnumerateArray()
                            .Select(r => new MessageReaction
                            {
                                Type = r.TryGetProperty("type", out var t) ? t.GetString() : "emoji",
                                Activity = r.TryGetProperty("activity", out var a) ? a.GetString() : "👍"
                            })
                            .ToList()
                        : new List<MessageReaction>();

                    message = new UserMessage
                    {
                        Content = new List<AIContent>
                        {
                            new MessageReactionContent
                            {
                                ReplyToId = replyToId,
                                Reaction = reactionsAdded.FirstOrDefault()
                            }
                        }
                    };
                }
                else
                {
                    // Regular text message
                    message = new UserMessage
                    {
                        Content = new List<AIContent>
                        {
                            new TextContent { Text = text }
                        }
                    };
                }

                // Create run request
                var runRequest = new RunRequest
                {
                    ThreadId = conversation.ValueKind != JsonValueKind.Undefined
                        ? conversation.TryGetProperty("id", out var idProp) ? idProp.GetString() : null
                        : null,
                    Messages = new List<ChatMessage> { message }
                };

                // Execute run
                var result = await runner.ExecuteRunAsync(runRequest, cancellationToken);

                // Get first response message
                var responseText = result.Messages.FirstOrDefault()?.Content
                    ?.OfType<TextContent>()
                    .FirstOrDefault()?.Text ?? "OK";

                // Return Bot Framework compatible response
                return Results.Ok(new
                {
                    type = "message",
                    text = responseText,
                    from = new { id = "bot" },
                    recipient = from.ValueKind != JsonValueKind.Undefined
                        ? JsonSerializer.Deserialize<object>(from.GetRawText())
                        : new { id = "user" },
                    conversation = conversation.ValueKind != JsonValueKind.Undefined
                        ? JsonSerializer.Deserialize<object>(conversation.GetRawText())
                        : new { id = "default" }
                });
            }
            catch (Exception ex)
            {
                return Results.Problem(
                    detail: ex.Message,
                    statusCode: 500,
                    title: "Error processing message");
            }
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

        return endpoints;
    }
}
