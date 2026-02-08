# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .connection import Connection


@dataclass
class LifecycleHook:
    """
    Lifecycle Hook
ADDITION: Not in any framework (generic pattern)
REPRESENTS: Executable hook in tool lifecycle
PATTERN: Same as AITool - callable function with parameters
    """
    # Hook name (for debugging/logging).
    name: str
    # Hook implementation endpoint.
- Local hooks: omitted (executed in-process)
- Remote hooks: URL to hook implementation

EXAMPLES:
- null: In-process guardrail function
- "https://guardrails.example.com/validate": Remote guardrail service
    endpoint: Optional[str] = None
    # Authentication for remote hook.
    connection: Optional[Connection] = None
    # Hook-specific configuration.
FLEXIBLE: Each hook can have its own config

EXAMPLES:
- { "maxTokens": 1000 } for output validator
- { "journalThreadId": "thread-123" } for memory persistence
- { "policyId": "policy-456" } for guardrail
    config: Optional[Dict[str, Any]] = None
