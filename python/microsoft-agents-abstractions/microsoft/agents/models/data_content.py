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
class DataContent(AIContentBase):
    """
    Data Content
BASE: Microsoft.Extensions.AI.DataContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/DataContent.cs
REPRESENTS: Arbitrary structured data
XML: <data uri="..." mime-type="...">base64data</data>
    """
    uri: Optional[str] = None
    mime_type: Optional[str] = None
    value: Optional[str] = None

    @property
    def kind(self) -> str:
        return "data"
