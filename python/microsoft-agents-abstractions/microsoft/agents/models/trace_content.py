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
class TraceContent(AIContentBase):
    """
    XML: <trace name="..." label="..." severity="information" timestamp="...">{value}</trace>
    """
    name: str
    label: Optional[str] = None
    severity: Optional[str] = None
    timestamp: Optional[datetime] = None
    value: Optional[str] = None

    @property
    def kind(self) -> str:
        return "trace"
