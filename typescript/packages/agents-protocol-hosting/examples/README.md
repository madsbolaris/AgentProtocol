# Examples

This directory contains example implementations demonstrating various features of the Agents Hosting SDK.

## Running the Examples

1. Build the SDK:
   ```bash
   npm run build
   ```

2. Run an example:
   ```bash
   node examples/basic-agent.js
   ```

## Available Examples

### basic-agent.ts

A complete example showing:
- Creating an agent with LLM configuration
- Adding multiple functions with type-safe schemas
- Implementing user message handlers
- Graceful shutdown handling

### Coming Soon

- **multi-agent-routing.ts**: Routing requests to different specialized agents
- **production-config.ts**: Production-ready configuration with PostgreSQL and Redis
- **streaming-responses.ts**: Real-time streaming of LLM responses
- **state-management.ts**: Managing conversation state across turns
- **custom-storage.ts**: Implementing a custom storage backend
- **testing-example.ts**: Unit testing agents with mocks

## Notes

- All examples require environment variables (API keys, connection strings, etc.)
- See each example file for specific requirements
- Examples are written in TypeScript but can be compiled to JavaScript
