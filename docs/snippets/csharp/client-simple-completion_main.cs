// Send message and get response
string response = await client.CompleteChatAsync("What can you help me with?");
Console.WriteLine(response);