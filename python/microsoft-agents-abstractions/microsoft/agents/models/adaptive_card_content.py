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
class AdaptiveCardContent(AIContentBase):
    """
    XML: <adaptive-card version="1.5" fallback-text="...">{"type":"AdaptiveCard",...}</adaptive-card>
    """
    version: Optional[str] = None
    fallback_text: Optional[str] = None
    card: str

    @property
    def kind(self) -> str:
        return "adaptiveCard"
