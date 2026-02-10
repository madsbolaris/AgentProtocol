# Hosting SDK Quickstart

Get your first agent running in 5 minutes.

## Overview

The Hosting SDK lets you build and run AI agents that handle conversations, execute tools, and integrate with various LLM providers.

---

## Installation

=== "TypeScript"
    ```bash
    npm install @microsoft/agents-hosting
    ```

=== "Python"
    ```bash
    pip install microsoft-agents-hosting
    ```

=== ".NET"
    ```bash
    dotnet add package Microsoft.Agents.Hosting
    ```

---

## Your First Agent (5 lines)

=== "TypeScript"
    ```typescript
    import { AgentHostBuilder } from '@microsoft/agents-hosting';

    const agentHost = new AgentHostBuilder()
        .addDefaultAgent(agent => agent
            .useLLM('gpt-4', 'You are a helpful assistant.')
        )
        .build();

    agentHost.start(3000);
    ```

=== "Python"
    ```python
    from microsoft.agents.hosting import AgentHostBuilder

    agent_host = AgentHostBuilder() \
        .add_default_agent(lambda agent: agent
            .use_llm('gpt-4', 'You are a helpful assistant.')
        ) \
        .build()

    agent_host.start(3000)
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Hosting;

    var agentHost = new AgentHostBuilder()
        .AddDefaultAgent(agent => agent
            .UseLLM("gpt-4", "You are a helpful assistant.")
        )
        .Build();

    await agentHost.StartAsync(3000);
    ```

---

## Test Your Agent

```bash
curl http://localhost:3000/v1/threads/new \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

---

## Add Tools

Give your agent capabilities by adding tools:

=== "TypeScript"
    ```typescript
    .addDefaultAgent(agent => agent
        .useLLM('gpt-4', 'You are a helpful assistant.')
        .addFunctions(f => f
            .add('get_time@v1', 'Gets current time',
                () => new Date().toISOString())
        )
    )
    ```

=== "Python"
    ```python
    .add_default_agent(lambda agent: agent
        .use_llm('gpt-4', 'You are a helpful assistant.')
        .add_functions(lambda f: f
            .add('get_time@v1', 'Gets current time',
                lambda: datetime.now().isoformat())
        )
    )
    ```

=== "C#"
    ```csharp
    .AddDefaultAgent(agent => agent
        .UseLLM("gpt-4", "You are a helpful assistant.")
        .AddFunctions(f => f
            .Add("get_time@v1", "Gets current time",
                () => DateTime.UtcNow.ToString("o"))
        )
    )
    ```

---

## Next Steps

1. [Complete Getting Started Guide](getting-started.md) - Full walkthrough
2. [Core Concepts](concepts/README.md) - Understand the architecture  
3. [Add Tools](learn/how-to/add-tools.md) - Give your agent capabilities
4. [Deploy to Production](production/index.md) - Production best practices

---

## Need Help?

- [Troubleshooting](troubleshooting/README.md)
- [API Reference](api-reference/README.md)
- [GitHub Discussions](https://github.com/microsoft/AgentProtocol/discussions)
