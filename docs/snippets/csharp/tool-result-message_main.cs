// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create tool result message
var message = new ToolMessage
{
    MessageId = "msg-result-1",
    Contents = new List<AIContent>
    {
        new FunctionResultContent
        {
            CallId = "call_abc123",
            Name = "get_weather",
            Result = "{\"temperature\": 55, \"conditions\": \"partly cloudy\"}"
        }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);