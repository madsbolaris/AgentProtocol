# Client SDK Integrations

Connect your Agent Protocol applications with popular platforms, services, and tools.

## Overview

The Client SDK provides seamless integration with a wide range of external services, including LLM providers, communication channels, vector databases, and third-party APIs. This section covers all available integrations and how to implement them.

---

## Available Integrations

### LLM Providers

Connect to leading language model providers:

- **[OpenAI](llm-providers/openai.md)** - GPT-4, GPT-3.5-turbo, embeddings
- **[Azure OpenAI](llm-providers/azure-openai.md)** - Enterprise-grade Azure deployment
- **[Anthropic](llm-providers/anthropic.md)** - Claude models and API
- **[Google AI](llm-providers/google.md)** - Gemini and PaLM models
- **[Cohere](llm-providers/cohere.md)** - Command and embedding models
- **[Hugging Face](llm-providers/huggingface.md)** - Open-source models

### Communication Channels

Deploy agents across messaging platforms:

- **[Microsoft Teams](channels/teams.md)** - Enterprise collaboration
- **[Slack](channels/slack.md)** - Team communication
- **[Discord](channels/discord.md)** - Community engagement
- **[Telegram](channels/telegram.md)** - Messaging platform
- **[WhatsApp](channels/whatsapp.md)** - Global messaging
- **[Web Chat](channels/webchat.md)** - Website integration

### Vector Stores

Implement semantic search and RAG:

- **[Pinecone](vector-stores/pinecone.md)** - Managed vector database
- **[Weaviate](vector-stores/weaviate.md)** - Open-source vector search
- **[Chroma](vector-stores/chroma.md)** - Embedded vector database
- **[Qdrant](vector-stores/qdrant.md)** - Vector similarity search
- **[Milvus](vector-stores/milvus.md)** - Scalable vector database
- **[FAISS](vector-stores/faiss.md)** - Facebook AI similarity search

### Tools and APIs

Extend agent capabilities with external tools:

- **[Weather APIs](tools/weather-api.md)** - Real-time weather data
- **[Database Tools](tools/database.md)** - SQL and NoSQL databases
- **[Search APIs](tools/search-apis.md)** - Web and enterprise search
- **[Calendar Tools](tools/calendar.md)** - Scheduling and events
- **[Email Services](tools/email.md)** - Email integration
- **[File Storage](tools/file-storage.md)** - Cloud storage services

---

## Quick Start Example

Here's a quick example of integrating with OpenAI and Pinecone:

=== "Python"

    ```python
    from microsoft.agents import AgentProtocolClient
    from openai import AsyncOpenAI
    from pinecone import Pinecone

    # Initialize OpenAI
    openai_client = AsyncOpenAI(api_key="your-api-key")

    # Initialize Pinecone
    pc = Pinecone(api_key="your-pinecone-key")
    index = pc.Index("your-index")

    # Create Agent Protocol client
    agent_client = AgentProtocolClient(base_url="http://localhost:3978")

    # Define a RAG tool
    async def search_knowledge_base(query: str) -> str:
        """Search the knowledge base using Pinecone."""
        # Get embedding from OpenAI
        embedding_response = await openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding

        # Search Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )

        # Format results
        context = "\n".join([
            match.metadata.get('text', '')
            for match in results.matches
        ])
        return context

    # Use with agent
    async def main():
        # Get relevant context
        context = await search_knowledge_base("What is Agent Protocol?")

        # Send to agent with context
        response = await agent_client.send_one_off(
            f"Context: {context}\n\nQuestion: What is Agent Protocol?"
        )
        print(response.text)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-client';
    import { OpenAI } from 'openai';
    import { Pinecone } from '@pinecone-database/pinecone';

    // Initialize OpenAI
    const openai = new OpenAI({ apiKey: 'your-api-key' });

    // Initialize Pinecone
    const pc = new Pinecone({ apiKey: 'your-pinecone-key' });
    const index = pc.Index('your-index');

    // Create Agent Protocol client
    const agentClient = new AgentProtocolClient({
      baseUrl: 'http://localhost:3978'
    });

    // Define a RAG tool
    async function searchKnowledgeBase(query: string): Promise<string> {
      // Get embedding from OpenAI
      const embeddingResponse = await openai.embeddings.create({
        model: 'text-embedding-ada-002',
        input: query
      });
      const queryEmbedding = embeddingResponse.data[0].embedding;

      // Search Pinecone
      const results = await index.query({
        vector: queryEmbedding,
        topK: 5,
        includeMetadata: true
      });

      // Format results
      const context = results.matches
        .map(match => match.metadata?.text || '')
        .join('\n');
      return context;
    }

    // Use with agent
    async function main() {
      // Get relevant context
      const context = await searchKnowledgeBase('What is Agent Protocol?');

      // Send to agent with context
      const response = await agentClient.sendOneOff(
        `Context: ${context}\n\nQuestion: What is Agent Protocol?`
      );
      console.log(response.text);
    }
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Client;
    using OpenAI;
    using Pinecone;

    // Initialize OpenAI
    var openaiClient = new OpenAIClient("your-api-key");

    // Initialize Pinecone
    var pinecone = new PineconeClient("your-pinecone-key");
    var index = pinecone.GetIndex("your-index");

    // Create Agent Protocol client
    var agentClient = new AgentProtocolClient("http://localhost:3978");

    // Define a RAG tool
    async Task<string> SearchKnowledgeBase(string query)
    {
        // Get embedding from OpenAI
        var embeddingResponse = await openaiClient.CreateEmbeddingAsync(
            new EmbeddingRequest
            {
                Model = "text-embedding-ada-002",
                Input = query
            });
        var queryEmbedding = embeddingResponse.Data[0].Embedding;

        // Search Pinecone
        var results = await index.QueryAsync(new QueryRequest
        {
            Vector = queryEmbedding,
            TopK = 5,
            IncludeMetadata = true
        });

        // Format results
        var context = string.Join("\n",
            results.Matches.Select(m => m.Metadata?.GetValueOrDefault("text", "").ToString() ?? ""));
        return context;
    }

    // Use with agent
    async Task Main()
    {
        // Get relevant context
        var context = await SearchKnowledgeBase("What is Agent Protocol?");

        // Send to agent with context
        var response = await agentClient.SendOneOffAsync(
            $"Context: {context}\n\nQuestion: What is Agent Protocol?");
        Console.WriteLine(response.Text);
    }
    ```

---

## Integration Categories

### By Use Case

#### Conversational AI

- [Teams](channels/teams.md), [Slack](channels/slack.md), [Discord](channels/discord.md)
- [OpenAI](llm-providers/openai.md), [Anthropic](llm-providers/anthropic.md)

#### Retrieval-Augmented Generation (RAG)

- [Pinecone](vector-stores/pinecone.md), [Weaviate](vector-stores/weaviate.md), [Chroma](vector-stores/chroma.md)
- [Search APIs](tools/search-apis.md), [Database Tools](tools/database.md)

#### Task Automation

- [Calendar Tools](tools/calendar.md), [Email Services](tools/email.md)
- [File Storage](tools/file-storage.md), [Database Tools](tools/database.md)

#### Enterprise Solutions

- [Azure OpenAI](llm-providers/azure-openai.md), [Teams](channels/teams.md)
- [Microsoft Graph](tools/microsoft-graph.md), [SharePoint](tools/sharepoint.md)

### By Deployment

#### Cloud-Native

- Azure OpenAI, AWS services, GCP services
- Managed vector stores (Pinecone, Weaviate Cloud)

#### On-Premises

- Self-hosted LLMs, Local vector databases
- Enterprise databases, Internal APIs

#### Hybrid

- Azure OpenAI with on-prem data
- Hybrid search solutions

---

## Integration Patterns

### Pattern 1: Direct Integration

Connect directly to external services:

```python
# Direct API calls
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="sk-...")
response = await client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Pattern 2: Tool-Based Integration

Expose integrations as agent tools:

```python
from microsoft.agents import Tool

weather_tool = Tool(
    name="get_weather",
    description="Get current weather for a location",
    function=get_weather_data
)

response = await client.send_with_tools(
    "What's the weather in Seattle?",
    tools=[weather_tool]
)
```

### Pattern 3: Middleware Integration

Use middleware for cross-cutting concerns:

```python
class RateLimitMiddleware:
    async def __call__(self, request, next):
        await self.check_rate_limit(request.user)
        return await next(request)

client.add_middleware(RateLimitMiddleware())
```

---

## Authentication

### API Key Authentication

Most integrations use API key authentication:

=== "Python"

    ```python
    import os
    from openai import AsyncOpenAI

    # Load from environment
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    ```

=== "TypeScript"

    ```typescript
    import { OpenAI } from 'openai';

    // Load from environment
    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    ```

=== "C#"

    ```csharp
    using OpenAI;

    // Load from configuration
    var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
    var client = new OpenAIClient(apiKey);
    ```

### OAuth2 Authentication

For services requiring OAuth2:

```python
from microsoft.identity.web import IdentityWebPython

# Configure OAuth2
identity = IdentityWebPython(
    client_id="your-client-id",
    tenant_id="your-tenant-id"
)

# Get access token
token = await identity.acquire_token_for_client(
    scopes=["https://graph.microsoft.com/.default"]
)
```

---

## Best Practices

### 1. Configuration Management

Store credentials securely:

```python
# Use environment variables
API_KEY = os.environ.get("SERVICE_API_KEY")

# Use secret management services
from azure.keyvault.secrets import SecretClient
secret = await secret_client.get_secret("api-key")
```

### 2. Error Handling

Handle integration failures gracefully:

```python
try:
    response = await external_service.call()
except ServiceUnavailable:
    # Fallback to cached data or alternative service
    response = await get_cached_response()
```

### 3. Rate Limiting

Respect API rate limits:

```python
from aiolimiter import AsyncLimiter

limiter = AsyncLimiter(max_rate=100, time_period=60)

async def rate_limited_call():
    async with limiter:
        return await external_service.call()
```

### 4. Monitoring

Monitor integration health:

```python
import prometheus_client as prom

integration_calls = prom.Counter(
    'integration_calls_total',
    'Total integration calls',
    ['service', 'status']
)

@integration_calls.labels(service='openai', status='success').count_exceptions()
async def call_openai():
    return await openai_client.chat.completions.create(...)
```

---

## Troubleshooting

### Common Issues

**Authentication Errors**

- Verify API keys are correct and not expired
- Check environment variable names
- Ensure proper scopes for OAuth2

**Rate Limiting**

- Implement exponential backoff
- Use caching to reduce API calls
- Consider upgrading service tier

**Network Timeouts**

- Increase timeout values
- Implement retry logic
- Check network connectivity

**Integration Failures**

- Enable debug logging
- Verify service status
- Check API version compatibility

---

## Migration Guide

### From Direct API Calls

If you're currently making direct API calls:

**Before:**

```python
import requests
response = requests.post("https://api.openai.com/v1/chat/completions", ...)
```

**After:**

```python
from openai import AsyncOpenAI
client = AsyncOpenAI()
response = await client.chat.completions.create(...)
```

### Adding Agent Protocol

To add Agent Protocol to existing integrations:

```python
# Wrap existing integration
from microsoft.agents import Tool

existing_function = your_integration.method

tool = Tool(
    name="your_tool",
    description="Description",
    function=existing_function
)

# Use with agent
response = await agent_client.send_with_tools(
    "Use the tool",
    tools=[tool]
)
```

---

## See Also

- [Client SDK Overview](../index.md)
- [Guides](../guides/README.md)
- [API Reference](../api-reference/index.md)
- [Use Cases](../use-cases/index.md)
- [Examples Repository](https://github.com/microsoft/agent-protocol/tree/main/examples/integrations)
