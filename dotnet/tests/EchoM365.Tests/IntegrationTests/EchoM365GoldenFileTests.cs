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
using XunitAssert = Xunit.Assert;
using Xunit.Abstractions;

namespace EchoM365.Tests.IntegrationTests;

/// <summary>
/// EchoM365 Integration Tests - Validates against golden files.
///
/// This test suite:
/// 1. Connects to running echo bot servers on ports 3978, 3979, 3980
/// 2. Sends test-data/input/threads/*.xml files to each bot
/// 3. Validates responses against test-data/results/samples/echo-m365/json/ and xml/ golden files
/// 4. Ensures all three language implementations (Python, C#, TypeScript) behave identically
/// 5. Tests both JSON and XML output formats
///
/// Run with:
///     # Start all echo bots first
///     ./scripts/start-all-echo-m365s.sh
///
///     # Then run tests
///     dotnet test --filter "Category=GoldenFileIntegration"
///
///     # Or test specific language
///     dotnet test --filter "FullyQualifiedName~Python"
///     dotnet test --filter "FullyQualifiedName~DotNet"
///     dotnet test --filter "FullyQualifiedName~TypeScript"
/// </summary>
[Trait("Category", "GoldenFileIntegration")]
public class EchoM365GoldenFileTests : IDisposable
{
    private readonly ITestOutputHelper _output;
    private readonly HttpClient _httpClient;
    private static readonly string RepoRoot = FindRepoRoot();

    // Echo bot server configurations
    private static readonly Dictionary<string, string> EchoM365Servers = new()
    {
        { "Python", "http://localhost:3978" },
        { "DotNet", "http://localhost:3979" },
        { "TypeScript", "http://localhost:3980" }
    };

    public EchoM365GoldenFileTests(ITestOutputHelper output)
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
        var inputDir = Path.Combine(RepoRoot, "test-data", "input", "threads");
        return Directory.GetFiles(inputDir, "*.xml", SearchOption.AllDirectories)
            .Where(f =>
            {
                var fileName = Path.GetFileName(f);
                var dirName = Path.GetFileName(Path.GetDirectoryName(f));
                // Exclude files in the invalid subdirectory
                return dirName != "invalid" && !fileName.StartsWith("error-") && !fileName.Contains("errors") && !f.Contains("/invalid/");
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
                // Trim whitespace from XML formatting (newlines, indentation, etc.)
                Text = (textElem.Value ?? "").Trim()
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

    private static XDocument NormalizeXmlToDocument(string xmlContent)
    {
        var doc = XDocument.Parse(xmlContent, LoadOptions.None);

        // Remove dynamic attributes that change on every run
        // These include: thread-id, created-at, and any timestamp fields
        foreach (var element in doc.Descendants())
        {
            // Remove thread-id attribute (changes on every run)
            element.Attribute("thread-id")?.Remove();

            // Remove created-at attribute (timestamp changes on every run)
            element.Attribute("created-at")?.Remove();

            // Remove other timestamp attributes if present
            element.Attribute("timestamp")?.Remove();
            element.Attribute("completed-at")?.Remove();
        }

        return doc;
    }

    private static string NormalizeXml(string xmlContent)
    {
        var doc = NormalizeXmlToDocument(xmlContent);

        // Create a settings that produces consistent output with explicit closing tags
        var settings = new XmlWriterSettings
        {
            OmitXmlDeclaration = true,
            Indent = false,
            NewLineHandling = NewLineHandling.None
        };

        using var stringWriter = new StringWriter();
        using var xmlWriter = XmlWriter.Create(stringWriter, settings);
        doc.WriteTo(xmlWriter);
        xmlWriter.Flush();

        return stringWriter.ToString();
    }

    /// <summary>
    /// Validates XML output for common formatting bugs that were previously found.
    /// This catches issues like:
    /// - Newlines being inserted after opening tags (e.g., "<text>\ncontent" instead of "<text>content")
    /// - Wrong role names (e.g., "assistant" instead of "agent")
    /// </summary>
    private static void ValidateXmlFormatting(string xmlContent, string serverName)
    {
        var doc = XDocument.Parse(xmlContent);

        // Check 1: No newlines immediately after <text> opening tag
        // This catches the bug where XmlWriter with Indent=true adds newlines inside text elements
        var textElements = doc.Descendants("text");
        foreach (var textElem in textElements)
        {
            var textValue = textElem.Value;
            if (!string.IsNullOrEmpty(textValue) && textValue.StartsWith("\n"))
            {
                throw new Exception(
                    $"\n❌ XML FORMATTING BUG DETECTED in {serverName}:\n" +
                    $"   Text element has unwanted leading newline.\n" +
                    $"   This indicates XmlWriter is adding formatting newlines inside text content.\n" +
                    $"   Expected: <text>content...</text>\n" +
                    $"   Actual: <text>\\ncontent...</text>\n" +
                    $"   Full element: {textElem}\n" +
                    $"\n   FIX: Use WriteElementString() or set proper indentation rules for text elements.");
            }
        }

        // Check 2: Agent responses must use "agent" role, not "assistant"
        // This catches copy-paste errors from other protocols (OpenAI, etc.)
        var agentMessages = doc.Descendants().Where(e =>
            e.Name.LocalName == "assistant" || e.Name.LocalName == "agent");

        foreach (var msg in agentMessages)
        {
            if (msg.Name.LocalName == "assistant")
            {
                throw new Exception(
                    $"\n❌ ROLE NAME BUG DETECTED in {serverName}:\n" +
                    $"   Found <assistant> element - should be <agent>.\n" +
                    $"   Agent Protocol uses 'agent' role, NOT 'assistant'.\n" +
                    $"   This is likely a copy-paste error from OpenAI or other protocols.\n" +
                    $"   Full element: {msg}\n" +
                    $"\n   FIX: Change role from 'assistant' to 'agent' in response conversion code.");
            }
        }
    }

    public static IEnumerable<object[]> GetTestData()
    {
        var inputFiles = GetInputFiles();
        var formats = new[] { "json", "xml" };

        // Only test first 3 input files for now (to speed up initial test run)
        var limitedFiles = inputFiles.Take(3).ToList();

        // Test all servers to ensure cross-language consistency
        var activeServers = new[] { "Python", "DotNet", "TypeScript" };

        foreach (var language in activeServers)
        {
            foreach (var format in formats)
            {
                foreach (var inputFile in limitedFiles)
                {
                    var testName = Path.GetFileNameWithoutExtension(inputFile);
                    yield return new object[] { language, format, testName, inputFile };
                }
            }
        }
    }

    [Theory]
    [MemberData(nameof(GetTestData))]
    public async Task EchoM365_ShouldMatchGoldenFiles(
        string language,
        string format,
        string testName,
        string inputFile)
    {
        var baseUrl = EchoM365Servers[language];

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
                $"❌ Echo bot server not running: {language} at {baseUrl}\n" +
                $"Error: {ex.Message}\n\n" +
                "Please start all echo bots first:\n" +
                "  ./scripts/start-all-echo-m365s.sh\n",
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
            AgentId = "echo-agent",
            Input = new List<AgentMessage> { message }
        };

        // Send to echo bot with specified format
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
                $"Failed to connect to {language} echo bot at {baseUrl}: {ex.Message}\n\n" +
                "Make sure the echo bot is running:\n" +
                "  ./scripts/start-all-echo-m365s.sh",
                ex);
        }

        _output.WriteLine($"✅ {language} echo bot responded with {format.ToUpper()}");

        // Load golden file
        var goldenPath = Path.Combine(
            RepoRoot,
            "test-data",
            "results",
            "echo-m365",
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
                    $"{language} echo bot JSON response contains 'input' field!\n" +
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

                // Normalize both to consistent string format
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

                // Additional validation: Check for common XML formatting bugs
                ValidateXmlFormatting(actualContent, language);

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
        _output.WriteLine("Checking all echo bot servers for health...");

        foreach (var (language, url) in EchoM365Servers)
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
                    "Please start all echo bots first:\n" +
                    "  ./scripts/start-all-echo-m365s.sh",
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
                new MessageContent { Kind = "text", Text = "test" }
            }
        };

        var runRequest = new RunRequest
        {
            AgentId = "echo-agent",
            Input = new List<AgentMessage> { testMessage }
        };

        foreach (var (language, url) in EchoM365Servers)
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
                throw new Exception($"{language} echo bot not running: {ex.Message}", ex);
            }
        }
    }

    [Fact]
    public async Task AllServers_ShouldNotSupportReactionContentType()
    {
        _output.WriteLine("Checking all servers to verify they don't support reaction content type...");

        foreach (var (language, url) in EchoM365Servers)
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

                    // EchoM365 bots should NOT support reaction content type
                    var hasReactionSupport = contentTypes.Any(t =>
                        t.Equals("reaction", StringComparison.OrdinalIgnoreCase) ||
                        t.Equals("message-reaction", StringComparison.OrdinalIgnoreCase));

                    Assert.False(hasReactionSupport,
                        $"{language} EchoM365 bot should NOT support reaction content type, but it does. " +
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
                throw new Exception($"{language} echo bot not running: {ex.Message}", ex);
            }
        }
    }
}
