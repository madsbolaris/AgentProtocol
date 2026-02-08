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

from .suggested_action import SuggestedAction


@dataclass
class SuggestedActionsContent(AIContentBase):
    """
    XML: <suggested-actions><action title="Yes" type="message" value="yes" /></suggested-actions>
    """
    actions: List[SuggestedAction] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return "suggestedActions"
