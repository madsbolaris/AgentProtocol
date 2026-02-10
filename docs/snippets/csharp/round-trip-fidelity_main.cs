// using Microsoft.Agents.Xml.Generated.Models;
// using Microsoft.Agents.Protocol.Xml;

// Original message
var original = new UserMessage
{
    MessageId = "msg-roundtrip",
    Contents = new List<AIContent>
    {
        new TextContent { Text = "Test message" }
    }
};

// Serialize then deserialize
var serializer = new MessageSerializer();
var xml = serializer.Serialize(original);
var restored = serializer.Deserialize(xml);

// Verify fidelity
Assert.Equal(original.Role, restored.Role);
Assert.Equal(original.MessageId, restored.MessageId);
Assert.Equal((original.Contents[0] as TextContent)?.Text, (restored.Contents[0] as TextContent)?.Text);

Console.WriteLine("✓ Round-trip successful");