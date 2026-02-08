# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class SuggestedAction:
    """
    Suggested Action
Represents a single quick reply button/action
    """
    title: str
    action_type: str
    value: Optional[str] = None
    text: Optional[str] = None
