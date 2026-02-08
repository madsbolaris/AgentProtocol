using Microsoft.Agents.Xml.Generated.Models;
using Microsoft.Agents.Xml.Serialization;
using System.Linq;

// Create conversation thread
var thread = new List<object>
{
    new SystemMessage { Contents = new List<AIContentBase> { new TextContent { Text = "You are a helpful assistant." } } },
    new ChatMessage { Role = "user", Contents = new List<AIContentBase> { new TextContent { Text = "Hello!" } } },
    new AgentMessage { Contents = new List<AIContentBase> { new TextContent { Text = "Hi! How can I help?" } } }
};

// Serialize thread
var serializer = new MessageSerializer();
var threadXml = thread.Select(msg => serializer.Serialize(msg)).ToList();

Console.WriteLine($"Thread length: {threadXml.Count} messages");