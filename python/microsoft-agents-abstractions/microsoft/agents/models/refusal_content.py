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
class RefusalContent(AIContentBase):
    """
    Refusal Content
FROM: Azure Agent API (RefusalContent)
ADDITION: Not in MAF
RATIONALE: Model refuses to complete request (safety/policy)
M365: Compliance and content policy tracking
XML: <refusal reason="...">Detailed refusal message</refusal>
    """
    reason: str

    @property
    def kind(self) -> str:
        return "refusal"
