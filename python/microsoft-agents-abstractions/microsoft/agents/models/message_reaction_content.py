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

from .message_reaction import MessageReaction


@dataclass
class MessageReactionContent(AIContentBase):
    referenced_message_id: str
    reactions_added: Optional[List[MessageReaction]] = None
    reactions_removed: Optional[List[MessageReaction]] = None

    @property
    def kind(self) -> str:
        return "messageReaction"
