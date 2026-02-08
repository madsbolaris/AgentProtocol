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
class AutoToolChoice:
    """
    Tool Choice Behavior
FROM: Azure Agent API (ToolChoiceBehavior)
CONTROLS: How agent uses tools
MESSAGING APP ANALOGY:
- "auto": Bot decides when to use commands
- "required": Bot must use a command
- "none": Bot cannot use commands (text-only response)
- "specific": Force specific command (like /help shortcut)
    """
    kind: str
