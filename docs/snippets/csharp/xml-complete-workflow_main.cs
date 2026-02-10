using Microsoft.Agents.Protocol.Client;
using Microsoft.Agents.Protocol.Xml;
using Microsoft.Agents.Validation;

public class ProductionAgentService
{
    private readonly AgentProtocolClient _client;
    private readonly MessageSerializer _serializer = new();
    private readonly ThreadValidator _validator = new();

    public ProductionAgentService(string endpoint)
    {
        // Enable automatic logging
        _client = new AgentProtocolClient(
            endpoint,
            enableLogging: true,
            logDirectory: "logs/production"
        );
    }

    // 1. Have conversations via Client SDK (auto-logged)
    public async Task<string> ChatAsync(string userInput, string? threadId = null)
    {
        var conversation = threadId == null
            ? _client.CreateConversation()
            : _client.ResumeConversation(threadId);

        return await conversation.SendAsync(userInput).ConfigureAwait(false);
    }

    // 2. Export conversation XML instantly
    public string ExportConversation(string threadId)
    {
        var conversation = _client.ResumeConversation(threadId);
        return conversation.ToString();  // Instant XML export
    }

    // 3. Run tests from XML eval files
    public async Task<bool> RunTestAsync(string evalFile)
    {
        var xml = await File.ReadAllTextAsync(evalFile).ConfigureAwait(false);
        var testMessages = _serializer.DeserializeMany(xml, "eval");

        var userMsg = testMessages.OfType<UserMessage>().First();
        var conversation = _client.CreateConversation();

        var userText = userMsg.Contents.OfType<TextContent>().First().Text;
        await conversation.SendAsync(userText).ConfigureAwait(false);

        // Use local message cache (no HTTP call)
        var actual = conversation.Messages.ToArray();

        return _validator.Validate(actual, testMessages.ToArray()).IsValid;
    }

    // 4. Replay logged conversations for debugging
    public async Task ReplayAsync(string logFile)
    {
        var xml = await File.ReadAllTextAsync(logFile).ConfigureAwait(false);
        var messages = _serializer.DeserializeMany(xml, "thread");

        var conversation = _client.CreateConversation();

        foreach (var msg in messages.OfType<UserMessage>())
        {
            var text = msg.Contents.OfType<TextContent>().First().Text;
            var response = await conversation.SendAsync(text).ConfigureAwait(false);
            Console.WriteLine($"User: {text}\nAgent: {response}\n");
        }
    }
}
