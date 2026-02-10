// Define tools using lambda functions
const tools = new ToolCollection();
tools.add('get_weather', (location: string) => `The weather in ${location} is sunny and 72°F`);
tools.add('get_time', (_timezone: string) => '2024-01-15 14:30:00');

// Use tools in chat  (client.completeChat would be called with { tools } option)
console.log(`Created ${tools.size} tools`);