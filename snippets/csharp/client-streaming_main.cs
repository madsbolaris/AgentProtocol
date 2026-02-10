Console.Write("Agent: ");
await client.StreamChatAsync(
    "Tell me a story about a robot",
    onTextChunk: text => Console.Write(text)
);
Console.WriteLine();