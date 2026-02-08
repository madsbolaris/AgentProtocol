# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Generated from TypeSpec definitions.
DO NOT EDIT MANUALLY
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .j_s_o_n_schema import JSONSchema


@dataclass
class JSONSchema:
    """
    JSON Schema
FROM: Azure Agent API + JSON Schema Draft 7
REPRESENTS: Parameter schema for tool validation
UNIVERSAL STANDARD: Used by OpenAI, Anthropic, Azure, etc.
    """
    properties: Optional[Dict[str, Any]] = None
    items: Optional[JSONSchema] = None
    required: Optional[List[str]] = None
    description: Optional[str] = None
    format: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    pattern: Optional[str] = None
