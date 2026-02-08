# Agent Samples

This directory contains agent samples demonstrating various capabilities of the Agent Framework.

## Available Samples

### 1. EchoBot
A simple echo bot that demonstrates the basic agent structure and message handling.

**Path**: `EchoBot/`

**Features**:
- Basic agent setup
- Message echo functionality
- ASP.NET Core integration
- Teams manifest configuration

### 2. FunctionToolsAgent
An agent with custom function calling capabilities demonstrating tool integration.

**Path**: `FunctionToolsAgent/`

**Features**:
- Custom function tools (weather, time)
- Streaming and non-streaming responses
- Microsoft Foundry integration
- Multiple tool usage patterns

**Run it**:
```bash
cd FunctionToolsAgent
dotnet run
```

## Configuration

All samples use the `.env` file in the project root for configuration. Make sure you have:

```bash
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
```

See `.env.example` in the project root for a template.

## Prerequisites

- .NET 8.0 or .NET 10.0 SDK
- Microsoft Foundry endpoint and API key
- Azure CLI (optional, for Azure authentication)

## Next Steps

Explore the Python and TypeScript samples in `python/samples/agents/` and `typescript/samples/agents/` respectively.
