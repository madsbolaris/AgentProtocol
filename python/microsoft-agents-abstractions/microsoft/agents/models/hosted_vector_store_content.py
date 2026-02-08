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
class HostedVectorStoreContent(AIContentBase):
    vector_store_id: str
    name: Optional[str] = None
    document_count: Optional[int] = None

    @property
    def kind(self) -> str:
        return "hostedVectorStore"
