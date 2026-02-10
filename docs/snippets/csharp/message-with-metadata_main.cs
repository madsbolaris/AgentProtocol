// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create message with metadata
var message = new UserMessage
{
    MessageId = "msg-meta-1",
    CreatedAt = DateTime.Parse("2024-01-15T10:30:00Z").ToUniversalTime(),
    Contents = new List<AIContent>
    {
        new TextContent { Text = "Hello!" }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);