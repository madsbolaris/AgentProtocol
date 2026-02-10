// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Create message with error
var message = new AgentMessage
{
    AgentId = "agent-456",
    MessageId = "msg-error-1",
    Contents = new List<AIContent>
    {
        new ErrorContent
        {
            Code = "rate_limit_exceeded",
            Message = "Rate limit exceeded. Please try again in 60 seconds."
        }
    }
};

var serializer = new MessageSerializer();
var xmlOutput = serializer.Serialize(message);
Console.WriteLine(xmlOutput);