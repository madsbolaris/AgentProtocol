// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create a message with text and image
var message = new UserMessage
{
    MessageId = "msg-002",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "What's in this image?" },
        new ImageContent
        {
            Uri = "https://example.com/image.jpg",
            Alt = "A photo of a sunset"
        }
    }
};

// Serialize to XML
var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);