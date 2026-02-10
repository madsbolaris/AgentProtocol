public async Task<bool> RunMultiTurnEvalAsync(string testFilePath)
{
    // Load eval
    var xml = await File.ReadAllTextAsync(testFilePath).ConfigureAwait(false);
    var testMessages = _serializer.DeserializeMany(xml, "eval");

    // Extract user messages and expected responses
    var userMessages = testMessages.OfType<UserMessage>().ToList();

    // Use Client SDK with persistent conversation
    var conversation = _client.CreateConversation();
    var stopwatch = Stopwatch.StartNew();

    // Send each user message in sequence
    foreach (var userMsg in userMessages)
    {
        var text = userMsg.Contents.OfType<TextContent>().First().Text;
        await conversation.SendAsync(text).ConfigureAwait(false);
    }

    stopwatch.Stop();

    // Get messages from local cache (no HTTP call)
    var actualMessages = conversation.Messages.ToArray();

    // Validate against expected behavior
    var result = _validator.Validate(actualMessages, testMessages.ToArray());

    // Check metrics
    if (stopwatch.ElapsedMilliseconds > 2000)
    {
        Console.WriteLine($"⚠ Performance threshold exceeded: {stopwatch.ElapsedMilliseconds}ms");
    }

    return result.IsValid;
}
