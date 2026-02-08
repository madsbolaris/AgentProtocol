# Function Tools Agent Samples

This document describes the Function Tools Agent samples that have been added to the project.

## Overview

Three samples have been created demonstrating agent function calling capabilities:

1. **.NET Sample** - Full Agent Framework SDK example
2. **Python Sample** - Python Agent Framework example  
3. **TypeScript Sample** - Protocol-level message structure example

## Sample Locations

```
AgentProtocol/
├── dotnet/samples/agents/FunctionToolsAgent/
│   ├── Program.cs
│   ├── FunctionToolsAgent.csproj
│   └── README.md
├── python/samples/agents/function_tools_agent/
│   ├── function_tools_agent.py
│   ├── requirements.txt
│   ├── __init__.py
│   └── README.md
└── typescript/samples/agents/function-tools-agent/
    ├── function-tools-agent.ts
    ├── package.json
    ├── tsconfig.json
    └── README.md
```

## Configuration

All samples use the `.env` file in the project root:

```bash
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
```

**Important**: The `.env` file contains secrets and is in `.gitignore`. A template is available at `.env.example`.

## Sample Details

### .NET Sample

**Status**: ⚠️ Reference Sample (requires Agent Framework SDK)

**Features**:
- Custom function tools (weather, time)
- Streaming and non-streaming responses
- Microsoft Foundry integration
- Multiple tool usage

**Note**: This sample demonstrates the Agent Framework SDK, which is separate from this protocol repository. To run it:
- Reference the [agent-framework repository](https://github.com/microsoft/agent-framework) locally, or
- Wait for Agent Framework NuGet packages to be published

### Python Sample

**Status**: ✅ Ready to Run (with agent-framework package)

**Features**:
- Agent-level and run-level tool configuration
- Custom function calling
- Microsoft Foundry integration
- Three usage patterns demonstrated

**Run it**:
```bash
cd python/samples/agents/function_tools_agent
pip install -r requirements.txt
python function_tools_agent.py
```

**Installation**:
```bash
# Install from agent-framework repo
cd ~/repos/agent-framework/python
pip install -e .

# Or wait for PyPI package
pip install agent-framework
```

### TypeScript Sample

**Status**: ✅ Ready to Run (Protocol Demo)

**Features**:
- Protocol message structure demonstrations
- Function calling message format
- Tool result response patterns
- No SDK dependency

**Run it**:
```bash
cd typescript/samples/agents/function-tools-agent
npm install
npm start
```

**Note**: This is a protocol-level example showing message structures. It does not make actual API calls but demonstrates the correct message format for function calling according to the Agent Protocol specification.

## What These Samples Demonstrate

### 1. Function Tool Definition
How to define custom functions that an agent can call:

**.NET**:
```csharp
[Description("Get the weather for a given location.")]
static string GetWeather([Description("The location to get the weather for.")] string location)
    => $"The weather in {location} is cloudy with a high of 15°C.";
```

**Python**:
```python
@tool(approval_mode="never_require")
def get_weather(location: Annotated[str, Field(description="The location to get the weather for.")]) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny with a high of 20°C."
```

**TypeScript** (Protocol):
```typescript
const functionTools = {
    get_weather: (location: string): string => {
        return `The weather in ${location} is sunny with a high of 20°C.`;
    }
};
```

### 2. Tool Integration Patterns

- **Agent-level tools**: Available for all queries
- **Run-level tools**: Specific to individual queries
- **Mixed tools**: Combining both approaches

### 3. Microsoft Foundry Integration

All samples are configured to use Microsoft Foundry as the LLM backend, reading configuration from the `.env` file.

## Relationship to AgentProtocol Project

This **AgentProtocol** repository focuses on:
- Message protocol definition
- XML/JSON serialization
- Protocol message models
- Type safety and validation

The **Agent Framework** (separate repo) provides:
- High-level agent APIs
- LLM integration
- Tool execution
- Conversation management

These samples demonstrate Agent Framework capabilities but are included here for reference and to show how the protocol is used in practice.

## Running the Samples

### Prerequisites
1. Microsoft Foundry endpoint and API key
2. `.env` file configured (copy from `.env.example`)
3. Appropriate SDK installed for each language

### Quick Start

**.NET** (requires Agent Framework SDK):
```bash
cd dotnet/samples/agents/FunctionToolsAgent
# Update project reference to agent-framework repo
dotnet run
```

**Python** (requires agent-framework package):
```bash
cd python/samples/agents/function_tools_agent
pip install agent-framework
python function_tools_agent.py
```

**TypeScript** (protocol demo - no SDK needed):
```bash
cd typescript/samples/agents/function-tools-agent
npm install
npm start
```

## Next Steps

1. **Try the Python sample** - Most straightforward to run if you have the agent-framework package
2. **Explore the TypeScript protocol example** - Understand message structures
3. **Review the .NET sample** - See how it would work with the SDK
4. **Check out the EchoBot sample** - See a working example using just the protocol layer

## Related Documentation

- [Agent Framework Repository](https://github.com/microsoft/agent-framework)
- [EchoBot Sample](dotnet/samples/agents/EchoBot/)
- [Microsoft Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)

## Script Used

The samples were created using `copy-function-tools-sample.sh` which:
1. Copied samples from the agent-framework repository
2. Modified them to use Foundry configuration
3. Added appropriate documentation
4. Created language-specific project files

To recreate or update:
```bash
./copy-function-tools-sample.sh
```
