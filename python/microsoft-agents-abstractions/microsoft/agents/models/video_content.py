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
class VideoContent(AIContentBase):
    """
    Video Content
FROM: Azure Agent API (VideoContent)
ADDITION: Not in MAF
Represents video data that can be included in messages.
M365: Multi-modal scenarios (video input, video responses, screen recordings)
XML: <video uri="..." mime-type="..." width="1920" height="1080" duration="120" frame-rate="30" />
    """
    uri: Optional[str] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    frame_rate: Optional[int] = None

    @property
    def kind(self) -> str:
        return "video"
