# @microsoft/agents-common

Shared utilities for Microsoft Agents Protocol Client and Hosting SDKs.

## Overview

This package provides common utilities that are used by both the Client SDK and the Hosting SDK (`@microsoft/agents-hosting`). It eliminates duplication of tool-related functionality across the SDKs.

## Features

### Tool Schema Generation

Utilities for creating and validating JSON schemas:

```typescript
import { ToolSchemaGenerator } from '@microsoft/agents-common';

// Create object schema
const schema = ToolSchemaGenerator.createObjectSchema({
  name: { type: 'string', description: 'Person name' },
  age: { type: 'number', description: 'Person age' }
}, ['name', 'age']);

// Create string schema with constraints
const emailSchema = ToolSchemaGenerator.createStringSchema(
  'User email',
  {
    pattern: '^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$',
    maxLength: 255
  }
);

// Validate schema
ToolSchemaGenerator.validateSchema(schema); // Throws if invalid
```

### Tool Execution

Centralized tool execution with validation:

```typescript
import { ToolExecutor } from '@microsoft/agents-common';

const handler = ({ a, b }: { a: number; b: number }) => {
  return (a + b).toString();
};

const schema = {
  type: 'object',
  properties: {
    a: { type: 'number' },
    b: { type: 'number' }
  },
  required: ['a', 'b']
};

const result = await ToolExecutor.execute(
  handler,
  schema,
  '{"a": 5, "b": 3}'
);
// result === "8"
```

## Installation

```bash
npm install @microsoft/agents-common
```

## API Reference

### ToolSchemaGenerator

Static utility class for creating and validating JSON schemas:

- `createObjectSchema(properties, required?)` - Create object schema
- `createStringSchema(description, options?)` - Create string schema
- `createNumberSchema(description, options?)` - Create number schema
- `createBooleanSchema(description)` - Create boolean schema
- `createArraySchema(description, items, options?)` - Create array schema
- `validateSchema(schema)` - Validate a JSON schema
- `mergeSchemas(base, extension)` - Merge two schemas

### ToolExecutor

Static utility class for executing tools with validation:

- `execute<TParams>(handler, schema, argumentsJson)` - Execute with validation
- `executeUnsafe<TParams>(handler, argumentsJson)` - Execute without validation
- `validateArguments(args, schema)` - Validate arguments against schema

## Usage Examples

### Creating Complex Schemas

```typescript
import { ToolSchemaGenerator } from '@microsoft/agents-common';

// Array of strings
const tagsSchema = ToolSchemaGenerator.createArraySchema(
  'List of tags',
  { type: 'string' },
  { minItems: 1, maxItems: 10 }
);

// Number with range
const ageSchema = ToolSchemaGenerator.createNumberSchema(
  'Age in years',
  { minimum: 0, maximum: 120, type: 'integer' }
);

// String with pattern
const phoneSchema = ToolSchemaGenerator.createStringSchema(
  'Phone number',
  { pattern: '^\\+?[1-9]\\d{1,14}$' }
);
```

### Tool Execution with Validation

```typescript
import { ToolExecutor } from '@microsoft/agents-common';

const handler = async (params: { query: string; limit: number }) => {
  const results = await searchDatabase(params.query, params.limit);
  return JSON.stringify(results);
};

const schema = {
  type: 'object',
  properties: {
    query: { type: 'string', minLength: 1, maxLength: 100 },
    limit: { type: 'number', minimum: 1, maximum: 100 }
  },
  required: ['query']
};

try {
  const result = await ToolExecutor.execute(
    handler,
    schema,
    '{"query": "typescript", "limit": 10}'
  );
  console.log('Results:', result);
} catch (error) {
  console.error('Validation or execution error:', error.message);
}
```

## Error Handling

Both `ToolSchemaGenerator` and `ToolExecutor` throw descriptive errors:

- **JSON Parse Errors**: "Invalid JSON arguments: ..."
- **Type Errors**: "Expected object, got string"
- **Required Field Errors**: "Missing required parameter: name"
- **Validation Errors**: "Value 150 is greater than maximum 120"
- **Pattern Errors**: "String does not match pattern: ..."

## TypeScript Support

Full TypeScript support with generics:

```typescript
interface SearchParams {
  query: string;
  limit?: number;
}

const handler = (params: SearchParams) => {
  return `Searching for: ${params.query}`;
};

// Type-safe execution
const result = await ToolExecutor.execute<SearchParams>(
  handler,
  schema,
  argumentsJson
);
```

## License

MIT - Copyright (c) Microsoft Corporation

## Related Packages

- [@microsoft/agents](../agents) - Protocol models and abstractions
- [@microsoft/agents-hosting](../agents-hosting) - Hosting SDK for building agents
