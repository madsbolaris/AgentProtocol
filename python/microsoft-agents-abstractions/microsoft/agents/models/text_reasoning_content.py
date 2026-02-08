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
class TextReasoningContent(AIContentBase):
    """
    Text Reasoning Content
BASE: Microsoft.Extensions.AI.TextReasoningContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextReasoningContent.cs
FROM: Extended thinking support (Anthropic, OpenAI o1/o3)
ADDITION: Added 'exposed' flag from Anthropic
- exposed = true: Reasoning visible to user
- exposed = false: Internal reasoning trace
XML: <thinking exposed="false">Internal reasoning...</thinking>
    """
    text: str
    exposed: Optional[bool] = None

    @property
    def kind(self) -> str:
        return "textReasoning"
