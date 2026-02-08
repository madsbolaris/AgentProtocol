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
class Citation:
    """
    Citation
FROM: LLMProxy + Anthropic (search_result_location pattern)
ADDITION: Not in MAF or Azure Agent API
M365: Critical for compliance and attribution
    """
    source: str
    text: Optional[str] = None
    start: int
    end: int
    score: Optional[float] = None
