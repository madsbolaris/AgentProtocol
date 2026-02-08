# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from enum import Enum
from typing import Literal


class ChatRole(str, Enum):
    """Message role types."""
    SYSTEM = "system"
    DEVELOPER = "developer"
    AGENT = "agent"
    USER = "user"
    TOOL = "tool"
    CHANNEL = "channel"


ChatRoleType = Literal["system", "developer", "agent", "user", "tool", "channel"]
