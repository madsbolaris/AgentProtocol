// Define tools with lambda functions
var tools = new ToolCollection
{
    ["get_weather"] = (string location) =>
        $"The weather in {location} is 72°F and sunny",

    ["get_time"] = (string timezone) =>
        DateTime.UtcNow.ToString("HH:mm")
};

// SDK automatically executes tools when agent requests them
var options = new ChatOptions { Tools = tools };
var response = await client.CompleteChatAsync(
    "What's the weather in San Francisco?",
    options
);

Console.WriteLine(response);