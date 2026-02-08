# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from enum import Enum
from typing import Literal


class ThreadStatus(str, Enum):
    """
    Thread Status Enum
RATIONALE: Type-safe status values for thread lifecycle
ALIGNED WITH: Messaging app conversation states
- active: Thread is ongoing (like WhatsApp/Teams active chat)
- closed: Thread is completed but archived (like closed ticket)
- archived: Thread is hidden from active view (like archived email)
    """
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


ThreadStatusType = Literal["active", "closed", "archived"]
