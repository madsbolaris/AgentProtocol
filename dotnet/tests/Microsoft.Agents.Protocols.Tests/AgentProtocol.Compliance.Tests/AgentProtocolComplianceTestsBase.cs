using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Xml;

namespace Microsoft.Agents.Protocol.Tests.Compliance;

/// <summary>
/// Base class for Agent Protocol compliance tests.
/// Contains shared test logic that can be reused across all agent samples.
/// </summary>
public abstract class AgentProtocolComplianceTestsBase
{
    protected readonly HttpClient _client;
    protected readonly MessageSerializer _serializer;
    protected readonly string _agentName;

    protected AgentProtocolComplianceTestsBase(HttpClient client, string agentName)
    {
        _client = client;
        _serializer = new MessageSerializer();
        _agentName = agentName;
    }

    protected async Task AssertAgentProducesValidXml()
    {
        // Arrange: Create a run request with user message
        var runRequest = new
        {
            agentId = _agentName,
            threadId = $"test-thread-xml-{_agentName}",
            input = new[]
            {
                new
                {
                    role = "user",
                    contents = new[]
                    {
                        new { kind = "text", text = "Test XML compliance" }
                    }
                }
            }
        };

        var json = JsonSerializer.Serialize(runRequest);
        var content = new StringContent(json, Encoding.UTF8);
        content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");

        // Act: Post to Agent Protocol endpoint
        var response = await _client.PostAsync("/runs/wait", content);
        response.StatusCode.Should().Be(HttpStatusCode.OK, $"{_agentName} should respond successfully");

        var responseJson = await response.Content.ReadAsStringAsync();
        var runResponse = JsonSerializer.Deserialize<JsonElement>(responseJson);

        // Assert: Validate output messages can be serialized/deserialized as XML
        var outputArray = runResponse.GetProperty("output");
        outputArray.GetArrayLength().Should().BeGreaterThan(0, $"{_agentName} should return output messages");

        // Get the first output message (should be AgentMessage)
        var firstOutput = outputArray[0];
        var role = firstOutput.GetProperty("role").GetString();
        role.Should().Be("agent", $"{_agentName} output should contain agent message");

        // Convert to AgentMessage and serialize to XML
        var agentMessage = new AgentMessage
        {
            MessageId = firstOutput.GetProperty("messageId").GetString(),
            Contents = new List<AIContent>()
        };

        if (firstOutput.TryGetProperty("contents", out var contents))
        {
            foreach (var contentItem in contents.EnumerateArray())
            {
                if (contentItem.GetProperty("kind").GetString() == "text")
                {
                    agentMessage.Contents.Add(new TextContent
                    {
                        Text = contentItem.GetProperty("text").GetString()
                    });
                }
            }
        }

        // Verify XML serialization works (no nullable DateTime errors)
        var xml = _serializer.Serialize(agentMessage);
        xml.Should().NotBeNullOrEmpty($"{_agentName} XML serialization should succeed");

        // Verify XML can be deserialized
        var deserialized = _serializer.Deserialize(xml);
        deserialized.Should().NotBeNull($"{_agentName} XML deserialization should succeed");
        deserialized.Should().BeOfType<AgentMessage>($"{_agentName} deserialized message should be AgentMessage");
    }

    protected async Task AssertAgentSupportsJsonFormat()
    {
        // Arrange
        var runRequest = new
        {
            agentId = _agentName,
            threadId = $"test-thread-json-{_agentName}",
            input = new[]
            {
                new
                {
                    role = "user",
                    contents = new[]
                    {
                        new { kind = "text", text = "Test JSON" }
                    }
                }
            }
        };

        var json = JsonSerializer.Serialize(runRequest);
        var content = new StringContent(json, Encoding.UTF8);
        content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");

        // Act
        var response = await _client.PostAsync("/runs/wait", content);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK, $"{_agentName} should accept JSON");
        response.Content.Headers.ContentType?.MediaType.Should().Be("application/json", $"{_agentName} should return JSON");
    }
}
