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
class UserInputRequestContent(AIContentBase):
    """
    XML: <user-input-request request-id="..." prompt="..." input-type="choice" required="true" />
    """
    request_id: str
    prompt: str
    input_type: Optional[str] = None
    required: Optional[bool] = None

    @property
    def kind(self) -> str:
        return "userInputRequest"
