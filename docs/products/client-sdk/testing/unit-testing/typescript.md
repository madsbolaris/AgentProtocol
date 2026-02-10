# TypeScript Unit Testing

Unit testing patterns for TypeScript Client SDK applications.

## Overview

Best practices for unit testing Client SDK code in TypeScript using Jest or Vitest, the most popular testing frameworks for TypeScript/JavaScript.

---

## Prerequisites

- Node.js 18+
- Jest or Vitest test framework
- TypeScript configured

### Installation

=== "Jest"
    ```bash
    npm install --save-dev jest @jest/globals ts-jest @types/jest
    ```

=== "Vitest"
    ```bash
    npm install --save-dev vitest @vitest/ui
    ```

---

## Basic Test Structure

### Test File Organization

```
tests/
├── setup.ts                 # Test setup
├── unit/
│   ├── client.test.ts      # Client tests
│   ├── conversation.test.ts # Conversation tests
│   └── tools.test.ts       # Tool tests
└── integration/
    └── agentFlows.test.ts  # Integration tests
```

### Jest Configuration

```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts'
  ]
};
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  }
});
```

---

## Complete Test Examples

### Basic Conversation Tests

=== "client.test.ts"
    ```typescript
    import { describe, it, expect, beforeEach, jest } from '@jest/globals';
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    describe('Basic Conversation Tests', () => {
      let client: AgentProtocolClient;

      beforeEach(() => {
        client = new AgentProtocolClient({
          baseUrl: 'http://localhost:3978'
        });
      });

      describe('Message Sending', () => {
        it('should send a simple message', async () => {
          // Mock the response
          const mockResponse = {
            text: 'Hello, world!',
            role: 'assistant'
          };
          
          jest.spyOn(client, 'sendOneOff').mockResolvedValue(mockResponse);
          
          const response = await client.sendOneOff('Hello');
          
          expect(response).toBeDefined();
          expect(response.text).toBe('Hello, world!');
          expect(response.role).toBe('assistant');
        });

        it('should create a conversation', () => {
          const conversation = client.createConversation();
          
          expect(conversation).toBeDefined();
          expect(conversation.threadId).toBeDefined();
        });

        it('should send multiple messages in sequence', async () => {
          const conversation = client.createConversation();
          
          // Mock multiple responses
          const mockSend = jest.spyOn(conversation, 'send')
            .mockResolvedValueOnce({ text: 'Response 1', role: 'assistant' })
            .mockResolvedValueOnce({ text: 'Response 2', role: 'assistant' });
          
          const response1 = await conversation.send('Message 1');
          const response2 = await conversation.send('Message 2');
          
          expect(response1.text).toBe('Response 1');
          expect(response2.text).toBe('Response 2');
          expect(mockSend).toHaveBeenCalledTimes(2);
        });
      });

      describe('Error Handling', () => {
        it('should handle connection errors', async () => {
          const invalidClient = new AgentProtocolClient({
            baseUrl: 'http://invalid:9999'
          });
          
          jest.spyOn(invalidClient, 'sendOneOff').mockRejectedValue(
            new Error('Connection failed')
          );
          
          await expect(invalidClient.sendOneOff('Hello'))
            .rejects.toThrow('Connection failed');
        });

        it('should handle rate limit errors', async () => {
          jest.spyOn(client, 'sendOneOff').mockRejectedValue(
            new Error('Rate limit exceeded')
          );
          
          await expect(client.sendOneOff('Hello'))
            .rejects.toThrow('Rate limit exceeded');
        });

        it('should handle timeout errors', async () => {
          const timeoutClient = new AgentProtocolClient({
            baseUrl: 'http://localhost:3978',
            timeout: 100
          });
          
          jest.spyOn(timeoutClient, 'sendOneOff').mockRejectedValue(
            new Error('Request timeout')
          );
          
          await expect(timeoutClient.sendOneOff('Hello'))
            .rejects.toThrow('Request timeout');
        });
      });
    });

    // Run with: npm test
    ```

### Tool Testing

=== "tools.test.ts"
    ```typescript
    import { describe, it, expect, beforeEach } from '@jest/globals';
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol-client';

    describe('Tool Execution Tests', () => {
      let client: AgentProtocolClient;
      let tools: ToolCollection;

      beforeEach(() => {
        client = new AgentProtocolClient({ baseUrl: 'http://localhost:3978' });
        tools = new ToolCollection();

        // Simple calculator tool
        tools.add({
          name: 'calculate',
          description: 'Perform basic calculations',
          parameters: {
            type: 'object',
            properties: {
              expression: { type: 'string' }
            },
            required: ['expression']
          }
        }, ({ expression }: { expression: string }) => {
          return eval(expression);
        });

        // Weather tool (mocked)
        tools.add({
          name: 'get_weather',
          description: 'Get weather for a location',
          parameters: {
            type: 'object',
            properties: {
              location: { type: 'string' }
            },
            required: ['location']
          }
        }, async ({ location }: { location: string }) => {
          return { location, temperature: 72, condition: 'Sunny' };
        });
      });

      it('should execute a simple tool', async () => {
        const mockResponse = {
          text: 'The answer is 4',
          toolCalls: [
            { name: 'calculate', args: { expression: '2+2' } }
          ]
        };

        jest.spyOn(client, 'sendOneOff').mockResolvedValue(mockResponse);

        const response = await client.sendOneOff('What is 2+2?', tools);

        expect(response.toolCalls).toBeDefined();
        expect(response.toolCalls).toHaveLength(1);
        expect(response.toolCalls![0].name).toBe('calculate');
      });

      it('should execute an async tool', async () => {
        const mockResponse = {
          text: "It's sunny and 72°F",
          toolCalls: [
            { name: 'get_weather', args: { location: 'Seattle' } }
          ]
        };

        jest.spyOn(client, 'sendOneOff').mockResolvedValue(mockResponse);

        const response = await client.sendOneOff(
          "What's the weather in Seattle?",
          tools
        );

        expect(response.toolCalls).toBeDefined();
        expect(response.toolCalls![0].name).toBe('get_weather');
      });

      it('should handle tool errors', async () => {
        tools.add({
          name: 'failing_tool',
          description: 'A tool that fails'
        }, () => {
          throw new Error('Tool execution failed');
        });

        const tool = tools.get('failing_tool');
        expect(() => tool.execute()).toThrow('Tool execution failed');
      });

      it('should handle multiple tool calls', async () => {
        const mockResponse = {
          text: 'Results calculated',
          toolCalls: [
            { name: 'calculate', args: { expression: '10+5' } },
            { name: 'calculate', args: { expression: '20*2' } }
          ]
        };

        jest.spyOn(client, 'sendOneOff').mockResolvedValue(mockResponse);

        const response = await client.sendOneOff(
          'Calculate 10+5 and 20*2',
          tools
        );

        expect(response.toolCalls).toHaveLength(2);
        expect(response.toolCalls!.every(tc => tc.name === 'calculate')).toBe(true);
      });
    });

    describe('Tool Validation Tests', () => {
      let tools: ToolCollection;

      beforeEach(() => {
        tools = new ToolCollection();
      });

      it('should validate tool parameters', () => {
        tools.add({
          name: 'search',
          description: 'Search for information',
          parameters: {
            type: 'object',
            properties: {
              query: { type: 'string', minLength: 1 }
            },
            required: ['query']
          }
        }, ({ query }: { query: string }) => {
          return `Results for: ${query}`;
        });

        const tool = tools.get('search');
        expect(tool).toBeDefined();
        expect(tool.parameters.required).toContain('query');
      });

      it('should reject invalid tool parameters', () => {
        tools.add({
          name: 'typed_tool',
          description: 'Tool with typed parameters',
          parameters: {
            type: 'object',
            properties: {
              count: { type: 'number', minimum: 1 }
            },
            required: ['count']
          }
        }, ({ count }: { count: number }) => {
          return `Count: ${count}`;
        });

        const tool = tools.get('typed_tool');
        expect(tool.parameters.properties.count.minimum).toBe(1);
      });
    });
    ```

---

## Mocking Patterns

### Mocking with Jest

```typescript
import { jest } from '@jest/globals';

// Mock entire module
jest.mock('@microsoft/agents-protocol-client');

// Mock specific method
const mockSend = jest.fn();
jest.spyOn(client, 'sendOneOff').mockImplementation(mockSend);

// Mock resolved value
jest.spyOn(client, 'sendOneOff').mockResolvedValue({
  text: 'Mocked response',
  role: 'assistant'
});

// Mock rejected value
jest.spyOn(client, 'sendOneOff').mockRejectedValue(
  new Error('Mock error')
);
```

### Mocking Streaming Responses

```typescript
it('should handle streaming responses', async () => {
  const conversation = client.createConversation();
  
  async function* mockStream() {
    yield { type: 'text', text: 'Hello ' };
    yield { type: 'text', text: 'world!' };
  }
  
  jest.spyOn(conversation, 'stream').mockReturnValue(mockStream());
  
  const chunks: string[] = [];
  for await (const event of conversation.stream('Test')) {
    if (event.type === 'text') {
      chunks.push(event.text);
    }
  }
  
  expect(chunks.join('')).toBe('Hello world!');
});
```

---

## Running Tests

### Run All Tests

=== "Jest"
    ```bash
    npm test
    ```

=== "Vitest"
    ```bash
    npx vitest
    ```

### Run Specific Test File

=== "Jest"
    ```bash
    npm test -- client.test.ts
    ```

=== "Vitest"
    ```bash
    npx vitest client.test.ts
    ```

### Run With Coverage

=== "Jest"
    ```bash
    npm test -- --coverage
    ```

=== "Vitest"
    ```bash
    npx vitest --coverage
    ```

### Watch Mode

=== "Jest"
    ```bash
    npm test -- --watch
    ```

=== "Vitest"
    ```bash
    npx vitest --watch
    ```

---

## TypeScript-Specific Patterns

### Type Testing

```typescript
import { expectType, expectError } from 'tsd';

// Test type inference
const client = new AgentProtocolClient({ baseUrl: 'http://localhost:3978' });
expectType<AgentProtocolClient>(client);

// Test error on invalid types
expectError(new AgentProtocolClient({ baseUrl: 123 }));
```

### Generic Type Testing

```typescript
it('should handle typed responses', async () => {
  interface CustomResponse {
    data: string;
    metadata: Record<string, any>;
  }
  
  const response = await client.sendOneOff<CustomResponse>('Test');
  
  // TypeScript ensures type safety
  expect(response.data).toBeDefined();
  expect(response.metadata).toBeDefined();
});
```

---

## Best Practices

### ✅ Do

- Use TypeScript strict mode
- Leverage type inference in tests
- Use async/await for async tests
- Mock external dependencies
- Test error cases
- Use descriptive test names

### ❌ Don't

- Use `any` type unnecessarily
- Skip type checking in tests
- Ignore promise rejections
- Share mutable state between tests
- Test implementation details

---

## Debugging Tests

### VS Code Configuration

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Jest Current File",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["${fileBasename}", "--runInBand"],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    }
  ]
}
```

---

## See Also

- [Unit Testing Overview](index.md)
- [Testing Guide](../../guides/testing.md)
- [Integration Testing](../integration-testing/index.md)
- [Mocking Patterns](../integration-testing/mocking.md)
