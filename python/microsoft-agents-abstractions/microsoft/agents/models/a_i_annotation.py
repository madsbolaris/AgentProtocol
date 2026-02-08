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
class AIAnnotation:
    """
    AI Annotation
BASE: Microsoft.Extensions.AI.AIAnnotation (base class for annotations)
SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/AIAnnotation.cs
REPRESENTS: Metadata attached to content (e.g., citations)
    """
    type: str
    data: Optional[Dict[str, Any]] = None
