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
class AudioContent(AIContentBase):
    """
    XML: <audio uri="..." mime-type="..." duration="15" />
    """
    uri: Optional[str] = None
    mime_type: Optional[str] = None
    duration: Optional[int] = None

    @property
    def kind(self) -> str:
        return "audio"
