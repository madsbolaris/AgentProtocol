using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Extension methods for mapping Agent Protocol HTTP endpoints.
/// </summary>
public static class EndpointRouteBuilderExtensions
{
    /// <summary>
    /// Maps Agent Protocol HTTP endpoints including thread-level streaming.
    /// </summary>
    /// <param name="endpoints">The endpoint route builder.</param>
    /// <returns>The endpoint route builder for method chaining.</returns>
    public static IEndpointRouteBuilder MapAgentProtocol(this IEndpointRouteBuilder endpoints)
    {
        if (endpoints == null) throw new ArgumentNullException(nameof(endpoints));

        // Thread-level streaming endpoint (new in unified spec)
        endpoints.MapGet("/threads/{threadId}/stream", async (string threadId, HttpContext context) =>
        {
            // TODO: Implement actual SSE streaming
            context.Response.ContentType = "text/event-stream";
            context.Response.Headers.Add("Cache-Control", "no-cache");
            context.Response.Headers.Add("Connection", "keep-alive");

            await context.Response.WriteAsync($"event: connected\ndata: {{\"threadId\":\"{threadId}\"}}\n\n");
            await context.Response.Body.FlushAsync();

            // Keep connection open
            await Task.Delay(Timeout.Infinite, context.RequestAborted);
        })
        .WithName("StreamThread")
        .WithTags("Agent Protocol");

        // Run-level streaming endpoint
        endpoints.MapGet("/runs/{runId}/stream", async (string runId, HttpContext context) =>
        {
            // TODO: Implement actual SSE streaming
            context.Response.ContentType = "text/event-stream";
            context.Response.Headers.Add("Cache-Control", "no-cache");
            context.Response.Headers.Add("Connection", "keep-alive");

            await context.Response.WriteAsync($"event: connected\ndata: {{\"runId\":\"{runId}\"}}\n\n");
            await context.Response.Body.FlushAsync();

            await Task.Delay(Timeout.Infinite, context.RequestAborted);
        })
        .WithName("StreamRun")
        .WithTags("Agent Protocol");

        // Additional endpoints would go here (create run, get run, etc.)
        // TODO: Map all TypeSpec-defined endpoints

        return endpoints;
    }
}
