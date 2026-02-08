# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .j_s_o_n_schema import JSONSchema
from .connection import Connection
from .scopes import Scopes
from .tool_lifecycle_hooks import ToolLifecycleHooks


@dataclass
class AITool:
    # Tool name (unique identifier).
BASE: MAF AITool.Name (virtual, defaults to GetType().Name)

EXAMPLES: "search_memory", "send_email", "get_calendar", "web_search"
    name: str
    # Tool description for LLM.
BASE: MAF AITool.Description (virtual, defaults to empty string)

IMPORTANT: This is shown to the LLM to decide when to call the tool

GUIDANCE: Be specific about:
- What the tool does
- When to use it
- What parameters it expects

EXAMPLE: "Search the agent's long-term memory for relevant information
from previous conversations. Use this when the user asks about past
interactions or stored preferences."
    description: str
    # Tool parameters (JSON Schema).
FROM: Azure Agent API (FunctionTool.parameters)

RATIONALE: JSON Schema is universal standard for describing parameters
- Used by OpenAI, Anthropic, Azure, etc.
- Enables validation and IDE autocomplete

MESSAGING APP PATTERN:
Like command syntax: /command <required> [optional]
    parameters: Optional[JSONSchema] = None
    # Strict schema validation (OpenAI-specific).
FROM: OpenAI structured outputs

When true, enforces exact schema adherence (no additional properties)
    strict: Optional[bool] = None
    # Execution endpoint for remote tools.

@usage

Rationale:
- Local tools: endpoint is omitted (executed in-process)
- Remote tools: endpoint specifies URL (like MCP server, webhooks, APIs)
- No need for separate MCPTool type - just a tool with an endpoint

EXAMPLES:
- "https://mcp-server.example.com/tools/search" (MCP)
- "https://api.example.com/webhooks/action" (Webhook)
- null (local execution)

    endpoint: Optional[str] = None
    # Authentication for remote endpoint.
FROM: MCP pattern + A2A Protocol
ALIGNED WITH: Agent Schema Tool.connection

RATIONALE: Remote tools need authentication
    connection: Optional[Connection] = None
    # OAuth2 scopes required for this tool.

@usage

Rationale:
- Fine-grained permissions per tool (vs agent-wide scopes)
- Runtime can validate if agent has required scopes before tool execution
- Enables dynamic consent flows (request scopes only when tool is used)
- Follows OpenAPI 3.0 OAuth2 security scheme format

EXAMPLES:
- { "https://graph.microsoft.com/Calendars.ReadWrite": "Read and write calendar events" }
- { "https://graph.microsoft.com/Mail.Send": "Send mail as the signed-in user" }
- { "read:pets": "Read pet information", "write:pets": "Modify pet information" }

    scopes: Optional[Scopes] = None
    # Lifecycle hooks for this tool.

@usage

Rationale:
- Some tools need lifecycle hooks (before_execute, after_execute, on_error)
- Enables guardrails, memory persistence, audit logging
- Generic pattern vs separate GuardrailTool/MemoryTool types

EXAMPLES:
- Guardrails: before_execute validates parameters, after_execute validates output
- Memory: after_execute persists result to journal
- Audit: before_execute logs invocation

    lifecycle_hooks: Optional[ToolLifecycleHooks] = None
    # Requires user approval before execution (HITL).
FROM: AG-UI pattern

RATIONALE: Sensitive operations need human-in-the-loop approval

M365: Critical for operations like:
- Sending emails
- Deleting files
- Making purchases
- Modifying permissions
    requires_approval: Optional[bool] = None
    # Additional properties.
BASE: MAF AITool.AdditionalProperties (IReadOnlyDictionary<string, object?>)

FLEXIBLE: Store tool-specific metadata

EXAMPLES:
- { "category": "productivity", "icon": "calendar" }
- { "rateLimit": 10, "rateLimitPeriod": "1m" }
- { "journalThreadId": "thread-123" } (for recall tool)
    metadata: Optional[Dict[str, Any]] = None
