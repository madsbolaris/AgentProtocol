# Agents

An **agent** is an AI-powered entity that processes messages and generates responses. Agents are the core actors in the Agent Protocol.

## What is an Agent?

An agent receives input messages, processes them (often using AI models), and produces output messages. Agents can:
- Answer questions
- Execute tools/functions
- Generate content
- Make decisions
- Coordinate with other agents

## Agent Types

### Prompt Agent
Uses an LLM with instructions:
```
Agent {
  model: "gpt-4"
  instructions: "You are a helpful assistant..."
  tools: [calculator, search, email]
}
```

**Use when:** Standard AI assistant behavior

### Code Agent
Custom logic with optional LLM:
```
Agent {
  code: custom_logic()
  llm: optional
}
```

**Use when:** Deterministic behavior, complex logic, integrations

### Remote Agent
Agent hosted elsewhere:
```
Agent {
  url: "https://api.example.com/agent"
}
```

**Use when:** Third-party agents, microservices architecture

## Agent Properties

- **ID** - Unique identifier
- **Name** - Human-readable name
- **Description** - What the agent does
- **Instructions** - How to behave
- **Model** - Which LLM to use (if applicable)
- **Tools** - Available functions
- **Configuration** - Settings and options

## Agent Lifecycle

```
Define agent → Register → Execute runs → Update → Retire
```

### States
- **Enabled** - Active and available
- **Disabled** - Temporarily inactive
- **Deleted** - Permanently removed

## How Agents Work

### 1. Receive Context
Agent gets:
- Thread history
- Current message(s)
- Available tools
- Instructions

### 2. Process
Agent:
- Analyzes input
- Decides on response
- Calls tools if needed
- Generates output

### 3. Return Result
Agent produces:
- Response messages
- Tool calls
- Status updates
- Metadata

## Agent Capabilities

### Tool Usage
Agents can call functions:
```
User: "What's the weather in Seattle?"
Agent: [calls get_weather("Seattle")]
Tool: {"temp": 72, "condition": "sunny"}
Agent: "It's 72°F and sunny in Seattle"
```

### Multi-turn Conversations
Agents maintain context:
```
User: "My name is Alice"
Agent: "Nice to meet you, Alice!"
User: "What's my name?"
Agent: "Your name is Alice"
```

### Multimodal Understanding
Agents process various content:
```
User: [image] "What's in this picture?"
Agent: "I see a cat sitting on a couch"
```

## Agent Configuration

### Model Options
- **Temperature** - Creativity level (0-2)
- **Max tokens** - Response length
- **Top-p** - Nucleus sampling
- **Frequency penalty** - Reduce repetition

### Tool Configuration
- **Tool choice** - Auto, required, specific, none
- **Parallel tools** - Call multiple at once
- **Tool timeout** - Execution limits

### Instructions
- **System prompt** - Core behavior
- **Guardrails** - What not to do
- **Examples** - Few-shot learning
- **Constraints** - Output format, length

## Agent Patterns

### Single Agent
One agent handles entire conversation:
```
User → Agent → Response
```

### Multi-Agent Orchestration
Multiple agents collaborate:
```
User → Coordinator Agent
         ├─ Research Agent
         ├─ Analysis Agent
         └─ Response Agent → Response
```

### Agent Handoff
Transfer between agents:
```
User → Support Agent → Technical Agent → Resolution
```

## Related Concepts

- **[Runs](runs.md)** - How agents execute
- **[Tools](tools.md)** - Agent capabilities
- **[Threads](threads.md)** - Conversation context
- **[Events](events.md)** - Agent lifecycle notifications

## Best Practices

✅ **Do:**
- Write clear, specific instructions
- Test agent behavior thoroughly
- Provide relevant tools
- Set appropriate model parameters
- Handle errors gracefully

❌ **Don't:**
- Make instructions too vague
- Give agents too many tools
- Ignore agent limitations
- Skip error handling
- Forget to version instructions

## Agent Events

Agents emit lifecycle events:
- **agent_created** - New agent defined
- **agent_updated** - Configuration changed
- **agent_enabled** - Agent activated
- **agent_disabled** - Agent deactivated
- **agent_deleted** - Agent removed

## Next Steps

- Learn about [Tools](tools.md) to extend agent capabilities
- Understand [Runs](runs.md) to execute agents
- Explore the [Hosting SDK](../products/hosting-sdk/) to build agents
