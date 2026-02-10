// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;
// using System.Linq;

// Create conversation thread
var thread = new List<ChatMessage>
{
    new SystemMessage { Contents = new List<AIContent> { new TextContent { Text = "You are a helpful assistant." } } },
    new UserMessage { Contents = new List<AIContent> { new TextContent { Text = "Hello!" } } },
    new AgentMessage { Contents = new List<AIContent> { new TextContent { Text = "Hi! How can I help?" } } }
};

// Serialize thread
var serializer = new MessageSerializer();
var threadXml = thread.Select(msg => serializer.Serialize(msg)).ToList();

Console.WriteLine($"Thread length: {threadXml.Count} messages");