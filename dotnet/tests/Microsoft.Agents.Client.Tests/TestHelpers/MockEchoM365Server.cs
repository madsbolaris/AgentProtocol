using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using RichardSzalay.MockHttp;

namespace Microsoft.Agents.Client.Tests.TestHelpers;

/// <summary>
/// Mock EchoM365 server for integration tests.
/// Responds to /health, /runs, and /runs/wait endpoints with echoed messages.
/// </summary>
public static class MockEchoM365Server
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
    };

    /// <summary>
    /// Sets up mock responses for EchoM365 server endpoints.
    /// </summary>
    public static void SetupMockServer(MockHttpMessageHandler mockHandler)
    {
        // Mock health endpoint
        mockHandler.When(HttpMethod.Get, "http://localhost:3978/health")
            .Respond(HttpStatusCode.OK);

        // Mock POST /runs endpoint
        mockHandler.When(HttpMethod.Post, "http://localhost:3978/runs")
            .Respond(async req =>
            {
                var run = await req.Content!.ReadFromJsonAsync<Run>();
                if (run == null)
                    return new HttpResponseMessage(HttpStatusCode.BadRequest);

                var echoedRun = CreateEchoRun(run);
                var json = JsonSerializer.Serialize(echoedRun, JsonOptions);
                return new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                };
            });

        // Mock POST /runs/wait endpoint
        mockHandler.When(HttpMethod.Post, "http://localhost:3978/runs/wait")
            .Respond(async req =>
            {
                var run = await req.Content!.ReadFromJsonAsync<Run>();
                if (run == null)
                    return new HttpResponseMessage(HttpStatusCode.BadRequest);

                var response = CreateEchoWaitResponse(run);
                var json = JsonSerializer.Serialize(response, JsonOptions);
                return new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                };
            });
    }

    /// <summary>
    /// Creates an echoed Run response by copying input messages to output.
    /// </summary>
    private static Run CreateEchoRun(Run inputRun)
    {
        var runId = $"run_{Guid.NewGuid():N}";
        var threadId = inputRun.ThreadId ?? $"thread_{Guid.NewGuid():N}";

        // Echo logic: create agent messages that echo the input
        var echoedMessages = new List<ChatMessage>();
        foreach (var inputMessage in inputRun.Input)
        {
            var echoMessage = CreateEchoMessage(inputMessage);
            if (echoMessage != null)
                echoedMessages.Add(echoMessage);
        }

        return new Run
        {
            RunId = runId,
            AgentId = inputRun.AgentId,
            ThreadId = threadId,
            Status = RunStatus.Completed,
            Input = inputRun.Input,
            Output = echoedMessages,
            CreatedAt = DateTime.UtcNow,
            CompletedAt = DateTime.UtcNow
        };
    }

    /// <summary>
    /// Creates an echoed RunWaitResponse by copying input messages to output.
    /// </summary>
    private static RunWaitResponse CreateEchoWaitResponse(Run inputRun)
    {
        var runId = $"run_{Guid.NewGuid():N}";
        var threadId = inputRun.ThreadId ?? $"thread_{Guid.NewGuid():N}";

        // Echo logic: create agent messages that echo the input
        var echoedMessages = new List<ChatMessage>();
        foreach (var inputMessage in inputRun.Input)
        {
            var echoMessage = CreateEchoMessage(inputMessage);
            if (echoMessage != null)
                echoedMessages.Add(echoMessage);
        }

        return new RunWaitResponse
        {
            RunId = runId,
            AgentId = inputRun.AgentId,
            ThreadId = threadId,
            Status = RunStatus.Completed,
            Input = inputRun.Input,
            Output = echoedMessages,
            CreatedAt = DateTime.UtcNow
        };
    }

    /// <summary>
    /// Creates an agent message that echoes the input message.
    /// </summary>
    private static ChatMessage? CreateEchoMessage(ChatMessage inputMessage)
    {
        // Extract text from input message
        var text = ExtractText(inputMessage);
        if (text == null)
            return null;

        // Create echo message
        var echoText = $"you said: \n{text}";

        return new ChatMessage
        {
            MessageId = $"msg_{Guid.NewGuid():N}",
            Role = "assistant",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<Content>
            {
                new TextContent { Text = echoText }
            }
        };
    }

    /// <summary>
    /// Extracts text content from a chat message.
    /// </summary>
    private static string? ExtractText(ChatMessage message)
    {
        if (message.Contents == null || message.Contents.Count == 0)
            return null;

        var textContents = message.Contents
            .OfType<TextContent>()
            .Select(tc => tc.Text)
            .Where(t => !string.IsNullOrWhiteSpace(t));

        var result = string.Join("\n", textContents);
        return string.IsNullOrWhiteSpace(result) ? null : result;
    }
}
