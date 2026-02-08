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
class FunctionResultContent(AIContentBase):
    """
    Function Result Content
BASE: Microsoft.Extensions.AI.FunctionResultContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionResultContent.cs
REPRESENTS: Result of tool execution
XML: <function-result call-id="..." name="...">{"result": "value"}</function-result>
    """
    call_id: Optional[str] = None
    name: Optional[str] = None
    result: str

    @property
    def kind(self) -> str:
        return "functionResult"
