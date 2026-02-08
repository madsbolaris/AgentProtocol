# Function Tools Agent (Python)

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
src/
├── agent.py          - Agent implementation with function tools
├── start_server.py   - aiohttp server with Agent Protocol routes
├── main.py          - Entry point
└── __init__.py
```

## Prerequisites

- Python 3.10 or later
- Microsoft Agents packages

## Installation

```bash
# Install from the parent python package
cd ../../../..
pip install -e .

# Or install specific dependencies
pip install microsoft-agents python-dotenv aiohttp
```

## Running the Sample

```bash
# From this directory
python -m src.main

# Or from project root
python -m python.samples.agents.function_tools_agent.src.main
```

The agent will start on port **3982** (configured in `agent-config.json`).

## Agent Protocol Endpoints

Once running, the following endpoints are available:

- `POST http://localhost:3982/api/messages` - Bot Framework messages
- `GET http://localhost:3982/health` - Health check
- `POST http://localhost:3982/runs` - Create a run
- `POST http://localhost:3982/runs/wait` - Create and wait for completion
- `POST http://localhost:3982/runs/stream` - Create and stream results

## Testing the Agent

### Using curl

```bash
# Health check
curl http://localhost:3982/health

# Create a run
curl -X POST http://localhost:3982/runs \
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
2. Connect to `http://localhost:3982/api/messages`
3. Send messages like:
   - "What's the weather in Seattle?"
   - "What time is it?"

## Function Tools

This agent implements two function tools:

### 1. get_weather(location)
Returns simulated weather information for a location.

**Example**: "What's the weather in London?"  
**Response**: "🌤️ The weather in London is cloudy with a temperature of 18°C."

### 2. get_time()
Returns the current UTC time.

**Example**: "What time is it?"  
**Response**: "🕐 The current UTC time is 2026-02-07 21:30:00."

## Configuration

The agent reads its port from `agent-config.json` in the repository root:

```json
{
  "bots": {
    "python-function-tools": {
      "name": "FunctionToolsAgent (Python)",
      "port": 3982,
      "baseUrl": "http://localhost"
    }
  }
}
```

## Implementation Notes

- Uses `AgentApplication` with decorator-based routing
- Implements simple pattern matching for function calling (in production, use actual LLM function calling)
- Supports Bot Framework activities and Agent Protocol messages
- CORS enabled for local development
- Async/await throughout

## Next Steps

- Integrate with an LLM for actual function calling (see Azure OpenAI, OpenAI, etc.)
- Add more sophisticated function tools
- Implement tool approval workflows
- Add persistent conversation state

## Related Samples

- [EchoBot](../echo-bot/) - Simple echo bot showing basic structure
- [.NET Function Tools Agent](../../../../dotnet/samples/agents/FunctionToolsAgent/) - C# equivalent
- [TypeScript Function Tools Agent](../../../../typescript/samples/agents/function-tools-agent/) - TypeScript equivalent
