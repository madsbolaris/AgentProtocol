# Microsoft Agents Protocol Hosting

Server SDK for Microsoft Agents Protocol.

This package provides server-side functionality for hosting Agent Protocol endpoints, allowing you to create Agent Protocol-compliant servers.

## Installation

```bash
pip install microsoft-agents-protocol-hosting
```

## Usage

```python
from aiohttp import web
from microsoft.agents.protocol.hosting import add_agent_protocol_routes

# Create your aiohttp application
app = web.Application()

# Add Agent Protocol routes
add_agent_protocol_routes(app, agent=my_agent)

# Run the server
web.run_app(app, port=8000)
```

## Features

- Agent Protocol server implementation
- aiohttp-based
- Full support for Agent Protocol APIs
- Thread management
- Run management
- Message handling
- Streaming support

## Version

0.2.0
