# Microsoft Agents Protocol Client

HTTP client for Microsoft Agents Protocol APIs.

This package provides a Python client for interacting with Agent Protocol servers, allowing you to create agents, manage threads, run conversations, and handle streaming responses.

## Installation

```bash
pip install microsoft-agents-protocol-client
```

## Usage

```python
from microsoft.agents.protocol.client import AgentProtocolClient, ClientOptions

# Create a client
options = ClientOptions(base_url="http://localhost:8000")
client = AgentProtocolClient(options)

# Create a thread
thread = await client.threads.create()

# Send a message
message = await client.threads.send_message(
    thread_id=thread.id,
    content="Hello, agent!"
)

# Run the conversation
run = await client.threads.create_run(thread_id=thread.id)
```

## Features

- Full support for Agent Protocol APIs
- Streaming support for real-time responses
- Thread management
- Run management
- Message handling
- Async/await support

## Version

0.2.0
