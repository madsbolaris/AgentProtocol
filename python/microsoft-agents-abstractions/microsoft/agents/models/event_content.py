# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .ai_content_base import AIContentBase


@dataclass
class EventContent(AIContentBase):
    """
    XML: <event name="..." timestamp="...">{value}</event>
    """
    name: str
    timestamp: Optional[datetime] = None
    value: Optional[str] = None

    @property
    def kind(self) -> str:
        return "event"
