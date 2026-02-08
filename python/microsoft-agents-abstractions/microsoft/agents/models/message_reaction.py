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
class MessageReaction:
    """
    Message Reaction (Individual Reaction)
    """
    type: str
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
