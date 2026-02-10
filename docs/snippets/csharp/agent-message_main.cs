// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create agent response
var message = new AgentMessage
{
    AgentId = "agent-456",
    MessageId = "msg-789",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "The current weather in Seattle is 55°F and partly cloudy." }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);