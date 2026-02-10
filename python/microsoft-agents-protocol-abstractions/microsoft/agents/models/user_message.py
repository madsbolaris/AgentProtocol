# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass

from .chat_message import ChatMessage
from .chat_role import ChatRole


@dataclass
class UserMessage(ChatMessage):
    """
    Message with role 'user'."
    """

    @property
    def role(self) -> ChatRole:
        return ChatRole.USER
