# Microsoft Agents Protocol Client

A TypeScript client SDK for interacting with Agent Protocol-compliant services. Provides both low-level and high-level APIs for building AI agent applications.

## Installation

```bash
npm install @microsoft/agents-protocol-client
```

## Quick Start

### High-Level API (Recommended)

The simplified client provides an easy-to-use API for common scenarios:

```typescript
import { SimplifiedClient } from '@microsoft/agents-protocol-client';

const client = new SimplifiedClient({
  baseUrl: 'http://localhost:5000',
  authToken: 'your-token', // optional
});

// Simple text completion
const response = await client.completeChat('What is the weather today?');
console.log(response); // "The weather is sunny and 72°F"

// Streaming responses
await client.streamChat(
  'Tell me a story',
  (chunk) => {
    process.stdout.write(chunk);
  }
);
```

### Stateful Conversations

Maintain conversation state across multiple messages:

```typescript
const conversation = client.createConversation();

// First message
const response1 = await conversation.send('My name is Alice');
console.log(response1); // "Nice to meet you, Alice!"

// Second message - agent remembers context
const response2 = await conversation.send('What is my name?');
console.log(response2); // "Your name is Alice"

// Resume an existing conversation
const resumed = client.resumeConversation('thread-123');
```

### Structured Messages

Send and receive multi-modal messages:

```typescript
import type { ChatMessage } from '@microsoft/agents';

const message: ChatMessage = {
  role: 'user',
  messageId: 'msg-1',
  contents: [
    { type: 'text', text: 'What is in this image?' },
    { type: 'image', url: 'https://example.com/image.jpg' },
  ],
};

const response = await client.completeChatStructured(message);
console.log(response.contents);
```

### Tool Calling (Function Calling)

Register tools that the agent can call:

```typescript
import { ToolCollection } from '@microsoft/agents-protocol-client';

const tools = new ToolCollection();

// Add tools
tools.add(
  'get_weather',
  async (location: string) => {
    // Your implementation
    return { temperature: 72, condition: 'sunny' };
  },
  'Gets the current weather for a location'
);

tools.add(
  'calculate',
  (operation: string, x: number, y: number) => {
    if (operation === 'add') return x + y;
    if (operation === 'multiply') return x * y;
    return 0;
  },
  'Performs mathematical calculations'
);

// Use tools in chat
const response = await client.completeChat(
  'What is 5 + 3 and what is the weather in Seattle?',
  {
    tools,
    onToolCallStarted: async (info) => {
      console.log(`Calling tool: ${info.name}`);
    },
    onToolCallCompleted: async (info, result) => {
      console.log(`Tool ${info.name} returned:`, result);
    },
  }
);
```

### Streaming Events

Stream raw events for full control:

```typescript
const conversation = client.createConversation();

for await (const event of conversation.streamEvents('Hello')) {
  console.log(`Event: ${event.eventType}`, event.data);

  if (event.eventType === 'message.created') {
    console.log('New message created');
  } else if (event.eventType === 'message.delta') {
    console.log('Message updated');
  } else if (event.eventType === 'run.completed') {
    console.log('Run completed');
  }
}
```

### Streaming Messages

Stream structured messages during a conversation:

```typescript
const conversation = client.createConversation();

for await (const message of conversation.streamMessages('Tell me about AI')) {
  console.log(`Message ${message.messageId}:`, message.contents);
}
```

## Low-Level API

For advanced use cases, use the low-level client:

```typescript
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

const client = new AgentProtocolClient({
  baseUrl: 'http://localhost:5000',
  authToken: 'your-token',
  timeout: 30000,
  maxRetries: 3,
});

// Direct access to API resources
const run = await client.runs.create({
  agentId: 'agent-123',
  input: [{ role: 'user', messageId: 'msg-1', contents: [...] }],
});

const thread = await client.threads.get('thread-123');
const messages = await client.messages.list({ threadId: 'thread-123' });
```

## Configuration Options

```typescript
interface AgentProtocolClientConfig {
  /** Base URL of the Agent Protocol API */
  baseUrl: string;

  /** Authentication token (Bearer) */
  authToken?: string;

  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;

  /** Maximum retry attempts for failed requests (default: 3) */
  maxRetries?: number;

  /** Custom headers to include in all requests */
  headers?: Record<string, string>;

  /** Enable debug logging */
  debug?: boolean;
}
```

## Chat Options

```typescript
interface ChatOptions {
  /** Agent ID to use (optional if only one agent registered) */
  agentId?: string;

  /** Tools available for the agent to call */
  tools?: ToolCollection;

  /** Additional metadata for the request */
  metadata?: Record<string, unknown>;

  /** Callback fired when a tool call starts */
  onToolCallStarted?: (info: ToolCallInfo) => Promise<void>;

  /** Callback fired when a tool call completes */
  onToolCallCompleted?: (info: ToolCallInfo, result: unknown) => Promise<void>;

  /** Callback fired when a tool call fails */
  onToolCallFailed?: (info: ToolCallInfo, error: Error) => Promise<void>;
}
```

## Error Handling

The client provides typed errors:

```typescript
import {
  AgentProtocolError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
  TimeoutError,
  NetworkError,
} from '@microsoft/agents-protocol-client';

try {
  const response = await client.completeChat('Hello');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid auth token');
  } else if (error instanceof NotFoundError) {
    console.error('Agent or resource not found');
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded, retry after:', error.retryAfter);
  } else if (error instanceof TimeoutError) {
    console.error('Request timed out');
  } else if (error instanceof NetworkError) {
    console.error('Network error occurred');
  }
}
```

## Cancellation

All async methods support cancellation via AbortSignal:

```typescript
const controller = new AbortController();

// Cancel after 5 seconds
setTimeout(() => controller.abort(), 5000);

try {
  const response = await client.completeChat(
    'Long running task',
    undefined,
    controller.signal
  );
} catch (error) {
  if (controller.signal.aborted) {
    console.log('Request was cancelled');
  }
}
```

## TypeScript Support

The client is written in TypeScript with full type definitions:

```typescript
import type {
  ChatMessage,
  ChatRole,
  TextContent,
  ImageContent,
  Run,
  Thread,
  AITool,
} from '@microsoft/agents';

// All types are fully typed
const message: ChatMessage = {
  role: 'user',
  messageId: 'msg-1',
  contents: [
    { type: 'text', text: 'Hello' } as TextContent,
  ],
};
```

## Examples

See the [examples](./examples) directory for complete working examples:

- Basic chat completion
- Streaming responses
- Stateful conversations
- Tool calling
- Multi-modal messages
- Error handling
- Advanced usage

## API Reference

### SimplifiedClient

- `completeChat(message, options?, signal?)` - Send text message and get text response
- `completeChatStructured(message, options?, signal?)` - Send structured message
- `streamChat(message, onTextChunk, options?, signal?)` - Stream text responses
- `createConversation()` - Create new stateful conversation
- `resumeConversation(threadId)` - Resume existing conversation

### IConversation

- `threadId` - Current thread ID (undefined until first message)
- `send(message, signal?)` - Send text message
- `sendStructured(message, signal?)` - Send structured message
- `streamMessages(message, signal?)` - Stream messages
- `streamEvents(message, signal?)` - Stream raw events

### ToolCollection

- `add(name, handler, description?)` - Add a tool
- `get(name)` - Get tool by name
- `getAll()` - Get all tools
- `execute(name, argumentsJson)` - Execute a tool
- `has(name)` - Check if tool exists
- `remove(name)` - Remove a tool
- `clear()` - Remove all tools
- `size` - Number of tools

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.
