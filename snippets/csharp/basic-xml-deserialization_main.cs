// using Microsoft.Agents.Xml.Generated.Models;
            // using Microsoft.Agents.Protocol.Xml;

            var xmlInput = @"<?xml version=""1.0"" encoding=""utf-8""?>
<chat role=""user"" messageId=""msg-001"">
  <text>Hello, agent!</text>
</chat>";

            // Deserialize XML to object
            var serializer = new MessageSerializer();
            var message = serializer.Deserialize(xmlInput);

            Console.WriteLine($"Role: {message.Role}");
            Console.WriteLine($"Text: {(message.Contents[0] as TextContent)?.Text}");