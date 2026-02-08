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
class WordTiming:
    """
    Word Timing
ADDITION: For synchronized transcript playback
PURPOSE: Word-level timestamps for highlighting during audio/video playback
    """
    word: str
    start: float
    end: float
    confidence: Optional[float] = None
