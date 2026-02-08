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
class DocumentContent(AIContentBase):
    """
    XML: <document title="..." document-id="..." source="..." mime-type="..."><content>...</content></document>
    """
    title: str
    document_id: str
    source: str
    mime_type: Optional[str] = None
    content: Optional[str] = None

    @property
    def kind(self) -> str:
        return "document"
