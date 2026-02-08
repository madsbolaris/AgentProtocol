# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .connection import Connection
from .history_retrieval_options import HistoryRetrievalOptions


@dataclass
class ChatHistoryProviderConfig:
    # Connection configuration (for database/service providers).
ALIGNED WITH: Agent Schema Connection system
    connection: Optional[Connection] = None
    # History retrieval options.
    retrieval_options: Optional[HistoryRetrievalOptions] = None
    # Custom provider configuration.
    config: Optional[Dict[str, Any]] = None
