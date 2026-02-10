using Microsoft.Agents.Protocol.Client;
using Microsoft.Agents.Protocol.Xml;
using Microsoft.Agents.Validation;
using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

public class EvaluationRunner
{
    private readonly AgentProtocolClient _client;
    private readonly MessageSerializer _serializer = new();
    private readonly ThreadValidator _validator = new();

    public EvaluationRunner(string agentEndpoint)
    {
        _client = new AgentProtocolClient(agentEndpoint);
    }

    public async Task<bool> RunEvaluationAsync(string testFilePath)
    {
        // Load evaluation test case from XML
        string evalXml = await File.ReadAllTextAsync(testFilePath).ConfigureAwait(false);
        var testMessages = _serializer.DeserializeMany(evalXml, "eval");

        // Extract the user input from the test case
        var userMessage = testMessages.OfType<UserMessage>().First();
        var expectedMessages = testMessages.Skip(1).ToList();

        // Send to agent via Client SDK
        var conversation = _client.CreateConversation();
        var userText = userMessage.Contents.OfType<TextContent>().First().Text;
        await conversation.SendAsync(userText).ConfigureAwait(false);

        // Get messages from local cache (no HTTP call)
        var actualMessages = conversation.Messages.ToArray();

        // Validate actual vs expected behavior
        var validationResult = _validator.Validate(actualMessages, expectedMessages.ToArray());

        if (validationResult.IsValid)
        {
            Console.WriteLine($"✓ Test passed: {testFilePath}");
            return true;
        }
        else
        {
            Console.WriteLine($"✗ Test failed: {testFilePath}");
            foreach (var error in validationResult.Errors)
            {
                Console.WriteLine($"  - {error.Message}");
            }
            return false;
        }
    }
}

// Usage: Run all evals
var runner = new EvaluationRunner("http://localhost:5000");
var testFiles = Directory.GetFiles("test-cases", "*.xml");
foreach (var testFile in testFiles)
{
    await runner.RunEvaluationAsync(testFile).ConfigureAwait(false);
}
