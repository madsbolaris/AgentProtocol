# Define tools using lambda functions
tools = ToolCollection()
tools.add("get_weather", lambda location: f"The weather in {location} is sunny and 72°F")
tools.add("get_time", lambda timezone: "2024-01-15 14:30:00")

# Use tools in chat
options = ChatOptions(tools=tools)
response = await client.complete_chat("What's the weather in Seattle?", options)
print(response)