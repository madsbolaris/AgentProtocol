using System;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

/// <summary>
/// Tests to validate SSE streaming format correctness.
/// These tests prevent regression of issues where:
/// - Event types were duplicated in JSON data
/// - Event types were not properly parsed from "event:" line
/// - Property names were inconsistent (PascalCase vs camelCase)
/// </summary>
public class SseStreamingFormatTests
{
    [Fact]
    public async Task RunsStreamEndpoint_SendsEventTypeOnEventLine()
    {
        // Arrange
        using var host = await CreateTestHost();
        var client = host.GetTestClient();

        var request = new HttpRequestMessage(HttpMethod.Post, "/runs/stream")
        {
            Content = new StringContent("{\"input\": [{\"role\": \"user\", \"contents\": [{\"kind\": \"text\", \"text\": \"test\"}]}]}", Encoding.UTF8, "application/json")
        };

        // Act
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(2));
        var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cts.Token);

        // Read first few lines to get at least one complete event
        var stream = await response.Content.ReadAsStreamAsync();
        var reader = new StreamReader(stream);
        var lines = new StringBuilder();

        try
        {
            for (int i = 0; i < 10; i++)
            {
                var line = await reader.ReadLineAsync();
                if (line != null) lines.AppendLine(line);
            }
        }
        catch (OperationCanceledException) { }

        var output = lines.ToString();

        // Assert - SSE format has event type on "event:" line
        output.Should().Contain("event: run.created", "SSE events must have event type on 'event:' line");
        output.Should().Contain("event: run.started", "SSE events must have event type on 'event:' line");
    }

    [Fact]
    public async Task RunsStreamEndpoint_DataLineContainsJsonWithoutEventField()
    {
        // Arrange
        using var host = await CreateTestHost();
        var client = host.GetTestClient();

        var request = new HttpRequestMessage(HttpMethod.Post, "/runs/stream")
        {
            Content = new StringContent("{\"input\": [{\"role\": \"user\", \"contents\": [{\"kind\": \"text\", \"text\": \"test\"}]}]}", Encoding.UTF8, "application/json")
        };

        // Act
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(2));
        var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cts.Token);

        var stream = await response.Content.ReadAsStreamAsync();
        var reader = new StreamReader(stream);

        string? currentEvent = null;
        string? dataLine = null;

        try
        {
            // Parse SSE format to find first complete event
            while (dataLine == null)
            {
                var line = await reader.ReadLineAsync();
                if (line == null) break;

                if (line.StartsWith("event: "))
                {
                    currentEvent = line.Substring(7);
                }
                else if (line.StartsWith("data: ") && currentEvent != null)
                {
                    dataLine = line.Substring(6);
                    break;
                }
            }
        }
        catch (OperationCanceledException) { }

        // Assert - data should be valid JSON without duplicate event field
        dataLine.Should().NotBeNullOrEmpty("SSE events must have data line");

        var json = JsonDocument.Parse(dataLine!);
        var root = json.RootElement;

        // Event type should NOT be duplicated in the JSON data
        root.TryGetProperty("event", out _).Should().BeFalse(
            "Event type should be on 'event:' line, not duplicated in JSON data");

        // Verify expected properties exist with camelCase naming
        root.TryGetProperty("runId", out _).Should().BeTrue("JSON should use camelCase property names");
        root.TryGetProperty("threadId", out _).Should().BeTrue("JSON should use camelCase property names");
        root.TryGetProperty("eventSeq", out _).Should().BeTrue("JSON should include event sequence number");
    }

    [Fact]
    public async Task RunsStreamEndpoint_UsesCamelCasePropertyNames()
    {
        // Arrange
        using var host = await CreateTestHost();
        var client = host.GetTestClient();

        var request = new HttpRequestMessage(HttpMethod.Post, "/runs/stream")
        {
            Content = new StringContent("{\"input\": [{\"role\": \"user\", \"contents\": [{\"kind\": \"text\", \"text\": \"test\"}]}]}", Encoding.UTF8, "application/json")
        };

        // Act
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(2));
        var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cts.Token);

        var stream = await response.Content.ReadAsStreamAsync();
        var reader = new StreamReader(stream);
        var allData = new StringBuilder();

        try
        {
            for (int i = 0; i < 20; i++)
            {
                var line = await reader.ReadLineAsync();
                if (line != null && line.StartsWith("data: "))
                {
                    allData.AppendLine(line);
                }
            }
        }
        catch (OperationCanceledException) { }

        var dataLines = allData.ToString();

        // Assert - verify camelCase is used consistently
        dataLines.Should().Contain("\"runId\"", "Property names should be camelCase");
        dataLines.Should().Contain("\"threadId\"", "Property names should be camelCase");
        dataLines.Should().Contain("\"agentId\"", "Property names should be camelCase");
        dataLines.Should().Contain("\"createdAt\"", "Property names should be camelCase");
        dataLines.Should().Contain("\"eventSeq\"", "Property names should be camelCase");

        // These PascalCase names should NOT appear (they were causing UI parsing errors)
        dataLines.Should().NotContain("\"RunId\"", "Should not use PascalCase");
        dataLines.Should().NotContain("\"ThreadId\"", "Should not use PascalCase");
    }

    [Fact]
    public async Task RunsStreamEndpoint_SendsAllRequiredEventTypes()
    {
        // Arrange
        using var host = await CreateTestHost();
        var client = host.GetTestClient();

        var request = new HttpRequestMessage(HttpMethod.Post, "/runs/stream")
        {
            Content = new StringContent("{\"input\": [{\"role\": \"user\", \"contents\": [{\"kind\": \"text\", \"text\": \"test\"}]}]}", Encoding.UTF8, "application/json")
        };

        // Act
        using var cts = new System.Threading.CancellationTokenSource(TimeSpan.FromSeconds(5));
        var response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cts.Token);

        var stream = await response.Content.ReadAsStreamAsync();
        var reader = new StreamReader(stream);
        var events = new StringBuilder();

        try
        {
            string? line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                if (line.StartsWith("event: "))
                {
                    events.AppendLine(line);
                }
            }
        }
        catch (OperationCanceledException) { }
        catch (IOException) { } // Stream may close when cancellation happens

        var eventList = events.ToString();

        // Assert - verify all required event types are sent
        eventList.Should().Contain("event: run.created", "Must send run.created event");
        eventList.Should().Contain("event: run.started", "Must send run.started event");
        eventList.Should().Contain("event: message.created", "Must send message.created event");
        eventList.Should().Contain("event: message.delta", "Must send message.delta events for streaming");
        eventList.Should().Contain("event: message.completed", "Must send message.completed event");
        eventList.Should().Contain("event: run.completed", "Must send run.completed event");
    }

    private static async Task<IHost> CreateTestHost()
    {
        return await new HostBuilder()
            .ConfigureWebHost(webBuilder =>
            {
                webBuilder
                    .UseTestServer()
                    .ConfigureServices(services =>
                    {
                        services.AddRouting();
                    })
                    .Configure(app =>
                    {
                        app.UseRouting();
                        app.UseEndpoints(endpoints =>
                        {
                            endpoints.MapAgentProtocol();
                        });
                    });
            })
            .StartAsync();
    }
}
