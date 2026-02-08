# EmojiChatBot Sample

A demonstration chatbot built with the Agent Protocol SDK that showcases three key capabilities:

## Features

### 1. **Tool Calling with Attributes**
The bot has two tools that the LLM can automatically discover and call:

- **`AddEmojiToMessage`**: Adds an emoji reaction to a specific message
  ```csharp
  [Tool("Add an emoji reaction to a specific message...")]
  public async Task<AddEmojiResult> AddEmojiToMessage(
      [Description("The ID of the message to add emoji to")] string messageId,
      [Description("The emoji to add")] string emoji)
  ```

- **`SuggestEmoji`**: Suggests appropriate emojis based on message sentiment
  ```csharp
  [Tool("Suggest appropriate emojis based on the sentiment...")]
  public async Task<EmojiSuggestion> SuggestEmoji(
      [Description("The message text to analyze")] string messageText)
  ```

### 2. **System Event Handling**
The bot handles system events to augment the LLM's understanding:

- **User Joined**: Sends a welcome message when someone joins
  ```csharp
  OnEvent<EventContent>("system.user_joined", HandleUserJoinedAsync);
  ```

- **User Left**: Logs when someone leaves the conversation
  ```csharp
  OnEvent<EventContent>("system.user_left", HandleUserLeftAsync);
  ```

### 3. **Emoji Reaction Handling**
The bot responds to emoji reactions from users:

```csharp
OnEvent<MessageReactionContent>(HandleEmojiReactionAsync);
```

When a user reacts with an emoji, the bot:
- Tracks the reaction in its context
- Responds with a friendly message
- Remembers the last emoji used

## How It Works

### Attribute-Based Tool Discovery
The `[Tool]` attribute marks methods that should be automatically discovered:
- JSON schemas are generated automatically from method signatures
- The LLM can call these tools without manual registration
- Parameters are documented with `[Description]` attributes

### Event Handler Augmentation
Event handlers **augment the LLM** with knowledge it wasn't trained on:
- **Standard events** (text messages, images): LLM understands natively, no handler needed
- **Custom events** (emoji reactions, system events): Handlers teach the LLM what these mean

### Context Management
Each conversation maintains a `ChatContext`:
```csharp
public class ChatContext
{
    public int MessageCount { get; set; }
    public string? LastEmojiUsed { get; set; }
}
```

## Running the Sample

### Prerequisites
- .NET 10.0 SDK or later
- Visual Studio 2025 or VS Code

### Start the Bot

```bash
cd dotnet/samples/agents/EmojiChatBot
dotnet run
```

The bot will start on port **3984** (configured in `agent-config.json`).

### Configuration

The bot reads its port from the centralized `agent-config.json` in the repository root:

```json
{
  "bots": {
    "dotnet-emoji-chat": {
      "name": "EmojiChatBot (.NET)",
      "port": 3984,
      "baseUrl": "http://localhost"
    }
  }
}
```

## Code Structure

```
EmojiChatBot/
├── EmojiBotAgent.cs      # Main agent class with tools and handlers
├── Program.cs            # ASP.NET Core startup and configuration
├── EmojiChatBot.csproj   # Project file
└── README.md             # This file
```

## Key SDK Features Demonstrated

1. **`AgentProtocolApplication<TContext>`**: Base class for building agents
2. **`[Tool]` attribute**: Automatic tool discovery via reflection
3. **`OnEvent<TContent>()`**: Register handlers for system and custom events
4. **`IMessageContext<TContext>`**: Context provided to handlers
5. **`CreateContextAsync()`**: Factory method for custom context creation
6. **Automatic JSON schema generation**: From C# method signatures

## Code Reduction

Compare traditional approach vs. this SDK:

### Traditional (30+ lines per tool)
```csharp
OnToolCall("add_emoji", async (context, toolCall, ct) => {
    var args = JsonSerializer.Deserialize<AddEmojiArgs>(toolCall.Arguments);
    // ... manual parameter extraction
    // ... manual validation
    // ... manual error handling
    return result;
}, new ToolDefinition {
    Name = "add_emoji",
    Description = "...",
    ParametersSchema = new {
        type = "object",
        properties = new {
            messageId = new { type = "string", description = "..." },
            emoji = new { type = "string", description = "..." }
        },
        required = new[] { "messageId", "emoji" }
    }
});
```

### With SDK (7 lines per tool)
```csharp
[Tool("Add an emoji reaction to a specific message...")]
public async Task<AddEmojiResult> AddEmojiToMessage(
    [Description("The ID of the message")] string messageId,
    [Description("The emoji to add")] string emoji)
{
    return new AddEmojiResult { Success = true, MessageId = messageId, Emoji = emoji };
}
```

**77% code reduction per tool** (30 lines → 7 lines)

## Next Steps

- Add more sophisticated emoji suggestions using AI/ML
- Integrate with real messaging platforms (Teams, Slack)
- Add persistent storage for emoji statistics
- Implement emoji analytics and trending emojis
