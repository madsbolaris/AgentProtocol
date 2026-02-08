# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Microsoft Agents Protocol

This package provides:
1. Server: Add Agent Protocol routes to your M365 Agents SDK application
2. Client: Call Agent Protocol APIs from Python

Server Usage:
    from microsoft.agents.protocol import add_agent_protocol_routes

    app = Application()
    add_agent_protocol_routes(app, agent_application)

Client Usage:
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    client = AgentProtocolClient(AgentProtocolClientOptions(
        base_url="https://agents.example.com/v1",
        api_key="your-api-key"
    ))

    async with client:
        result = await client.runs.create({...})
"""

from .server import add_agent_protocol_routes
from .client import (
    AgentProtocolClient,
    AgentProtocolClientOptions,
)

__all__ = [
    # Server
    "add_agent_protocol_routes",
    # Client
    "AgentProtocolClient",
    "AgentProtocolClientOptions",
]
__version__ = "0.1.0"
