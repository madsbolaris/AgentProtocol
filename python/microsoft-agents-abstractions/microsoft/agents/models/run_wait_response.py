# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .run_status import RunStatus
from .chat_message import ChatMessage
from .completion_usage import CompletionUsage
from .run_error import RunError


@dataclass
class RunWaitResponse:
    # Unique identifier for the completed run.
    run_id: str
    # Thread ID if run was stateful (null for ephemeral runs).
OPTIONAL: Omitted when threadCleanup=delete
    thread_id: Optional[str] = None
    # Final run status (completed, failed, cancelled, timeout, incomplete).
    status: RunStatus
    # Messages generated during the run.
    output: List[ChatMessage] = field(default_factory=list)
    # Token usage statistics.
    usage: Optional[CompletionUsage] = None
    # Error details if run failed or completed incompletely.
    error: Optional[RunError] = None
    # Timestamp when run was created.
    created_at: datetime
    # Timestamp when run finished.
    completed_at: Optional[datetime] = None
