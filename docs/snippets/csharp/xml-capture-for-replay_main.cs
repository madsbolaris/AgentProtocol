using Microsoft.Agents.Protocol.Client;

// Have a conversation via Client SDK
var client = new AgentProtocolClient("http://localhost:5000");
var conversation = client.CreateConversation();
await conversation.SendAsync("Book a flight to Seattle").ConfigureAwait(false);
await conversation.SendAsync("The first one").ConfigureAwait(false);

// Export conversation instantly with ToString()
var xml = conversation.ToString();

// Save or send to developer
await File.WriteAllTextAsync("customer-issue-456.xml", xml).ConfigureAwait(false);
Console.WriteLine("Exported conversation to customer-issue-456.xml");
