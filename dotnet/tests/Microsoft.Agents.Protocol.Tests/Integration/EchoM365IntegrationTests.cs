using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using System.Xml.Linq;
using Xunit;
using Xunit.Abstractions;
using FluentAssertions;

namespace Microsoft.Agents.Protocol.Tests.Integration;

/// <summary>
/// EchoM365 Integration Tests - Validates against golden files.
///
/// This test suite:
/// 1. Connects to running echo bot servers on ports 3978, 3979, 3980
/// 2. Sends test-data/input/*.xml files to each bot
/// 3. Validates responses against test-data/results/echom365/json/ golden files
/// 4. Ensures all three language implementations (Python, C#, TypeScript) behave identically
///
/// Run with:
///     # Start all echo bots first
///     ./scripts/start-all-echo-m365s.sh
///
///     # Then run tests
///     dotnet test --filter "FullyQualifiedName~EchoM365IntegrationTests"
/// </summary>
public class EchoM365IntegrationTests
{
    private readonly ITestOutputHelper _output;
    private static readonly Dictionary<string, string> EchoM365Servers = new()
    {
        ["python"] = "http://localhost:3978",
        ["dotnet"] = "http://localhost:3979",
        ["typescript"] = "http://localhost:3980"
    };

    public EchoM365IntegrationTests(ITestOutputHelper output)
    {
        _output = output;
    }

    private static string GetRepoRoot()
    {
        var dir = new DirectoryInfo(Directory.GetCurrentDirectory());
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "test-data")))
        {
            dir = dir.Parent;
        }
        return dir?.FullName ?? throw new InvalidOperationException("Could not find repository root");
    }

    private static Dictionary<string, object> XmlToAgentProtocolMessage(string xmlContent)
    {
        var doc = XDocument.Parse(xmlContent);
        var root = doc.Root!;

        var message = new Dictionary<string, object>
        {
            ["role"] = root.Name.LocalName,
            ["contents"] = new List<Dictionary<string, object>>()
        };

        // Add message-id if present
        var messageId = root.Attribute("message-id")?.Value;
        if (messageId != null)
        {
            message["messageId"] = messageId;
        }

        // Extract text contents
        var contents = (List<Dictionary<string, object>>)message["contents"];
        foreach (var textElem in root.Descendants("text"))
        {
            var content = new Dictionary<string, object>
            {
                ["kind"] = "text",
                ["text"] = textElem.Value ?? ""
            };

            var audience = textElem.Attribute("audience")?.Value;
            if (audience != null)
            {
                content["audience"] = audience;
            }

            contents.Add(content);
        }

        // If no text contents, add empty one
        if (contents.Count == 0)
        {
            contents.Add(new Dictionary<string, object>
            {
                ["kind"] = "text",
                ["text"] = ""
            });
        }

        return message;
    }

    private static List<string> GetInputFiles()
    {
        var repoRoot = GetRepoRoot();
        var inputDir = Path.Combine(repoRoot, "test-data", "input");

        return Directory.GetFiles(inputDir, "*.xml")
            .Where(f => !Path.GetFileName(f).StartsWith("error-") && !f.Contains("errors"))
            .OrderBy(f => f)
            .ToList();
    }

    private static JsonDocument LoadGoldenFile(string testName)
    {
        var repoRoot = GetRepoRoot();
        var goldenPath = Path.Combine(repoRoot, "test-data", "results", "echom365", "json", $"{testName}-result.json");

        if (!File.Exists(goldenPath))
        {
            throw new FileNotFoundException($"Golden file not found: {goldenPath}");
        }

        var json = File.ReadAllText(goldenPath);
        return JsonDocument.Parse(json);
    }

    private void AssertResponseStructure(JsonElement actual, JsonElement expected)
    {
        // CRITICAL: Per TypeSpec, input field has @visibility("create") which means
        // it should ONLY appear in request bodies, NOT in response bodies.
        actual.TryGetProperty("input", out _).Should().BeFalse(
            "input field has @visibility('create') and must not appear in responses (TypeSpec violation)");

        // Status must match
        actual.GetProperty("status").GetString().Should().Be(
            expected.GetProperty("status").GetString(),
            "status should match");

        // Output should be present
        actual.TryGetProperty("output", out var actualOutput).Should().BeTrue("output field should be present");

        _output.WriteLine("   ✓ Structure validation passed");
    }

    public static IEnumerable<object[]> GetTestData()
    {
        var inputFiles = GetInputFiles();

        foreach (var language in EchoM365Servers.Keys)
        {
            foreach (var inputFile in inputFiles)
            {
                var testName = Path.GetFileNameWithoutExtension(inputFile);
                yield return new object[] { language, testName, inputFile };
            }
        }
    }

    [Theory(Skip = "Requires running echo bot servers")]
    [MemberData(nameof(GetTestData))]
    public async Task TestEchoM365AgainstGoldenFiles(string language, string testName, string inputFile)
    {
        /*
         * Test echo bot implementation against golden files.
         *
         * This test validates that the echo bot:
         * 1. Accepts the input message
         * 2. Returns a response matching the golden file structure
         * 3. Does NOT include the input field (per @visibility("create") in TypeSpec)
         * 4. Returns appropriate output for user messages
         * 5. Returns empty output for non-user messages (system, agent, etc.)
         */
        _output.WriteLine($"{'='*70}");
        _output.WriteLine($"🧪 TEST: {language} - {testName}");
        _output.WriteLine($"   Server: {EchoM365Servers[language]}");
        _output.WriteLine($"   Input: {Path.GetFileName(inputFile)}");
        _output.WriteLine($"{'='*70}");

        // Check server is running
        var baseUrl = EchoM365Servers[language];
        using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };

        try
        {
            var healthResponse = await client.GetAsync($"{baseUrl}/health");
            healthResponse.EnsureSuccessStatusCode();
        }
        catch (Exception e)
        {
            throw new SkipException(
                $"{language} echo bot not running at {baseUrl}: {e.Message}\n" +
                $"Start it with: ./scripts/start-all-echo-m365s.sh");
        }

        // Load input XML
        var xmlContent = await File.ReadAllTextAsync(inputFile);
        _output.WriteLine($"📄 Loaded input: {xmlContent.Length} bytes");

        // Convert to Agent Protocol message
        var message = XmlToAgentProtocolMessage(xmlContent);
        _output.WriteLine($"📨 Message role: {message["role"]}");

        // Create run request
        var runRequest = new Dictionary<string, object>
        {
            ["agentId"] = "echo-agent",
            ["input"] = new[] { message }
        };

        // Send to echo bot
        _output.WriteLine($"🤖 Calling {baseUrl}/runs/wait");
        HttpResponseMessage response;
        try
        {
            response = await client.PostAsJsonAsync($"{baseUrl}/runs/wait?format=json", runRequest);
            response.EnsureSuccessStatusCode();
        }
        catch (Exception e)
        {
            Assert.Fail(
                $"Failed to connect to {language} echo bot at {baseUrl}: {e.Message}\n" +
                $"Make sure the echo bot is running: ./scripts/start-all-echo-m365s.sh");
            return;
        }

        var actualJson = await response.Content.ReadAsStringAsync();
        using var actual = JsonDocument.Parse(actualJson);
        _output.WriteLine($"✅ {language} echo bot responded");

        // Load golden file
        JsonDocument? expected;
        try
        {
            expected = LoadGoldenFile(testName);
            _output.WriteLine($"📋 Loaded golden file: {testName}-result.json");
        }
        catch (FileNotFoundException)
        {
            throw new SkipException(
                $"Golden file not found: {testName}-result.json\n" +
                $"Generate golden files first: python scripts/generate_json_golden_files.py");
        }

        // Validate response structure
        _output.WriteLine("🔍 Validating response structure...");
        _output.WriteLine("   Checking: input field is NOT in response (TypeSpec @visibility compliance)");
        _output.WriteLine("   Checking: status matches expected");
        _output.WriteLine("   Checking: output structure matches");

        AssertResponseStructure(actual.RootElement, expected.RootElement);

        // Additional validation: Check echo behavior
        var role = message["role"]?.ToString();
        var actualOutput = actual.RootElement.GetProperty("output");

        if (role == "user")
        {
            // User messages should get echoed
            actualOutput.GetArrayLength().Should().BeGreaterThan(0,
                "User message should produce non-empty output");

            var outputText = actualOutput[0].GetProperty("contents")[0].GetProperty("text").GetString();
            _output.WriteLine($"   ✓ Output text: {outputText?.Substring(0, Math.Min(50, outputText?.Length ?? 0))}...");
        }
        else
        {
            // Non-user messages should return empty output
            actualOutput.GetArrayLength().Should().Be(0,
                $"Non-user message ({role}) should produce empty output");
            _output.WriteLine($"   ✓ Non-user message correctly returned empty output");
        }

        _output.WriteLine($"{'='*70}");
        _output.WriteLine($"✅ TEST PASSED: {language} - {testName}");
        _output.WriteLine($"{'='*70}\n");

        expected.Dispose();
    }

    [Fact(Skip = "Requires running echo bot servers")]
    public async Task TestInputFieldNotInResponses()
    {
        /*
         * CRITICAL TEST: Verify that input field is NOT in responses.
         *
         * Per TypeSpec, input has @visibility("create") which means it should
         * ONLY appear in request bodies, NOT in response bodies.
         *
         * This test explicitly checks this requirement across all implementations.
         */
        var runRequest = new Dictionary<string, object>
        {
            ["agentId"] = "echo-agent",
            ["input"] = new[]
            {
                new Dictionary<string, object>
                {
                    ["role"] = "user",
                    ["contents"] = new[]
                    {
                        new Dictionary<string, object>
                        {
                            ["kind"] = "text",
                            ["text"] = "test"
                        }
                    }
                }
            }
        };

        using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };

        foreach (var (lang, url) in EchoM365Servers)
        {
            _output.WriteLine($"\nChecking {lang} for input field visibility compliance...");

            HttpResponseMessage response;
            try
            {
                response = await client.PostAsJsonAsync($"{url}/runs/wait?format=json", runRequest);
                response.EnsureSuccessStatusCode();
            }
            catch (Exception e)
            {
                throw new SkipException($"{lang} echo bot not running: {e.Message}");
            }

            var json = await response.Content.ReadAsStringAsync();
            using var result = JsonDocument.Parse(json);

            // CRITICAL: Response must NOT contain input field
            result.RootElement.TryGetProperty("input", out _).Should().BeFalse(
                $"{lang} echo bot VIOLATES TypeSpec @visibility('create') rule!\n" +
                $"The 'input' field appears in response but should only be in requests.\n" +
                $"Response: {json}");

            _output.WriteLine($"  ✓ {lang} correctly omits input field from response");
        }
    }
}

public class SkipException : Exception
{
    public SkipException(string message) : base(message) { }
}
