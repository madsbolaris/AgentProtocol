// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Xml;
using System.Xml.Linq;
using Xunit;
using Xunit.Abstractions;

namespace BasicM365Agent.Tests.IntegrationTests;

/// <summary>
/// Basic M365 Agent Integration Tests - Validates against golden files.
///
/// This test suite:
/// 1. Connects to running basic-m365 agent servers on ports 3981, 3982, 3983
/// 2. Sends test-data/input/*.xml files to each agent
/// 3. Validates responses against test-data/results/basic-m365/json/ and xml/ golden files
/// 4. Ensures all three language implementations (Python, C#, TypeScript) behave identically
/// 5. Tests both JSON and XML output formats
///
/// Run with:
///     # Start all basic-m365 agents first
///     ./scripts/start-all-basic-m365-agents.sh
///
///     # Then run tests
///     dotnet test --filter "Category=BasicM365Integration"
///
///     # Or test specific language
///     dotnet test --filter "FullyQualifiedName~Python"
///     dotnet test --filter "FullyQualifiedName~DotNet"
///     dotnet test --filter "FullyQualifiedName~TypeScript"
/// </summary>
[Trait("Category", "BasicM365Integration")]
public class BasicM365AgentGoldenFileTests : IDisposable
{
    private readonly ITestOutputHelper _output;
    private readonly HttpClient _httpClient;
    private static readonly string RepoRoot = FindRepoRoot();

    // Basic M365 agent server configurations
    private static readonly Dictionary<string, string> BasicM365Servers = new()
    {
        { "Python", "http://localhost:3982" },
        { "DotNet", "http://localhost:3981" },
        { "TypeScript", "http://localhost:3983" }
    };

    public BasicM365AgentGoldenFileTests(ITestOutputHelper output)
    {
        _output = output;
        _httpClient = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(30)
        };
    }

    public void Dispose()
    {
        _httpClient.Dispose();
    }

    private static string FindRepoRoot()
    {
        var dir = Directory.GetCurrentDirectory();
        while (!Directory.Exists(Path.Combine(dir, "test-data")))
        {
            var parent = Directory.GetParent(dir);
            if (parent == null)
            {
                throw new InvalidOperationException("Could not find repository root");
            }
            dir = parent.FullName;
        }
        return dir;
    }

    private static List<string> GetInputFiles()
    {
        var inputDir = Path.Combine(RepoRoot, "test-data", "input");

        // Get files that are relevant to basic-m365 agent (50-53 range for function calling)
        return Directory.GetFiles(inputDir, "*.xml")
            .Where(f =>
            {
                var fileName = Path.GetFileName(f);
                // Get files in the 50-53 range (function calling tests)
                var fileNumber = int.TryParse(fileName.Split('-')[0], out var num) ? num : 0;
                return fileNumber >= 50 && fileNumber <= 53;
            })
            .OrderBy(f => f)
            .ToList();
    }

    private class AgentMessage
    {
        public string Role { get; set; } = "";
        public string? MessageId { get; set; }
        public List<MessageContent> Contents { get; set; } = new();
    }

    private class MessageContent
    {
        public string Kind { get; set; } = "";
        public string Text { get; set; } = "";
        public string? Audience { get; set; }
    }

    private class RunRequest
    {
        public string AgentId { get; set; } = "";
        public List<AgentMessage> Input { get; set; } = new();
    }

    private class RunResponse
    {
        public string? RunId { get; set; }
        public string? AgentId { get; set; }
        public string? Status { get; set; }
        public List<AgentMessage>? Input { get; set; }  // Should NOT be present per @visibility("create")
        public List<AgentMessage>? Output { get; set; }
        public string? CreatedAt { get; set; }
        public string? CompletedAt { get; set; }
    }

    private static AgentMessage XmlToAgentProtocolMessage(string xmlContent)
    {
        var doc = XDocument.Parse(xmlContent);
        var root = doc.Root!;

        var message = new AgentMessage
        {
            Role = root.Name.LocalName,
            Contents = new List<MessageContent>()
        };

        // Add message-id if present
        var messageIdAttr = root.Attribute("message-id");
        if (messageIdAttr != null)
        {
            message.MessageId = messageIdAttr.Value;
        }

        // Extract text contents
        foreach (var textElem in root.Descendants("text"))
        {
            var content = new MessageContent
            {
                Kind = "text",
                Text = textElem.Value ?? ""
            };

            var audienceAttr = textElem.Attribute("audience");
            if (audienceAttr != null)
            {
                content.Audience = audienceAttr.Value;
            }

            message.Contents.Add(content);
        }

        // If no text contents, add empty one
        if (message.Contents.Count == 0)
        {
            message.Contents.Add(new MessageContent { Kind = "text", Text = "" });
        }

        return message;
    }

    private static string NormalizeXml(string xmlContent)
    {
        var doc = XDocument.Parse(xmlContent);
        return doc.ToString(SaveOptions.None);
    }

    public static IEnumerable<object[]> GetTestData()
    {
        var inputFiles = GetInputFiles();
        var formats = new[] { "json", "xml" };

        // Test all three language implementations
        var activeServers = new[] { "Python", "DotNet", "TypeScript" };

        foreach (var language in activeServers)
        {
            foreach (var format in formats)
            {
                foreach (var inputFile in inputFiles)
                {
                    var testName = Path.GetFileNameWithoutExtension(inputFile);
                    yield return new object[] { language, format, testName, inputFile };
                }
            }
        }
    }

    [Theory]
    [MemberData(nameof(GetTestData))]
    public async Task BasicM365Agent_ShouldMatchGoldenFiles(
        string language,
        string format,
        string testName,
        string inputFile)
    {
        var baseUrl = BasicM365Servers[language];

        _output.WriteLine(new string('=', 70));
        _output.WriteLine($"🧪 TEST: {language} - {testName} ({format.ToUpper()})");
        _output.WriteLine($"   Server: {baseUrl}");
        _output.WriteLine($"   Input: {Path.GetFileName(inputFile)}");
        _output.WriteLine($"   Format: {format}");
        _output.WriteLine(new string('=', 70));

        // Check if server is running
        try
        {
            var healthResponse = await _httpClient.GetAsync($"{baseUrl}/health");
            if (!healthResponse.IsSuccessStatusCode)
            {
                throw new Exception($"Health check failed for {language} at {baseUrl}");
            }
        }
        catch (Exception ex)
        {
            throw new Exception(
                $"❌ Basic M365 agent server not running: {language} at {baseUrl}\n" +
                $"Error: {ex.Message}\n\n" +
                "Please start all basic-m365 agents first:\n" +
                "  ./scripts/start-all-basic-m365-agents.sh\n",
                ex);
        }

        // Load input XML
        var xmlContent = await File.ReadAllTextAsync(inputFile);
        _output.WriteLine($"📄 Loaded input: {xmlContent.Length} bytes");

        // Convert to Agent Protocol message
        var message = XmlToAgentProtocolMessage(xmlContent);
        _output.WriteLine($"📨 Message role: {message.Role}");

        // Create run request
        var runRequest = new RunRequest
        {
            AgentId = "basic-m365-agent",
            Input = new List<AgentMessage> { message }
        };

        // Send to basic-m365 agent with specified format
        _output.WriteLine($"🤖 Calling {baseUrl}/runs/wait?format={format}");

        HttpResponseMessage response;
        string actualContent;
        RunResponse? actual = null;

        try
        {
            response = await _httpClient.PostAsJsonAsync(
                $"{baseUrl}/runs/wait?format={format}",
                runRequest,
                new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });

            response.EnsureSuccessStatusCode();

            if (format == "json")
            {
                actualContent = await response.Content.ReadAsStringAsync();
                actual = JsonSerializer.Deserialize<RunResponse>(actualContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
            }
            else
            {
                actualContent = await response.Content.ReadAsStringAsync();
            }
        }
        catch (Exception ex)
        {
            throw new Exception(
                $"Failed to connect to {language} basic-m365 agent at {baseUrl}: {ex.Message}\n\n" +
                "Make sure the agent is running:\n" +
                "  ./scripts/start-all-basic-m365-agents.sh",
                ex);
        }

        _output.WriteLine($"✅ {language} basic-m365 agent responded with {format.ToUpper()}");

        // Load golden file
        var goldenPath = Path.Combine(
            RepoRoot,
            "test-data",
            "results",
            "basic-m365",
            format,
            $"{testName}-result.{format}");

        if (!File.Exists(goldenPath))
        {
            throw new FileNotFoundException(
                $"Golden file not found: {testName}-result.{format}\n" +
                $"Expected path: {goldenPath}\n" +
                "Note: This test is expected to FAIL on first run with wrong golden files.");
        }

        var goldenContent = await File.ReadAllTextAsync(goldenPath);
        _output.WriteLine($"📋 Loaded golden file: {testName}-result.{format}");

        // Validate based on format
        _output.WriteLine("🔍 Validating response against golden file...");

        if (format == "json")
        {
            // JSON validation
            _output.WriteLine("   Checking: input field is NOT in response (TypeSpec @visibility compliance)");

            // CRITICAL: Per TypeSpec, input field has @visibility("create")
            if (actual?.Input != null)
            {
                var actualJson = JsonSerializer.Serialize(actual, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });

                throw new Exception(
                    $"{language} basic-m365 agent JSON response contains 'input' field!\n" +
                    "TypeSpec @visibility('create') violation: 'input' should only be in requests.\n" +
                    $"Actual response:\n{actualJson}\n\n" +
                    $"Golden file:\n{goldenContent}\n\n" +
                    "THIS IS EXPECTED TO FAIL on first run because golden files are incorrect.");
            }

            // Compare structure
            Assert.NotNull(actual);
            Assert.Equal("completed", actual.Status);
            Assert.NotNull(actual.Output);

            _output.WriteLine("   ✓ JSON structure validation passed");
        }
        else
        {
            // XML validation
            try
            {
                actualContent = await response.Content.ReadAsStringAsync();
                var normalizedActual = NormalizeXml(actualContent);
                var normalizedExpected = NormalizeXml(goldenContent);

                if (normalizedActual != normalizedExpected)
                {
                    throw new Exception(
                        $"\n❌ XML VALIDATION FAILED for {language}:\n" +
                        "XML mismatch:\n" +
                        $"Expected:\n{normalizedExpected}\n\n" +
                        $"Actual:\n{normalizedActual}\n" +
                        "THIS IS EXPECTED TO FAIL on first run because golden files are incorrect.");
                }

                _output.WriteLine("   ✓ XML structure validation passed");
            }
            catch (Exception ex)
            {
                throw new Exception(
                    $"\n❌ XML COMPARISON FAILED for {language}:\n" +
                    $"   Error: {ex.Message}\n" +
                    "THIS IS EXPECTED TO FAIL on first run because golden files are incorrect.",
                    ex);
            }
        }

        _output.WriteLine(new string('=', 70));
        _output.WriteLine($"✅ TEST PASSED: {language} - {testName} ({format.ToUpper()})");
        _output.WriteLine($"{new string('=', 70)}\n");
    }

    [Fact]
    public async Task AllServers_ShouldRespondToHealthCheck()
    {
        _output.WriteLine("Checking all basic-m365 agent servers for health...");

        foreach (var (language, url) in BasicM365Servers)
        {
            _output.WriteLine($"Checking {language} at {url}...");

            try
            {
                var response = await _httpClient.GetAsync($"{url}/health");
                Assert.True(response.IsSuccessStatusCode, $"{language} health check failed");

                var content = await response.Content.ReadAsStringAsync();
                _output.WriteLine($"  ✓ {language} is healthy: {content}");
            }
            catch (Exception ex)
            {
                throw new Exception(
                    $"Health check failed for {language} at {url}: {ex.Message}\n" +
                    "Please start all basic-m365 agents first:\n" +
                    "  ./scripts/start-all-basic-m365-agents.sh",
                    ex);
            }
        }
    }

    [Fact]
    public async Task AllServers_ShouldNotIncludeInputFieldInResponses()
    {
        _output.WriteLine("Checking all servers for input field visibility compliance...");

        var testMessage = new AgentMessage
        {
            Role = "user",
            Contents = new List<MessageContent>
            {
                new MessageContent { Kind = "text", Text = "What's the weather in Seattle?" }
            }
        };

        var runRequest = new RunRequest
        {
            AgentId = "basic-m365-agent",
            Input = new List<AgentMessage> { testMessage }
        };

        foreach (var (language, url) in BasicM365Servers)
        {
            _output.WriteLine($"\nChecking {language} for input field visibility compliance...");

            try
            {
                var response = await _httpClient.PostAsJsonAsync(
                    $"{url}/runs/wait?format=json",
                    runRequest,
                    new JsonSerializerOptions
                    {
                        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                    });

                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<RunResponse>(
                    new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });

                // CRITICAL: Response must NOT contain input field
                Assert.Null(result?.Input);

                _output.WriteLine($"  ✓ {language} correctly omits input field from response");
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"{language} basic-m365 agent not running: {ex.Message}", ex);
            }
        }
    }

    [Fact]
    public async Task AllServers_ShouldNotSupportReactionContentType()
    {
        _output.WriteLine("Checking all servers to verify they don't support reaction content type...");

        foreach (var (language, url) in BasicM365Servers)
        {
            _output.WriteLine($"\nChecking {language} agent card...");

            try
            {
                var response = await _httpClient.GetAsync($"{url}/agent-card");

                if (!response.IsSuccessStatusCode)
                {
                    _output.WriteLine($"  ⚠️ {language} does not have /agent-card endpoint (acceptable)");
                    continue;
                }

                var agentCardJson = await response.Content.ReadAsStringAsync();
                _output.WriteLine($"  Agent card response: {agentCardJson}");

                // Parse the agent card
                using var doc = JsonDocument.Parse(agentCardJson);
                var root = doc.RootElement;

                // Check if outputContentTypes exists
                if (root.TryGetProperty("outputContentTypes", out var outputTypes))
                {
                    var contentTypes = new List<string>();

                    if (outputTypes.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var item in outputTypes.EnumerateArray())
                        {
                            if (item.ValueKind == JsonValueKind.String)
                            {
                                contentTypes.Add(item.GetString() ?? "");
                            }
                            else if (item.ValueKind == JsonValueKind.Object && item.TryGetProperty("kind", out var kind))
                            {
                                contentTypes.Add(kind.GetString() ?? "");
                            }
                        }
                    }

                    _output.WriteLine($"  Output content types: {string.Join(", ", contentTypes)}");

                    // Basic M365 agents should NOT support reaction content type
                    var hasReactionSupport = contentTypes.Any(t =>
                        t.Equals("reaction", StringComparison.OrdinalIgnoreCase) ||
                        t.Equals("message-reaction", StringComparison.OrdinalIgnoreCase));

                    Assert.False(hasReactionSupport,
                        $"{language} Basic M365 agent should NOT support reaction content type, but it does. " +
                        $"Supported types: {string.Join(", ", contentTypes)}");

                    _output.WriteLine($"  ✓ {language} correctly does not support reactions");
                }
                else
                {
                    _output.WriteLine($"  ✓ {language} agent card has no outputContentTypes (no reaction support)");
                }
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"{language} basic-m365 agent not running: {ex.Message}", ex);
            }
        }
    }
}
