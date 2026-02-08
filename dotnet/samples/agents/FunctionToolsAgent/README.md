# Function Tools Agent (.NET)

An agent demonstrating custom function calling capabilities using the Microsoft Agent Protocol.

## Features

- **Custom Function Tools**: Weather and time information functions
- **Agent Protocol Support**: Full Agent Protocol HTTP endpoints (`/health`, `/runs`, etc.)
- **Bot Framework Compatible**: Works with `/api/messages` endpoint
- **Port Configuration**: Reads from centralized `agent-config.json`
- **Pattern Matching**: Simple text-based function calling simulation

## Architecture

This sample follows the Agent Protocol architecture:

```
FunctionToolsAgent.cs     - Agent implementation with function tools
Program.cs                - ASP.NET Core web host with Agent Protocol routes
AspNetExtensions.cs       - Authentication extensions
appsettings.json         - Agent configuration
```

## Prerequisites

- .NET 10.0 SDK or later
- Microsoft Agent Protocol packages (from this repository)

## Running the Sample

```bash
# From this directory
dotnet run

# Or from project root
dotnet run --project dotnet/samples/agents/FunctionToolsAgent
```

The agent will start on port **3981** (configured in `agent-config.json`).

## Agent Protocol Endpoints

Once running, the following endpoints are available:

- `GET http://localhost:3981/` - Root endpoint
- `POST http://localhost:3981/api/messages` - Bot Framework messages
- `GET http://localhost:3981/health` - Health check
- `POST http://localhost:3981/runs` - Create a run
- `POST http://localhost:3981/runs/wait` - Create and wait for completion
- `POST http://localhost:3981/runs/stream` - Create and stream results

## Testing the Agent

### Using curl

```bash
# Health check
curl http://localhost:3981/health

# Create a run
curl -X POST http://localhost:3981/runs \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "function-tools-agent",
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What'\''s the weather in Seattle?"}]
    }]
  }'
```

### Using Bot Framework Emulator

1. Open Bot Framework Emulator
2. Connect to `http://localhost:3981/api/messages`
3. Send messages like:
   - "What's the weather in Seattle?"
   - "What time is it?"

## Function Tools

This agent implements two function tools:

### 1. GetWeather(location)
Returns simulated weather information for a location.

**Example**: "What's the weather in London?"  
**Response**: "🌤️ The weather in London is cloudy with a temperature of 18°C."

### 2. GetTime()
Returns the current UTC time.

**Example**: "What time is it?"  
**Response**: "🕐 The current UTC time is 2026-02-07 21:30:00."

## Configuration

The agent reads its port from `agent-config.json` in the repository root:

```json
{
  "bots": {
    "dotnet-function-tools": {
      "name": "FunctionToolsAgent (.NET)",
      "port": 3981,
      "baseUrl": "http://localhost"
    }
  }
}
```

## Implementation Notes

- Uses `AgentApplication` base class for agent logic
- Implements simple pattern matching for function calling (in production, use actual LLM function calling)
- Supports Bot Framework activities and Agent Protocol messages
- CORS enabled for local development

## Next Steps

- Integrate with an LLM for actual function calling (see Azure OpenAI, OpenAI, etc.)
- Add more sophisticated function tools
- Implement tool approval workflows
- Add persistent conversation state

## Related Samples

- [EchoBot](../EchoBot/) - Simple echo bot showing basic structure
- [Python Function Tools Agent](../../../python/samples/agents/function_tools_agent/) - Python equivalent
- [TypeScript Function Tools Agent](../../../../typescript/samples/agents/function-tools-agent/) - TypeScript equivalent
