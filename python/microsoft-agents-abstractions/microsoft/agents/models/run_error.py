# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class RunError:
    """
    Run Error
FROM: Azure Agent API (IncompleteDetails) - generalized
GENERALIZED: Standard error model with code + message pattern
Like HTTP status codes, gRPC status codes, or messaging app error codes
    """
    # Machine-readable error code.
EXAMPLES:
- "max_turns_exceeded": Run hit max_turns limit
- "tool_execution_failed": Tool execution error
- "rate_limit_exceeded": API rate limit hit
- "context_length_exceeded": Token limit exceeded
- "auth_required": Authentication needed
- "user_cancelled": User cancelled the run
    code: str
    # Human-readable error message.
    message: str
    # Optional additional error details.
FLEXIBLE: Can include stack traces, request IDs, etc.
    details: Optional[Dict[str, Any]] = None
