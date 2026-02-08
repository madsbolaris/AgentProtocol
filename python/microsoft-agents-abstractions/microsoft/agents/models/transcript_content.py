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
class TranscriptContent(AIContentBase):
    """
    XML: <transcript text="..." language="en" confidence="0.98" speaker="..." />
    """
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    speaker: Optional[str] = None

    @property
    def kind(self) -> str:
        return "transcript"
