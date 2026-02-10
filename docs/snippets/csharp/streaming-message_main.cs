// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create streaming chunk
var chunk = new AgentMessage
{
    AgentId = "agent-456",
    MessageId = "msg-stream-1",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "The weather " }
    }
};

var serializer = new MessageSerializer();
var xmlChunk = serializer.Serialize(chunk);
Console.WriteLine($"Chunk: {xmlChunk}");