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
class TypingIndicatorContent(AIContentBase):
    """
    XML: <typing-indicator from="user_123" status="typing" timestamp="..." />
    """
    from: str
    timestamp: Optional[datetime] = None

    @property
    def kind(self) -> str:
        return "typingIndicator"
