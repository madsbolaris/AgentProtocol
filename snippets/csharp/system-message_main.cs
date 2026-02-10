// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create system message with instructions
var message = new SystemMessage
{
    Contents = new List<AIContent>
    {
        new TextContent { Text = "You are a helpful assistant. Be concise and accurate." }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);