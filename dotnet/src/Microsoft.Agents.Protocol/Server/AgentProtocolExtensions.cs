// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Agents.Builder;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;
using Microsoft.Agents.Hosting.AspNetCore;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Xml;

namespace Microsoft.Agents.Protocol.Server;

/// <summary>
/// Extension methods for adding Agent Protocol endpoints to ASP.NET Core applications.
/// </summary>
public static class AgentProtocolExtensions
{
    /// <summary>
    /// Adds Agent Protocol routes to the application.
    /// This includes /health, /runs, /runs/wait, /runs/stream, and /runs/{runId}/stream endpoints.
    /// </summary>
    /// <param name="app">The web application.</param>
    /// <param name="healthPath">Path for the health check endpoint (default: "/health").</param>
    /// <param name="runsPath">Base path for runs endpoints (default: "/runs").</param>
    /// <returns>The IEndpointRouteBuilder for chaining.</returns>
    public static IEndpointRouteBuilder MapAgentProtocol(
        this IEndpointRouteBuilder app,
        string healthPath = "/health",
        string runsPath = "/runs")
    {
        var server = new AgentProtocolServer();

        // Register all Agent Protocol endpoints
        app.MapGet(healthPath, server.HealthCheck);
        app.MapPost(runsPath, async (HttpContext context) => await server.CreateRun(context));
        app.MapPost($"{runsPath}/wait", async (HttpContext context) => await server.CreateAndWait(context));
        app.MapPost($"{runsPath}/stream", async (HttpContext context) => await server.CreateAndStream(context));
        app.MapGet($"{runsPath}/{{runId}}/stream", async (string runId, HttpContext context) => await server.StreamRun(runId, context));

        return app;
    }
}

/// <summary>
/// Internal Agent Protocol server implementation.
/// </summary>
internal class AgentProtocolServer
{
    private readonly ConcurrentDictionary<string, object> _runsDb = new();

    private string CreateRunId() => $"run_{Guid.NewGuid():N}"[..20];

    /// <summary>
    /// Converts an Agent Protocol message to a Bot Framework Activity.
    /// </summary>
    private Activity ConvertToActivity(Dictionary<string, object> message)
    {
        // Extract role from message
        var role = message.ContainsKey("role") ? message["role"]?.ToString() ?? "user" : "user";

        // Extract text from message contents
        var text = "";
        if (message.ContainsKey("contents"))
        {
            // Handle JsonElement from System.Text.Json deserialization
            if (message["contents"] is JsonElement contentsElement && contentsElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in contentsElement.EnumerateArray())
                {
                    if (item.TryGetProperty("kind", out var kindProp) && kindProp.GetString() == "text" &&
                        item.TryGetProperty("text", out var textProp))
                    {
                        text = textProp.GetString() ?? "";
                        break;
                    }
                }
            }
            // Fallback for other list types
            else if (message["contents"] is List<object> contents)
            {
                foreach (var content in contents)
                {
                    if (content is Dictionary<string, object> contentDict &&
                        contentDict.ContainsKey("kind") && contentDict["kind"]?.ToString() == "text" &&
                        contentDict.ContainsKey("text"))
                    {
                        text = contentDict["text"]?.ToString() ?? "";
                        break;
                    }
                }
            }
        }

        var activity = new Activity
        {
            Type = ActivityTypes.Message,
            Text = text,
            From = new ChannelAccount { Id = "user", Name = "User" },
            Recipient = new ChannelAccount { Id = "bot", Name = "Bot" },
            Conversation = new ConversationAccount { Id = Guid.NewGuid().ToString() },
            ChannelId = "agent-protocol",
            ServiceUrl = "https://agent-protocol"
        };

        // Store role in Properties dictionary for reliable extraction
        // Properties expects JsonElement, so serialize the role string
        activity.Properties["agentProtocol.role"] = JsonSerializer.SerializeToElement(role);

        return activity;
    }

    /// <summary>
    /// Converts a Bot Framework Activity to an Agent Protocol message.
    /// </summary>
    private Dictionary<string, object> ConvertToMessage(Activity activity)
    {
        // Check if the activity has Agent Protocol message data in Value field
        if (activity.Value != null)
        {
            try
            {
                // Try to deserialize as Agent Protocol message
                var jsonString = activity.Value is JsonElement jsonElement
                    ? jsonElement.GetRawText()
                    : JsonSerializer.Serialize(activity.Value);
                var message = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);
                if (message != null && message.ContainsKey("role") && message.ContainsKey("contents"))
                {
                    return message;
                }
            }
            catch
            {
                // If parsing fails, fall through to default text handling
            }
        }

        // Default: Convert activity text to TextContent
        return new Dictionary<string, object>
        {
            ["role"] = "assistant",
            ["contents"] = new List<object>
            {
                new Dictionary<string, object>
                {
                    ["kind"] = "text",
                    ["text"] = activity.Text ?? ""
                }
            }
        };
    }

    /// <summary>
    /// Processes a message through the agent.
    /// </summary>
    private async Task<List<Dictionary<string, object>>> ProcessMessage(Dictionary<string, object> inputMessage, IAgent agent, IAgentHttpAdapter adapter)
    {
        // Convert to Activity
        var activity = ConvertToActivity(inputMessage);

        // Create a turn context
        var turnContext = new SimpleTurnContext(activity);

        // Process through the agent
        await agent.OnTurnAsync(turnContext);

        // Convert ALL response activities back to Agent Protocol format
        var outputMessages = new List<Dictionary<string, object>>();
        foreach (var responseActivity in turnContext.ResponseActivities.Where(a => a.Type == ActivityTypes.Message))
        {
            outputMessages.Add(ConvertToMessage(responseActivity));
        }

        return outputMessages;
    }

    /// <summary>
    /// Builds a Thread XML document from output messages.
    /// </summary>
    private string BuildThreadXml(string threadId, List<object> outputMessages, DateTime createdAt, string status = "active")
    {
        var settings = new XmlWriterSettings
        {
            Indent = true,
            IndentChars = "  ",
            OmitXmlDeclaration = false,
            Encoding = Encoding.UTF8
        };

        var sb = new StringBuilder();
        using (var writer = XmlWriter.Create(sb, settings))
        {
            writer.WriteStartDocument();
            writer.WriteStartElement("thread");
            writer.WriteAttributeString("thread-id", threadId);
            writer.WriteAttributeString("status", status);
            writer.WriteAttributeString("created-at", createdAt.ToString("yyyy-MM-ddTHH:mm:ssZ"));

            // Add each message as a child element
            foreach (var msgObj in outputMessages)
            {
                if (msgObj is not Dictionary<string, object> msg) continue;

                var role = msg.ContainsKey("role") ? msg["role"]?.ToString() ?? "agent" : "agent";
                writer.WriteStartElement(role);

                // Add message-id if present
                if (msg.ContainsKey("messageId"))
                {
                    writer.WriteAttributeString("message-id", msg["messageId"]?.ToString());
                }

                // Add contents
                List<Dictionary<string, object>>? contentsList = null;

                // Handle JsonElement from System.Text.Json deserialization
                if (msg.ContainsKey("contents") && msg["contents"] is JsonElement contentsElement && contentsElement.ValueKind == JsonValueKind.Array)
                {
                    contentsList = new List<Dictionary<string, object>>();
                    foreach (var item in contentsElement.EnumerateArray())
                    {
                        var contentDict = new Dictionary<string, object>();
                        foreach (var prop in item.EnumerateObject())
                        {
                            contentDict[prop.Name] = prop.Value.ValueKind == JsonValueKind.String ? prop.Value.GetString()! : prop.Value;
                        }
                        contentsList.Add(contentDict);
                    }
                }
                // Fallback for other list types
                else if (msg.ContainsKey("contents") && msg["contents"] is List<object> contents)
                {
                    contentsList = contents.OfType<Dictionary<string, object>>().ToList();
                }

                if (contentsList != null)
                {
                    foreach (var content in contentsList)
                    {
                        var kind = content.ContainsKey("kind") ? content["kind"]?.ToString() : "text";

                        if (kind == "text")
                        {
                            writer.WriteStartElement("text");
                            if (content.ContainsKey("audience"))
                            {
                                writer.WriteAttributeString("audience", content["audience"]?.ToString());
                            }
                            writer.WriteString(content.ContainsKey("text") ? content["text"]?.ToString() ?? "" : "");
                            writer.WriteEndElement();
                        }
                        else if (kind == "functionCall")
                        {
                            writer.WriteStartElement("function-call");
                            if (content.ContainsKey("callId"))
                            {
                                writer.WriteAttributeString("call-id", content["callId"]?.ToString());
                            }
                            if (content.ContainsKey("name"))
                            {
                                writer.WriteAttributeString("name", content["name"]?.ToString());
                            }
                            if (content.ContainsKey("arguments"))
                            {
                                writer.WriteString(content["arguments"]?.ToString() ?? "");
                            }
                            writer.WriteEndElement();
                        }
                        else if (kind == "functionResult")
                        {
                            writer.WriteStartElement("function-result");
                            if (content.ContainsKey("callId"))
                            {
                                writer.WriteAttributeString("call-id", content["callId"]?.ToString());
                            }
                            if (content.ContainsKey("name"))
                            {
                                writer.WriteAttributeString("name", content["name"]?.ToString());
                            }
                            if (content.ContainsKey("result"))
                            {
                                writer.WriteString(content["result"]?.ToString() ?? "");
                            }
                            writer.WriteEndElement();
                        }
                    }
                }

                writer.WriteEndElement(); // Close role element
            }

            writer.WriteEndElement(); // Close thread
            writer.WriteEndDocument();
        }

        // Fix encoding declaration (StringBuilder always uses UTF-16, but we want UTF-8)
        var xmlString = sb.ToString();
        return xmlString.Replace("encoding=\"utf-16\"", "encoding=\"utf-8\"");
    }

    public IResult HealthCheck() => Results.Ok("OK");

    public async Task<IResult> CreateRun(HttpContext context)
    {
        // Get format query parameter (default to json)
        var format = context.Request.Query["format"].FirstOrDefault() ?? "json";

        try
        {
            // Use JsonDocument to properly parse the request
            using var jsonDoc = await JsonDocument.ParseAsync(context.Request.Body);
            var root = jsonDoc.RootElement;

            var runId = CreateRunId();
            var agentId = root.TryGetProperty("agentId", out var agentIdProp) ? agentIdProp.GetString() : "agent";
            var threadId = root.TryGetProperty("threadId", out var threadIdProp) ? threadIdProp.GetString() : $"thread_{Guid.NewGuid():N}"[..20];

            // Parse input messages array
            var inputMessages = new List<Dictionary<string, object>>();
            if (root.TryGetProperty("input", out var inputArray) && inputArray.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in inputArray.EnumerateArray())
                {
                    var msg = JsonSerializer.Deserialize<Dictionary<string, object>>(item.GetRawText());
                    if (msg != null)
                    {
                        inputMessages.Add(msg);
                    }
                }
            }

            // Get agent and adapter from DI
            var agent = context.RequestServices.GetService(typeof(IAgent)) as IAgent;
            var adapter = context.RequestServices.GetService(typeof(IAgentHttpAdapter)) as IAgentHttpAdapter;

            if (agent == null || adapter == null)
            {
                return Results.Json(new { error = "Agent or adapter not configured" }, statusCode: 500);
            }

            // Process each message through the agent (only user messages)
            var outputMessages = new List<object>();
            foreach (var msg in inputMessages)
            {
                // Only process user messages
                if (msg.ContainsKey("role") && msg["role"]?.ToString() == "user")
                {
                    var outputs = await ProcessMessage(msg, agent, adapter);
                    outputMessages.AddRange(outputs);
                }
            }

            var createdAt = DateTime.UtcNow;
            var completedAt = DateTime.UtcNow;

            // Per TypeSpec, input field has @visibility("create") which means it should
            // ONLY appear in request bodies, NOT in response bodies.
            var run = new Dictionary<string, object>
            {
                ["runId"] = runId,
                ["agentId"] = agentId,
                ["threadId"] = threadId,
                ["status"] = "completed",
                ["output"] = outputMessages,
                ["createdAt"] = createdAt,
                ["completedAt"] = completedAt
            };

            _runsDb[runId] = run;

            // Return XML or JSON based on format parameter
            if (format == "xml")
            {
                var xml = BuildThreadXml(threadId, outputMessages, createdAt);
                return Results.Content(xml, "application/xml", Encoding.UTF8, 201);
            }
            else
            {
                return Results.Json(run, statusCode: 201);
            }
        }
        catch (Exception ex)
        {
            return Results.Json(new { error = ex.Message }, statusCode: 400);
        }
    }

    public async Task CreateAndWait(HttpContext context)
    {
        // Get format query parameter (default to json)
        var format = context.Request.Query["format"].FirstOrDefault() ?? "json";

        try
        {
            // Use JsonDocument to properly parse the request
            using var jsonDoc = await JsonDocument.ParseAsync(context.Request.Body);
            var root = jsonDoc.RootElement;

            var runId = CreateRunId();
            var agentId = root.TryGetProperty("agentId", out var agentIdProp) ? agentIdProp.GetString() : "agent";
            var threadId = root.TryGetProperty("threadId", out var threadIdProp) ? threadIdProp.GetString() : $"thread_{Guid.NewGuid():N}"[..20];

            // Parse input messages array
            var inputMessages = new List<Dictionary<string, object>>();
            if (root.TryGetProperty("input", out var inputArray) && inputArray.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in inputArray.EnumerateArray())
                {
                    var msg = JsonSerializer.Deserialize<Dictionary<string, object>>(item.GetRawText());
                    if (msg != null)
                    {
                        inputMessages.Add(msg);
                    }
                }
            }

            // Get agent and adapter from DI
            var agent = context.RequestServices.GetService(typeof(IAgent)) as IAgent;
            var adapter = context.RequestServices.GetService(typeof(IAgentHttpAdapter)) as IAgentHttpAdapter;

            if (agent == null || adapter == null)
            {
                context.Response.StatusCode = 500;
                context.Response.ContentType = "application/json";
                await context.Response.WriteAsJsonAsync(new { error = "Agent or adapter not configured" });
                return;
            }

            // Process each message through the agent (only user messages)
            var outputMessages = new List<object>();
            foreach (var msg in inputMessages)
            {
                // Only process user messages
                if (msg.ContainsKey("role") && msg["role"]?.ToString() == "user")
                {
                    var outputs = await ProcessMessage(msg, agent, adapter);
                    outputMessages.AddRange(outputs);
                }
            }

            var createdAt = DateTime.UtcNow;
            var completedAt = DateTime.UtcNow;

            // Per TypeSpec, input field has @visibility("create") which means it should
            // ONLY appear in request bodies, NOT in response bodies.
            var run = new Dictionary<string, object>
            {
                ["runId"] = runId,
                ["agentId"] = agentId,
                ["threadId"] = threadId,
                ["status"] = "completed",
                ["output"] = outputMessages,
                ["createdAt"] = createdAt,
                ["completedAt"] = completedAt
            };

            _runsDb[runId] = run;

            // Return XML or JSON based on format parameter
            if (format == "xml")
            {
                var xml = BuildThreadXml(threadId, outputMessages, createdAt);
                context.Response.ContentType = "application/xml";
                await context.Response.WriteAsync(xml, Encoding.UTF8);
            }
            else
            {
                context.Response.ContentType = "application/json";
                await context.Response.WriteAsJsonAsync(run);
            }
        }
        catch (Exception ex)
        {
            context.Response.StatusCode = 400;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsJsonAsync(new { error = ex.Message });
        }
    }

    public async Task<IResult> CreateAndStream(HttpContext context)
    {
        try
        {
            var data = await JsonSerializer.DeserializeAsync<Dictionary<string, object>>(context.Request.Body);
            var runId = CreateRunId();
            var agentId = data?.ContainsKey("agentId") == true ? data["agentId"]?.ToString() : "agent";

            // Parse input - when deserializing with JsonSerializer, arrays become JsonElement
            var inputMessages = new List<Dictionary<string, object>>();
            if (data?.ContainsKey("input") == true && data["input"] is JsonElement inputElement && inputElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in inputElement.EnumerateArray())
                {
                    var msg = JsonSerializer.Deserialize<Dictionary<string, object>>(item.GetRawText());
                    if (msg != null) inputMessages.Add(msg);
                }
            }

            // Get agent and adapter from DI
            var agent = context.RequestServices.GetService(typeof(IAgent)) as IAgent;
            var adapter = context.RequestServices.GetService(typeof(IAgentHttpAdapter)) as IAgentHttpAdapter;

            if (agent == null || adapter == null)
            {
                return Results.Json(new { error = "Agent or adapter not configured" }, statusCode: 500);
            }

            context.Response.ContentType = "text/event-stream";
            context.Response.Headers.Append("Cache-Control", "no-cache");
            context.Response.Headers.Append("Connection", "keep-alive");

            var eventSeq = 0;
            var messageId = $"msg_{Guid.NewGuid():N}"[..20];

            // Event 1: run.started
            eventSeq++;
            await context.Response.WriteAsync($"event: run.started\n");
            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new {
                @event = "run.started",
                data = new { runId, agentId, status = "in_progress", eventSeq, startedAt = DateTime.UtcNow }
            })}\n\n");
            await context.Response.Body.FlushAsync();
            await Task.Delay(50);

            // Event 2: message.created
            eventSeq++;
            await context.Response.WriteAsync($"event: message.created\n");
            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new {
                @event = "message.created",
                data = new { runId, agentId, eventSeq, message = new { messageId, role = "assistant", contents = new[] { new { kind = "text", text = "" } } }, createdAt = DateTime.UtcNow }
            })}\n\n");
            await context.Response.Body.FlushAsync();
            await Task.Delay(50);

            // Process the first user message through the agent
            var firstUserMessage = inputMessages.FirstOrDefault(msg => msg.ContainsKey("role") && msg["role"]?.ToString() == "user");

            var outputMessages = firstUserMessage != null
                ? await ProcessMessage(firstUserMessage, agent, adapter)
                : new List<Dictionary<string, object>> { new Dictionary<string, object> { ["contents"] = new[] { new Dictionary<string, object> { ["text"] = "" } } } };

            // Get the last message (final response) for streaming
            var outputMessage = outputMessages.LastOrDefault() ?? new Dictionary<string, object> { ["contents"] = new[] { new Dictionary<string, object> { ["text"] = "" } } };

            var fullOutputText = "";

            if (outputMessage.ContainsKey("contents"))
            {
                var contentsObj = outputMessage["contents"];

                // Handle JsonElement from System.Text.Json deserialization
                if (contentsObj is JsonElement contentsElement && contentsElement.ValueKind == JsonValueKind.Array)
                {
                    foreach (var item in contentsElement.EnumerateArray())
                    {
                        if (item.TryGetProperty("kind", out var kindProp) && kindProp.GetString() == "text" &&
                            item.TryGetProperty("text", out var textProp))
                        {
                            fullOutputText = textProp.GetString() ?? "";
                            break;
                        }
                    }
                }
                // Handle List<object> for directly constructed messages
                else if (contentsObj is List<object> outContents && outContents.Count > 0)
                {
                    var firstOutContent = outContents[0] as Dictionary<string, object>;
                    fullOutputText = firstOutContent?.ContainsKey("text") == true ? firstOutContent["text"]?.ToString() ?? "" : "";
                }
            }

            // Stream the output text in chunks (split by words) - send incremental chunks
            var words = fullOutputText.Split(' ');

            for (var i = 0; i < words.Length; i++)
            {
                // Send incremental chunk (just the current word, with space prefix if not first)
                var chunk = i == 0 ? words[i] : " " + words[i];
                eventSeq++;
                await context.Response.WriteAsync($"event: message.delta\n");
                await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new {
                    @event = "message.delta",
                    data = new {
                        runId,
                        agentId,
                        messageId,
                        eventSeq,
                        delta = new { contents = new[] { new { kind = "text", text = chunk } } }
                    }
                })}\n\n");
                await context.Response.Body.FlushAsync();
                await Task.Delay(50);
            }

            // Event: message.completed
            eventSeq++;
            await context.Response.WriteAsync($"event: message.completed\n");
            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new {
                @event = "message.completed",
                data = new { runId, agentId, messageId, eventSeq, completedAt = DateTime.UtcNow }
            })}\n\n");
            await context.Response.Body.FlushAsync();
            await Task.Delay(50);

            // Event: run.completed
            eventSeq++;
            await context.Response.WriteAsync($"event: run.completed\n");
            await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new {
                @event = "run.completed",
                data = new { runId, agentId, status = "completed", output = outputMessages, eventSeq, completedAt = DateTime.UtcNow }
            })}\n\n");
            await context.Response.Body.FlushAsync();

            return Results.Empty;
        }
        catch (Exception ex)
        {
            return Results.Json(new { error = ex.Message }, statusCode: 400);
        }
    }

    public async Task<IResult> StreamRun(string runId, HttpContext context)
    {
        if (!_runsDb.TryGetValue(runId, out var run))
        {
            return Results.NotFound(new { error = "Run not found" });
        }

        context.Response.ContentType = "text/event-stream";
        context.Response.Headers.Append("Cache-Control", "no-cache");
        context.Response.Headers.Append("Connection", "keep-alive");

        var eventSeq = 0;

        // run.started
        eventSeq++;
        await context.Response.WriteAsync($"event: run.started\n");
        await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new { runId, status = "in_progress", eventSeq })}\n\n");
        await context.Response.Body.FlushAsync();

        // run.completed
        eventSeq++;
        var runDict = run as Dictionary<string, object>;
        await context.Response.WriteAsync($"event: run.completed\n");
        await context.Response.WriteAsync($"data: {JsonSerializer.Serialize(new { runId, status = "completed", output = runDict?["output"], eventSeq })}\n\n");
        await context.Response.Body.FlushAsync();

        return Results.Empty;
    }
}

/// <summary>
/// Simple turn context implementation for Agent Protocol message processing.
/// </summary>
internal class SimpleTurnContext : ITurnContext
{
    private readonly Activity _activity;
    private readonly List<Activity> _responseActivities = new();
    private readonly List<SendActivitiesHandler> _onSendActivities = new();

    public SimpleTurnContext(Activity activity)
    {
        _activity = activity;
    }

    public IActivity Activity => _activity;
    public IChannelAdapter Adapter => null!;
    public TurnContextStateCollection Services { get; } = new TurnContextStateCollection();
    public TurnContextStateCollection StackState { get; } = new TurnContextStateCollection();
    public IStreamingResponse StreamingResponse => null!;
    public bool Responded { get; set; }
    public ClaimsIdentity Identity => null!;

    public List<Activity> ResponseActivities => _responseActivities;

    public Task<ResourceResponse> SendActivityAsync(IActivity activity, CancellationToken cancellationToken = default)
    {
        if (activity is Activity act)
        {
            _responseActivities.Add(act);
        }
        Responded = true;
        return Task.FromResult(new ResourceResponse(activity.Id ?? Guid.NewGuid().ToString()));
    }

    public async Task<ResourceResponse[]> SendActivitiesAsync(IActivity[] activities, CancellationToken cancellationToken = default)
    {
        Responded = true;
        var responses = new List<ResourceResponse>();

        if (_onSendActivities.Count > 0)
        {
            var activitiesList = activities.ToList();
            Func<Task<ResourceResponse[]>> next = () => Task.FromResult(activities.Select(a => new ResourceResponse(a.Id ?? Guid.NewGuid().ToString())).ToArray());

            for (int i = _onSendActivities.Count - 1; i >= 0; i--)
            {
                var handler = _onSendActivities[i];
                var currentNext = next;
                next = () => handler(this, activitiesList, currentNext);
            }

            return await next();
        }

        foreach (var activity in activities)
        {
            if (activity is Activity act)
            {
                _responseActivities.Add(act);
            }
            responses.Add(new ResourceResponse(activity.Id ?? Guid.NewGuid().ToString()));
        }
        return responses.ToArray();
    }

    public Task<ResourceResponse> SendActivityAsync(string textReplyToSend, string? speak = null, string? inputHint = null, CancellationToken cancellationToken = default)
    {
        var activity = new Activity
        {
            Type = ActivityTypes.Message,
            Text = textReplyToSend,
            Speak = speak,
            InputHint = inputHint
        };
        return SendActivityAsync(activity, cancellationToken);
    }

    public Task<ResourceResponse> UpdateActivityAsync(IActivity activity, CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new ResourceResponse(activity.Id ?? Guid.NewGuid().ToString()));
    }

    public Task DeleteActivityAsync(string activityId, CancellationToken cancellationToken = default)
    {
        return Task.CompletedTask;
    }

    public Task DeleteActivityAsync(ConversationReference conversationReference, CancellationToken cancellationToken = default)
    {
        return Task.CompletedTask;
    }

    public ITurnContext OnSendActivities(SendActivitiesHandler handler)
    {
        _onSendActivities.Add(handler);
        return this;
    }

    public ITurnContext OnUpdateActivity(UpdateActivityHandler handler)
    {
        // Not implemented for Agent Protocol
        return this;
    }

    public ITurnContext OnDeleteActivity(DeleteActivityHandler handler)
    {
        // Not implemented for Agent Protocol
        return this;
    }

    public Task<ResourceResponse> TraceActivityAsync(string name, object value = null, string valueType = null, string label = null, CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new ResourceResponse());
    }
}
