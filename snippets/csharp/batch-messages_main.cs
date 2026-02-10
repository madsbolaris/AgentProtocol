// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;
// using System.Linq;

// Create batch of messages
var messages = new List<ChatMessage>
{
    new UserMessage { Contents = new List<AIContent> { new TextContent { Text = "Message 1" } } },
    new UserMessage { Contents = new List<AIContent> { new TextContent { Text = "Message 2" } } },
    new UserMessage { Contents = new List<AIContent> { new TextContent { Text = "Message 3" } } }
};

// Process batch
var serializer = new MessageSerializer();
var xmlOutputs = messages.Select(msg => serializer.Serialize(msg)).ToList();

Console.WriteLine($"Processed {xmlOutputs.Count} messages");