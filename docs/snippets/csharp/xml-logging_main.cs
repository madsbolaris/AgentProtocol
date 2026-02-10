// Create client with automatic logging enabled
var client = new AgentProtocolClient(
    baseUrl: "http://localhost:5000",
    enableLogging: true  // That's it! Auto-saves to logs/conversations/
);

// Have a conversation - it's automatically logged
var conversation = client.CreateConversation();
var response = await conversation.SendAsync("What's the weather in Seattle?").ConfigureAwait(false);
Console.WriteLine($"Agent: {response}");

// Done! Conversation automatically saved to:
// logs/conversations/{threadId}.xml

// Or manually save to a custom location
var xml = conversation.ToString();
await File.WriteAllTextAsync("my-conversation.xml", xml).ConfigureAwait(false);
Console.WriteLine($"Saved conversation XML ({xml.Length} bytes)");
