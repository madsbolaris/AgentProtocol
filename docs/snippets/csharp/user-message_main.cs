// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create user message
var message = new UserMessage
{
    MessageId = "user-123",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "What is the weather in Seattle?" }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);