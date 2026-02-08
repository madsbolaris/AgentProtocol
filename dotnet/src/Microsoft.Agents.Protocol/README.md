# Microsoft.Agents.Client

A .NET client library for interacting with Agent Protocol APIs. This library provides strongly-typed models and an intuitive HTTP client for creating agents, running conversations, and managing threads.

## Installation

```bash
dotnet add package Microsoft.Agents.Client
```

## Quick Start

```csharp
using Microsoft.Agents.Client;
using Microsoft.Agents.Client.Models.Agents;
using Microsoft.Agents.Client.Models.Execution;
using Microsoft.Agents.Client.Models.Messages;

// Initialize the client
var client = new AgentProtocolClient("https://api.example.com", "your-api-key");

// Create a simple agent and run
var run = new Run
{
    AgentId = "agent_001",
    Input = new List<ChatMessage>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "Hello! What's the weather like?" }
            }
        }
    }
};

var result = await client.Runs.CreateAsync(run);
Console.WriteLine($"Run status: {result.Status}");
```

## Core Features

### 1. Runs API - Execute Agent Conversations

#### Create and Execute a Run

```csharp
// Create a run with an existing agent
var run = new Run
{
    AgentId = "agent_001",
    ThreadId = "thread_123", // Optional: omit for stateless execution
    Input = new List<ChatMessage>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "What's 2+2?" }
            }
        }
    }
};

var result = await client.Runs.CreateAsync(run);
```

#### Create and Wait for Completion (Blocking)

```csharp
// For ephemeral runs, use CreateAndWait
var waitResult = await client.Runs.CreateAndWaitAsync(new Run
{
    AgentId = "agent_001",
    Input = new List<ChatMessage>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "Translate 'hello' to Spanish" }
            }
        }
    },
    ThreadCleanup = ThreadCleanup.Delete // Clean up thread after completion
});

Console.WriteLine($"Status: {waitResult.Status}");
foreach (var message in waitResult.Output)
{
    foreach (var content in message.Contents)
    {
        if (content is TextContent textContent)
        {
            Console.WriteLine($"Response: {textContent.Text}");
        }
    }
}
```

#### List Runs with Filtering

```csharp
// Get all runs for a specific thread
var runs = await client.Runs.ListAsync(threadId: "thread_123", limit: 50);

// Filter by status
var completedRuns = await client.Runs.ListAsync(
    status: RunStatus.Completed,
    limit: 100
);
```

#### Cancel a Running Execution

```csharp
// Interrupt - stops but preserves state
await client.Runs.CancelAsync("run_456", CancelAction.Interrupt, "User stopped generation");

// Rollback - stops and cleans up completely
await client.Runs.CancelAsync("run_456", CancelAction.Rollback, "Failed run cleanup");
```

#### Handle Tool Calls (HITL - Human-in-the-Loop)

```csharp
// When a run requires tool execution
var run = await client.Runs.GetAsync("run_789");

if (run.Status == RunStatus.RequiresAction)
{
    // Execute tools and submit results
    var toolOutputs = new List<ToolOutput>
    {
        new ToolOutput
        {
            ToolCallId = "call_abc123",
            Output = "File deleted successfully"
        }
    };

    var updatedRun = await client.Runs.SubmitToolOutputsAsync("run_789", toolOutputs);
}
```

#### Handle User Input Requests

```csharp
// When a run needs user input
if (run.Status == RunStatus.InputRequired)
{
    var updatedRun = await client.Runs.SubmitInputAsync("run_789", "Option 1");
}
```

### 2. Threads API - Manage Conversations

#### Create a Thread

```csharp
using Microsoft.Agents.Client.Models.Common;
using Microsoft.Agents.Client.Models.Threads;

var thread = new Thread
{
    Title = "Customer Support Conversation",
    Participants = new List<Participant>
    {
        new Participant
        {
            Id = "user_001",
            Kind = "user",
            Name = "John Doe"
        }
    }
};

var createdThread = await client.Threads.CreateAsync(thread);
```

#### Add Messages to a Thread

```csharp
var message = new ChatMessage
{
    Role = "user",
    Contents = new List<Content>
    {
        new TextContent { Text = "I need help with my order" }
    },
    UserId = "user_001"
};

await client.Threads.AddMessageAsync("thread_123", message);
```

#### Get Thread Messages

```csharp
// Get all messages in a thread
var messages = await client.Threads.GetMessagesAsync("thread_123", limit: 100);

// Get a specific message
var specificMessage = await client.Threads.GetMessageAsync("thread_123", "msg_456");
```

#### Create a Run within a Thread

```csharp
// Multi-turn conversation pattern
var run = new Run
{
    AgentId = "agent_support",
    Input = new List<ChatMessage>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "What's my order status?" }
            }
        }
    }
};

var threadRun = await client.Threads.CreateRunAsync("thread_123", run);
```

#### List Threads

```csharp
// Get active threads
var activeThreads = await client.Threads.ListAsync(
    status: ThreadStatus.Active,
    limit: 50
);

// Get recently updated threads
var recentThreads = await client.Threads.ListAsync(
    updatedSince: DateTime.UtcNow.AddDays(-7)
);
```

#### Update Thread Status

```csharp
// Archive a thread
var thread = await client.Threads.GetAsync("thread_123");
thread.Status = ThreadStatus.Archived;
await client.Threads.UpdateAsync("thread_123", thread);

// Mark thread as read
await client.Threads.MarkAsReadAsync("thread_123");
```

#### Copy a Thread

```csharp
// Create an independent copy of a thread
var copiedThread = await client.Threads.CopyAsync("thread_123", new ThreadCopyRequest
{
    Title = "Copied Thread",
    IncludeMessages = true,
    IncludeParticipants = true
});
```

#### Watch Threads (Agent Subscriptions)

```csharp
// Subscribe an agent to watch a thread
var watch = await client.Threads.WatchThreadAsync("thread_123", "agent_monitor");

// List all watchers
var watchers = await client.Threads.ListWatchersAsync("thread_123");

// Unsubscribe agent
await client.Threads.UnwatchThreadAsync("thread_123", "agent_monitor");
```

### 3. Agents API - Inspect and Discover Agents

#### Get Agent Card

```csharp
// Retrieve agent capabilities and metadata
var agentCard = await client.Agents.GetCardAsync("agent_001");

Console.WriteLine($"Agent: {agentCard.Name}");
Console.WriteLine($"Supports vision: {agentCard.Capabilities?.Vision}");
Console.WriteLine($"Max tokens: {agentCard.Capabilities?.MaxTokens}");
```

#### Inspect Agent Before Running

```csharp
// Validate agent configuration without persisting
var agent = new PromptAgent
{
    Model = "gpt-4o",
    Instructions = "You are a helpful assistant",
    Temperature = 0.7,
    Tools = new List<AITool>
    {
        new AITool
        {
            Name = "get_weather",
            Description = "Get current weather for a location",
            Parameters = new JSONSchema
            {
                SchemaType = "object",
                Properties = new Dictionary<string, JSONSchema>
                {
                    ["location"] = new JSONSchema
                    {
                        SchemaType = "string",
                        Description = "City name"
                    }
                },
                Required = new List<string> { "location" }
            }
        }
    }
};

var inspectionResult = await client.Agents.InspectAsync(agent);
Console.WriteLine($"Vision supported: {inspectionResult.Capabilities?.Vision}");
Console.WriteLine($"Tools supported: {inspectionResult.Capabilities?.Tools}");
```

## Advanced Usage

### Using Inline Agent Definitions

```csharp
// Run with inline agent configuration (no pre-registered agent needed)
var run = new Run
{
    AgentId = "ephemeral", // Can use any ID for inline agents
    Agent = new PromptAgent
    {
        Model = "gpt-4o",
        Instructions = "You are a math tutor",
        Temperature = 0.3
    },
    Input = new List<ChatMessage>
    {
        new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "Explain calculus" }
            }
        }
    },
    ThreadCleanup = ThreadCleanup.Delete // Ephemeral execution
};

var result = await client.Runs.CreateAndWaitAsync(run);
```

### Working with Images

```csharp
var message = new ChatMessage
{
    Role = "user",
    Contents = new List<Content>
    {
        new TextContent { Text = "What's in this image?" },
        new ImageContent
        {
            Url = "https://example.com/image.jpg",
            Detail = "high"
        }
    }
};

var run = new Run
{
    AgentId = "agent_vision",
    Input = new List<ChatMessage> { message }
};

var result = await client.Runs.CreateAsync(run);
```

### Tool Execution with Approval

```csharp
// Define a tool that requires user approval
var agent = new PromptAgent
{
    Model = "gpt-4o",
    Instructions = "You help manage files",
    Tools = new List<AITool>
    {
        new AITool
        {
            Name = "delete_file",
            Description = "Delete a file from the system",
            RequiresApproval = true, // Human-in-the-loop required
            Parameters = new JSONSchema
            {
                SchemaType = "object",
                Properties = new Dictionary<string, JSONSchema>
                {
                    ["path"] = new JSONSchema
                    {
                        SchemaType = "string",
                        Description = "File path to delete"
                    }
                },
                Required = new List<string> { "path" }
            }
        }
    }
};
```

### Custom HTTP Client Configuration

```csharp
using System.Net.Http;

// Use a custom HTTP client with specific configuration
var httpClient = new HttpClient
{
    Timeout = TimeSpan.FromMinutes(5)
};

var options = new AgentProtocolClientOptions
{
    BaseUrl = new Uri("https://api.example.com"),
    ApiKey = "your-api-key",
    HttpClient = httpClient,
    MaxRetries = 5
};

var client = new AgentProtocolClient(options);
```

### Error Handling

```csharp
try
{
    var run = await client.Runs.CreateAsync(newRun);
}
catch (HttpRequestException ex)
{
    Console.WriteLine($"HTTP error: {ex.Message}");
}
catch (Exception ex)
{
    Console.WriteLine($"Error: {ex.Message}");
}

// Check run status for errors
var run = await client.Runs.GetAsync("run_123");
if (run.Status == RunStatus.Failed && run.Error != null)
{
    Console.WriteLine($"Run failed: {run.Error.Code} - {run.Error.Message}");
}
```

## Model Reference

### Key Models

- **Run**: Represents an agent execution instance
  - `RunId`: Unique identifier
  - `AgentId`: Agent performing the execution
  - `ThreadId`: Optional conversation thread
  - `Status`: Current lifecycle state (queued, in_progress, completed, etc.)
  - `Input`: Messages that started the run
  - `Output`: Messages generated during execution
  - `Usage`: Token consumption statistics

- **Thread**: Represents a conversation
  - `ThreadId`: Unique identifier
  - `Title`: Thread title/subject
  - `Participants`: Users and agents in the conversation
  - `Status`: Thread state (active, archived, closed)
  - `Messages`: Conversation history (accessed via ThreadsClient)

- **ChatMessage**: Represents a message in a conversation
  - `MessageId`: Unique identifier
  - `Role`: Message role (user, assistant, tool, channel, system)
  - `Contents`: List of content items (text, images, tool calls, etc.)
  - `UserId`: User who sent the message (for role=user)
  - `AgentId`: Agent that generated the message (for role=assistant)

- **Content Types**:
  - `TextContent`: Plain text or markdown
  - `ImageContent`: Image URL or data
  - `FunctionCallContent`: AI-generated tool call
  - `FunctionResultContent`: Tool execution result

- **AgentDefinition**: Agent configuration
  - `PromptAgent`: LLM-based agent with instructions and tools
  - `Model`: Model identifier (e.g., "gpt-4o")
  - `Instructions`: System instructions
  - `Tools`: Available capabilities

## Status Enums

### RunStatus

- `Queued`: Run is waiting to start
- `InProgress`: Run is executing
- `RequiresAction`: Tool execution needed
- `InputRequired`: Human input needed
- `AuthRequired`: Authentication needed
- `Cancelling`: User requested cancellation
- `Cancelled`: Run was cancelled
- `Failed`: Run encountered an error
- `Completed`: Run finished successfully
- `Incomplete`: Run stopped before completion
- `Timeout`: Run exceeded time limit

### ThreadStatus

- `Active`: Thread is active
- `Archived`: Thread is archived
- `Closed`: Thread is closed
- `Deleted`: Thread is deleted

## Contributing

Contributions are welcome! Please open issues or submit pull requests on the GitHub repository.

## License

This project is licensed under the MIT License.
