# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .chat_role import ChatRole


@dataclass
class ChatMessage(ABC):
    message_id: str
    parent_message_id: Optional[str] = None
    thread_id: Optional[str] = None
    contents: List[AIContent] = field(default_factory=list)
    text: Optional[str] = None
    author_name: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    completion_id: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_representation: Optional[Any] = None

    @property
    @abstractmethod
    def role(self) -> ChatRole:
        """The role of the message sender."""
        ...
