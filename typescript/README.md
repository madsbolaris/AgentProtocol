# Microsoft Agents - TypeScript Packages

TypeScript implementation of the Microsoft Agents Protocol, including client libraries, server middleware, validation, and React UI components.

## Packages

### Core Packages

- **[@microsoft/agents](./packages/agents/)** - Core TypeScript types generated from TypeSpec definitions
- **[@microsoft/agents-protocol-client](./packages/agents-protocol-client/)** - HTTP/SSE client for consuming Agent Protocol APIs
- **[@microsoft/agents-protocol](./packages/agents-protocol/)** - Express middleware for building Agent Protocol servers
- **[@microsoft/agents-validation](./packages/agents-validation/)** - Runtime validation framework for protocol types

### UI & Utilities

- **[@microsoft/agents-react](./packages/agents-react/)** - React component library for chat interfaces
- **[@microsoft/agents-xml](./packages/agents-xml/)** - XML serialization/deserialization support

### Testing

- **[@microsoft/agents-test-helpers](./packages/test-helpers/)** - Test utilities and helpers

## Getting Started

### Installation

```bash
# Install dependencies for all packages
npm install

# Generate TypeScript types from TypeSpec
npm run generate

# Build all packages
npm run build
```

### Development

```bash
# Watch mode for all packages
npm run dev

# Run tests
npm run test

# Clean build artifacts
npm run clean
```

## Package Overview

### Building a Chat Application

```typescript
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { AgentProvider, ChatThread } from '@microsoft/agents-react';

const client = new AgentProtocolClient({
  baseUrl: 'http://localhost:3980'
});

function App() {
  return (
    <AgentProvider client={client}>
      <ChatThread
        threadId="thread_123"
        agentId="agent_456"
        userId="user_789"
        enableStreaming={true}
      />
    </AgentProvider>
  );
}
```

### Building an Agent Server

```typescript
import express from 'express';
import { createAgentProtocolRouter } from '@microsoft/agents-protocol';

const app = express();
app.use(express.json());

app.use(createAgentProtocolRouter({
  handlers: {
    onRunCreate: async (request) => {
      // Your agent logic
      return { runId: 'run_123', status: 'completed', output: [...] };
    }
  }
}));

app.listen(3980);
```

## Samples

- **[EchoBot](./samples/EchoBot/)** - Simple echo bot server implementation
- **[chat-demo](./samples/chat-demo/)** - React chat UI demonstration
- **[custom-ui-demo](./samples/custom-ui-demo/)** - Headless hooks for custom UIs

## Documentation

- [TypeSpec Definitions](../specs/typespec/) - Protocol type definitions
- [API Reference](https://madsbolaris.github.io/AgentFramework/) - Complete API documentation
- [Implementation Guide](../TYPESCRIPT_PACKAGES_REVISED_PLAN.md) - Package architecture and design

## Contributing

This is part of the Microsoft Agent Protocol monorepo. See the main [README](../README.md) for contribution guidelines.

## License

MIT
