#!/bin/bash

# Script to copy Agent with Function Tools sample for all languages
# and configure them to use Microsoft Foundry

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Copying Function Tools Samples${NC}"
echo -e "${BLUE}================================${NC}\n"

# Source and destination directories
AGENT_FRAMEWORK_DIR="$HOME/repos/agent-framework"
PROJECT_ROOT="/Users/mabolan/AgentProtocol"

# Check if agent-framework repo exists
if [ ! -d "$AGENT_FRAMEWORK_DIR" ]; then
    echo -e "${YELLOW}Error: Agent Framework repo not found at $AGENT_FRAMEWORK_DIR${NC}"
    exit 1
fi

# ============================================
# 1. Copy .NET Sample
# ============================================
echo -e "${GREEN}[1/3] Copying .NET Function Tools Sample...${NC}"

DOTNET_SRC="$AGENT_FRAMEWORK_DIR/dotnet/samples/GettingStarted/Agents/Agent_Step03_UsingFunctionTools"
DOTNET_DEST="$PROJECT_ROOT/dotnet/samples/agents/BasicM365Agent"

mkdir -p "$DOTNET_DEST"

# Copy the files
cp "$DOTNET_SRC/Program.cs" "$DOTNET_DEST/Program.cs"
cp "$DOTNET_SRC/Agent_Step03_UsingFunctionTools.csproj" "$DOTNET_DEST/BasicM365Agent.csproj"

# Modify Program.cs to use Foundry configuration
cat > "$DOTNET_DEST/Program.cs" << 'EOF'
// Copyright (c) Microsoft. All rights reserved.

// This sample demonstrates how to use a ChatClientAgent with function tools.
// It shows both non-streaming and streaming agent interactions using weather-related tools.
// Configured for Microsoft Foundry.

using System.ComponentModel;
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using OpenAI.Chat;

// Load configuration from environment variables (from .env file)
var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT")
    ?? throw new InvalidOperationException("FOUNDRY_ENDPOINT is not set in .env file.");
var deploymentName = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT") ?? "gpt-4o-mini";
var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY");

Console.WriteLine($"Using Foundry Endpoint: {endpoint}");
Console.WriteLine($"Using Model Deployment: {deploymentName}\n");

// Define function tools
[Description("Get the weather for a given location.")]
static string GetWeather([Description("The location to get the weather for.")] string location)
    => $"The weather in {location} is cloudy with a high of 15°C.";

[Description("Get the current UTC time.")]
static string GetTime()
{
    var currentTime = DateTime.UtcNow;
    return $"The current UTC time is {currentTime:yyyy-MM-dd HH:mm:ss}.";
}

// Create the chat client and agent with function tools
// Note: Using API key authentication for Foundry
AIAgent agent = new AzureOpenAIClient(
    new Uri(endpoint),
    string.IsNullOrEmpty(apiKey) ? new AzureCliCredential() : new System.ClientModel.ApiKeyCredential(apiKey))
    .GetChatClient(deploymentName)
    .AsAIAgent(
        instructions: "You are a helpful assistant that can provide weather and time information.",
        tools: [AIFunctionFactory.Create(GetWeather), AIFunctionFactory.Create(GetTime)]);

// Example 1: Non-streaming agent interaction with function tools
Console.WriteLine("=== Example 1: Non-streaming Function Call ===");
Console.WriteLine("User: What is the weather like in Amsterdam?");
var result1 = await agent.RunAsync("What is the weather like in Amsterdam?");
Console.WriteLine($"Agent: {result1}\n");

// Example 2: Streaming agent interaction with function tools
Console.WriteLine("=== Example 2: Streaming Function Call ===");
Console.WriteLine("User: What is the current time?");
Console.Write("Agent: ");
await foreach (var update in agent.RunStreamingAsync("What is the current time?"))
{
    Console.Write(update);
}
Console.WriteLine("\n");

// Example 3: Using multiple tools in one query
Console.WriteLine("=== Example 3: Multiple Function Calls ===");
Console.WriteLine("User: What's the weather in London and what's the current time?");
var result3 = await agent.RunAsync("What's the weather in London and what's the current time?");
Console.WriteLine($"Agent: {result3}\n");

Console.WriteLine("=== Function Tools Sample Complete ===");
EOF

# Modify the .csproj file to reference the correct paths
cat > "$DOTNET_DEST/BasicM365Agent.csproj" << 'EOF'
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFrameworks>net10.0;net8.0</TargetFrameworks>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Azure.AI.OpenAI" />
    <PackageReference Include="Azure.Identity" />
    <PackageReference Include="Microsoft.Extensions.AI.OpenAI" />
    <PackageReference Include="DotNetEnv" Version="3.1.1" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\..\src\Microsoft.Agents.AI.OpenAI\Microsoft.Agents.AI.OpenAI.csproj" />
  </ItemGroup>

</Project>
EOF

# Create a README for the .NET sample
cat > "$DOTNET_DEST/README.md" << 'EOF'
# Basic M365 Agent (.NET)

This sample demonstrates how to create an agent with custom function tools using the Microsoft Agent Framework for .NET.

## Features

- Custom function calling (weather, time)
- Streaming and non-streaming responses
- Microsoft Foundry integration
- Multiple tool usage in single query

## Prerequisites

- .NET 8.0 or .NET 10.0 SDK
- Microsoft Foundry endpoint and API key (configured in root `.env` file)

## Configuration

The sample reads configuration from the `.env` file in the project root:

```bash
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
```

## Running the Sample

```bash
# From this directory
dotnet run

# Or from project root
dotnet run --project dotnet/samples/agents/BasicM365Agent
```

## What This Sample Demonstrates

1. **Function Tool Definition**: How to define custom functions that the agent can call
2. **Tool Integration**: Passing tools to the agent for decision-making
3. **Non-streaming Responses**: Traditional request-response pattern
4. **Streaming Responses**: Real-time token streaming
5. **Multiple Tools**: Agent reasoning about which tools to use
EOF

echo -e "${GREEN}✓ .NET sample copied to: $DOTNET_DEST${NC}\n"

# ============================================
# 2. Copy Python Sample
# ============================================
echo -e "${GREEN}[2/3] Copying Python Function Tools Sample...${NC}"

PYTHON_SRC="$AGENT_FRAMEWORK_DIR/python/samples/getting_started/agents/openai/openai_chat_client_with_function_tools.py"
PYTHON_DEST="$PROJECT_ROOT/python/samples/agents/basic_m365_agent"

mkdir -p "$PYTHON_DEST"

# Create modified Python sample
cat > "$PYTHON_DEST/basic_m365_agent.py" << 'EOF'
# Copyright (c) Microsoft. All rights reserved.

"""
Basic M365 Agent Example

This sample demonstrates function tool integration with Microsoft Foundry,
showing how to create an agent with custom function calling capabilities.
"""

import asyncio
import os
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework import tool
from agent_framework.openai import OpenAIChatClient
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Foundry configuration
FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY")
FOUNDRY_MODEL_DEPLOYMENT = os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o-mini")

if not FOUNDRY_ENDPOINT:
    raise ValueError("FOUNDRY_ENDPOINT not found in .env file")
if not FOUNDRY_API_KEY:
    raise ValueError("FOUNDRY_API_KEY not found in .env file")

print(f"Using Foundry Endpoint: {FOUNDRY_ENDPOINT}")
print(f"Using Model Deployment: {FOUNDRY_MODEL_DEPLOYMENT}\n")


# Define function tools
# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for user approval workflows.
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


@tool(approval_mode="never_require")
def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def example_agent_level_tools() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Example 1: Tools Defined on Agent Level ===\n")

    # Create agent with tools provided at creation time
    # The agent can use these tools for any query during its lifetime
    agent = ChatAgent(
        chat_client=OpenAIChatClient(
            endpoint=FOUNDRY_ENDPOINT,
            api_key=FOUNDRY_API_KEY,
            model_id=FOUNDRY_MODEL_DEPLOYMENT,
        ),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    )

    # Query 1: Weather information
    query1 = "What's the weather like in New York?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # Query 2: Time information
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")

    # Query 3: Multiple tools
    query3 = "What's the weather in London and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3)
    print(f"Agent: {result3}\n")


async def example_run_level_tools() -> None:
    """Example showing tools passed to the run method."""
    print("=== Example 2: Tools Passed to Run Method ===\n")

    # Agent created without tools
    agent = ChatAgent(
        chat_client=OpenAIChatClient(
            endpoint=FOUNDRY_ENDPOINT,
            api_key=FOUNDRY_API_KEY,
            model_id=FOUNDRY_MODEL_DEPLOYMENT,
        ),
        instructions="You are a helpful assistant.",
    )

    # Query with specific tools for this run only
    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query, tools=[get_weather])  # Tool passed to run method
    print(f"Agent: {result}\n")


async def example_mixed_tools() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Example 3: Mixed Tools (Agent + Run Method) ===\n")

    # Agent created with base tools
    agent = ChatAgent(
        chat_client=OpenAIChatClient(
            endpoint=FOUNDRY_ENDPOINT,
            api_key=FOUNDRY_API_KEY,
            model_id=FOUNDRY_MODEL_DEPLOYMENT,
        ),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    )

    # Query using both agent tool and additional run-method tools
    query = "What's the weather in Denver and what's the current UTC time?"
    print(f"User: {query}")
    result = await agent.run(
        query,
        tools=[get_time],  # Additional tools for this specific query
    )
    print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Microsoft Foundry - Basic M365 Agent ===\n")

    await example_agent_level_tools()
    await example_run_level_tools()
    await example_mixed_tools()

    print("=== Function Tools Sample Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
EOF

# Create requirements.txt for Python sample
cat > "$PYTHON_DEST/requirements.txt" << 'EOF'
agent-framework>=0.1.0
python-dotenv>=1.0.0
pydantic>=2.0.0
EOF

# Create README for Python sample
cat > "$PYTHON_DEST/README.md" << 'EOF'
# Basic M365 Agent (Python)

This sample demonstrates how to create an agent with custom function tools using the Microsoft Agent Framework for Python.

## Features

- Custom function calling (weather, time)
- Agent-level and run-level tool configuration
- Microsoft Foundry integration
- Multiple tool usage patterns

## Prerequisites

- Python 3.10 or later
- Microsoft Foundry endpoint and API key (configured in root `.env` file)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install from the parent python package
cd ../../../
pip install -e .
```

## Configuration

The sample reads configuration from the `.env` file in the project root:

```bash
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
```

## Running the Sample

```bash
# From this directory
python basic_m365_agent.py

# Or from project root
python python/samples/agents/basic_m365_agent/basic_m365_agent.py
```

## What This Sample Demonstrates

1. **Function Tool Definition**: Using the `@tool` decorator to define custom functions
2. **Agent-Level Tools**: Tools available for all agent queries
3. **Run-Level Tools**: Tools specific to individual queries
4. **Mixed Tools**: Combining agent-level and run-level tools
5. **Foundry Integration**: Using Microsoft Foundry as the LLM backend
EOF

# Create __init__.py
touch "$PYTHON_DEST/__init__.py"

echo -e "${GREEN}✓ Python sample copied to: $PYTHON_DEST${NC}\n"

# ============================================
# 3. Create TypeScript Protocol Example
# ============================================
echo -e "${GREEN}[3/3] Creating TypeScript Protocol Example...${NC}"

TS_DEST="$PROJECT_ROOT/typescript/samples/agents/basic-m365-agent"

mkdir -p "$TS_DEST"

# Create TypeScript example (protocol-level since no SDK exists yet)
cat > "$TS_DEST/basic-m365-agent.ts" << 'EOF'
/**
 * Basic M365 Agent Example (TypeScript)
 *
 * This sample demonstrates the Agent Protocol messages for function calling.
 * Note: This is a protocol-level example as there is no TypeScript SDK yet.
 * It shows how to construct and handle function tool messages.
 */

import * as dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config({ path: '../../../.env' });

const FOUNDRY_ENDPOINT = process.env.FOUNDRY_ENDPOINT;
const FOUNDRY_API_KEY = process.env.FOUNDRY_API_KEY;
const FOUNDRY_MODEL_DEPLOYMENT = process.env.FOUNDRY_MODEL_DEPLOYMENT || 'gpt-4o-mini';

if (!FOUNDRY_ENDPOINT) {
    throw new Error('FOUNDRY_ENDPOINT not found in .env file');
}
if (!FOUNDRY_API_KEY) {
    throw new Error('FOUNDRY_API_KEY not found in .env file');
}

console.log(`Using Foundry Endpoint: ${FOUNDRY_ENDPOINT}`);
console.log(`Using Model Deployment: ${FOUNDRY_MODEL_DEPLOYMENT}\n`);

/**
 * Example function tools that could be called by the agent
 */
const functionTools = {
    get_weather: (location: string): string => {
        const conditions = ['sunny', 'cloudy', 'rainy', 'stormy'];
        const condition = conditions[Math.floor(Math.random() * conditions.length)];
        const temp = Math.floor(Math.random() * 20) + 10;
        return `The weather in ${location} is ${condition} with a high of ${temp}°C.`;
    },

    get_time: (): string => {
        const currentTime = new Date().toISOString();
        return `The current UTC time is ${currentTime}.`;
    }
};

/**
 * Protocol message types for function calling
 * These match the Agent Protocol specification
 */

interface ToolMessage {
    role: 'tool';
    content: string;
    toolCallId: string;
    toolName: string;
}

interface FunctionCallContent {
    type: 'function_call';
    name: string;
    arguments: string;
    callId: string;
}

interface UserMessage {
    role: 'user';
    content: string;
}

interface AssistantMessage {
    role: 'assistant';
    content: Array<{ type: 'text'; text: string } | FunctionCallContent>;
}

/**
 * Example: Constructing a user message with available tools
 */
function createUserMessageWithTools(query: string) {
    return {
        role: 'user' as const,
        content: query,
        // Tool definitions would be passed to the LLM
        availableTools: [
            {
                type: 'function',
                function: {
                    name: 'get_weather',
                    description: 'Get the weather for a given location.',
                    parameters: {
                        type: 'object',
                        properties: {
                            location: {
                                type: 'string',
                                description: 'The location to get the weather for.'
                            }
                        },
                        required: ['location']
                    }
                }
            },
            {
                type: 'function',
                function: {
                    name: 'get_time',
                    description: 'Get the current UTC time.',
                    parameters: {
                        type: 'object',
                        properties: {}
                    }
                }
            }
        ]
    };
}

/**
 * Example: Handling a function call response from the LLM
 */
function handleFunctionCall(functionCall: FunctionCallContent): ToolMessage {
    console.log(`\n🔧 Agent wants to call function: ${functionCall.name}`);
    console.log(`   Arguments: ${functionCall.arguments}`);

    let result: string;

    if (functionCall.name === 'get_weather') {
        const args = JSON.parse(functionCall.arguments);
        result = functionTools.get_weather(args.location);
    } else if (functionCall.name === 'get_time') {
        result = functionTools.get_time();
    } else {
        result = `Error: Unknown function ${functionCall.name}`;
    }

    console.log(`   Result: ${result}`);

    return {
        role: 'tool',
        content: result,
        toolCallId: functionCall.callId,
        toolName: functionCall.name
    };
}

/**
 * Main example demonstrating the protocol flow
 */
async function main() {
    console.log('=== TypeScript Agent Protocol - Function Tools Example ===\n');
    console.log('Note: This is a protocol-level example showing message structures.');
    console.log('For actual API calls, you would integrate with an HTTP client.\n');

    // Example 1: User query with available tools
    console.log('=== Example 1: User Query with Function Tools ===');
    const userMessage = createUserMessageWithTools("What's the weather in Amsterdam?");
    console.log('\n📤 User Message:');
    console.log(JSON.stringify(userMessage, null, 2));

    // Example 2: Simulated LLM response with function call
    console.log('\n=== Example 2: Agent Function Call Response ===');
    const functionCallMessage: AssistantMessage = {
        role: 'assistant',
        content: [
            {
                type: 'function_call',
                name: 'get_weather',
                arguments: JSON.stringify({ location: 'Amsterdam' }),
                callId: 'call_123abc'
            }
        ]
    };
    console.log('\n📥 Assistant Message (with function call):');
    console.log(JSON.stringify(functionCallMessage, null, 2));

    // Example 3: Execute function and create tool response
    console.log('\n=== Example 3: Tool Result Response ===');
    const functionCall = functionCallMessage.content[0] as FunctionCallContent;
    const toolResponse = handleFunctionCall(functionCall);
    console.log('\n📤 Tool Message:');
    console.log(JSON.stringify(toolResponse, null, 2));

    // Example 4: Multiple function calls
    console.log('\n\n=== Example 4: Multiple Function Calls ===');
    const multiCallMessage: AssistantMessage = {
        role: 'assistant',
        content: [
            {
                type: 'function_call',
                name: 'get_weather',
                arguments: JSON.stringify({ location: 'London' }),
                callId: 'call_456def'
            },
            {
                type: 'function_call',
                name: 'get_time',
                arguments: '{}',
                callId: 'call_789ghi'
            }
        ]
    };

    console.log('\n📥 Assistant Message (multiple function calls):');
    console.log(JSON.stringify(multiCallMessage, null, 2));

    console.log('\n🔧 Executing function calls:');
    for (const content of multiCallMessage.content) {
        if (content.type === 'function_call') {
            handleFunctionCall(content);
        }
    }

    console.log('\n\n=== Protocol Example Complete ===');
    console.log('\n💡 Next Steps:');
    console.log('   - This example shows the message protocol structures');
    console.log('   - To implement actual API calls, use an HTTP client');
    console.log('   - Reference the .NET and Python samples for SDK usage');
    console.log('   - Consider using the protocol messages directly with your HTTP library');
}

main().catch(console.error);
EOF

# Create package.json for TypeScript sample
cat > "$TS_DEST/package.json" << 'EOF'
{
  "name": "basic-m365-agent-typescript",
  "version": "1.0.0",
  "description": "Basic M365 Agent example showing Agent Protocol message structures",
  "main": "basic-m365-agent.ts",
  "scripts": {
    "start": "ts-node basic-m365-agent.ts",
    "build": "tsc basic-m365-agent.ts"
  },
  "keywords": ["agent-protocol", "function-calling", "typescript"],
  "author": "Microsoft",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.0.0"
  }
}
EOF

# Create tsconfig.json
cat > "$TS_DEST/tsconfig.json" << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["*.ts"],
  "exclude": ["node_modules", "dist"]
}
EOF

# Create README for TypeScript sample
cat > "$TS_DEST/README.md" << 'EOF'
# Basic M365 Agent (TypeScript - Protocol Example)

This sample demonstrates the Agent Protocol message structures for function calling in TypeScript.

**Note**: This is a protocol-level example as there is no TypeScript SDK for the Agent Framework yet. It shows how to construct and handle function tool messages according to the Agent Protocol specification.

## Features

- Protocol message structure examples
- Function tool definition format
- Function call handling patterns
- Tool result response construction

## Prerequisites

- Node.js 18+ or later
- TypeScript 5.0+
- Microsoft Foundry endpoint and API key (configured in root `.env` file)

## Installation

```bash
# Install dependencies
npm install

# Or using yarn
yarn install
```

## Configuration

The sample reads configuration from the `.env` file in the project root:

```bash
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o-mini
```

## Running the Sample

```bash
# Using npm
npm start

# Using yarn
yarn start

# Or using ts-node directly
npx ts-node basic-m365-agent.ts
```

## What This Sample Demonstrates

1. **Protocol Message Structures**: Agent Protocol format for function calling
2. **Tool Definitions**: How to define available tools for the agent
3. **Function Call Messages**: Format of function call requests from the LLM
4. **Tool Result Messages**: How to respond with function execution results
5. **Multi-Tool Calling**: Handling multiple function calls in one response

## Implementation Notes

This is a **protocol-level example** that demonstrates message structures. To implement actual API calls:

1. Use an HTTP client (axios, fetch, etc.) to call your Foundry endpoint
2. Send messages in the format shown in this example
3. Parse responses and extract function calls
4. Execute functions and send tool result messages back
5. Continue the conversation loop until completion

For full SDK implementations, see the .NET and Python samples.

## Future TypeScript SDK

When a TypeScript SDK becomes available, you'll be able to use high-level APIs similar to:

```typescript
const agent = new ChatAgent({
    chatClient: new FoundryChatClient({
        endpoint: FOUNDRY_ENDPOINT,
        apiKey: FOUNDRY_API_KEY,
        model: FOUNDRY_MODEL_DEPLOYMENT
    }),
    instructions: "You are a helpful assistant",
    tools: [getWeather, getTime]
});

const result = await agent.run("What's the weather?");
```
EOF

echo -e "${GREEN}✓ TypeScript sample created at: $TS_DEST${NC}\n"

# ============================================
# Summary and Next Steps
# ============================================
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}✅ Sample Copy Complete!${NC}"
echo -e "${BLUE}================================${NC}\n"

echo -e "${GREEN}Samples have been copied and configured for Microsoft Foundry:${NC}\n"
echo -e "  📁 .NET:        $DOTNET_DEST"
echo -e "  📁 Python:      $PYTHON_DEST"
echo -e "  📁 TypeScript:  $TS_DEST"
echo -e ""
echo -e "${YELLOW}Next Steps:${NC}\n"
echo -e "  .NET Sample:"
echo -e "    cd $DOTNET_DEST"
echo -e "    dotnet run"
echo -e ""
echo -e "  Python Sample:"
echo -e "    cd $PYTHON_DEST"
echo -e "    pip install -r requirements.txt"
echo -e "    python basic_m365_agent.py"
echo -e ""
echo -e "  TypeScript Sample:"
echo -e "    cd $TS_DEST"
echo -e "    npm install"
echo -e "    npm start"
echo -e ""
echo -e "${GREEN}All samples are configured to use your Foundry credentials from .env${NC}\n"
