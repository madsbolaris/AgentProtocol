# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .chat_role import ChatRole


@dataclass
class HistoryRetrievalOptions:
    """
    History Retrieval Options
FROM: MAF ChatHistoryProvider filters
SOURCE: /agent-framework/dotnet/src/Microsoft.Agents.AI.Abstractions/ChatHistoryProvider.cs
REPRESENTS: Filters applied when retrieving conversation history
MAF PATTERN: Filter chain to control which history is included
    """
    # Maximum messages to retrieve.
MAF: Message count filter
    max_messages: Optional[int] = None
    # Maximum tokens to include (context window management).
MAF: Token budget filter
    max_tokens: Optional[int] = None
    # Time range filter.
MAF: Time-based filter
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    # Filter by message roles.
EXAMPLES: Only include user/assistant messages, exclude system
    include_roles: Optional[List[ChatRole]] = None
    # Filter by message roles to exclude.
    exclude_roles: Optional[List[ChatRole]] = None
