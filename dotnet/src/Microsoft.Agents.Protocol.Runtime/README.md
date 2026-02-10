# Microsoft.Agents.Common

Shared utilities for Microsoft Agents Protocol Client and Hosting SDKs.

## Overview

This package provides common utilities that are used by both the Client SDK (`Microsoft.Agents.Protocol.Client`) and the Hosting SDK (`Microsoft.Agents.Protocol.Hosting`). It eliminates duplication of tool-related functionality across the SDKs.

## Features

### Tool Schema Generation

Automatic JSON schema generation from .NET method signatures using reflection:

```csharp
using Microsoft.Agents.Common.Tools;

Func<string, int, string> handler = (name, age) => $"{name} is {age}";
var schema = ToolSchemaGenerator.GenerateSchema(handler);

// schema.Type == "object"
// schema.Properties["name"].Type == "string"
// schema.Properties["age"].Type == "integer"
// schema.Required == ["name", "age"]
```

### Tool Execution

Centralized tool execution with JSON argument binding:

```csharp
using Microsoft.Agents.Common.Tools;

Func<string, int, string> handler = (name, age) => $"{name} is {age}";
string json = "{\"name\": \"Alice\", \"age\": 30}";

var result = await ToolExecutor.ExecuteAsync(handler, json);
// result == "Alice is 30"
```

## Installation

```bash
dotnet add package Microsoft.Agents.Common
```

## Dependencies

- `Microsoft.Agents.Abstractions` - Protocol models (auto-generated from TypeSpec)
- `System.Text.Json` - JSON serialization

## Usage

### In Client SDK

```csharp
using Microsoft.Agents.Common.Tools;
using Microsoft.Agents.Protocol.Client;

var tools = new ToolCollection();
tools.Add("greet", (string name) => $"Hello, {name}!");

// Internally uses ToolSchemaGenerator and ToolExecutor
```

### In Hosting SDK

```csharp
using Microsoft.Agents.Common.Tools;
using Microsoft.Agents.Protocol.Hosting;

var builder = new FunctionBuilder();
builder.Add("greet", "Greets a person",
    (string name) => $"Hello, {name}!",
    new FunctionExecutionOptions { TrustLevel = TrustLevel.Trusted });

// Internally uses ToolSchemaGenerator and ToolExecutor
```

## API Reference

### ToolSchemaGenerator

- `GenerateSchema(Delegate handler)` - Generate JSON schema from method signature
- `GenerateSchemaWithDescriptions(Delegate handler, Dictionary<string, string> descriptions)` - Generate schema with custom descriptions

### ToolExecutor

- `ExecuteAsync(Delegate handler, string argumentsJson, CancellationToken)` - Execute tool with JSON arguments
- `ExecuteAsStringAsync(Delegate handler, string argumentsJson, CancellationToken)` - Execute tool and return string result

## Type Mapping

| .NET Type | JSON Schema Type |
|-----------|------------------|
| `string` | `"string"` |
| `int`, `long`, `short`, `byte` | `"integer"` |
| `double`, `float`, `decimal` | `"number"` |
| `bool` | `"boolean"` |
| `T[]`, `List<T>`, `IEnumerable<T>` | `"array"` |
| Other types | `"object"` |

## Error Handling

- `ArgumentNullException` - If handler or argumentsJson is null
- `ArgumentException` - If required parameter is missing or JSON is malformed
- `JsonException` - If JSON deserialization fails
- `TargetInvocationException` - If handler throws (unwrapped to preserve original exception)

## License

MIT - Copyright (c) Microsoft Corporation

## Related Packages

- [Microsoft.Agents.Abstractions](../Microsoft.Agents.Abstractions) - Protocol models
- [Microsoft.Agents.Protocol.Client](../Microsoft.Agents.Protocol.Client) - Client SDK
- [Microsoft.Agents.Protocol.Hosting](../Microsoft.Agents.Protocol.Hosting) - Hosting SDK
