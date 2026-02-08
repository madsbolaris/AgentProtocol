# Foundry LLM Integration Summary

This document summarizes the integration of Microsoft Foundry LLM with the Function Tools Agent samples across all three languages (.NET, Python, TypeScript).

## Overview

All three Function Tools Agent samples have been updated to use actual LLM function calling with Microsoft Foundry instead of simple pattern matching. The agents now:

1. **Connect to Foundry LLM** using credentials from `.env` file
2. **Use real function calling** where the LLM decides when to call functions
3. **Maintain conversation history** for context-aware responses
4. **Handle multi-turn interactions** with tool calls and responses

## Configuration

All samples read from the `.env` file in the repository root:

```env
FOUNDRY_ENDPOINT=https://east-us-2-proj-resource.services.ai.azure.com/api/projects/east-us-2-proj
FOUNDRY_API_KEY=<your-api-key>
FOUNDRY_MODEL_DEPLOYMENT=gpt-5-nano
```

## Implementation Details

### .NET Implementation

**Files Modified:**
- `FunctionToolsAgent.csproj` - Added `DotNetEnv` package (v3.1.1)
- `FunctionToolsAgent.cs` - Integrated OpenAI ChatClient with function calling
- `Program.cs` - Added `.env` file loading

**Key Changes:**
```csharp
// Initialize ChatClient with Foundry credentials
_chatClient = new ChatClient(
    credential: new ApiKeyCredential(apiKey),
    model: model,
    options: new OpenAIClientOptions()
    {
        Endpoint = new Uri($"{endpoint}/openai/v1/")
    });

// Define function tools for the LLM
var tools = new List<ChatTool>
{
    ChatTool.CreateFunctionTool(
        functionName: "GetWeatherAsync",
        functionDescription: "Get the weather for a given location.",
        functionParameters: BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": { "type": "string", "description": "..." }
            },
            "required": ["location"]
        }
        """))
};

// Call LLM in a loop to handle function calls
while (iteration < maxIterations)
{
    var completion = await _chatClient.CompleteChatAsync(messages, chatOptions, cancellationToken);

    if (completion.Value.FinishReason == ChatFinishReason.ToolCalls)
    {
        // Execute function and add result to conversation
        foreach (var toolCall in completion.Value.ToolCalls)
        {
            var result = await ExecuteFunctionAsync(toolCall);
            messages.Add(new ToolChatMessage(toolCall.Id, result));
        }
    }
    else
    {
        // Get final response from LLM
        break;
    }
}
```

**Dependencies:**
- `Azure.AI.OpenAI` (v2.1.0) - Already present
- `DotNetEnv` (v3.1.1) - Newly added

### Python Implementation

**Files Modified:**
- `requirements.txt` - Added `openai>=1.0.0`
- `agent.py` - Integrated AsyncOpenAI client with function calling

**Key Changes:**
```python
# Initialize OpenAI client for Foundry
openai_client = AsyncOpenAI(
    api_key=foundry_api_key,
    base_url=f"{foundry_endpoint}/openai/v1"
)

# Define function tools for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "..."}
                },
                "required": ["location"]
            }
        }
    }
]

# Call LLM with function calling
completion = await openai_client.chat.completions.create(
    model=foundry_model,
    messages=conversation_history[conversation_id],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if choice.finish_reason == "tool_calls" and message.tool_calls:
    for tool_call in message.tool_calls:
        function_result = execute_function(tool_call)
        conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": function_result
        })
```

**Dependencies:**
- `openai>=1.0.0` - Newly added

### TypeScript Implementation

**Files Modified:**
- `package.json` - Added `openai@^4.0.0`
- `index.ts` - Integrated OpenAI client with function calling, loaded `.env`

**Key Changes:**
```typescript
// Initialize OpenAI client for Foundry
const openaiClient = new OpenAI({
  apiKey: foundryApiKey,
  baseURL: `${foundryEndpoint}/openai/v1`
});

// Define function tools for the LLM
const tools: OpenAI.Chat.ChatCompletionTool[] = [
  {
    type: 'function',
    function: {
      name: 'getWeather',
      description: 'Get the weather for a given location.',
      parameters: {
        type: 'object',
        properties: {
          location: { type: 'string', description: '...' }
        },
        required: ['location']
      }
    }
  }
];

// Call LLM with function calling
const completion = await openaiClient.chat.completions.create({
  model: foundryModel,
  messages: conversationHistory[conversationId],
  tools: tools,
  tool_choice: 'auto'
});

// Handle tool calls
if (choice.finish_reason === 'tool_calls' && message.tool_calls) {
  for (const toolCall of message.tool_calls) {
    const functionResult = executeFunction(toolCall);
    conversationHistory.push({
      role: 'tool',
      tool_call_id: toolCall.id,
      content: functionResult
    });
  }
}
```

**Dependencies:**
- `openai@^4.0.0` - Newly added

## Architecture Pattern

All three implementations follow the same architectural pattern:

1. **Initialization**:
   - Load environment variables from `.env` file
   - Create LLM client with Foundry endpoint and API key
   - Initialize conversation history storage

2. **Message Handling**:
   - Add user message to conversation history
   - Define available function tools
   - Call LLM with tools in a loop (max 5 iterations)

3. **Function Calling Loop**:
   - LLM decides if it needs to call a function
   - If yes: Execute the function and add result to history, then loop
   - If no: Return the LLM's final response to the user

4. **Conversation Context**:
   - Maintain conversation history per conversation ID
   - Include system message with agent instructions
   - Preserve full context across turns

## Available Functions

Both samples expose two function tools to the LLM:

1. **GetWeather / get_weather / getWeather**
   - Description: Get the weather for a given location
   - Parameters: `location` (string)
   - Returns: Simulated weather information

2. **GetCurrentTime / get_time / getTime**
   - Description: Get the current UTC time
   - Parameters: None
   - Returns: Current UTC timestamp

## Testing

To test the integration:

1. **Start the agent**:
   ```bash
   # .NET
   cd dotnet/samples/agents/FunctionToolsAgent
   dotnet run

   # Python
   cd python/samples/agents/function_tools_agent
   python -m src.main

   # TypeScript
   cd typescript/samples/agents/function-tools-agent
   npm start
   ```

2. **Send a message** to the `/api/messages` endpoint:
   ```bash
   curl -X POST http://localhost:3981/api/messages \
     -H "Content-Type: application/json" \
     -d '{
       "type": "message",
       "from": {"id": "user1"},
       "conversation": {"id": "conv1"},
       "text": "What is the weather in Seattle?"
     }'
   ```

3. **Expected behavior**:
   - The LLM will recognize the need to call the weather function
   - It will extract "Seattle" as the location parameter
   - The agent will execute `GetWeather("Seattle")`
   - The LLM will format a natural response using the weather data

## Benefits Over Pattern Matching

The new LLM-based approach provides several advantages:

1. **Natural Language Understanding**: The LLM can understand intent without exact keyword matching
2. **Parameter Extraction**: The LLM extracts function parameters intelligently
3. **Multi-step Reasoning**: Can call multiple functions in sequence if needed
4. **Natural Responses**: Responses are more conversational and context-aware
5. **Extensibility**: Easy to add new functions - just define them in the tools array

## Example Interaction

**User**: "Hey, what's the weather like in Tokyo and what time is it?"

**Without LLM (old pattern matching)**:
- Would only respond to one query (whichever keyword matches first)

**With LLM (new implementation)**:
1. LLM recognizes need for both weather and time functions
2. Calls `getWeather("Tokyo")` → Gets weather data
3. Calls `getTime()` → Gets current time
4. LLM synthesizes: "The weather in Tokyo is sunny with a temperature of 22°C. The current UTC time is 2024-01-15 14:30:00."

## Next Steps

Potential enhancements:

1. **Add Real APIs**: Replace simulated functions with actual weather and time APIs
2. **More Functions**: Add calendar, search, calculator, etc.
3. **Streaming**: Implement streaming responses for real-time feedback
4. **Error Handling**: Enhanced error handling for API failures
5. **Rate Limiting**: Add rate limiting for LLM calls
6. **Caching**: Cache LLM responses for common queries
7. **Telemetry**: Add logging and telemetry for function calls

## Troubleshooting

**Issue**: "FOUNDRY_ENDPOINT environment variable is required"
- **Solution**: Ensure `.env` file exists in repository root with correct values

**Issue**: Build fails with OpenAI SDK errors
- **Solution**: Run `dotnet restore` / `pip install -r requirements.txt` / `npm install`

**Issue**: LLM doesn't call functions
- **Solution**: Check that `tool_choice` is set to `"auto"` and functions are properly defined

**Issue**: Functions execute but LLM doesn't respond
- **Solution**: Check max iterations limit and ensure loop exits correctly
