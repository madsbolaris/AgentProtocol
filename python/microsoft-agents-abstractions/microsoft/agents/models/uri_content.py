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
class UriContent(AIContentBase):
    """
    URI Content
BASE: Microsoft.Extensions.AI.UriContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/UriContent.cs
REPRESENTS: Reference to external content via URI
XML: <uri>https://example.com</uri>
    """
    uri: str

    @property
    def kind(self) -> str:
        return "uri"
