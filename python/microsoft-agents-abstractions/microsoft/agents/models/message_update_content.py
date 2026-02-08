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
class MessageUpdateContent(AIContentBase):
    """
    Message Update Content (Message Edit)
FROM: Activity Protocol messageUpdate activity
ADDITION: Not in MAF or Azure Agent API
REPRESENTS: Update to an existing message
MESSAGING APP PATTERN:
- Like editing a message in Slack or Teams
- Message ID references the message to update
- Updated content provided in separate ChatMessage
XML: <message-update message-id="msg_123" reason="typo_fix" />
    """
    message_id: str
    reason: Optional[str] = None

    @property
    def kind(self) -> str:
        return "messageUpdate"
