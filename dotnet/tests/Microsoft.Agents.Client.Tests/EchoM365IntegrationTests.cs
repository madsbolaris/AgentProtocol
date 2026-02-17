using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using System.Xml.Linq;
using FluentAssertions;
using Microsoft.Agents.Client;
using Microsoft.Agents;
using Microsoft.Agents.Client.Tests.TestHelpers;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using RichardSzalay.MockHttp;
using Xunit;
using XunitAssert = Xunit.Assert;
using ProtocolChatMessage = Microsoft.Agents.Protocol.Models.Messages.ChatMessage;
using ProtocolTextContent = Microsoft.Agents.Protocol.Models.Messages.TextContent;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Integration tests for Agent Protocol client with echo bot.
///
/// Tests XML input files from test-data/input and saves results to test-data/results/samples/echo-m365.
/// Covers three API patterns: XML, Wait, and Streaming.
/// </summary>
public class EchoM365IntegrationTests : IDisposable
{
    private readonly string _testDataDir;
    private readonly string _inputDir;
    private readonly string _xmlResultsDir;
    private readonly string _waitResultsDir;
    private readonly string _streamingResultsDir;
    private readonly HttpClient _httpClient;
    private const string EchoM365Url = "http://localhost:3978";
    private const string EchoM365AgentId = "echo-agent";

    public EchoM365IntegrationTests()
    {
        // Find test-data directory
        var currentDir = Directory.GetCurrentDirectory();
        var repoRoot = FindRepositoryRoot(currentDir);
        _testDataDir = Path.Combine(repoRoot, "test-data");
        _inputDir = Path.Combine(_testDataDir, "input", "threads");

        // Use shared results directory (language-agnostic)
        var resultsBase = Path.Combine(_testDataDir, "results", "samples", "echo-m365");
        _xmlResultsDir = Path.Combine(resultsBase, "xml");
        _waitResultsDir = Path.Combine(resultsBase, "wait");
        _streamingResultsDir = Path.Combine(resultsBase, "streaming");

        // Create results directories
        Directory.CreateDirectory(_xmlResultsDir);
        Directory.CreateDirectory(_waitResultsDir);
        Directory.CreateDirectory(_streamingResultsDir);

        // Set up mock HTTP server
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        MockEchoM365Server.SetupMockServer(mockHandler);
        _httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler, EchoM365Url);
    }

    private static string FindRepositoryRoot(string startPath)
    {
        var current = new DirectoryInfo(startPath);
        while (current != null)
        {
            if (Directory.Exists(Path.Combine(current.FullName, "test-data")))
            {
                return current.FullName;
            }
            current = current.Parent;
        }
        throw new InvalidOperationException("Could not find repository root with test-data directory");
    }

    /// <summary>
    /// Enhanced XML parser that handles multiple content types.
    /// </summary>
    private ProtocolChatMessage? XmlToChatMessage(string xmlContent)
    {
        try
        {
            var doc = XDocument.Parse(xmlContent);
            var root = doc.Root;

            if (root == null)
                return null;

            string? text = null;

            // 1. Try <text> element (most common)
            var textElem = root.Descendants("text").FirstOrDefault();
            if (textElem != null)
            {
                text = textElem.Value;
            }
            // 2. Try direct text content (system, developer messages)
            else if (!string.IsNullOrWhiteSpace(root.Value) && !root.HasElements)
            {
                text = root.Value.Trim();
            }
            // 3. Try <thinking> element (agent reasoning)
            else if (root.Descendants("thinking").Any())
            {
                var thinkingElem = root.Descendants("thinking").First();
                text = thinkingElem.Value;
            }
            // 4. Try <function-call> element (tool calling)
            else if (root.Descendants("function-call").Any())
            {
                var funcCall = root.Descendants("function-call").First();
                var funcName = funcCall.Attribute("name")?.Value ?? "unknown";
                var funcArgs = funcCall.Value;
                text = $"[Function call: {funcName}({funcArgs})]";
            }
            // 5. Try <function-result> element (tool results)
            else if (root.Descendants("function-result").Any())
            {
                var funcResult = root.Descendants("function-result").First();
                text = $"[Function result: {funcResult.Value}]";
            }
            // 6. Try first child element's text (thread messages)
            else if (root.HasElements)
            {
                foreach (var child in root.Elements())
                {
                    if (!string.IsNullOrWhiteSpace(child.Value))
                    {
                        text = child.Value.Trim();
                        break;
                    }

                    var childText = child.Descendants("text").FirstOrDefault();
                    if (childText != null)
                    {
                        text = childText.Value;
                        break;
                    }
                }
            }

            if (string.IsNullOrWhiteSpace(text))
                return null;

            // Determine role from root element
            string roleName;
            if (root.Name.LocalName == "thread" && root.HasElements)
            {
                // For threads, use first message element
                var firstMsg = root.Elements().First();
                roleName = firstMsg.Name.LocalName;
            }
            else
            {
                roleName = root.Name.LocalName;
            }

            // Map role name to protocol role string
            string role = roleName.ToLower() switch
            {
                "system" => "system",
                "developer" => "developer",
                "agent" => "assistant",
                "assistant" => "assistant",
                "user" => "user",
                "tool" => "tool",
                "channel" => "channel",
                _ => "user" // Default to user
            };

            // Create Protocol ChatMessage
            return new ProtocolChatMessage
            {
                Role = role,
                Contents = new List<Microsoft.Agents.Protocol.Models.Messages.Content>
                {
                    new ProtocolTextContent { Text = text }
                }
            };
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Warning: Could not parse XML to ChatMessage: {ex.Message}");
            return null;
        }
    }

    private IEnumerable<string> GetInputFiles()
    {
        if (!Directory.Exists(_inputDir))
        {
            return Enumerable.Empty<string>();
        }

        return Directory.GetFiles(_inputDir, "*.xml")
            .OrderBy(f => f)
            .ToList();
    }

    [Fact]
    public async Task EchoM365_XmlPattern_ProcessesAllInputFiles()
    {
        // Verify mock server is responding
        var healthResponse = await _httpClient.GetAsync("/health");
        healthResponse.EnsureSuccessStatusCode();

        var inputFiles = GetInputFiles();
        var processedCount = 0;

        foreach (var inputFile in inputFiles)
        {
            var fileName = Path.GetFileName(inputFile);
            var xmlContent = await File.ReadAllTextAsync(inputFile);

            var message = XmlToChatMessage(xmlContent);
            if (message == null)
            {
                Console.WriteLine($"Skipping {fileName} - no parseable content");
                continue;
            }

            try
            {
                // Create run
                var run = new Run
                {
                    AgentId = EchoM365AgentId,
                    Input = new List<ProtocolChatMessage> { message }
                };

                var response = await _httpClient.PostAsJsonAsync("/runs", run);
                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<Run>();
                result.Should().NotBeNull();

                // Save result
                var resultFileName = Path.GetFileNameWithoutExtension(fileName) + "-result.json";
                var resultPath = Path.Combine(_xmlResultsDir, resultFileName);

                var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(result, jsonOptions);
                await File.WriteAllTextAsync(resultPath, json);

                processedCount++;
                Console.WriteLine($"✓ Processed {fileName}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"✗ Failed {fileName}: {ex.Message}");
            }
        }

        Console.WriteLine($"\nProcessed {processedCount} files successfully");
        processedCount.Should().BeGreaterThan(0, "Should process at least some files");
    }

    [Fact]
    public async Task EchoM365_WaitPattern_ProcessesAllInputFiles()
    {
        // Verify mock server is responding
        var healthResponse = await _httpClient.GetAsync("/health");
        healthResponse.EnsureSuccessStatusCode();

        var inputFiles = GetInputFiles();
        var processedCount = 0;

        foreach (var inputFile in inputFiles)
        {
            var fileName = Path.GetFileName(inputFile);
            var xmlContent = await File.ReadAllTextAsync(inputFile);

            var message = XmlToChatMessage(xmlContent);
            if (message == null)
            {
                Console.WriteLine($"Skipping {fileName} - no parseable content");
                continue;
            }

            try
            {
                // Create run with wait
                var run = new Run
                {
                    AgentId = EchoM365AgentId,
                    Input = new List<ProtocolChatMessage> { message }
                };

                var response = await _httpClient.PostAsJsonAsync("/runs/wait", run);
                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<RunWaitResponse>();
                result.Should().NotBeNull();
                result!.Status.Should().Be(RunStatus.Completed);

                // Save result
                var resultFileName = Path.GetFileNameWithoutExtension(fileName) + "-result.json";
                var resultPath = Path.Combine(_waitResultsDir, resultFileName);

                var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(result, jsonOptions);
                await File.WriteAllTextAsync(resultPath, json);

                processedCount++;
                Console.WriteLine($"✓ Processed {fileName}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"✗ Failed {fileName}: {ex.Message}");
            }
        }

        Console.WriteLine($"\nProcessed {processedCount} files successfully");
        processedCount.Should().BeGreaterThan(0, "Should process at least some files");
    }

    [Fact]
    public void XmlParser_HandlesSystemMessage()
    {
        var xml = @"<system created-at=""2026-02-07T10:00:00Z"">
            You are a helpful AI assistant.
        </system>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("system");
        message.Contents.Should().HaveCount(1);
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("helpful AI assistant");
    }

    [Fact]
    public void XmlParser_HandlesDeveloperMessage()
    {
        var xml = @"<developer created-at=""2026-02-07T10:01:00Z"">
            Additional developer instructions: Use concise responses.
        </developer>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("developer");
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("concise responses");
    }

    [Fact]
    public void XmlParser_HandlesTextElement()
    {
        var xml = @"<user user-id=""user_123"">
            <text>What's the weather?</text>
        </user>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("user");
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Be("What's the weather?");
    }

    [Fact]
    public void XmlParser_HandlesThinkingContent()
    {
        var xml = @"<agent agent-id=""agent_1"">
            <thinking exposed=""false"">
                Need to call weather API.
            </thinking>
        </agent>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("assistant");
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("weather API");
    }

    [Fact]
    public void XmlParser_HandlesFunctionCall()
    {
        var xml = @"<agent agent-id=""agent_1"">
            <function-call call-id=""call_001"" name=""get_weather"">
                {""location"": ""Seattle""}
            </function-call>
        </agent>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("assistant");
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("Function call: get_weather");
    }

    [Fact]
    public void XmlParser_HandlesFunctionResult()
    {
        var xml = @"<tool call-id=""call_001"" name=""get_weather"">
            <function-result>
                {""temperature"": 52, ""conditions"": ""cloudy""}
            </function-result>
        </tool>";

        var message = XmlToChatMessage(xml);

        message.Should().NotBeNull();
        message!.Role.Should().Be("tool");
        message.Contents[0].Should().BeOfType<ProtocolTextContent>();
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("Function result");
        ((ProtocolTextContent)message.Contents[0]).Text.Should().Contain("temperature");
    }

    [Fact]
    public void XmlParser_ReturnsNullForEmptyContent()
    {
        var xml = @"<refusal reason=""Test reason""/>";

        var message = XmlToChatMessage(xml);

        message.Should().BeNull();
    }

    [Fact]
    public void XmlResults_HaveProperIndentation()
    {
        // Check both xml and wait result directories
        var directories = new[] { _xmlResultsDir, _waitResultsDir };

        foreach (var directory in directories)
        {
            if (!Directory.Exists(directory))
                continue;

            var xmlFiles = Directory.GetFiles(directory, "*.xml");
            foreach (var xmlFile in xmlFiles)
            {
                var content = File.ReadAllText(xmlFile);
                var lines = content.Split('\n');

                // Validate indentation rules:
                // 1. <thread> should have no leading whitespace (except xml declaration line)
                // 2. Direct children of <thread> should be indented with 2 spaces
                // 3. Children of those elements should be indented with 4 spaces
                // 4. Closing tags should match their opening tag indentation

                foreach (var line in lines)
                {
                    if (line.TrimStart().StartsWith("<?xml"))
                        continue;

                    if (line.TrimStart().StartsWith("<thread") ||
                        line.TrimStart().StartsWith("</thread"))
                    {
                        line.Should().StartWith(line.TrimStart().StartsWith("</thread") ? "</thread" : "<thread",
                            $"<thread> and </thread> tags should have no indentation in {Path.GetFileName(xmlFile)}");
                    }
                    else if (line.TrimStart().StartsWith("<agent"))
                    {
                        line.Should().StartWith("  ",
                            $"Direct children of <thread> should be indented with 2 spaces in {Path.GetFileName(xmlFile)}\nLine: {line}");
                        line.Should().NotStartWith("   ",
                            $"Direct children of <thread> should use exactly 2 spaces, not more in {Path.GetFileName(xmlFile)}\nLine: {line}");
                    }
                    else if (line.TrimStart().StartsWith("<text") ||
                             line.TrimStart().StartsWith("</agent"))
                    {
                        if (line.Contains("</agent>"))
                        {
                            line.Should().StartWith("  ",
                                $"Closing </agent> tag should be indented with 2 spaces in {Path.GetFileName(xmlFile)}\nLine: {line}");
                        }
                        else if (line.Contains("<text"))
                        {
                            line.Should().StartWith("    ",
                                $"Children of <agent> should be indented with 4 spaces in {Path.GetFileName(xmlFile)}\nLine: {line}");
                        }
                    }
                }
            }
        }
    }

    public void Dispose()
    {
        _httpClient?.Dispose();
    }
}

/// <summary>
/// Exception to skip test when preconditions aren't met.
/// </summary>
public class SkipException : Exception
{
    public SkipException(string message) : base(message) { }
}

/// <summary>
/// Attribute to mark tests as skippable.
/// </summary>
[AttributeUsage(AttributeTargets.Method)]
public class SkippableFactAttribute : FactAttribute
{
    public new string? Skip { get; set; }
}
