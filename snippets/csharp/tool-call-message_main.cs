// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create agent message with tool call
var message = new AgentMessage
{
    AgentId = "agent-456",
    MessageId = "msg-call-1",
    Contents = new List<AIContent>
    {
        new FunctionCallContent
        {
            CallId = "call_abc123",
            Name = "get_weather",
            Arguments = "{\"location\": \"Seattle\", \"unit\": \"fahrenheit\"}"
        }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);