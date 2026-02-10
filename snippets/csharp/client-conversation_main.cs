// Create a persistent conversation
var conversation = client.CreateConversation();

// First message
var response1 = await conversation.SendAsync("What's the capital of France?");
Console.WriteLine($"Agent: {response1}");

// Follow-up - context is automatically maintained
var response2 = await conversation.SendAsync("What's the population?");
Console.WriteLine($"Agent: {response2}");

// Save thread ID to resume later
Console.WriteLine($"Thread ID: {conversation.ThreadId}");