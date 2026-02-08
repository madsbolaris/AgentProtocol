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
class ThreadWatch:
    """
    Thread Watch - Agent Participation Tracking
@usage
Use Cases:
- Support agents: Watch support threads for user messages
- Monitoring agents: Watch threads for specific content types
- Multi-agent: Multiple agents watching same thread with different conditions
    """
    # Unique watch identifier.
GENERATED: Server-generated GUID
    watch_id: str
    # Thread being watched.
REQUIRED: Must be valid threadId
    thread_id: str
    # Agent watching the thread.
REQUIRED: Must be valid agentId with autoResponse configuration

VALIDATION:
- Agent must exist
- Agent must have AutoResponseConfig defined
- AutoResponseConfig.runCondition determines when agent participates
    agent_id: str
    # Whether watch is currently active.
DEFAULT: true

RATIONALE: Allows temporary disable without deletion
- false: Watch exists but agent doesn't evaluate for participation
- true: Agent actively watching and evaluating conditions
    active: Optional[bool] = None
    # Timestamp when watch was created.
    created_at: datetime
    # Timestamp of last activation (last time agent created run for this thread).
UPDATED: By server after each automatic run creation
    last_activated_at: Optional[datetime] = None
    # Number of runs created by this watch.
INCREMENTED: Each time agent automatically creates run

RATIONALE: Analytics and monitoring
    activation_count: Optional[int] = None
    # Custom metadata for watch.
FLEXIBLE: Client can store correlation IDs, user info, etc.
    metadata: Optional[Dict[str, Any]] = None
