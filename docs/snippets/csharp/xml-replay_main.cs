using Microsoft.Agents.Protocol.Client;
using Microsoft.Agents.Protocol.Xml;
using System.Diagnostics;

// Load customer's conversation from XML
string xml = await File.ReadAllTextAsync("customer-issue-456.xml").ConfigureAwait(false);
var serializer = new MessageSerializer();
var messages = serializer.DeserializeMany(xml, "thread");

// Extract thread ID if it exists (for resuming context)
var threadId = ExtractThreadId(xml); // Parse thread-id attribute

// Replay through agent using Client SDK
var client = new AgentProtocolClient("http://localhost:5000");
var stopwatch = Stopwatch.StartNew();

foreach (var message in messages.OfType<UserMessage>())
{
    Console.WriteLine($"\n--- User Message ---");
    var userText = message.Contents.OfType<TextContent>().First().Text;
    Console.WriteLine($"User: {userText}");

    // Re-run through agent via Client SDK
    var conversation = threadId != null
        ? client.ResumeConversation(threadId)
        : client.CreateConversation();

    stopwatch.Restart();
    var response = await conversation.SendAsync(userText).ConfigureAwait(false);
    stopwatch.Stop();

    Console.WriteLine($"Response time: {stopwatch.ElapsedMilliseconds}ms");
    Console.WriteLine($"Agent: {response}");
}

Console.WriteLine("\n✓ Replay complete - verify behavior matches expectations");
