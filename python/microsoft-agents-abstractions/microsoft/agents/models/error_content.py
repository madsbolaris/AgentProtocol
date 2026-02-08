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
class ErrorContent(AIContentBase):
    """
    Error Content
BASE: Microsoft.Extensions.AI.ErrorContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/ErrorContent.cs
XML: <error code="..."><message>...</message><stack-trace>...</stack-trace></error>
    """
    code: Optional[str] = None
    message: str
    stack_trace: Optional[str] = None

    @property
    def kind(self) -> str:
        return "error"
