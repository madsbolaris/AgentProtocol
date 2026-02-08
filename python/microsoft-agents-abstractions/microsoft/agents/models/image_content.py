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
class ImageContent(AIContentBase):
    """
    Image Content
FROM: Azure Agent API (ImageContent)
ADDITION: Not in MAF
Provides three delivery methods: uri, dataUri, or raw data bytes.
M365: Future multi-modal scenarios
XML: <image uri="..." mime-type="..." width="1920" height="1080" />
    """
    uri: Optional[str] = None
    alt: Optional[str] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    @property
    def kind(self) -> str:
        return "image"
