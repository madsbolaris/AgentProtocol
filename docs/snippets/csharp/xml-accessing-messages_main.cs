var conversation = client.CreateConversation();
await conversation.SendAsync("Hello!").ConfigureAwait(false);
await conversation.SendAsync("How are you?").ConfigureAwait(false);

// Access cached messages (no HTTP call)
var messages = conversation.Messages;
Console.WriteLine($"Conversation has {messages.Count} messages");

// Or convert to XML instantly
var xml = conversation.ToString();
Console.WriteLine(xml);
