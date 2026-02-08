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
class ActionContent(AIContentBase):
    """
    XML: <action name="button_clicked" text="Refresh" timestamp="...">{value}</action>
    """
    name: str
    text: Optional[str] = None
    timestamp: Optional[datetime] = None
    value: Optional[str] = None

    @property
    def kind(self) -> str:
        return "action"
