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
class SearchResultContent(AIContentBase):
    """
    XML: <search-result title="..." url="..." score="0.94"><snippet>...</snippet></search-result>
    """
    title: str
    url: str
    score: Optional[float] = None
    snippet: str

    @property
    def kind(self) -> str:
        return "searchResult"
