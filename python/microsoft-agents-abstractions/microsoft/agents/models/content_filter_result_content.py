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
class ContentFilterResultContent(AIContentBase):
    """
    Content Filter Result Content
FROM: Azure Agent API (ContentFilterResultContent)
ADDITION: Not in MAF
RATIONALE: Azure content moderation results
M365: Compliance and audit requirements
XML: <content-filter-result filtered="true" category="hate" severity="medium" />
    """
    filtered: bool
    category: str
    severity: str

    @property
    def kind(self) -> str:
        return "filterResult"
