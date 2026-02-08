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
class HostedFileContent(AIContentBase):
    file_id: str
    filename: Optional[str] = None
    media_type: Optional[str] = None
    size_bytes: Optional[int] = None

    @property
    def kind(self) -> str:
        return "hostedFile"
