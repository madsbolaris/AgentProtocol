# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from enum import Enum
from typing import Literal


class RunStatus(str, Enum):
    """
    Run Status Enum
FROM: OpenAI Agents SDK (8 states) + A2A Protocol (interruption states) + LangChain Agent Protocol
EXPANDED from Azure Agent API (5 states)
    """
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    INPUT_REQUIRED = "input_required"
    AUTH_REQUIRED = "auth_required"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    TIMEOUT = "timeout"


RunStatusType = Literal["queued", "in_progress", "requires_action", "input_required", "auth_required", "cancelling", "cancelled", "failed", "completed", "incomplete", "timeout"]
