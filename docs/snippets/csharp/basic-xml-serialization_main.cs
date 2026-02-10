// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create a simple text message
var message = new UserMessage
{
    MessageId = "msg-001",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "Hello, how can you help me today?" }
    }
};

// Serialize to XML
var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);

Console.WriteLine(xmlOutput);