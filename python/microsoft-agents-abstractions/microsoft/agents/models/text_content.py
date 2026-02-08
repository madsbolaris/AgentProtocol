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
class TextContent(AIContentBase):
    """
    Text Content
BASE: Microsoft.Extensions.AI.TextContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextContent.cs
XML: <text>Hello world</text>
    """
    text: str

    @property
    def kind(self) -> str:
        return "text"
