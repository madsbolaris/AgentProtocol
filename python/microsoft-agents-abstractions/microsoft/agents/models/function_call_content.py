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
class FunctionCallContent(AIContentBase):
    """
    Function Call Content
BASE: Microsoft.Extensions.AI.FunctionCallContent
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionCallContent.cs
REPRESENTS: Agent's request to execute a tool
XML: <function-call call-id="..." name="...">{"arg": "value"}</function-call>
    """
    call_id: str
    name: str
    arguments: str

    @property
    def kind(self) -> str:
        return "functionCall"
